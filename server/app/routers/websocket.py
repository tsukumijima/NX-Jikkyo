
import asyncio
import json
import random
import time
import traceback
import websockets.exceptions
from datetime import datetime
from fastapi import (
    APIRouter,
    Path,
    Query,
)
from starlette.websockets import (
    WebSocket,
    WebSocketDisconnect,
    WebSocketState,
)
from tortoise import timezone
from tortoise.transactions import in_transaction
from typing import Annotated, cast

from app import logging
from app.constants import (
    REDIS_CHANNEL_THREAD_COMMENTS_PREFIX,
    REDIS_CLIENT,
    REDIS_KEY_JIKKYO_FORCE_COUNT,
    REDIS_KEY_VIEWER_COUNT,
)
from app.models.comment import (
    Comment,
    CommentCounter,
    XMLCompatibleCommentResponse,
    Thread,
)
from app.utils import GenerateClientID


# ルーター
router = APIRouter(
    tags = ['WebSocket'],
    prefix = '/api/v1',
)

# 現在アクティブなスレッドの情報を保存する辞書
__active_threads: dict[int, Thread] = {}


async def GetActiveThread(channel_id_int: int) -> Thread | None:
    """
    現在アクティブな (放送されている) スレッド情報を取得する

    Args:
        channel_id_int (int): 実況チャンネル ID (jk の prefix を取り除いた数値)

    Returns:
        Thread | None: 現在アクティブなスレッドの情報。見つからない場合は None を返す
    """

    # 現在のサーバー時刻 (datetime)
    current_time_datetime = timezone.now()

    # 実況チャンネル ID に対応する現在アクティブなスレッド情報が保存されていないか、キャッシュされたスレッド情報がすでに放送を終了している場合は、
    # 実況チャンネル ID に対応する現在アクティブなスレッド情報を取得し、__active_threads に保存する
    if channel_id_int not in __active_threads or __active_threads[channel_id_int].end_at < current_time_datetime:
        thread = await Thread.filter(
            channel_id = channel_id_int,
            start_at__lte = current_time_datetime,
            end_at__gte = current_time_datetime,
        ).first()

        # 実況チャンネル ID に対応するスレッドが見つからなかった
        if not thread:
            return None

        # キャッシュを新しいスレッド情報で更新
        __active_threads[channel_id_int] = thread
        logging.info(f'GetActiveThread [jk{channel_id_int}]: Active thread has been updated.')

    # 現在アクティブなスレッド情報を取得して返す
    return __active_threads[channel_id_int]


def ConvertToXMLCompatibleCommentResponse(comment: Comment) -> XMLCompatibleCommentResponse:
    """
    コメント情報をニコ生 XML 互換の XMLCompatibleCommentResponse 形式に変換する
    戻り値の辞書は SetYourPostFlag() を通した後、await websocket.send_json() に渡してクライアントに送信できる

    この関数では yourpost フラグは設定されないので、別途 SetYourPostFlag() を通して設定する必要がある
    """

    response: XMLCompatibleCommentResponse = {
        'chat': {
            'thread': str(comment.thread_id),
            'no': comment.no,
            'vpos': comment.vpos,
            'date': int(comment.date.timestamp()),
            'date_usec': int((comment.date.timestamp() - int(comment.date.timestamp())) * 1000000),
            'mail': comment.mail,
            'user_id': comment.user_id,
            'premium': 1 if comment.premium else 0,
            'anonymity': 1 if comment.anonymity else 0,
            'content': comment.content,
        },
    }

    # 数値を返すフィールドは 0 の場合に省略される本家ニコ生の謎仕様に合わせる
    if 'premium' in response['chat'] and response['chat']['premium'] == 0:
        del response['chat']['premium']
    if 'anonymity' in response['chat'] and response['chat']['anonymity'] == 0:
        del response['chat']['anonymity']

    return response


def SetYourPostFlag(response: XMLCompatibleCommentResponse, thread_key: str) -> XMLCompatibleCommentResponse:
    """
    スレッドキーとユーザー ID が一致する場合のみ、コメント情報に yourpost (自分が投稿したコメントかどうか) フラグを設定する
    """

    # スレッドキーとユーザー ID が一致する場合のみ yourpost フラグを設定
    response['chat']['yourpost'] = (1 if thread_key == response['chat']['user_id'] else 0)
    # 数値を返すフィールドは 0 の場合に省略される本家ニコ生の謎仕様に合わせる
    if 'yourpost' in response['chat'] and response['chat']['yourpost'] == 0:
        del response['chat']['yourpost']

    return response


@router.websocket('/channels/{channel_id}/ws/watch')
async def WatchSessionAPI(
    websocket: WebSocket,
    channel_id: Annotated[str, Path(description='実況チャンネル ID 。ex: jk211')],
    thread_id: Annotated[int | None, Query(description='スレッド ID 。過去の特定スレッドの過去ログコメントを取得する際に指定する。')] = None,
):
    """
    ニコ生の視聴セッション WebSocket 互換 API
    """

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得
    try:
        channel_id_int = int(channel_id.replace('jk', ''))
    except ValueError:
        logging.error(f'WatchSessionAPI [{channel_id}]: Invalid channel ID.')
        await websocket.close(code=1008, reason=f'[{channel_id}]: Invalid channel ID.')
        return

    # スレッド ID が指定されていなければ、現在アクティブな (放送中の) スレッドを取得
    if not thread_id:
        thread = await GetActiveThread(channel_id_int)
        if not thread:
            # 存在しないチャンネル ID を指定された場合にも発生して頻度が多すぎるのでログをコメントアウト中
            # logging.error(f'WatchSessionAPI [{channel_id}]: Active thread not found.')
            await websocket.close(code=1002, reason=f'[{channel_id}]: Active thread not found.')
            return

    # スレッド ID が指定されていれば、そのスレッドを取得
    ## 放送開始前のスレッドが指定された場合はエラーを返す
    else:
        thread = await Thread.filter(
            id = thread_id,
            channel_id = channel_id_int,
        ).first()
        if not thread:
            logging.error(f'WatchSessionAPI [{channel_id}]: Thread not found.')
            await websocket.close(code=1002, reason=f'[{channel_id}]: Thread not found.')
            return
        if timezone.now() < thread.start_at:
            logging.error(f'WatchSessionAPI [{channel_id}]: Thread is upcoming.')
            await websocket.close(code=1002, reason=f'[{channel_id}]: Thread is upcoming.')
            return

    # クライアント ID を生成
    ## 同一 IP 同一クライアントからなら UA が変更されない限り同一値になるはず
    watch_session_client_id = GenerateClientID(websocket)
    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} connected.')
    logging.info(f'WatchSessionAPI [{channel_id}]: Thread ID: {thread.id} User-Agent: {websocket.headers.get("User-Agent", "Unknown")}')

    # 接続を受け入れる
    await websocket.accept()

    async def RunReceiverTask() -> None:
        """ クライアントからのメッセージを受信するタスク """

        # 最後にコメントを投稿した時刻
        last_comment_time: float = 0

        # 短期間の荒らし連投によりサイレントにコメントを破棄する一時 BAN 処理が何回行われたかのカウント
        silent_discard_count = 0
        SILENT_DISCARD_COUNT_THRESHOLD = 3  # 3回以上一時 BAN されたら、この WebSocket 接続が切断されるまで永久 BAN する

        while True:

            # クライアントから JSON 形式のメッセージを受信
            try:
                message = await websocket.receive_json()
            except json.JSONDecodeError:
                # JSONとしてデコードできないメッセージが送られてきた場合は単に無視する
                # これには接続を維持しようと空文字列が送られてくるケースを含む
                continue

            try:
                message_type = message.get('type')
            except KeyError:
                # メッセージに type がない場合はエラーを返す
                await websocket.send_json({
                    'type': 'error',
                    'data': {
                        'message': 'INVALID_MESSAGE',
                    },
                })
                continue

            # 視聴開始リクエスト
            ## リクエストの中身は無視して処理を進める
            ## 本家ニコ生では stream オブジェクトがオプションとして渡された際に視聴 URL などを送るが、ここでは常にコメントのみとする
            ## 大元も基本視聴負荷の関係で映像がいらないなら省略してくれという話があった
            if message_type == 'startWatching':

                # 現在のサーバー時刻 (ISO 8601) を送信
                await websocket.send_json({
                    'type': 'serverTime',
                    'data': {
                        'currentMs': timezone.now().isoformat(),
                    },
                })

                # 座席取得が完了した旨を送信
                await websocket.send_json({
                    'type': 'seat',
                    'data': {
                        # 「座席を維持するために送信する keepSeat メッセージ (クライアントメッセージ) の送信間隔時間（秒）」
                        'keepIntervalSec': 30,
                    },
                })

                # スレッドの放送開始時刻・放送終了時刻を送信
                await websocket.send_json({
                    'type': 'schedule',
                    'data': {
                        'begin': thread.start_at.isoformat(),
                        'end': thread.end_at.isoformat(),
                    },
                })

                # リクエスト元の URL を組み立てる
                ## scheme はそのままだと多段プロキシの場合に ws:// になってしまうので、
                ## X-Forwarded-Proto ヘッダから scheme を取得してから URI を組み立てる
                ## X-Forwarded-Proto が https 固定の場合も考慮して wss に変換している
                scheme = websocket.headers.get('X-Forwarded-Proto', websocket.url.scheme).replace('https', 'wss')
                uri = f'{scheme}://{websocket.url.netloc}/api/v1/channels/{channel_id}/ws/comment'

                # コメント部屋情報を送信
                await websocket.send_json({
                    'type': 'room',
                    'data': {
                        'messageServer': {
                            # 「メッセージサーバーの URI (WebSocket)」
                            'uri': uri,
                            # 「メッセージサーバの種類 (現在常に `niwavided`)」
                            'type': 'niwavided',
                        },
                        # 「部屋名」
                        'name': 'アリーナ',
                        # 「メッセージサーバーのスレッド ID」
                        'threadId': str(thread.id),
                        # 「(互換性確保のためのダミー値, 現在常に `true`)」
                        'isFirst': True,
                        # 「(互換性確保のためのダミー文字列)」
                        'waybackkey': 'DUMMY_TOKEN',
                        # 「メッセージサーバーから受信するコメント（chatメッセージ）に yourpost フラグを付けるためのキー。
                        # thread メッセージの threadkey パラメータに設定する」
                        ## NX-Jikkyo ではコメントの user_id に入れられる watch_session_client_id をセットする
                        'yourPostKey': watch_session_client_id,
                        # 「vpos を計算する基準 (vpos:0) となる時刻。(ISO8601 形式)」
                        ## 確か本家ニコ生では番組開始時刻が vpos (相対的なコメント時刻) に入っていたはず (忘れた…)
                        ## NX-Jikkyo でも本家ニコ生同様に番組開始時刻を ISO 8601 形式で入れている
                        'vposBaseTime': thread.start_at.isoformat(),
                    },
                })

                # 視聴の統計情報を送信
                await websocket.send_json({
                    'type': 'statistics',
                    'data': {
                        'viewers': int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, channel_id) or 0),
                        'comments': (await CommentCounter.get(thread_id=thread.id)).max_no,
                        'adPoints': 0,  # NX-Jikkyo では常に 0 を返す
                        'giftPoints': 0,  # NX-Jikkyo では常に 0 を返す
                    },
                })

            # 座席維持リクエスト
            ## 本家ニコ生では keepSeat メッセージが一定期間の間に送られてこなかった場合に接続を切断するが、モックなので今の所何もしない
            elif message_type == 'keepSeat':
                pass

            # pong リクエスト
            ## 本家ニコ生ではサーバーから ping メッセージを送ってから pong メッセージが
            ## 一定期間の間に送られてこなかった場合に接続を切断するが、モックなので今の所何もしない
            elif message_type == 'pong':
                pass

            # コメント投稿リクエスト
            elif message_type == 'postComment':

                # 放送が終了したスレッドにはコメントを投稿できない
                if thread.end_at < timezone.now():
                    await websocket.send_json({
                        'type': 'error',
                        'data': {
                            'message': 'NOT_ON_AIR',
                        },
                    })
                    continue

                try:
                    # 送られてきたリクエストから mail に相当するコメントコマンドを組み立てる
                    # リクエストでは直接は mail は送られてこないので、いい感じに組み立てる必要がある
                    comment_commands: list[str] = []
                    # 匿名フラグが True なら 184 を追加
                    if message['data']['isAnonymous'] is True:
                        comment_commands.append('184')
                    # コメント色コマンド (ex: white) があれば追加
                    if 'color' in message['data']:
                        comment_commands.append(message['data']['color'])
                    # コメント位置コマンド (ex: naka) があれば追加
                    if 'position' in message['data']:
                        comment_commands.append(message['data']['position'])
                    # コメントサイズコマンド (ex: medium) があれば追加
                    if 'size' in message['data']:
                        comment_commands.append(message['data']['size'])
                    # コメントフォントコマンド (ex: defont) があれば追加
                    if 'font' in message['data']:
                        comment_commands.append(message['data']['font'])

                    # 現在のサーバー時刻
                    current_time = time.time()

                    # 0.5 秒以内の連投チェック
                    ## 連投とみなされた場合、レスポンス上はコメント投稿が成功したように見せかけるが、
                    ## 実際にはサイレントにコメントを破棄する (一時 BAN 処理)
                    ## silent_discard_count が SILENT_DISCARD_COUNT_THRESHOLD を超えた場合も同様だが、
                    ## 接続が維持されている限り永久に BAN される点が異なる
                    if ((current_time - last_comment_time) < 0.5) or (silent_discard_count > SILENT_DISCARD_COUNT_THRESHOLD):

                        # 最後のコメント投稿時刻を更新
                        ## コメント投稿処理の成功 or 失敗に関わらず一律で更新する
                        ## これにより、0.5 秒以内の機械的な連投が続く場合に最初の1回以外の全コメントをサイレントに弾ける
                        last_comment_time = current_time

                        # ダミーのコメント投稿結果を返す
                        await websocket.send_json({
                            'type': 'postCommentResult',
                            'data': {
                                'chat': {
                                    'mail': ' '.join(comment_commands),
                                    'anonymity': 1 if message['data']['isAnonymous'] else 0,
                                    'content': message['data']['text'],
                                    'restricted': False,
                                },
                            },
                        })

                        silent_discard_count += 1
                        if silent_discard_count > SILENT_DISCARD_COUNT_THRESHOLD:
                            logging.warning(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id}\'s comment was banned for too many consecutive comments.')
                        else:
                            logging.warning(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} posted a comment too quickly.')
                        continue

                    # 最後のコメント投稿時刻を更新
                    ## コメント投稿処理の成功 or 失敗に関わらず一律で更新する
                    ## これにより、0.5 秒以内の機械的な連投が続く場合に最初の1回以外の全コメントをサイレントに弾ける
                    last_comment_time = current_time

                    # コメントを DB に登録
                    async with in_transaction() as connection:

                        # 採番テーブルに記録されたコメ番をインクリメント
                        await connection.execute_query(
                            'UPDATE comment_counters SET max_no = max_no + 1 WHERE thread_id = %s',
                            [thread.id]
                        )
                        # インクリメント後のコメ番を取得
                        ## 採番テーブルを使うことでコメ番の重複を防いでいる
                        new_no_result = await connection.execute_query_dict(
                            'SELECT max_no FROM comment_counters WHERE thread_id = %s',
                            [thread.id]
                        )
                        new_no = new_no_result[0]['max_no']

                        # 新しいコメントを作成
                        comment = await Comment.create(
                            thread_id = thread.id,
                            no = new_no,
                            vpos = message['data']['vpos'],  # リクエストで与えられた vpos をそのまま入れる
                            mail = ' '.join(comment_commands),  # コメントコマンド (mail) は空白区切りの文字列として組み立てる
                            user_id = watch_session_client_id,  # ユーザー ID は視聴セッションのクライアント ID をそのまま入れる
                            premium = False,  # 簡易実装なのでプレミアム会員判定は省略
                            anonymity = message['data']['isAnonymous'] is True,
                            content = message['data']['text'],
                        )

                    # ニコ生 XML 互換コメント形式に変換した上で、Redis Pub/Sub でコメントを送信
                    ## この段階ではまだ yourpost フラグを設定してはならない
                    ## yourpost フラグはコメントセッション WebSocket 側で設定しないと、意図しないコメントに yourpost フラグが付与されてしまう
                    await REDIS_CLIENT.publish(
                        channel = f'{REDIS_CHANNEL_THREAD_COMMENTS_PREFIX}:{thread.id}',
                        message = json.dumps(ConvertToXMLCompatibleCommentResponse(comment), ensure_ascii=False),
                    )

                    # 実況勢いカウント用の Redis ソート済みセット型にエントリを追加
                    ## スコア (UNIX タイムスタンプ) が現在時刻から 60 秒以内の範囲のエントリの数が実況勢いとなる
                    await REDIS_CLIENT.zadd(f'{REDIS_KEY_JIKKYO_FORCE_COUNT}:{channel_id}', {f'comment:{comment.id}': current_time})

                    # 1/10 の確率で現在時刻から 60 秒以上前のエントリを削除
                    ## 毎回削除する必要はないが (古いエントリが残ったままでもカウントする上では影響しない) 、
                    ## メモリ上に古いエントリが残りすぎないように、定期的に削除する
                    if random.random() < 0.1:
                        await REDIS_CLIENT.zremrangebyscore(f'{REDIS_KEY_JIKKYO_FORCE_COUNT}:{channel_id}', 0, current_time - 60)

                    # 投稿結果を返す
                    await websocket.send_json({
                        'type': 'postCommentResult',
                        'data': {
                            'chat': {
                                # 「コマンド。 `184`, `white`, `naka`, `medium` など」
                                'mail': comment.mail,
                                # 「匿名コメントかどうか。匿名のとき `1`、非匿名のとき `0`」
                                'anonymity': 1 if comment.anonymity else 0,
                                # 「コメント本文」
                                'content': comment.content,
                                # 「コメントを薄く表示するかどうか」
                                ## NX-Jikkyo では常に False を返す
                                'restricted': False,
                            },
                        },
                    })
                    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} posted a comment.')

                # コメント投稿に失敗した場合はエラーを返す
                except Exception:
                    logging.error(f'WatchSessionAPI [{channel_id}]: Failed to post a comment.')
                    logging.error(message)
                    logging.error(traceback.format_exc())
                    await websocket.send_json({
                        'type': 'error',
                        'data': {
                            'message': 'INVALID_MESSAGE',
                        },
                    })

            # 接続が切れたらタスクを終了
            if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                return

    async def RunSenderTask() -> None:
        """ 定期的にサーバーからクライアントにメッセージを送信するタスク """

        # 最後に視聴統計情報を送信した時刻
        last_statistics_time = time.time()
        # 最後にサーバー時刻を送信した時刻
        last_server_time_time = time.time()
        # 最後に ping を送信した時刻
        last_ping_time = time.time()

        # 処理開始時点でスレッドが放送中かどうか
        is_on_air = thread.start_at < timezone.now() < thread.end_at

        while True:

            # 60 秒に 1 回最新の視聴統計情報を送信 (互換性のため)
            if (time.time() - last_statistics_time) > 60:
                await websocket.send_json({
                    'type': 'statistics',
                    'data': {
                        'viewers': int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, channel_id) or 0),
                        'comments': (await CommentCounter.get(thread_id=thread.id)).max_no,
                        'adPoints': 0,  # NX-Jikkyo では常に 0 を返す
                        'giftPoints': 0,  # NX-Jikkyo では常に 0 を返す
                    },
                })
                last_statistics_time = time.time()

            # 45 秒に 1 回サーバー時刻を送信 (互換性のため)
            if (time.time() - last_server_time_time) > 45:
                await websocket.send_json({
                    'type': 'serverTime',
                    'data': {
                        'serverTime': timezone.now().isoformat(),
                    },
                })
                last_server_time_time = time.time()

            # 30 秒に 1 回 ping を送信 (互換性のため)
            if (time.time() - last_ping_time) > 30:
                await websocket.send_json({'type': 'ping'})
                last_ping_time = time.time()

            # 処理開始時点では放送中だった場合のみ、スレッドの放送終了時刻を過ぎたら接続を切断する
            ## 最初から過去のスレッドだった場合は実行しない
            if is_on_air is True and timezone.now() > thread.end_at:
                logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected because the thread ended.')
                await websocket.send_json({
                    'type': 'disconnect',
                    'data': {
                        'reason': 'END_PROGRAM',
                    },
                })
                await websocket.close(code=1000)  # 正常終了扱い
                return

            # 次の実行まで1秒待つ
            await asyncio.sleep(1)

            # 接続が切れたらタスクを終了
            if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                return

    try:

        # 同時接続数カウントを 1 増やす
        await REDIS_CLIENT.hincrby(REDIS_KEY_VIEWER_COUNT, channel_id, 1)

        # クライアントからのメッセージを受信するタスクを実行開始
        receiver_task = asyncio.create_task(RunReceiverTask())

        # 定期的にサーバーからクライアントにメッセージを送信するタスクを実行開始
        sender_task = asyncio.create_task(RunSenderTask())

        # 両方が完了するまで待機
        await asyncio.gather(sender_task, receiver_task)

    except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedOK):
        # 接続が切れた時の処理
        logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected.')

    except websockets.exceptions.WebSocketException:
        # 予期せぬエラー (向こう側のネットワーク接続問題など) で接続が切れた時の処理
        # 念のためこちらからも接続を切断しておく
        logging.error(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected by unexpected error.')
        logging.error(traceback.format_exc())
        await websocket.close(code=1011, reason=f'[{channel_id}]: Unexpected error.')

    except Exception:
        logging.error(f'WatchSessionAPI [{channel_id}]: Error during connection.')
        logging.error(traceback.format_exc())
        await websocket.send_json({
            'type': 'disconnect',
            'data': {
                'reason': 'SERVICE_TEMPORARILY_UNAVAILABLE',
            },
        })
        await websocket.close(code=1011, reason=f'[{channel_id}]: Error during connection.')

    finally:
        # ここまできたら確実に接続が切断されているので同時接続数カウントを 1 減らす
        ## 最低でも 0 未満にはならないようにする
        current_count = int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, channel_id) or 0)
        if current_count > 0:
            await REDIS_CLIENT.hincrby(REDIS_KEY_VIEWER_COUNT, channel_id, -1)


@router.websocket('/channels/{channel_id}/ws/comment')
async def CommentSessionAPI(
    websocket: WebSocket,
    channel_id: Annotated[str, Path(description='実況チャンネル ID 。ex: jk211')],
):
    """
    ニコ生のコメントセッション WebSocket 互換 API の実装
    視聴セッション側と違い明確なドキュメントがないため、本家が動いてない以上手探りで実装するほかない…
    ref: https://qiita.com/pasta04/items/33da06cf3c21e34fc4d1
    ref: https://github.com/xpadev-net/niconicomments/blob/develop/src/%40types/format.legacy.ts
    """

    # コメントセッションはあくまで WebSocket でリクエストされたスレッド ID に基づいて送るので、
    # チャンネル ID はログ出力とフォールバック以外では使わない

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得
    try:
        channel_id_int = int(channel_id.replace('jk', ''))
    except ValueError:
        logging.error(f'CommentSessionAPI [{channel_id}]: Invalid channel ID.')
        await websocket.close(code=1008, reason=f'[{channel_id}]: Invalid channel ID.')
        return

    # クライアント ID を生成
    ## 同一 IP 同一クライアントからなら UA が変更されない限り同一値になるはず
    comment_session_client_id = GenerateClientID(websocket)
    logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} connected.')
    logging.info(f'CommentSessionAPI [{channel_id}]: User-Agent: {websocket.headers.get("User-Agent", "Unknown")}')

    # 接続を受け入れる
    await websocket.accept()

    # 指定されたスレッドの新着コメントがあれば随時送信するタスク
    sender_task: asyncio.Task[None] | None = None

    async def RunReceiverTask() -> None:
        """
        クライアントからのメッセージを受信するタスク

        本家ニコ生では以下のような謎構造のメッセージ (ping / thread コマンド) をコメントセッション (コメントサーバー) に送ることでコメント受信が始まる
        NX-Jikkyo でもこの挙動をなんとなく再現する (詳細な仕様は本家が死んでるのでわかりません！生放送と過去ログでも微妙に違う…)
        [
            {ping: {content: 'rs:0'}},
            {ping: {content: 'ps:0'}},
            {
                thread: {
                    version: '20061206',  // 設定必須
                    thread: 'THREAD_ID',  // スレッド ID
                    threadkey: 'THREAD_KEY',  // スレッドキー
                    user_id: '',  // ユーザー ID（設定不要らしい）
                    res_from: -100,  // 最初にコメントを 100 個送信する
                }
            },
            {ping: {content: 'pf:0'}},
            {ping: {content: 'rf:0'}},
        ]
        """

        nonlocal sender_task

        while True:

            # クライアントから JSON 形式のメッセージを受信
            try:
                messages = await websocket.receive_json()
            except json.JSONDecodeError:
                # JSONとしてデコードできないメッセージが送られてきた場合は単に無視する
                # これには接続を維持しようと空文字列が送られてくるケースも含む
                continue

            # リストでなかった場合はエラーを返す
            if not isinstance(messages, list):
                logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message ({messages} not list).')
                await websocket.close(code=1008, reason=f'[{channel_id}]: Invalid message ({messages} not list).')
                return

            # 送られてくるメッセージは必ず list[dict[str, Any]] となる
            for message in messages:

                # もし辞書型でなかった場合はエラーを返す
                if not isinstance(message, dict):
                    logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message ({message} not dict).')
                    await websocket.close(code=1008, reason=f'[{channel_id}]: Invalid message ({message} not dict).')
                    return

                # ping コマンド
                if 'ping' in message:

                    # ping の名の通り、受け取った ping メッセージをそのままクライアントに送信するのが正しい挙動っぽい
                    ## 例えばコマンドが ping(rs:0), ping(ps:0), thread, ping(pf:0), ping(rf:0) の順で送られてきた場合、
                    ## コマンドのレスポンスは ping(rs:0), ping(ps:0), thread, chat(複数), ping(pf:0), ping(rf:0) の順で送信される
                    ## この挙動を利用すると、送られてくる chat メッセージがどこまで初回取得コメントかをクライアント側で判定できる
                    ## ref: https://scrapbox.io/rinsuki/%E3%83%8B%E3%82%B3%E3%83%8B%E3%82%B3%E7%94%9F%E6%94%BE%E9%80%81%E3%81%AE%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%82%92%E5%8F%96%E3%82%8B
                    await websocket.send_json(message)

                # thread コマンド
                if 'thread' in message:
                    try:

                        # thread: スレッド ID
                        if 'thread' in message['thread'] and message['thread']['thread'] != '':
                            thread_id = int(message['thread']['thread'])
                        else:
                            # スレッド ID が省略されたとき、現在アクティブな (放送中の) スレッドの ID を取得 (NX-Jikkyo 独自仕様)
                            ## 旧ニコ生のコメントサーバーではスレッド ID の指定は必須だった
                            ## スレッド ID に空文字が指定された場合も同様に処理する
                            thread = await GetActiveThread(channel_id_int)
                            if not thread:
                                logging.error(f'CommentSessionAPI [{channel_id}]: Active thread not found.')
                                await websocket.close(code=1002, reason=f'[{channel_id}]: Active thread not found.')
                                return
                            thread_id = thread.id
                        logging.info(f'CommentSessionAPI [{channel_id}]: Thread ID: {thread_id}')

                        # res_from: 初回にクライアントに送信する最新コメントの数
                        ## res_from が正の値になることはない (はず)
                        res_from = int(message['thread']['res_from'])
                        if res_from > 0:  # 1 以上の res_from には非対応 (本家ニコ生では正の値が来た場合コメ番換算で取得するらしい？)
                            logging.error(f'CommentSessionAPI [{channel_id}]: Invalid res_from: {res_from}')
                            await websocket.close(code=1008, reason=f'[{channel_id}]: Invalid res_from: {res_from}')
                            return

                        # threadkey: スレッドキー
                        ## 視聴セッション WebSocket の "room" メッセージから返される yourPostKey と同一
                        ## NX-Jikkyo では (コメントに user_id としてセットされる) watch_session_client_id を yourPostKey として返却している
                        if 'threadkey' in message['thread']:
                            thread_key = str(message['thread']['threadkey'])
                        else:
                            # 過去ログ取得時などで threadkey が指定されていない場合、空文字とする
                            thread_key = ''

                        # when: 取得するコメントの投稿日時の下限を示す UNIX タイムスタンプ
                        ## 過去ログ取得時のみ設定される
                        ## 例えば when が 2024-01-01 00:00:00 の場合、2023-12-31 23:59:59 までに投稿されたコメントから
                        ## res_from 件分だけコメント投稿時刻順に後ろから遡ってコメントを取得する
                        if 'when' in message['thread']:
                            when = datetime.fromtimestamp(message['thread']['when'])
                        else:
                            when = None

                    except Exception:
                        # 送られてきた thread コマンドの形式が不正
                        logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message.')
                        logging.error(message)
                        logging.error(traceback.format_exc())
                        await websocket.close(code=1008, reason=f'[{channel_id}]: Invalid message.')
                        return

                    # ここまできたらスレッド ID と res_from が取得できているので、当該スレッドの情報を取得
                    thread = await Thread.filter(id=thread_id).first()
                    if not thread:
                        # 指定された ID と一致するスレッドが見つからない
                        logging.error(f'CommentSessionAPI [{channel_id}]: Active thread not found.')
                        await websocket.close(code=1002, reason=f'[{channel_id}]: Active thread not found.')
                        return

                    # 当該スレッドの最新 res_from 件のコメントを取得
                    ## when が設定されている場合のみ、when より前のコメントを取得
                    if when is not None:
                        comments = await Comment.filter(thread_id=thread.id, date__lt=when).order_by('-id').limit(abs(res_from))  # res_from を正の値に変換
                    else:
                        comments = await Comment.filter(thread_id=thread.id).order_by('-id').limit(abs(res_from))  # res_from を正の値に変換
                    ## コメントを新しい順 (降順) に取得したので、古い順 (昇順) に並べ替える
                    comments.reverse()

                    # 取得したコメントの最後のコメ番を取得 (なければ -1)
                    last_comment_no = comments[-1].no if len(comments) > 0 else -1

                    # スレッド情報を送る
                    ## この辺フォーマットがよくわからないので本家ニコ生と合ってるか微妙…
                    await websocket.send_json({
                        'thread': {
                            "resultcode": 0,  # 成功
                            "thread": str(thread_id),
                            "last_res": last_comment_no,
                            "ticket": "0x12345678",  # よくわからん値だが NX-Jikkyo では固定値とする
                            "revision": 1,  # よくわからん値だが NX-Jikkyo では固定値とする
                            "server_time": int(time.time()),
                        },
                    })
                    logging.info(f'CommentSessionAPI [{channel_id}]: Thread info sent. thread: {thread_id} / last_res: {last_comment_no}')

                    # 初回取得コメントを連続送信する
                    ## XML 互換データ形式に変換した後、必要に応じて yourpost フラグを設定してから送信している
                    for comment in comments:
                        await websocket.send_json(SetYourPostFlag(ConvertToXMLCompatibleCommentResponse(comment), thread_key))

                    # when が指定されている場合は放送中かに関わらずここで終了し、次のコマンドを待ち受ける
                    ## when は取得するコメントの投稿日時の下限を示す UNIX タイムスタンプなので、指定時刻以降のコメントを送信する必要はない
                    if when is not None:
                        continue

                    # スレッドが放送中の場合のみ、指定されたスレッドの新着コメントがあれば随時配信するタスクを非同期で実行開始
                    ## このとき、既に他のスレッドの最新コメント配信タスクが起動していた場合はキャンセルして停止させてから実行する
                    ## 過去ログの場合はすでに放送が終わっているのでこの処理は行わない
                    if thread.start_at.timestamp() < time.time() < thread.end_at.timestamp():
                        if sender_task is not None:
                            sender_task.cancel()
                        sender_task = asyncio.create_task(RunSenderTask(thread, thread_key))

            # 接続が切れたらタスクを終了
            if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                return

    async def RunSenderTask(thread: Thread, thread_key: str) -> None:
        """
        指定されたスレッドの新着コメントがあれば随時配信するタスク
        thread コマンドで指定されたスレッドが現在放送中であることを前提に、RunReceiverTask() 側で初回送信した以降のコメントをリアルタイムに配信する

        Args:
            thread (Thread): 新着コメントの取得対象のスレッド情報
            thread_key (str): スレッドキー (互換性のためにこの名前になっているが、実際には接続先クライアントの watch_session_client_id)
        """

        # Redis Pub/Sub で指定スレッドに投稿されたコメントの購読を開始する
        pubsub = REDIS_CLIENT.pubsub()
        await pubsub.subscribe(f'{REDIS_CHANNEL_THREAD_COMMENTS_PREFIX}:{thread.id}')

        # スレッドの放送終了時刻の Unix 時間
        thread_end_time = thread.end_at.timestamp()

        try:
            while True:

                # 最新コメントを Redis Pub/Sub から随時取得
                ## この get_message() は最大 5 秒間コメントの受信を待機し、5 秒間に一度もコメントがなかった場合は None を返す
                ## こうすることで、可能な限りループ回数を削減して負荷を削減しつつ、5 秒に 1 回は確実に接続確認処理を回せるようになる
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)
                if message is not None:

                    # 取得したコメントに必要に応じて yourpost フラグを設定してから送信
                    xml_compatible_comment: XMLCompatibleCommentResponse = json.loads(message['data'])
                    await websocket.send_json(SetYourPostFlag(xml_compatible_comment, thread_key))

                # 接続が切れたらタスクを終了
                ## 通常は Receiver Task 側で接続切断を検知した後このタスク自体がキャンセルされるため、ここには到達しないはず
                if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                    return

                # 最新コメント配信中に当該スレッドの放送終了時刻を過ぎた場合は接続を切断する
                if time.time() > thread_end_time:
                    logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected because the thread ended.')
                    await websocket.close(code=1000)  # 正常終了扱い
                    return

        # タスク終了時に確実に Redis Pub/Sub の購読を解除する
        finally:
            await pubsub.unsubscribe(f'{REDIS_CHANNEL_THREAD_COMMENTS_PREFIX}:{thread.id}')
            await pubsub.close()

    try:

        # クライアントからのメッセージを受信するタスクの実行が完了するまで待機
        ## サーバーからクライアントにメッセージを送信するタスクは必要に応じて起動される
        await RunReceiverTask()

    except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedOK):
        # 接続が切れた時の処理
        logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected.')

    except websockets.exceptions.WebSocketException:
        # 予期せぬエラー (向こう側のネットワーク接続問題など) で接続が切れた時の処理
        # 念のためこちらからも接続を切断しておく
        logging.error(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected by unexpected error.')
        logging.error(traceback.format_exc())
        await websocket.close(code=1011, reason=f'[{channel_id}]: Unexpected error.')

    except Exception:
        logging.error(f'CommentSessionAPI [{channel_id}]: Error during connection.')
        logging.error(traceback.format_exc())
        await websocket.close(code=1011, reason=f'[{channel_id}]: Error during connection.')

    # コメントセッション WebSocket の接続切断時、Receiver Task 内から起動した
    # Sender Task を確実に終了する
    ## WebSocket の切断に気づくのは通常 Receiver Task の方が速いので、明示的に実行中の Sender Task をキャンセルする必要がある
    finally:
        if sender_task is not None:
            sender_task = cast(asyncio.Task[None], sender_task)
            sender_task.cancel()
            try:
                await sender_task
            except asyncio.CancelledError:
                pass
