
import asyncio
import json
import time
import traceback
import uuid
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
from typing import Annotated

from app import logging
from app.constants import REDIS_CLIENT, REDIS_VIEWER_COUNT_KEY
from app.models.comment import (
    Comment,
    CommentCounter,
    Thread,
)


# ルーター
router = APIRouter(
    tags = ['WebSocket'],
    prefix = '/api/v1',
)


@router.websocket('/channels/{channel_id}/ws/watch')
async def WatchSessionAPI(
    websocket: WebSocket,
    channel_id: Annotated[str, Path(description='実況チャンネル ID 。ex: jk211')],
    thread_id: Annotated[int | None, Query(description='スレッド ID 。過去の特定スレッドの過去ログコメントを取得する際に指定する。')] = None,
):
    """
    ニコ生の視聴セッション Web Socket 互換 API
    """

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得
    try:
        channel_id_int = int(channel_id.replace('jk', ''))
    except ValueError:
        logging.error(f'WatchSessionAPI [{channel_id}]: Invalid channel ID.')
        await websocket.close(code=4001)
        return

    # スレッド ID が指定されていなければ、現在アクティブな (放送中の) スレッドを取得
    if not thread_id:
        now = timezone.now()
        thread = await Thread.filter(
            channel_id = channel_id_int,
            start_at__lte = now,
            end_at__gte = now
        ).first()
        if not thread:
            logging.error(f'WatchSessionAPI [{channel_id}]: Active thread not found.')
            await websocket.close(code=4404)
            return

    # スレッド ID が指定されていれば、そのスレッドを取得
    ## 放送開始前のスレッドが指定された場合はエラーを返す
    else:
        thread = await Thread.filter(
            id=thread_id,
            channel_id=channel_id_int,
        ).first()
        if not thread:
            logging.error(f'WatchSessionAPI [{channel_id}]: Thread not found.')
            await websocket.close(code=4404)
            return
        if timezone.now() < thread.start_at:
            logging.error(f'WatchSessionAPI [{channel_id}]: Thread is upcoming.')
            await websocket.close(code=4404)
            return

    # クライアントごとにユニークな ID を割り当てる
    watch_session_client_id = str(uuid.uuid4())
    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} connected.')
    logging.info(f'WatchSessionAPI [{channel_id}]: Thread ID: {thread.id} User-Agent: {websocket.headers.get("User-Agent", "Unknown")}')

    # 接続を受け入れる
    await websocket.accept()

    async def RunReceiverTask():
        """ クライアントからのメッセージを受信するタスク """

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

                # 現在のサーバー時刻 (ISO 8601) を返す
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
                        'viewers': int(await REDIS_CLIENT.hget(REDIS_VIEWER_COUNT_KEY, channel_id) or 0),
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
                            thread = thread,
                            no = new_no,
                            vpos = message['data']['vpos'],  # リクエストで与えられた vpos をそのまま入れる
                            mail = ' '.join(comment_commands),  # コメントコマンド (mail) は空白区切りの文字列として組み立てる
                            user_id = watch_session_client_id,  # ユーザー ID は視聴セッションのクライアント ID をそのまま入れる
                            premium = False,  # 簡易実装なのでプレミアム会員判定は省略
                            anonymity = message['data']['isAnonymous'] is True,
                            content = message['data']['text'],
                        )

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
                    logging.error(f'WatchSessionAPI [{channel_id}]: Invalid message.')
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

    async def RunSenderTask():
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
                        'viewers': int(await REDIS_CLIENT.hget(REDIS_VIEWER_COUNT_KEY, channel_id) or 0),
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
                await websocket.close(code=1011)
                return

            # 接続が切れたらタスクを終了
            if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                return

            # 次の実行まで1秒待つ
            await asyncio.sleep(1)

    try:

        # 同時接続数カウントを 1 増やす
        await REDIS_CLIENT.hincrby(REDIS_VIEWER_COUNT_KEY, channel_id, 1)

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
        await websocket.close(code=1011)

    except Exception:
        logging.error(f'WatchSessionAPI [{channel_id}]: Error during connection.')
        logging.error(traceback.format_exc())
        await websocket.send_json({
            'type': 'disconnect',
            'data': {
                'reason': 'SERVICE_TEMPORARILY_UNAVAILABLE',
            },
        })
        await websocket.close(code=1011)

    finally:
        # ここまできたら確実に接続が切断されているので同時接続数カウントを 1 減らす
        ## 最低でも 0 未満にはならないようにする
        current_count = int(await REDIS_CLIENT.hget(REDIS_VIEWER_COUNT_KEY, channel_id) or 0)
        if current_count > 0:
            await REDIS_CLIENT.hincrby(REDIS_VIEWER_COUNT_KEY, channel_id, -1)


@router.websocket('/channels/{channel_id}/ws/comment')
async def CommentSessionAPI(
    websocket: WebSocket,
    channel_id: Annotated[str, Path(description='実況チャンネル ID 。ex: jk211')],
):
    """
    ニコ生のコメントセッション Web Socket 互換 API の実装
    視聴セッション側と違い明確なドキュメントがないため、本家が動いてない以上手探りで実装するほかない…
    ref: https://qiita.com/pasta04/items/33da06cf3c21e34fc4d1
    ref: https://github.com/xpadev-net/niconicomments/blob/develop/src/%40types/format.legacy.ts
    """

    # コメントセッションはあくまで WebSocket でリクエストされたスレッド ID に基づいて送るので、
    # チャンネル ID はログ出力以外では使わない

    # クライアントごとにユニークな ID を割り当てる
    comment_session_client_id = str(uuid.uuid4())
    logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} connected.')
    logging.info(f'CommentSessionAPI [{channel_id}]: User-Agent: {websocket.headers.get("User-Agent", "Unknown")}')

    # 接続を受け入れる
    await websocket.accept()

    async def SendCommentToClient(active_thread: Thread, thread_key: str, comment: Comment):
        """ 受信コメントをクライアント側に送信する """
        response = {
            'chat': {
                'thread': str(active_thread.id),
                'no': comment.no,
                'vpos': comment.vpos,
                'date': int(comment.date.timestamp()),
                'date_usec': int((comment.date.timestamp() - int(comment.date.timestamp())) * 1_000_000),
                'mail': comment.mail,
                'user_id': comment.user_id,
                'premium': 1 if comment.premium else 0,
                'anonymity': 1 if comment.anonymity else 0,
                'content': comment.content,
            },
        }
        # 数値を返すフィールドは 0 の場合に省略される本家ニコ生の謎仕様に合わせる
        if response['chat']['premium'] == 0:
            del response['chat']['premium']
        if response['chat']['anonymity'] == 0:
            del response['chat']['anonymity']
        # スレッドキーとユーザー ID が一致する場合のみ yourpost フラグを設定
        if thread_key == comment.user_id:
            response['chat']['yourpost'] = 1
        # コメントを送信
        await websocket.send_json(response)

    async def RunReceiverTask():
        """
        クライアントからのメッセージを受信するタスク

        本家ニコ生では以下のような謎構造のメッセージ (スレッドコマンド) をコメントセッション (コメントサーバー) に送ることでコメント受信が始まる
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

        # スレッド ID
        thread_id: int | None = None
        # スレッドキー
        thread_key: str | None = None
        # 初回にクライアントに送信する最新コメントの数
        res_from: int | None = None
        # 取得するコメントの投稿日時の下限
        when: datetime | None = None
        # コマンドのカウント
        command_count: int = 0
        # 指定されたスレッドの新着コメントがあれば随時送信するタスク
        sender_task: asyncio.Task[None] | None = None

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
                await websocket.close(code=4001)
                return

            # 送られてくるメッセージは必ず list[dict[str, Any]] となる
            for message in messages:

                # もし辞書型でなかった場合はエラーを返す
                if not isinstance(message, dict):
                    logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message ({message} not dict).')
                    await websocket.close(code=4001)
                    return

                # ping コマンド
                if 'ping' in message:
                    # 仕様がよくわからないので当面無視
                    continue

                # スレッドコマンド
                if 'thread' in message:
                    try:

                        # thread: スレッド ID
                        thread_id = int(message['thread']['thread'])
                        logging.info(f'CommentSessionAPI [{channel_id}]: Thread ID: {thread_id}')

                        # res_from: 初回にクライアントに送信する最新コメントの数
                        ## res_from が正の値になることはない (はず)
                        res_from = int(message['thread']['res_from'])
                        if res_from > 0:  # 1 以上の res_from には非対応 (本家ニコ生では正の値が来た場合コメ番換算で取得するらしい？)
                            logging.error(f'CommentSessionAPI [{channel_id}]: Invalid res_from: {res_from}')
                            await websocket.close(code=4001)
                            return

                        # threadkey: スレッドキー
                        ## 視聴セッション側の yourPostKey と同一
                        ## NX-Jikkyo では (コメントに user_id としてセットされる) watch_session_client_id がセットされている
                        ## 過去ログ取得時は設定されないため、その場合は空文字とする
                        if 'threadkey' in message['thread']:
                            thread_key = str(message['thread']['threadkey'])
                        else:
                            thread_key = ''

                        # when: 取得するコメントの投稿日時の下限を示す UNIX タイムスタンプ
                        ## 過去ログ取得時のみ設定される
                        ## 例えば when が 2024-01-01 00:00:00 の場合、2023-12-31 23:59:59 までに投稿されたコメントから
                        ## res_from 件分だけコメント投稿時刻順に後ろから遡ってコメントを取得する
                        if 'when' in message['thread']:
                            when = datetime.fromtimestamp(message['thread']['when'])

                    except Exception:
                        # 送られてきたスレッドコマンドの形式が不正
                        logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message.')
                        logging.error(message)
                        logging.error(traceback.format_exc())
                        await websocket.close(code=4001)
                        return

                    # ここまできたらスレッド ID と res_from が取得できているので、当該スレッドの情報を取得
                    active_thread = await Thread.filter(id=thread_id).first()
                    if not active_thread:
                        # 指定された ID と一致するスレッドが見つからない
                        logging.error(f'CommentSessionAPI [{channel_id}]: Active thread not found.')
                        await websocket.close(code=4404)
                        return

                    # 当該スレッドの最新 res_from 件のコメントを取得して送信
                    ## when が設定されている場合のみ、when より前のコメントを取得して送信
                    if when is not None:
                        comments = await Comment.filter(thread=active_thread, date__lt=when).order_by('-id').limit(abs(res_from))  # res_from を正の値に変換
                    else:
                        comments = await Comment.filter(thread=active_thread).order_by('-id').limit(abs(res_from))  # res_from を正の値に変換

                    # コメントを新しい順 (降順) に取得したので、古い順 (昇順) に並べ替える
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

                    # この rs,ps,pf,rf の謎コマンドに挟んでコメントを送るのが重要
                    ## : の後の数字は何回か送るごとに5ずつ増えるらしい…？
                    ## ref: https://qiita.com/kumaS-kumachan/items/706123c9a4a5aff5517c
                    await websocket.send_json({'ping': {'content': f'rs:{command_count}'}})
                    await websocket.send_json({'ping': {'content': f'ps:{command_count}'}})
                    for comment in comments:
                        await SendCommentToClient(active_thread, thread_key, comment)
                    await websocket.send_json({'ping': {'content': f'pf:{command_count}'}})
                    await websocket.send_json({'ping': {'content': f'rf:{command_count}'}})  # クライアントはこの謎コマンドを受信し終えたら初期コメントの受信が完了している
                    command_count += 5  # 新着コメントを全て送ったので、次送信要求が来た場合は5増やす

                    # 最後にクライアントに送信したコメントの ID
                    ## コメ番は (整合性を担保しようとしているとはいえ) ID ほど厳格ではないので、コメ番ではなく ID ベースでコメント取得時に絞り込む
                    ## 初回取得時のコメントが空の場合、現在当該スレッドに1つもコメントが投稿されていない状態を意味する
                    last_sent_comment_id = comments[-1].id if len(comments) > 0 else 0

                    # when が指定されている場合は放送中かに関わらずここで終了し、次のコマンドを待ち受ける
                    ## when は取得するコメントの投稿日時の下限を示す UNIX タイムスタンプなので、指定時刻以降のコメントを送信する必要はない
                    if when is not None:
                        continue

                    # スレッドが放送中の場合のみ、指定されたスレッドの新着コメントがあれば随時送信するタスクを非同期で実行開始
                    ## このとき、既に他のスレッド用にタスクが起動していた場合はキャンセルして停止させてから実行する
                    ## 過去ログの場合はすでに放送が終わっているのでこの処理は行わない
                    if active_thread.start_at.timestamp() < time.time() < active_thread.end_at.timestamp():
                        if sender_task is not None:
                            sender_task.cancel()
                        sender_task = asyncio.create_task(RunSenderTask(active_thread, thread_key, last_sent_comment_id))

            # 接続が切れたらタスクを終了
            if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                return

    async def RunSenderTask(active_thread: Thread, thread_key: str, last_sent_comment_id: int):
        """
        指定されたスレッドの新着コメントがあれば随時送信するタスク
        スレッドコマンドで指定されたスレッドが現在放送中の場合のみ、初回に送ったコメントの続きをリアルタイムに送信する

        Args:
            active_thread (Thread): スレッド
            thread_key (str): スレッドキー
            last_sent_comment_id (int): 最後にクライアントに送信したコメントの ID
        """

        while True:

            # 最後に取得したコメント ID 以降のコメントを最大 10 件まで取得
            ## 常に limit 句をつけた方がパフォーマンスが上がるらしい？
            comments = await Comment.filter(thread=active_thread, id__gt=last_sent_comment_id).order_by('-id').limit(10)

            # コメントを新しい順 (降順) に取得したので、古い順 (昇順) に並べ替える
            comments.reverse()

            # 取得したコメントを随時送信
            for comment in comments:
                await SendCommentToClient(active_thread, thread_key, comment)
                # 最後にクライアントに送信したコメントの ID を更新
                last_sent_comment_id = comment.id

            # 接続が切れたらタスクを終了
            if websocket.client_state == WebSocketState.DISCONNECTED or websocket.application_state == WebSocketState.DISCONNECTED:
                return

            # 少し待機してから次のループへ
            await asyncio.sleep(0.1)

    try:

        # クライアントからのメッセージを受信するタスクの実行が完了するまで待機
        # サーバーからクライアントにメッセージを送信するタスクは必要に応じて起動される
        await asyncio.create_task(RunReceiverTask())

    except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedOK):
        # 接続が切れた時の処理
        logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected.')

    except websockets.exceptions.WebSocketException:
        # 予期せぬエラー (向こう側のネットワーク接続問題など) で接続が切れた時の処理
        # 念のためこちらからも接続を切断しておく
        logging.error(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected by unexpected error.')
        logging.error(traceback.format_exc())
        await websocket.close(code=1011)

    except Exception:
        logging.error(f'CommentSessionAPI [{channel_id}]: Error during connection.')
        logging.error(traceback.format_exc())
        await websocket.close(code=1011)
