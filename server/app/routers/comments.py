
import hashlib
import time
import traceback
import uuid
from datetime import datetime
from fastapi import (
    APIRouter,
    Path,
    Request,
    Response,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from tortoise import connections
from typing import Annotated, cast
from zoneinfo import ZoneInfo

from app import logging
from app.constants import LOGO_DIR, VERSION
from app.models.comment import (
    ChannelResponse,
    Comment,
    Thread,
    ThreadResponse,
)


# ルーター
router = APIRouter(
    tags = ['Comments'],
    prefix = '/api/v1',
)

# 実況チャンネルごとの来場者数カウント
## 本家ニコ生は statistics メッセージで来場者数 (リアルタイムではなく番組累計) を送っている
## NX-Jikkyo ではリアルタイム来場者数を送るようにしている
__viewer_counts: dict[str, int] = {}


@router.get(
    '/channels',
    summary = 'チャンネル情報 API',
    response_description = 'チャンネル情報。',
    response_model = list[ChannelResponse],
)
async def ChannelsAPI():

    # ID 昇順、スレッドは新しい順でチャンネルを取得
    connection = connections.get('default')
    channels = await connection.execute_query_dict(
        '''
        SELECT
            c.id,
            c.name,
            c.description,
            t.id AS thread_id,
            t.start_at,
            t.end_at,
            t.duration,
            t.title,
            t.description AS thread_description,
            COUNT(com.id) AS comments_count,
            SUM(CASE WHEN com.date >= NOW() - INTERVAL 60 SECOND THEN 1 ELSE 0 END) AS jikkyo_force
        FROM channels c
        LEFT JOIN threads t ON c.id = t.channel_id
        LEFT JOIN comments com ON t.id = com.thread_id
        GROUP BY c.id, c.name, c.description, t.id, t.start_at, t.end_at, t.duration, t.title, t.description
        ORDER BY c.id ASC, t.start_at ASC
        '''
    )

    # チャンネルごとに
    response: list[ChannelResponse] = []
    current_channel_id: int | None = None
    current_channel_name: str | None = None
    current_channel_description: str | None = None
    threads: list[ThreadResponse] = []
    for row in channels:
        if current_channel_id != row['id']:
            if current_channel_id is not None:
                response.append(ChannelResponse(
                    id = f'jk{current_channel_id}',
                    name = cast(str, current_channel_name),
                    description = cast(str, current_channel_description),
                    threads = threads,
                ))
            current_channel_id = cast(int, row['id'])
            current_channel_name = cast(str, row['name'])
            current_channel_description = cast(str, row['description'])
            threads = []

        thread = ThreadResponse(
            id = cast(int, row['thread_id']),
            start_at = row['start_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo')),
            end_at = row['end_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo')),
            duration = cast(int, row['duration']),
            title = cast(str, row['title']),
            description = cast(str, row['thread_description']),
            jikkyo_force = cast(int, row['jikkyo_force']),
            viewers = __viewer_counts.get(f'jk{current_channel_id}', 0),
            comments = cast(int, row['comments_count']),
        )

        threads.append(thread)

    if current_channel_id is not None:
        response.append(ChannelResponse(
            id = f'jk{current_channel_id}',
            name = cast(str, current_channel_name),
            description = cast(str, current_channel_description),
            threads = threads,
        ))

    return response


@router.get(
    '/channels/{channel_id}/logo',
    summary = 'チャンネルロゴ API',
    response_class = Response,
    responses = {
        status.HTTP_200_OK: {
            'description': 'チャンネルロゴ。',
            'content': {'image/png': {}},
        }
    }
)
async def ChannelLogoAPI(
    request: Request,
    channel_id: Annotated[str, Path(description='チャンネル ID 。ex: jk101')],
):
    """
    指定されたチャンネルに紐づくロゴを取得する。
    """

    def GetETag(logo_data: bytes) -> str:
        """ ロゴデータのバイナリから ETag を生成する """
        return hashlib.sha256(logo_data).hexdigest()

    # HTTP レスポンスヘッダーの Cache-Control の設定
    ## 1ヶ月キャッシュする
    CACHE_CONTROL = 'public, no-transform, immutable, max-age=2592000'

    # ***** 同梱のロゴを利用（存在する場合）*****

    # 同梱されているロゴがあれば取得する (ない場合は None が返る)
    logo_path = LOGO_DIR / f'{channel_id}.png'
    if logo_path.exists():

        # リクエストに If-None-Match ヘッダが存在し、ETag が一致する場合は 304 を返す
        ## ETag はロゴファイルのパスとバージョン情報のハッシュから生成する
        etag = GetETag(f'{logo_path}{VERSION}'.encode())
        if request.headers.get('If-None-Match') == etag:
            return Response(status_code=304)

        # ロゴデータを返す
        return FileResponse(logo_path, headers={
            'Cache-Control': CACHE_CONTROL,
            'ETag': etag,
        })

    # ***** デフォルトのロゴ画像を利用 *****

    # 同梱のロゴファイルも Mirakurun や EDCB からのロゴもない場合は、デフォルトのロゴ画像を返す
    return FileResponse(LOGO_DIR / 'default.png', headers={
        'Cache-Control': CACHE_CONTROL,
        'ETag': GetETag('default'.encode()),
    })


@router.websocket('/channels/{channel_id}/ws/watch')
async def WatchSessionAPI(channel_id: str, websocket: WebSocket):
    """ ニコ生の視聴セッション Web Socket 互換 API """

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得
    try:
        channel_id_int = int(channel_id.replace('jk', ''))
    except ValueError:
        logging.error(f'WatchSessionAPI [{channel_id}]: Invalid channel ID.')
        await websocket.close(code=4001)
        return

    # 現在アクティブな (開催中の) スレッドを取得
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    active_thread = await Thread.filter(
        channel_id = channel_id_int,
        start_at__lte = now,
        end_at__gte = now
    ).first()
    if not active_thread:
        logging.error(f'WatchSessionAPI [{channel_id}]: Active thread not found.')
        await websocket.close(code=4404)
        return

    # クライアントごとにユニークな ID を割り当てる
    watch_session_client_id = str(uuid.uuid4())
    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} connected.')

    # 接続を受け入れる
    await websocket.accept()

    try:
        # 最後に視聴統計情報を送信した時刻を取得
        last_statistics_time = time.time()
        # 最後にサーバー時刻を送信した時刻を取得
        last_server_time_time = time.time()
        # 最後に ping を送信した時刻を取得
        last_ping_time = time.time()
        while True:
            message = await websocket.receive_json()
            message_type = message.get('type')

            # 視聴開始リクエスト
            ## リクエストの中身は無視して処理を進める
            ## 本家ニコ生では stream オブジェクトがオプションとして渡された際に視聴 URL などを送るが、ここでは常にコメントのみとする
            ## 大元も基本視聴負荷の関係で映像がいらないなら省略してくれという話があった
            if message_type == 'startWatching':

                # 視聴カウントをインクリメント
                if channel_id not in __viewer_counts:
                    __viewer_counts[channel_id] = 0
                __viewer_counts[channel_id] += 1

                # 現在のサーバー時刻 (ISO 8601) を返す
                await websocket.send_json({
                    'type': 'serverTime',
                    'data': {
                        'currentMs': datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),
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
                        'threadId': str(active_thread.id),
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
                        'vposBaseTime': active_thread.start_at.isoformat(),
                    },
                })

                # 視聴の統計情報を送信
                await websocket.send_json({
                    'type': 'statistics',
                    'data': {
                        'viewers': __viewer_counts[channel_id],
                        'comments': await Comment.filter(thread=active_thread).count(),
                        'adPoints': 0,  # NX-Jikkyo では常に 0 を返す
                        'giftPoints': 0,  # NX-Jikkyo では常に 0 を返す
                    },
                })

            # 定期的に送られてくる座席キープ要求
            ## 本家ニコ生ではこれが一定期間送られてこなかった場合に接続を切断するが、モックなので今の所何もしない
            elif message_type == 'keepSeat':
                pass

            # クライアントからの pong メッセージ
            ## 本家ニコ生ではこれが一定期間送られてこなかった場合に接続を切断するが、モックなので今の所何もしない
            elif message_type == 'pong':
                pass

            # コメント投稿要求
            elif message_type == 'postComment':
                try:
                    # 送られてきたリクエストから mail に相当するコメントコマンドを組み立てる
                    # リクエストでは直接は mail は送られてこないので、いい感じに組み立てる必要がある
                    comment_commands: list[str] = []
                    # 匿名フラグが True なら 184 を追加
                    if message['data']['isAnonymous'] is True:
                        comment_commands.append('184')
                    # コメント色コマンドがあれば追加 (ex: white)
                    if 'color' in message['data']:
                        comment_commands.append(message['data']['color'])
                    # コメント位置コマンドがあれば追加 (ex: naka)
                    if 'position' in message['data']:
                        comment_commands.append(message['data']['position'])
                    # コメントサイズコマンドがあれば追加 # (ex: medium)
                    if 'size' in message['data']:
                        comment_commands.append(message['data']['size'])
                    # コメントフォントコマンドがあれば追加 (ex: defont)
                    if 'font' in message['data']:
                        comment_commands.append(message['data']['font'])

                    # コメ番を算出
                    ## コメントがまだない場合は 1 から始まる
                    last_comment = await Comment.filter(thread=active_thread).order_by('-no').first()
                    if last_comment:
                        comment_no = last_comment.no + 1
                    else:
                        comment_no = 1

                    # コメントを DB に登録
                    comment = await Comment.create(
                        thread = active_thread,
                        no = comment_no,
                        vpos = message['data']['vpos'],  # リクエストで与えられた vpos をそのまま入れる
                        mail = ' '.join(comment_commands),  # コメントコマンドは空白区切りで組み立てる
                        user_id = watch_session_client_id,
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

            # 60 秒に 1 回最新の視聴統計情報を送信 (互換性のため)
            if (time.time() - last_statistics_time) > 60:
                await websocket.send_json({
                    'type': 'statistics',
                    'data': {
                        'viewers': __viewer_counts[channel_id],
                        'comments': await Comment.filter(thread=active_thread).count(),
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
                        'serverTime': datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),
                    },
                })
                last_server_time_time = time.time()

            # 30 秒に 1 回 ping を送信 (互換性のため)
            if (time.time() - last_ping_time) > 30:
                await websocket.send_json({'type': 'ping'})
                last_ping_time = time.time()

            # スレッドの開催終了時刻を過ぎたら接続を切断する
            if datetime.now(ZoneInfo('Asia/Tokyo')) > active_thread.end_at:
                logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected because the thread ended.')
                await websocket.send_json({
                    'type': 'disconnect',
                    'data': {
                        'reason': 'END_PROGRAM',
                    },
                })
                await websocket.close(code=1011)
                __viewer_counts[channel_id] -= 1  # 接続を切断したので来場者数を減らす
                return

    except WebSocketDisconnect:
        # 接続が切れた時の処理
        logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected.')
        __viewer_counts[channel_id] -= 1  # 接続を切断したので来場者数を減らす

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
        __viewer_counts[channel_id] -= 1  # 接続を切断したので来場者数を減らす


@router.websocket('/channels/{channel_id}/ws/comment')
async def CommentSessionAPI(channel_id: str, websocket: WebSocket):
    """ ニコ生のコメントセッション Web Socket 互換 API """

    # コメントセッションはあくまで WebSocket でリクエストされたスレッド ID に基づいて送るので、
    # チャンネル ID はログ出力以外では使わない

    # クライアントごとにユニークな ID を割り当てる
    comment_session_client_id = str(uuid.uuid4())
    logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} connected.')

    # 接続を受け入れる
    await websocket.accept()

    async def SendComment(active_thread: Thread, thread_key: str, comment: Comment):
        """
        受信コメントをクライアント側に送信する
        ref: https://qiita.com/pasta04/items/33da06cf3c21e34fc4d1
        """
        response = {
            'chat': {
                'thread': active_thread.id,
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

    try:

        ## 本家ニコ生では以下のような謎構造のメッセージ (thread コマンド) をコメントセッション (コメントサーバー) に送ることでコメント受信が始まる
        ## NX-Jikkyo でもこの挙動をなんとなく再現する (詳細な仕様は本家が死んでるのでわかりません！生放送と過去ログでも微妙に違う…)
        # [
        #     {ping: {content: 'rs:0'}},
        #     {ping: {content: 'ps:0'}},
        #     {
        #         thread: {
        #             version: '20061206',  // 設定必須
        #             thread: 'THREAD_ID',  // スレッド ID
        #             threadkey: 'THREAD_KEY',  // スレッドキー
        #             user_id: '',  // ユーザー ID（設定不要らしい）
        #             res_from: -50,  // 最初にコメントを 50 個送信する
        #         }
        #     },
        #     {ping: {content: 'pf:0'}},
        #     {ping: {content: 'rf:0'}},
        # ]
        thread_id: int | None = None
        thread_key: str | None = None
        res_from: int | None = None
        when: int | None = None

        # thread コマンドが降ってくるまで待機
        while True:
            messages = await websocket.receive_json()
            for message in messages:
                if 'thread' in message:
                    try:
                        # スレッド ID
                        thread_id = int(message['thread']['thread'])
                        # スレッドキー
                        ## 視聴セッション側の yourPostKey と同一
                        ## NX-Jikkyo ではコメントの user_id に入れられる watch_session_client_id がセットされている
                        thread_key = message['thread']['threadkey']
                        # 初回にクライアントに送信する最新コメントの数
                        ## res_from が正の値になることはない (はず)
                        res_from = int(message['thread']['res_from'])
                        if res_from >= 0:
                            logging.error(f'CommentSessionAPI [{channel_id}]: Invalid res_from: {res_from}')
                            await websocket.close(code=4001)
                            return
                        # when: 取得するコメントの投稿日時の下限を示す UNIX タイムスタンプ (過去ログ取得時のみ設定される)
                        ## 例えば when が 2024-01-01 00:00:00 の場合、2023-12-31 23:59:59 までに投稿されたコメントから
                        ## res_from 件分だけコメント投稿時刻順に後ろから遡ってコメントを取得する
                        if 'when' in message['thread']:
                            when = int(message['thread']['when'])
                        break
                    except Exception:
                        logging.error(f'CommentSessionAPI [{channel_id}]: invalid message.')
                        logging.error(message)
                        logging.error(traceback.format_exc())
                        await websocket.close(code=4001)
                        return

            if not thread_id or not thread_key or not res_from:
                logging.error(f'CommentSessionAPI [{channel_id}]: Invalid thread or thread_key or res_from.')
                await websocket.close(code=4001)
                return

            # ここまできたらスレッド ID と res_from が取得できているので、当該スレッドの情報を取得
            active_thread = await Thread.filter(id=thread_id).first()
            if not active_thread:
                logging.error(f'CommentSessionAPI [{channel_id}]: Active thread not found.')
                await websocket.close(code=4404)
                return

            # 初回接続時のみ常に当該スレッドの最新 res_from 件のコメントを取得して送信
            ## when が設定されている場合のみ when より前のコメントを取得して送信
            if when is not None:
                comments = await Comment.filter(thread=active_thread, date__lt=when).order_by('id').limit(abs(res_from))  # res_from を正の値に変換
            else:
                comments = await Comment.filter(thread=active_thread).order_by('id').limit(abs(res_from))  # res_from を正の値に変換
            await websocket.send_json({'ping': {'content': 'rs:0'}})
            await websocket.send_json({'ping': {'content': 'ps:0'}})
            for comment in comments:
                await SendComment(active_thread, thread_key, comment)
            await websocket.send_json({'ping': {'content': 'pf:0'}})
            await websocket.send_json({'ping': {'content': 'rf:0'}})  # クライアントはこの謎コマンドを受信し終えたら初期コメントの受信が完了している

            # 最後に取得したコメントの ID
            ## 初回送信で最後に送信したコメントの ID を初期値とする
            ## 初回取得コメントが存在しない場合、現在当該スレッドに1つもコメントがない状態
            last_comment_id = comments[-1].id if comments else 0  # None から 0 に変更

            # スレッドが放送中の場合のみ、当該スレッドの新着コメントがあれば随時取得して送信
            ## 過去ログの場合はすでに放送が終わっているのでここの処理は行われず、再度 thread コマンドによる追加取得を待ち受ける
            if active_thread.start_at < datetime.now(ZoneInfo('Asia/Tokyo')) < active_thread.end_at:
                while True:
                    comments = await Comment.filter(thread=active_thread, id__gt=last_comment_id).order_by('id')
                    for comment in comments:
                        await SendComment(active_thread, thread_key, comment)
                        last_comment_id = comment.id

                    # スレッドの開催終了時刻を過ぎたら接続を切断する
                    if datetime.now(ZoneInfo('Asia/Tokyo')) > active_thread.end_at:
                        logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected because the thread ended.')
                        await websocket.close(code=1011)
                        break

    except WebSocketDisconnect:
        logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected.')

    except Exception:
        logging.error(f'CommentSessionAPI [{channel_id}]: Error during connection.')
        logging.error(traceback.format_exc())
        await websocket.close(code=1011)
