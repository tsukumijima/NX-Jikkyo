
import asyncio
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, cast

import websockets.exceptions
from fastapi import APIRouter, Path, Query
from starlette.websockets import (
    WebSocket,
    WebSocketDisconnect,
    WebSocketState,
)
from tortoise import timezone
from tortoise.backends.base.client import TransactionalDBClient
from tortoise.exceptions import DoesNotExist

from app import logging
from app.constants import (
    KNOWN_JIKKYO_CHANNEL_IDS,
    REDIS_CHANNEL_THREAD_COMMENTS_PREFIX,
    REDIS_CLIENT,
    REDIS_KEY_JIKKYO_FORCE_COUNT,
    REDIS_KEY_VIEWER_COUNT,
)
from app.models.comment import (
    Comment,
    CommentCounter,
    Thread,
    XMLCompatibleCommentResponse,
    XMLCompatibleCommentResponseChat,
)
from app.utils import GenerateClientID
from app.utils.comment_counter_cache import (
    GetThreadCommentCounterCache,
    UpdateThreadCommentCounterCache,
)
from app.utils.transaction import (
    IsDatabaseConnectionUnavailableError,
    RunTransactionWithReconnectRetry,
)


# ルーター
router = APIRouter(
    tags = ['WebSocket'],
    prefix = '/api/v1',
)

# 現在アクティブなスレッドの情報を保存する辞書
__active_threads: dict[int, Thread] = {}

# 接続ごとのコメント送信キューの最大サイズ
COMMENT_QUEUE_MAX_SIZE = 200
# unknown channel の拒否ログを集約して出力する間隔 (秒)
UNKNOWN_CHANNEL_LOG_INTERVAL_SECONDS = 60.0
# unknown channel ごとの拒否回数
unknown_channel_reject_count_by_channel_id: dict[str, int] = {}
# unknown channel 拒否ログを最後に出力した時刻
last_unknown_channel_summary_log_time = 0.0
# unknown channel 集約カウンタ更新の排他ロック
unknown_channel_summary_lock = asyncio.Lock()

@dataclass(slots=True)
class CommentBroadcastMessage:
    """
    Redis Pub/Sub から受信したコメントを接続ごとの送信キューに流すためのメッセージ

    Attributes:
        raw_json (str): Redis Pub/Sub から受信した生の JSON 文字列
        base_comment (XMLCompatibleCommentResponse): JSON をデコードしたコメントデータ
        user_id (str): コメント投稿者のユーザー ID
    """

    raw_json: str
    base_comment: XMLCompatibleCommentResponse
    user_id: str


@dataclass(slots=True)
class CommentSubscriber:
    """
    リアルタイムコメント配信用の接続情報

    Attributes:
        client_id (str): コメントセッションのクライアント ID
        thread_key (str): thread コマンドで指定された threadkey
        queue (asyncio.Queue[CommentBroadcastMessage]): 接続ごとのコメント送信キュー
    """

    client_id: str
    thread_key: str
    queue: asyncio.Queue[CommentBroadcastMessage]


def CopyXMLCompatibleCommentResponse(response: XMLCompatibleCommentResponse) -> XMLCompatibleCommentResponse:
    """
    XMLCompatibleCommentResponse を浅くコピーして返す

    Args:
        response (XMLCompatibleCommentResponse): コピー対象のコメントデータ

    Returns:
        XMLCompatibleCommentResponse: コピーされたコメントデータ
    """

    copied_response = dict(response)
    copied_response['chat'] = cast(XMLCompatibleCommentResponseChat, dict(response['chat']))
    return cast(XMLCompatibleCommentResponse, copied_response)


def EnqueueBroadcastMessage(
    subscriber: CommentSubscriber,
    message: CommentBroadcastMessage,
) -> None:
    """
    接続ごとの送信キューへコメントを追加する

    Args:
        subscriber (CommentSubscriber): コメント送信先の接続情報
        message (CommentBroadcastMessage): 配信するコメント
    """

    if subscriber.queue.full() is True:
        # キューが溢れそうな場合は古いコメントを捨てる
        try:
            subscriber.queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

    try:
        subscriber.queue.put_nowait(message)
    except asyncio.QueueFull:
        # ここに到達するのは非常に稀だが、念のため握りつぶす
        pass


class ThreadCommentBroadcaster:
    """
    スレッド単位で Redis Pub/Sub を購読し、接続ごとの送信キューにコメントを配信する
    """

    def __init__(self, thread_id: int) -> None:
        """
        Args:
            thread_id (int): コメント配信対象のスレッド ID
        """

        self.thread_id = thread_id
        self.subscribers: dict[str, CommentSubscriber] = {}
        self.lock = asyncio.Lock()
        self._run_task: asyncio.Task[None] | None = None

    async def addSubscriber(self, subscriber_id: str, subscriber: CommentSubscriber) -> None:
        """
        コメント配信対象の接続を追加する

        Args:
            subscriber_id (str): 接続を識別する ID
            subscriber (CommentSubscriber): 追加する接続情報
        """

        # 接続一覧は複数タスクから同時に更新されるためロックで保護する
        async with self.lock:
            # 接続情報を登録する
            self.subscribers[subscriber_id] = subscriber
            # 配信タスクが未起動または終了済みなら新しいタスクを開始する
            # _run_task.done() は正常終了・例外終了・キャンセル済みのいずれも True を返す
            ## これにより、_run() が予期せぬ例外で終了した場合でも、次の購読者追加時に自動的に再起動される
            if self._run_task is None or self._run_task.done():
                self._run_task = asyncio.create_task(self._run())

    async def removeSubscriber(self, subscriber_id: str, subscriber: CommentSubscriber) -> None:
        """
        コメント配信対象の接続を削除する

        Args:
            subscriber_id (str): 削除する接続の ID
            subscriber (CommentSubscriber): 削除対象の接続情報
        """

        # 接続一覧は複数タスクから同時に更新されるためロックで保護する
        # タスクのキャンセルと待機もロック内で行い、レースコンディションを防ぐ
        ## キャンセルされたタスクは即座に終了するため、ロック内での await でもデッドロックは発生しない
        async with self.lock:
            # 接続が登録されている場合のみ削除する
            if subscriber_id in self.subscribers and self.subscribers[subscriber_id] is subscriber:
                del self.subscribers[subscriber_id]
            # 接続が存在しなくなった場合は配信タスクを停止する
            if len(self.subscribers) == 0 and self._run_task is not None:
                self._run_task.cancel()
                try:
                    await self._run_task
                except asyncio.CancelledError:
                    pass
                self._run_task = None

    async def getSubscriberCount(self) -> int:
        """
        現在の接続数を取得する

        Returns:
            int: 現在の接続数
        """

        # 接続一覧は複数タスクから同時に更新されるためロックで保護する
        async with self.lock:
            return len(self.subscribers)

    async def _getSubscriberSnapshot(self) -> list[CommentSubscriber]:
        """
        コメント配信対象の接続一覧をスナップショットとして取得する

        Returns:
            list[CommentSubscriber]: コメント配信対象の接続一覧
        """

        # 配信時は現在の接続一覧のスナップショットを使う
        ## 配信中に接続一覧が変わっても影響しないようにする
        async with self.lock:
            return list(self.subscribers.values())

    async def _run(self) -> None:
        """
        Redis Pub/Sub を購読し、接続ごとの送信キューにコメントを配信する

        予期せぬ例外が発生した場合は指数バックオフでリトライし、配信を継続する。
        CancelledError が発生した場合のみタスクを終了する。
        """

        # リトライ用のバックオフ設定
        retry_delay = 1.0  # 初期リトライ間隔 (秒)
        max_retry_delay = 30.0  # 最大リトライ間隔 (秒)

        while True:
            pubsub = REDIS_CLIENT.pubsub()
            should_retry = False

            try:
                # スレッド単位の Pub/Sub でコメントを受信する
                await pubsub.subscribe(f'{REDIS_CHANNEL_THREAD_COMMENTS_PREFIX}:{self.thread_id}')

                # 正常に接続できたらリトライ間隔をリセット
                retry_delay = 1.0

                while True:
                    # コメントが来るまで最大 5 秒待機する
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)
                    if message is None:
                        continue

                    # Redis から受信したコメントを JSON 文字列として扱う
                    raw_payload = message['data']
                    if isinstance(raw_payload, bytes | bytearray | memoryview):
                        raw_json = bytes(raw_payload).decode('utf-8')
                    elif isinstance(raw_payload, str):
                        raw_json = raw_payload
                    else:
                        raw_json = json.dumps(raw_payload, ensure_ascii=False, separators=(',', ':'))

                    try:
                        # Redis から受信した JSON をデコードする
                        base_comment: XMLCompatibleCommentResponse = json.loads(raw_json)
                    except json.JSONDecodeError:
                        logging.error('ThreadCommentBroadcaster: Failed to decode comment JSON.')
                        continue

                    if 'chat' not in base_comment:
                        logging.error('ThreadCommentBroadcaster: Comment JSON does not contain chat data.')
                        continue

                    # yourpost 判定に必要な情報を先に抽出する
                    # yourpost が含まれている場合は非 yourpost に流れないように事前に除去する
                    if 'yourpost' in base_comment['chat']:
                        del base_comment['chat']['yourpost']
                        raw_json = json.dumps(base_comment, ensure_ascii=False, separators=(',', ':'))

                    user_id = str(base_comment['chat'].get('user_id', ''))
                    broadcast_message = CommentBroadcastMessage(
                        raw_json = raw_json,
                        base_comment = base_comment,
                        user_id = user_id,
                    )

                    # 現在接続中の全クライアントへ同一メッセージを配信する
                    subscribers = await self._getSubscriberSnapshot()
                    for subscriber in subscribers:
                        EnqueueBroadcastMessage(subscriber, broadcast_message)

            except asyncio.CancelledError:
                # キャンセルされた場合はタスクを終了する
                raise

            except Exception as ex:
                # 予期せぬ例外が発生した場合はログを出力してリトライする
                logging.error(f'ThreadCommentBroadcaster: Unexpected error occurred while broadcasting. Retrying in {retry_delay} seconds...', exc_info=ex)
                should_retry = True

            finally:
                # 各リトライごとに確実に購読解除する
                try:
                    await pubsub.unsubscribe(f'{REDIS_CHANNEL_THREAD_COMMENTS_PREFIX}:{self.thread_id}')
                    await pubsub.close()
                except Exception as cleanup_ex:
                    logging.error('ThreadCommentBroadcaster: Failed to cleanup Redis pubsub connection:', exc_info=cleanup_ex)

            if should_retry is True:
                # 指数バックオフでリトライ間隔を増加させる
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)


# スレッド単位のコメント配信用 Broadcaster を保存する辞書
__thread_comment_broadcasters: dict[int, ThreadCommentBroadcaster] = {}
__thread_comment_broadcasters_lock = asyncio.Lock()


async def GetThreadCommentBroadcaster(thread_id: int) -> ThreadCommentBroadcaster:
    """
    スレッド単位のコメント配信用 Broadcaster を取得する

    Args:
        thread_id (int): コメント配信対象のスレッド ID

    Returns:
        ThreadCommentBroadcaster: スレッド単位のコメント配信用 Broadcaster
    """

    async with __thread_comment_broadcasters_lock:
        broadcaster = __thread_comment_broadcasters.get(thread_id)
        if broadcaster is None:
            broadcaster = ThreadCommentBroadcaster(thread_id)
            __thread_comment_broadcasters[thread_id] = broadcaster
        return broadcaster


async def CleanupThreadCommentBroadcaster(thread_id: int, broadcaster: ThreadCommentBroadcaster) -> None:
    """
    接続が存在しない Broadcaster を辞書から削除する

    Args:
        thread_id (int): 対象のスレッド ID
        broadcaster (ThreadCommentBroadcaster): 対象の Broadcaster
    """

    # デッドロックを防ぐため、ロック取得順序を固定する
    # 常に __thread_comment_broadcasters_lock → broadcaster.lock の順で取得する
    ## getSubscriberCount() は内部で broadcaster.lock を取得するため、
    ## __thread_comment_broadcasters_lock を保持した状態で呼び出すとネストされたロックになる
    ## そのため、ここでは直接 subscribers の長さを確認してデッドロックを回避する
    async with __thread_comment_broadcasters_lock:
        current_broadcaster = __thread_comment_broadcasters.get(thread_id)
        if current_broadcaster is not broadcaster:
            return
        # broadcaster.lock を取得して購読者数を確認し、0 なら削除する
        async with broadcaster.lock:
            if len(broadcaster.subscribers) == 0:
                del __thread_comment_broadcasters[thread_id]


async def LogUnknownChannelRejected(channel_id: str) -> None:
    """
    unknown channel 拒否ログを 1 分単位で集約して出力する

    Args:
        channel_id (str): 拒否対象の実況チャンネル ID
    """

    global last_unknown_channel_summary_log_time

    # ログ集約判定に使う現在時刻を取得する
    current_time = time.time()
    # ロック外で使う出力用の値を初期化する
    should_log_summary = False
    summary_total_count = 0
    summary_detail = ''

    # 集約カウンタは複数接続から同時に更新されるためロックで保護する
    async with unknown_channel_summary_lock:
        # チャンネルごとの拒否回数を加算する
        current_count = unknown_channel_reject_count_by_channel_id.get(channel_id, 0)
        unknown_channel_reject_count_by_channel_id[channel_id] = current_count + 1

        # 初回呼び出し時に集約開始時刻を初期化する
        if last_unknown_channel_summary_log_time == 0.0:
            last_unknown_channel_summary_log_time = current_time

        # まだ集約間隔に達していなければ次回へ持ち越す
        elapsed_seconds = current_time - last_unknown_channel_summary_log_time
        if elapsed_seconds < UNKNOWN_CHANNEL_LOG_INTERVAL_SECONDS:
            return

        # 現時点の集約結果をスナップショット化してカウンタをリセットする
        snapshot = dict(unknown_channel_reject_count_by_channel_id)
        unknown_channel_reject_count_by_channel_id.clear()
        last_unknown_channel_summary_log_time = current_time

        # 出力するチャンネル詳細は件数の多い順に上位 10 件までに絞る
        summary_total_count = sum(snapshot.values())
        sorted_snapshot = sorted(snapshot.items(), key=lambda item: item[1], reverse=True)
        top_channels = sorted_snapshot[:10]
        summary_detail = ', '.join(
            f'{snapshot_channel_id}: {snapshot_count}'
            for snapshot_channel_id, snapshot_count in top_channels
        )
        if summary_detail == '':
            summary_detail = 'none'
        should_log_summary = True

    # ロック外で warning を出すことで、ロック保持時間を最小化する
    if should_log_summary is True:
        logging.warning(
            'WatchSessionAPI: Rejected unknown channel requests in last 60 seconds. '
            f'total: {summary_total_count}, details: {summary_detail}'
        )


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


def IsWebSocketDisconnected(websocket: WebSocket) -> bool:
    """
    WebSocket が既に切断済みかどうかを判定する

    Args:
        websocket (WebSocket): 判定対象の WebSocket

    Returns:
        bool: 切断済みの場合は True
    """

    # Starlette 側とアプリ側のどちらかが切断済みなら、送信処理は中止する
    return (
        websocket.client_state == WebSocketState.DISCONNECTED
        or websocket.application_state == WebSocketState.DISCONNECTED
    )


def IsWebSocketClosedError(ex: Exception) -> bool:
    """
    WebSocket 切断済みで発生する想定内の送信例外かどうかを判定する

    Args:
        ex (Exception): 判定対象の例外

    Returns:
        bool: 想定内の切断例外の場合は True
    """

    # FastAPI / Starlette の標準的な切断例外
    if isinstance(ex, WebSocketDisconnect):
        return True
    # websockets ライブラリが送出する切断例外
    if isinstance(ex, websockets.exceptions.ConnectionClosed):
        return True
    # Starlette 実装で多発する close 済み送信例外
    if isinstance(ex, RuntimeError):
        return 'Cannot call "send" once a close message has been sent.' in str(ex)
    # Uvicorn の内部例外はクラスを直接 import しづらいため名前で判定する
    return ex.__class__.__name__ == 'ClientDisconnected'


async def SendJSONSafely(websocket: WebSocket, payload: Any) -> bool:
    """
    切断済みソケットへの送信例外を抑制しつつ JSON を送信する

    Args:
        websocket (WebSocket): 送信先 WebSocket
        payload (Any): JSON 送信する payload

    Returns:
        bool: 送信成功時は True、切断済みなどで送信不要な場合は False
    """

    # すでに切断済みなら送信せず即終了する
    if IsWebSocketDisconnected(websocket) is True:
        return False

    try:
        # 切断前であれば通常どおり送信する
        await websocket.send_json(payload)
        return True
    except Exception as ex:
        # 切断済み起因の例外は抑止し、それ以外は上位へ伝搬する
        if IsWebSocketClosedError(ex) is True:
            return False
        raise


async def SendTextSafely(websocket: WebSocket, text: str) -> bool:
    """
    切断済みソケットへの送信例外を抑制しつつテキストを送信する

    Args:
        websocket (WebSocket): 送信先 WebSocket
        text (str): 送信するテキスト

    Returns:
        bool: 送信成功時は True、切断済みなどで送信不要な場合は False
    """

    # すでに切断済みなら送信せず即終了する
    if IsWebSocketDisconnected(websocket) is True:
        return False

    try:
        # 切断前であれば通常どおり送信する
        await websocket.send_text(text)
        return True
    except Exception as ex:
        # 切断済み起因の例外は抑止し、それ以外は上位へ伝搬する
        if IsWebSocketClosedError(ex) is True:
            return False
        raise


async def CloseWebSocketSafely(
    websocket: WebSocket,
    code: int = 1000,
    reason: str | None = None,
) -> bool:
    """
    切断済みソケットへの close 例外を抑制しつつ接続を閉じる

    Args:
        websocket (WebSocket): クローズ対象の WebSocket
        code (int, optional): close code. Defaults to 1000.
        reason (str | None, optional): close reason. Defaults to None.

    Returns:
        bool: close 実行時は True、既に切断済みの場合は False
    """

    # すでに切断済みなら close を再送しない
    if IsWebSocketDisconnected(websocket) is True:
        return False

    try:
        # close は 1 回だけ実行し、成功時は True を返す
        await websocket.close(code=code, reason=reason)
        return True
    except Exception as ex:
        # close 済み起因の例外は抑止し、それ以外は上位へ伝搬する
        if IsWebSocketClosedError(ex) is True:
            return False
        raise


@router.websocket('/channels/{channel_id}/ws/watch')
async def WatchSessionAPI(
    websocket: WebSocket,
    channel_id: Annotated[str, Path(description='実況チャンネル ID 。ex: jk211')],
    thread_id: Annotated[int | None, Query(description='スレッド ID 。過去の特定スレッドの過去ログコメントを取得する際に指定する。')] = None,
):
    """
    ニコ生の視聴セッション WebSocket 互換 API
    """

    # チャンネル ID のリダイレクト処理
    ## jk263 (BSJapanext) への接続は jk200 (BS10) にリダイレクトする
    ## ただし、過去ログ取得時 (thread_id が指定されている場合) はリダイレクトしない
    original_channel_id = channel_id
    if channel_id == 'jk263':
        # thread_id が指定されている場合は、そのスレッドが jk263 のものかを確認
        if thread_id is not None:
            thread = await Thread.filter(id=thread_id).first()
            if thread and thread.channel_id == 263:
                # jk263 の過去ログの場合はリダイレクトしない
                pass
            else:
                # thread_id が存在しないか、jk263 以外のスレッドの場合は jk200 にリダイレクト
                channel_id = 'jk200'
                logging.info(f'WatchSessionAPI: Channel {original_channel_id} redirected to {channel_id} (thread not found or not jk263).')
        else:
            # 通常の接続時は jk200 にリダイレクト
            channel_id = 'jk200'
            logging.info(f'WatchSessionAPI: Channel {original_channel_id} redirected to {channel_id}.')

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得
    try:
        channel_id_int = int(channel_id.replace('jk', ''))
    except ValueError:
        logging.error(f'WatchSessionAPI [{channel_id}]: Invalid channel ID.')
        await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid channel ID.')
        return

    # DB へ到達する前に既知チャンネルかを判定し、無効チャンネルアクセスで DB を消費しないようにする
    ## サードパーティークライアント由来の jk309 などを早期拒否して、通常トラフィックへの影響を抑える
    if channel_id_int not in KNOWN_JIKKYO_CHANNEL_IDS:
        await LogUnknownChannelRejected(channel_id)
        await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid channel ID.')
        return

    # スレッド ID が指定されていなければ、現在アクティブな (放送中の) スレッドを取得
    if not thread_id:
        thread = await GetActiveThread(channel_id_int)
        if not thread:
            # 存在しないチャンネル ID を指定された場合にも発生して頻度が多すぎるのでログをコメントアウト中
            # logging.error(f'WatchSessionAPI [{channel_id}]: Active thread not found.')
            await CloseWebSocketSafely(websocket, code=1002, reason=f'[{channel_id}]: Active thread not found.')
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
            await CloseWebSocketSafely(websocket, code=1002, reason=f'[{channel_id}]: Thread not found.')
            return
        if timezone.now() < thread.start_at:
            logging.error(f'WatchSessionAPI [{channel_id}]: Thread is upcoming.')
            await CloseWebSocketSafely(websocket, code=1002, reason=f'[{channel_id}]: Thread is upcoming.')
            return

    # クライアント ID を生成
    ## 同一 IP 同一クライアントからなら UA が変更されない限り同一値になるはず
    watch_session_client_id = GenerateClientID(websocket)
    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} connected.')
    logging.info(f'WatchSessionAPI [{channel_id}]: Thread ID: {thread.id} User-Agent: {websocket.headers.get("User-Agent", "Unknown")}')

    # 接続を受け入れる
    await websocket.accept()
    # startWatching 時に送信した comments 値を sender task の初期フォールバック値へ引き継ぐ
    initial_statistics_comment_count: int | None = None

    async def RunReceiverTask() -> None:
        """ クライアントからのメッセージを受信するタスク """

        nonlocal initial_statistics_comment_count

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
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'error',
                    'data': {
                        'message': 'INVALID_MESSAGE',
                    },
                })
                if is_sent is False:
                    return
                continue

            # 視聴開始リクエスト
            ## リクエストの中身は無視して処理を進める
            ## 本家ニコ生では stream オブジェクトがオプションとして渡された際に視聴 URL などを送るが、ここでは常にコメントのみとする
            ## 大元も基本視聴負荷の関係で映像がいらないなら省略してくれという話があった
            if message_type == 'startWatching':

                # 現在のサーバー時刻 (ISO 8601) を送信
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'serverTime',
                    'data': {
                        'currentMs': timezone.now().isoformat(),
                    },
                })
                if is_sent is False:
                    return

                # 座席取得が完了した旨を送信
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'seat',
                    'data': {
                        # 「座席を維持するために送信する keepSeat メッセージ (クライアントメッセージ) の送信間隔時間（秒）」
                        'keepIntervalSec': 30,
                    },
                })
                if is_sent is False:
                    return

                # スレッドの放送開始時刻・放送終了時刻を送信
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'schedule',
                    'data': {
                        'begin': thread.start_at.isoformat(),
                        'end': thread.end_at.isoformat(),
                    },
                })
                if is_sent is False:
                    return

                # リクエスト元の URL を組み立てる
                ## scheme はそのままだと多段プロキシの場合に ws:// になってしまうので、
                ## X-Forwarded-Proto ヘッダから scheme を取得してから URI を組み立てる
                ## X-Forwarded-Proto が https 固定の場合も考慮して wss に変換している
                scheme = websocket.headers.get('X-Forwarded-Proto', websocket.url.scheme).replace('https', 'wss')
                uri = f'{scheme}://{websocket.url.netloc}/api/v1/channels/{channel_id}/ws/comment'

                # コメント部屋情報を送信
                is_sent = await SendJSONSafely(websocket, {
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
                if is_sent is False:
                    return

                # 視聴の統計情報を送信
                initial_viewer_count = 0
                try:
                    initial_viewer_count = int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, channel_id) or 0)
                except Exception as ex:
                    logging.warning(
                        f'WatchSessionAPI [{channel_id}]: Failed to fetch viewer counter for initial statistics. Falling back to zero.',
                        exc_info = ex,
                    )
                initial_comment_count = 0
                try:
                    initial_comment_count = (await CommentCounter.get(thread_id=thread.id)).max_no
                except DoesNotExist as ex:
                    # 稀に採番テーブルのレコードが欠損している場合は、0 にフォールバックして接続を継続する
                    ## 定期 statistics 送信側の回復ロジック (SyncCommentCounters) で最終的に修復される
                    logging.warning(
                        f'WatchSessionAPI [{channel_id}]: CommentCounter record is missing for initial statistics. Falling back to zero.',
                        exc_info = ex,
                    )
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'statistics',
                    'data': {
                        'viewers': initial_viewer_count,
                        'comments': initial_comment_count,
                        'adPoints': 0,  # NX-Jikkyo では常に 0 を返す
                        'giftPoints': 0,  # NX-Jikkyo では常に 0 を返す
                    },
                })
                if is_sent is False:
                    return
                initial_statistics_comment_count = initial_comment_count

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
                    is_sent = await SendJSONSafely(websocket, {
                        'type': 'error',
                        'data': {
                            'message': 'NOT_ON_AIR',
                        },
                    })
                    if is_sent is False:
                        return
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
                        is_sent = await SendJSONSafely(websocket, {
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
                        if is_sent is False:
                            return

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

                    async def CreateCommentInTransaction(connection: TransactionalDBClient) -> Comment:

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
                        return await Comment.create(
                            thread_id = thread.id,
                            no = new_no,
                            vpos = message['data']['vpos'],  # リクエストで与えられた vpos をそのまま入れる
                            mail = ' '.join(comment_commands),  # コメントコマンド (mail) は空白区切りの文字列として組み立てる
                            user_id = watch_session_client_id,  # ユーザー ID は視聴セッションのクライアント ID をそのまま入れる
                            premium = False,  # 簡易実装なのでプレミアム会員判定は省略
                            anonymity = message['data']['isAnonymous'] is True,
                            content = message['data']['text'],
                        )

                    # コメントを DB に登録
                    comment = await RunTransactionWithReconnectRetry(
                        operation = CreateCommentInTransaction,
                        operation_name = f'WatchSessionAPI [{channel_id}]',
                    )

                    # スレッドごとの最新コメ番キャッシュを更新
                    ## 投稿成功直後に反映しておくことで、statistics 送信時の DB アクセス頻度を抑える
                    try:
                        await UpdateThreadCommentCounterCache(thread.id, comment.no)
                    except Exception as ex:
                        # キャッシュ更新はベストエフォートで扱う
                        ## ここで例外を再送出すると投稿成功レスポンスまで失敗するため、ログのみ残して継続する
                        logging.warning(
                            f'WatchSessionAPI [{channel_id}]: Failed to update thread comment counter cache.',
                            exc_info = ex,
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
                    is_sent = await SendJSONSafely(websocket, {
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
                    if is_sent is False:
                        return
                    logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} posted a comment.')

                # コメント投稿に失敗した場合はエラーを返す
                except Exception as ex:
                    if IsWebSocketClosedError(ex) is True:
                        return
                    logging.error(f'WatchSessionAPI [{channel_id}]: Failed to post a comment. message: {message}', exc_info = ex)
                    is_sent = await SendJSONSafely(websocket, {
                        'type': 'error',
                        'data': {
                            'message': 'INVALID_MESSAGE',
                        },
                    })
                    if is_sent is False:
                        return

            # 接続が切れたらタスクを終了
            if IsWebSocketDisconnected(websocket) is True:
                return

    async def RunSenderTask() -> None:
        """ 定期的にサーバーからクライアントにメッセージを送信するタスク """

        # 最後に視聴統計情報を送信した時刻
        last_statistics_time = time.time()
        # 最後にサーバー時刻を送信した時刻
        last_server_time_time = time.time()
        # 最後に ping を送信した時刻
        last_ping_time = time.time()
        # 最後に送信したコメント数
        ## startWatching が sender task より後に処理される場合を考慮し、未確定を None で表現する
        last_statistics_comment_count: int | None = None
        # 最後にコメント数取得エラーをログ出力した時刻
        last_comment_counter_error_log_time = 0.0
        # 最後に視聴者数取得エラーをログ出力した時刻
        last_viewer_counter_error_log_time = 0.0
        # DB からのコメント数再取得を再試行するまで待機する時刻
        next_comment_counter_db_retry_time = 0.0
        # Redis キャッシュ値を DB で検証する間隔 (秒)
        comment_counter_db_validation_interval_seconds = 600.0
        # 次回 Redis キャッシュ値を DB で検証する時刻
        ## DB 接続断時の再試行抑制時刻とは責務を分離し、意図を明確化する
        next_comment_counter_validation_time = 0.0

        # 処理開始時点でスレッドが放送中かどうか
        is_on_air = thread.start_at < timezone.now() < thread.end_at

        while True:

            # 60 秒に 1 回最新の視聴統計情報を送信 (互換性のため)
            if (time.time() - last_statistics_time) > 60:
                current_time = time.time()
                if last_statistics_comment_count is not None:
                    comment_count = last_statistics_comment_count
                elif initial_statistics_comment_count is not None:
                    comment_count = initial_statistics_comment_count
                else:
                    comment_count = 0
                try:
                    cached_comment_counter: int | None = None
                    try:
                        # まず Redis キャッシュを参照し、通常時は DB クエリを避ける
                        cached_comment_counter = await GetThreadCommentCounterCache(thread.id)
                    except Exception as cache_ex:
                        # Redis 読み取り失敗時も DB フォールバックを継続し、コメント数の更新停止を防ぐ
                        if (current_time - last_comment_counter_error_log_time) > 15:
                            logging.warning(
                                f'WatchSessionAPI [{channel_id}]: Failed to fetch comment counter cache. Falling back to DB.',
                                exc_info = cache_ex,
                            )
                            last_comment_counter_error_log_time = current_time

                    if cached_comment_counter is not None:
                        comment_count = cached_comment_counter
                        # キャッシュがあっても無期限に信用しない
                        ## 一定間隔で DB の CommentCounter と突合し、キャッシュの stale 化を防ぐ
                        should_validate_cached_counter = (
                            current_time >= next_comment_counter_db_retry_time
                            and current_time >= next_comment_counter_validation_time
                        )
                        if should_validate_cached_counter is True:
                            # DB 値を正として再同期し、誤ったキャッシュを自己修復する
                            comment_count = (await CommentCounter.get(thread_id=thread.id)).max_no
                            try:
                                await UpdateThreadCommentCounterCache(thread.id, comment_count)
                            except Exception as cache_ex:
                                logging.warning(
                                    f'WatchSessionAPI [{channel_id}]: Failed to update validated comment counter cache.',
                                    exc_info = cache_ex,
                                )
                            next_comment_counter_db_retry_time = 0.0
                            next_comment_counter_validation_time = current_time + comment_counter_db_validation_interval_seconds
                    elif current_time >= next_comment_counter_db_retry_time:
                        # キャッシュ欠損時は DB から復元し、その値を Redis へ戻す
                        comment_count = (await CommentCounter.get(thread_id=thread.id)).max_no
                        try:
                            await UpdateThreadCommentCounterCache(thread.id, comment_count)
                        except Exception as cache_ex:
                            logging.warning(
                                f'WatchSessionAPI [{channel_id}]: Failed to update restored comment counter cache.',
                                exc_info = cache_ex,
                            )
                        next_comment_counter_db_retry_time = 0.0
                        next_comment_counter_validation_time = current_time + comment_counter_db_validation_interval_seconds
                except DoesNotExist as ex:
                    # 稀に採番テーブルのレコードが欠損している場合は、現存コメント数から再作成して回復を試みる
                    if (current_time - last_comment_counter_error_log_time) > 15:
                        logging.warning(
                            f'WatchSessionAPI [{channel_id}]: CommentCounter record is missing. Trying to recover from comments table.',
                            exc_info = ex,
                        )
                        last_comment_counter_error_log_time = current_time
                    if current_time >= next_comment_counter_db_retry_time:
                        try:
                            # no は採番テーブルで単調増加している前提なので、最新行判定には id を使って負荷を抑える
                            ## 欠損回復時のみ実行される経路のため、ここでは最小コストで復旧を優先する
                            latest_comment = await Comment.filter(thread_id=thread.id).order_by('-id').first()
                            comment_count = latest_comment.no if latest_comment is not None else 0
                            existing_comment_counter = await CommentCounter.filter(thread_id=thread.id).first()
                            synchronized_comment_count = comment_count
                            if existing_comment_counter is not None:
                                synchronized_comment_count = max(existing_comment_counter.max_no, comment_count)
                                if existing_comment_counter.max_no != synchronized_comment_count:
                                    existing_comment_counter.max_no = synchronized_comment_count
                                    await existing_comment_counter.save(update_fields=['max_no'])
                            else:
                                await CommentCounter.create(
                                    thread_id = thread.id,
                                    max_no = synchronized_comment_count,
                                )
                            try:
                                await UpdateThreadCommentCounterCache(thread.id, synchronized_comment_count)
                            except Exception as cache_ex:
                                logging.warning(
                                    f'WatchSessionAPI [{channel_id}]: Failed to update recovered comment counter cache.',
                                    exc_info = cache_ex,
                                )
                            comment_count = synchronized_comment_count
                            next_comment_counter_db_retry_time = 0.0
                            next_comment_counter_validation_time = current_time + comment_counter_db_validation_interval_seconds
                        except Exception as recovery_ex:
                            if IsDatabaseConnectionUnavailableError(recovery_ex) is True:
                                next_comment_counter_db_retry_time = max(next_comment_counter_db_retry_time, current_time + 15)
                            if (current_time - last_comment_counter_error_log_time) > 15:
                                logging.warning(
                                    f'WatchSessionAPI [{channel_id}]: Failed to recover missing CommentCounter. Falling back to cached value.',
                                    exc_info = recovery_ex,
                                )
                                last_comment_counter_error_log_time = current_time
                except Exception as ex:
                    if IsDatabaseConnectionUnavailableError(ex) is True:
                        # DB ダウン中に毎ループで再試行すると負荷が跳ねるため、再試行時刻を先送りする
                        next_comment_counter_db_retry_time = max(next_comment_counter_db_retry_time, current_time + 15)
                        # DB 接続断が継続している間は、同一エラーのログ連打を抑止する
                        if (current_time - last_comment_counter_error_log_time) > 15:
                            logging.warning(
                                f'WatchSessionAPI [{channel_id}]: Failed to fetch comment counter. Falling back to cached value.',
                                exc_info = ex,
                            )
                            last_comment_counter_error_log_time = current_time
                    else:
                        # Redis 障害など DB 接続断以外の取得失敗時も、接続維持を優先して前回値にフォールバックする
                        ## 短時間の障害でセッション自体を切断しないことを優先する
                        if (current_time - last_comment_counter_error_log_time) > 15:
                            logging.warning(
                                f'WatchSessionAPI [{channel_id}]: Failed to fetch comment counter by unexpected error. Falling back to cached value.',
                                exc_info = ex,
                            )
                            last_comment_counter_error_log_time = current_time

                # 送信した値を次回フォールバック値として保持する
                last_statistics_comment_count = comment_count
                viewer_count = 0
                try:
                    viewer_count = int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, channel_id) or 0)
                except Exception as ex:
                    # Redis 障害時でも statistics 送信を継続し、接続体験の劣化を最小限に抑える
                    if (current_time - last_viewer_counter_error_log_time) > 15:
                        logging.warning(
                            f'WatchSessionAPI [{channel_id}]: Failed to fetch viewer counter. Falling back to zero.',
                            exc_info = ex,
                        )
                        last_viewer_counter_error_log_time = current_time
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'statistics',
                    'data': {
                        'viewers': viewer_count,
                        'comments': comment_count,
                        'adPoints': 0,  # NX-Jikkyo では常に 0 を返す
                        'giftPoints': 0,  # NX-Jikkyo では常に 0 を返す
                    },
                })
                if is_sent is False:
                    return
                last_statistics_time = current_time

            # 45 秒に 1 回サーバー時刻を送信 (互換性のため)
            if (time.time() - last_server_time_time) > 45:
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'serverTime',
                    'data': {
                        'serverTime': timezone.now().isoformat(),
                    },
                })
                if is_sent is False:
                    return
                last_server_time_time = time.time()

            # 30 秒に 1 回 ping を送信 (互換性のため)
            if (time.time() - last_ping_time) > 30:
                is_sent = await SendJSONSafely(websocket, {'type': 'ping'})
                if is_sent is False:
                    return
                last_ping_time = time.time()

            # 処理開始時点では放送中だった場合のみ、スレッドの放送終了時刻を過ぎたら接続を切断する
            ## 最初から過去のスレッドだった場合は実行しない
            if is_on_air is True and timezone.now() > thread.end_at:
                logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected because the thread ended.')
                is_sent = await SendJSONSafely(websocket, {
                    'type': 'disconnect',
                    'data': {
                        'reason': 'END_PROGRAM',
                    },
                })
                if is_sent is False:
                    return
                await CloseWebSocketSafely(websocket, code=1000)  # 正常終了扱い
                return

            # 次の実行まで1秒待つ
            await asyncio.sleep(1)

            # 接続が切れたらタスクを終了
            if IsWebSocketDisconnected(websocket) is True:
                return

    try:

        # 同時接続数カウントを 1 増やす
        await REDIS_CLIENT.hincrby(REDIS_KEY_VIEWER_COUNT, channel_id, 1)

        # クライアントからのメッセージを受信するタスクを実行開始
        receiver_task = asyncio.create_task(RunReceiverTask())

        # 定期的にサーバーからクライアントにメッセージを送信するタスクを実行開始
        sender_task = asyncio.create_task(RunSenderTask())

        # どちらかのタスクが終了したら、もう片方を停止して接続終了処理へ移行する
        ## 片側だけが残ると送信先切断後の余計な例外が増えるため、明示的にキャンセルして整える
        done_tasks, pending_tasks = await asyncio.wait(
            {sender_task, receiver_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        for pending_task in pending_tasks:
            pending_task.cancel()
        if len(pending_tasks) > 0:
            await asyncio.gather(*pending_tasks, return_exceptions=True)
        for done_task in done_tasks:
            done_task_exception = done_task.exception()
            if done_task_exception is not None:
                raise done_task_exception

    except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedOK):
        # 接続が切れた時の処理
        logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected.')

    except websockets.exceptions.WebSocketException as ex:
        # 予期せぬエラー (向こう側のネットワーク接続問題など) で接続が切れた時の処理
        # 念のためこちらからも接続を切断しておく
        logging.error(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected by unexpected error:', exc_info = ex)
        await CloseWebSocketSafely(websocket, code=1011, reason=f'[{channel_id}]: Unexpected error.')

    except Exception as ex:
        if IsWebSocketClosedError(ex) is True:
            logging.info(f'WatchSessionAPI [{channel_id}]: Client {watch_session_client_id} disconnected.')
            return
        logging.error(f'WatchSessionAPI [{channel_id}]: Error during connection:', exc_info = ex)
        is_sent = await SendJSONSafely(websocket, {
            'type': 'disconnect',
            'data': {
                'reason': 'SERVICE_TEMPORARILY_UNAVAILABLE',
            },
        })
        if is_sent is True:
            await CloseWebSocketSafely(websocket, code=1011, reason=f'[{channel_id}]: Error during connection.')

    finally:
        # ここまできたら確実に接続が切断されているので同時接続数カウントを 1 減らす
        ## 最低でも 0 未満にはならないようにする
        try:
            current_count = int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, channel_id) or 0)
            if current_count > 0:
                await REDIS_CLIENT.hincrby(REDIS_KEY_VIEWER_COUNT, channel_id, -1)
        except Exception as ex:
            logging.warning(
                f'WatchSessionAPI [{channel_id}]: Failed to decrement viewer counter on disconnect.',
                exc_info = ex,
            )


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

    # チャンネル ID のリダイレクト処理
    ## jk263 (BSJapanext) への接続は jk200 (BS10) にリダイレクトする
    ## ただし、thread コマンドで指定されたスレッドが jk263 のものの場合はリダイレクトしない
    original_channel_id = channel_id
    if channel_id == 'jk263':
        channel_id = 'jk200'  # 一旦 jk200 にリダイレクト
        logging.info(f'CommentSessionAPI: Channel {original_channel_id} redirected to {channel_id}.')

    # チャンネル ID (jk の prefix 付きなので一旦数値に置換してから) を取得
    ## この channel_id_int はスレッド ID 指定が省略された場合にのみ利用される
    try:
        channel_id_int = int(channel_id.replace('jk', ''))
    except ValueError:
        logging.error(f'CommentSessionAPI [{channel_id}]: Invalid channel ID.')
        await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid channel ID.')
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
        nonlocal channel_id  # channel_id を変更可能にする

        # jk263 の場合のみ、スレッドの所属チャンネル確認処理が必要
        need_check_thread_owner = original_channel_id == 'jk263'

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
                await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid message ({messages} not list).')
                return

            # 送られてくるメッセージは必ず list[dict[str, Any]] となる
            for message in messages:

                # もし辞書型でなかった場合はエラーを返す
                if not isinstance(message, dict):
                    logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message ({message} not dict).')
                    await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid message ({message} not dict).')
                    return

                # ping コマンド
                if 'ping' in message:

                    # ping の名の通り、受け取った ping メッセージをそのままクライアントに送信するのが正しい挙動っぽい
                    ## 例えばコマンドが ping(rs:0), ping(ps:0), thread, ping(pf:0), ping(rf:0) の順で送られてきた場合、
                    ## コマンドのレスポンスは ping(rs:0), ping(ps:0), thread, chat(複数), ping(pf:0), ping(rf:0) の順で送信される
                    ## この挙動を利用すると、送られてくる chat メッセージがどこまで初回取得コメントかをクライアント側で判定できる
                    ## ref: https://scrapbox.io/rinsuki/%E3%83%8B%E3%82%B3%E3%83%8B%E3%82%B3%E7%94%9F%E6%94%BE%E9%80%81%E3%81%AE%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%82%92%E5%8F%96%E3%82%8B
                    is_sent = await SendJSONSafely(websocket, message)
                    if is_sent is False:
                        return

                # thread コマンド
                if 'thread' in message:
                    try:

                        # thread: スレッド ID
                        if 'thread' in message['thread'] and message['thread']['thread'] != '':
                            thread_id = int(message['thread']['thread'])
                            # jk263 の場合のみ、スレッドの所属チャンネル確認処理を実行
                            if need_check_thread_owner:
                                thread = await Thread.filter(id=thread_id).first()
                                if thread and thread.channel_id == 263:
                                    # jk263 の過去ログの場合は channel_id を jk263 に戻す
                                    channel_id = original_channel_id
                                    logging.info(f'CommentSessionAPI: Channel {channel_id} restored for jk263 thread.')
                        else:
                            # スレッド ID が省略されたとき、現在アクティブな (放送中の) スレッドの ID を取得 (NX-Jikkyo 独自仕様)
                            ## 旧ニコ生のコメントサーバーではスレッド ID の指定は必須だった
                            ## スレッド ID に空文字が指定された場合も同様に処理する
                            thread = await GetActiveThread(channel_id_int)
                            if not thread:
                                logging.error(f'CommentSessionAPI [{channel_id}]: Active thread not found.')
                                await CloseWebSocketSafely(websocket, code=1002, reason=f'[{channel_id}]: Active thread not found.')
                                return
                            thread_id = thread.id
                        logging.info(f'CommentSessionAPI [{channel_id}]: Thread ID: {thread_id}')

                        # res_from: 初回にクライアントに送信する最新コメントの数
                        ## res_from が正の値になることはない (はず)
                        res_from = int(message['thread']['res_from'])
                        if res_from > 0:  # 1 以上の res_from には非対応 (本家ニコ生では正の値が来た場合コメ番換算で取得するらしい？)
                            logging.error(f'CommentSessionAPI [{channel_id}]: Invalid res_from: {res_from}')
                            await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid res_from: {res_from}')
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

                    except Exception as ex:
                        if IsWebSocketClosedError(ex) is True:
                            return
                        # 送られてきた thread コマンドの形式が不正
                        logging.error(f'CommentSessionAPI [{channel_id}]: Invalid message. message: {message}', exc_info = ex)
                        await CloseWebSocketSafely(websocket, code=1008, reason=f'[{channel_id}]: Invalid message.')
                        return

                    # ここまできたらスレッド ID と res_from が取得できているので、当該スレッドの情報を取得
                    thread = await Thread.filter(id=thread_id).first()
                    if not thread:
                        # 指定された ID と一致するスレッドが見つからない
                        logging.error(f'CommentSessionAPI [{channel_id}]: Active thread not found.')
                        await CloseWebSocketSafely(websocket, code=1002, reason=f'[{channel_id}]: Active thread not found.')
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
                    is_sent = await SendJSONSafely(websocket, {
                        'thread': {
                            "resultcode": 0,  # 成功
                            "thread": str(thread_id),
                            "last_res": last_comment_no,
                            "ticket": "0x12345678",  # よくわからん値だが NX-Jikkyo では固定値とする
                            "revision": 1,  # よくわからん値だが NX-Jikkyo では固定値とする
                            "server_time": int(time.time()),
                        },
                    })
                    if is_sent is False:
                        return
                    logging.info(f'CommentSessionAPI [{channel_id}]: Thread info sent. thread: {thread_id} / last_res: {last_comment_no}')

                    # 初回取得コメントを連続送信する
                    ## XML 互換データ形式に変換した後、必要に応じて yourpost フラグを設定してから送信している
                    for comment in comments:
                        is_sent = await SendJSONSafely(
                            websocket,
                            SetYourPostFlag(ConvertToXMLCompatibleCommentResponse(comment), thread_key),
                        )
                        if is_sent is False:
                            return

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
            if IsWebSocketDisconnected(websocket) is True:
                return

    async def RunSenderTask(thread: Thread, thread_key: str) -> None:
        """
        指定されたスレッドの新着コメントがあれば随時配信するタスク
        thread コマンドで指定されたスレッドが現在放送中であることを前提に、RunReceiverTask() 側で初回送信した以降のコメントをリアルタイムに配信する

        Args:
            thread (Thread): 新着コメントの取得対象のスレッド情報
            thread_key (str): スレッドキー (互換性のためにこの名前になっているが、実際には接続先クライアントの watch_session_client_id)
        """

        # 接続ごとの送信キューを初期化
        subscriber_queue: asyncio.Queue[CommentBroadcastMessage] = asyncio.Queue(maxsize=COMMENT_QUEUE_MAX_SIZE)
        current_sender_task = asyncio.current_task()
        sender_task_id = id(current_sender_task) if current_sender_task is not None else time.time_ns()
        subscriber_id = f'{comment_session_client_id}:{id(websocket)}:{sender_task_id}'
        subscriber = CommentSubscriber(
            client_id = comment_session_client_id,
            thread_key = thread_key,
            queue = subscriber_queue,
        )

        # スレッド単位の Broadcaster に接続を登録する
        broadcaster = await GetThreadCommentBroadcaster(thread.id)
        await broadcaster.addSubscriber(subscriber_id, subscriber)

        # スレッドの放送終了時刻の Unix 時間
        thread_end_time = thread.end_at.timestamp()

        try:
            while True:

                # 送信キューからコメントを取得する
                ## この待機は最大 5 秒でタイムアウトし、タイムアウト時は接続状態や放送終了判定だけを行う
                try:
                    broadcast_message = await asyncio.wait_for(subscriber_queue.get(), timeout=5.0)
                except TimeoutError:
                    broadcast_message = None

                if broadcast_message is not None:

                    # 取得したコメントに必要に応じて yourpost フラグを設定してから送信
                    if subscriber.thread_key == broadcast_message.user_id:
                        yourpost_response = CopyXMLCompatibleCommentResponse(broadcast_message.base_comment)
                        is_sent = await SendJSONSafely(
                            websocket,
                            SetYourPostFlag(yourpost_response, subscriber.thread_key),
                        )
                        if is_sent is False:
                            return
                    else:
                        is_sent = await SendTextSafely(websocket, broadcast_message.raw_json)
                        if is_sent is False:
                            return

                # 接続が切れたらタスクを終了
                ## 通常は Receiver Task 側で接続切断を検知した後このタスク自体がキャンセルされるため、ここには到達しないはず
                if IsWebSocketDisconnected(websocket) is True:
                    return

                # 最新コメント配信中に当該スレッドの放送終了時刻を過ぎた場合は接続を切断する
                if time.time() > thread_end_time:
                    logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected because the thread ended.')
                    await CloseWebSocketSafely(websocket, code=1000)  # 正常終了扱い
                    return

        finally:
            # タスク終了時に確実に接続を削除する
            await broadcaster.removeSubscriber(subscriber_id, subscriber)
            await CleanupThreadCommentBroadcaster(thread.id, broadcaster)

    try:

        # クライアントからのメッセージを受信するタスクの実行が完了するまで待機
        ## サーバーからクライアントにメッセージを送信するタスクは必要に応じて起動される
        await RunReceiverTask()

    except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedOK):
        # 接続が切れた時の処理
        logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected.')

    except websockets.exceptions.WebSocketException as ex:
        # 予期せぬエラー (向こう側のネットワーク接続問題など) で接続が切れた時の処理
        # 念のためこちらからも接続を切断しておく
        logging.error(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected by unexpected error:', exc_info = ex)
        await CloseWebSocketSafely(websocket, code=1011, reason=f'[{channel_id}]: Unexpected error.')

    except Exception as ex:
        if IsWebSocketClosedError(ex) is True:
            logging.info(f'CommentSessionAPI [{channel_id}]: Client {comment_session_client_id} disconnected.')
            return
        logging.error(f'CommentSessionAPI [{channel_id}]: Error during connection:', exc_info = ex)
        await CloseWebSocketSafely(websocket, code=1011, reason=f'[{channel_id}]: Error during connection.')

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
            except Exception as ex:
                if IsWebSocketClosedError(ex) is False:
                    raise
