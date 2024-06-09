
import time
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from app import logging
from app.models.comment import (
    Channel,
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


@router.get(
    '/channels',
    summary = 'チャンネル情報 API',
    response_description = 'チャンネル情報。',
    response_model = list[ChannelResponse],
)
async def ChannelsAPI():

    # ID 昇順、スレッドは新しい順でチャンネルを取得
    channels = await Channel.all().prefetch_related('threads').order_by('threads__start_at').order_by('id')

    # チャンネルごとに
    response: list[ChannelResponse] = []
    for channel in channels:
        response.append(ChannelResponse(
            id = f'jk{channel.id}',
            name = channel.name,
            description = channel.description,
            threads = [ThreadResponse(
                id = thread.id,
                channel_id = thread.channel_id,
                start_at = thread.start_at,
                end_at = thread.end_at,
                duration = thread.duration,
                title = thread.title,
                description = thread.description,
            ) for thread in channel.threads],
        ))

    return response


@router.websocket('/channels/{channel_id}/ws/watch')
async def WatchSessionAPI(channel_id: str, websocket: WebSocket, request: Request):

    # 接続開始時刻を取得
    connected_at = time.time()

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得し、アクティブなスレッドを取得
    try:
        channel_id = int(channel_id.replace('jk', ''))  # type: ignore
    except ValueError:
        await websocket.close(code=4001)
        return

    active_thread = await Thread.filter(
        channel_id = channel_id,
        start_at__lte = connected_at,
        end_at__gte = connected_at
    ).first()
    if not active_thread:
        await websocket.close(code=4404)
        return

    # クライアントごとにユニークな ID を割り当てる
    watch_session_client_id = str(uuid.uuid4())
    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} connected.')

    # 接続を受け入れる
    await websocket.accept()

    try:
        # 接続完了後、即座に現在のサーバー時刻 (ISO 8601) を返す
        await websocket.send_json({
            'type': 'serverTime',
            'data': {
                'currentMs': datetime.now().isoformat(),
            },
        })

        last_ping_time = time.time()
        while True:
            message = await websocket.receive_json()
            message_type = message.get('type')

            # 視聴開始リクエスト
            ## 本家ニコ生では stream オブジェクトがオプションとして渡された際に視聴 URL などを送るが、ここでは常にコメントのみとする
            if message_type == 'startWatching':

                # 座席取得完了を送信
                await websocket.send_json({
                    'type': 'seat',
                    'data': {
                        # 座席を維持するために送信する keepSeat メッセージ (クライアントメッセージ)の送信間隔時間（秒）
                        'keepIntervalSec': 30,
                    },
                })

                # コメントの部屋情報を送信
                ## レスポンスはすべて本家ニコ生互換
                await websocket.send_json({
                    'type': 'room',
                    'data': {
                        'messageServer': {
                            # メッセージサーバーのURI (WebSocket)
                            'uri': f'wss://{request.url.hostname}/api/v1/channels/{channel_id}/ws/comment',
                            # メッセージサーバの種類 (現在常に `niwavided`)
                            'type': 'niwavided',
                        },
                        # 部屋名
                        'name': 'アリーナ',
                        # メッセージサーバーのスレッドID
                        'threadId': active_thread.id,
                        # (互換性確保のためのダミー値, 現在常に `true`)
                        'isFirst': True,
                        # (互換性確保のためのダミー文字列)
                        'waybackkey': 'DUMMY_TOKEN',
                        # メッセージサーバーから受信するコメント（chatメッセージ）にyourpostフラグを付けるためのキー。threadメッセージのthreadkeyパラメータに設定する
                        ## NXJikkyo ではコメントの user_id に入れられる client_id をセットする
                        'yourPostKey': watch_session_client_id,
                        # vposを計算する基準(vpos:0)となる時刻。 (ISO8601形式)
                        'vposBaseTime': active_thread.start_at.isoformat(),
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
                    last_comment = await Comment.filter(thread=active_thread).order_by('-no').first()
                    comment_no = last_comment.no + 1 if last_comment else 1  # コメントがまだない場合は 1 から始まる

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
                                # コマンド。 `184`, `white`, `naka`, `medium` など
                                'mail': comment.mail,
                                # 匿名コメントかどうか。匿名のとき `1`、非匿名のとき `0`
                                'anonymity': 1 if comment.anonymity else 0,
                                # コメント本文
                                'content': comment.content,
                                # コメントを薄く表示するかどうか (常に False)
                                'restricted': False,
                            },
                        },
                    })
                    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} posted a comment.')
                except Exception as e:
                    logging.error(f'WatchSessionAPI [{channel_id}]: INVALID_MESSAGE: {e}')
                    await websocket.send_json({
                        'type': 'error',
                        'data': {
                            'message': 'INVALID_MESSAGE',
                        },
                    })

            # 30 秒に 1 回 ping を送信 (互換性のため)
            if time.time() - last_ping_time > 30:
                await websocket.send_json({'type': 'ping'})
                last_ping_time = time.time()

            # スレッドの開催終了時刻を過ぎたら接続を切断する
            if datetime.now() > active_thread.end_at:
                logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected because the thread ended.')
                await websocket.send_json({
                    'type': 'disconnect',
                    'data': {
                        'reason': 'END_PROGRAM',
                    },
                })
                await websocket.close(code=1011)
                return

    except WebSocketDisconnect:
        # 接続が切れた時の処理
        logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected.')

    except Exception as e:
        logging.error(f'WatchSessionAPI [{channel_id}]: Error during connection: {e}')
        await websocket.send_json({
            'type': 'disconnect',
            'data': {
                'reason': 'SERVICE_TEMPORARILY_UNAVAILABLE',
            },
        })
        await websocket.close(code=1011)


@router.websocket('/channels/{channel_id}/ws/comment')
async def CommentSessionAPI(channel_id: str, websocket: WebSocket):

    # コメントセッションはあくまで WebSocket でリクエストされたスレッド ID に基づいて送るので、
    # チャンネル ID はログ以外では使わない

    # クライアントごとにユニークな ID を割り当てる
    comment_session_client_id = str(uuid.uuid4())
    logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} connected.')

    # 接続を受け入れる
    await websocket.accept()

    try:

        # "thread" コマンドが降ってくるまで待機
        thread_id: int | None = None
        res_from: int | None = None
        messages = await websocket.receive_json()
        for message in messages:
            if 'thread' in message:
                # スレッド ID
                thread_id = int(message['thread']['thread'])
                # 初回にクライアントに送信する最新コメントの数
                res_from = int(message['thread']['res_from'])
                break

        if not thread_id or not res_from:
            await websocket.close(code=4001)
            return

        # 当該スレッドの情報を取得
        active_thread = await Thread.filter(id=thread_id).first()
        if not active_thread:
            await websocket.close(code=4404)
            return

        async def SendComment(comment: Comment):
            """ コメントを送信する """
            nonlocal active_thread
            await websocket.send_json({
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
            })

        # 初回接続時は最新 res_from 件のコメントを送信
        comments = await Comment.filter(thread=active_thread).order_by('-date').limit(abs(res_from))  # res_from を正の値に変換
        for comment in comments:
            await SendComment(comment)

        # 新着コメントがあれば随時送信
        sent_comment_ids = set()
        last_comment_id = 0
        while True:
            comments = await Comment.filter(thread=active_thread, id__gt=last_comment_id).order_by('id')
            for comment in comments:
                if comment.id not in sent_comment_ids:
                    await SendComment(comment)
                    sent_comment_ids.add(comment.id)
                    last_comment_id = comment.id

            # スレッドの開催終了時刻を過ぎたら接続を切断する
            if datetime.now() > active_thread.end_at:
                logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected because the thread ended.')
                await websocket.close(code=1011)
                break

    except WebSocketDisconnect:
        logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected.')

    except Exception as e:
        logging.error(f'WatchSessionAPI [{channel_id}]: Error during connection: {e}')
        await websocket.close(code=1011)
