
import atexit
import logging
import logging.config
import time
from logging.handlers import QueueHandler, QueueListener
from queue import Full, Queue
from threading import Lock
from typing import Any, cast

from app.config import CONFIG
from app.constants import LOGGING_CONFIG


class NonBlockingQueueHandler(QueueHandler):
    """
    asyncio のイベントループをなるべく止めずにログをキューへ積む QueueHandler
    """

    def __init__(
        self,
        queue: Queue[logging.LogRecord],
        drop_report_interval_seconds: float = 60.0,
    ) -> None:
        """
        NonBlockingQueueHandler のコンストラクタ

        Args:
            queue (Queue[logging.LogRecord]): ログレコードを積むキュー
            drop_report_interval_seconds (float): ドロップ件数を警告として再通知する最短間隔 (秒)
        """

        # QueueHandler の標準初期化を先に行う
        super().__init__(queue)
        # ドロップ集計の通知間隔を保持する
        self.drop_report_interval_seconds = drop_report_interval_seconds
        # 低優先度ログ (INFO / DEBUG) のドロップ件数を保持する
        self._dropped_info_debug_count = 0
        # 高優先度ログ (WARNING / ERROR) のドロップ件数を保持する
        self._dropped_warning_error_count = 0
        # 直近でドロップ集計を通知した時刻を保持する
        self._last_drop_report_time = time.monotonic()
        # 複数スレッドからの件数更新を安全にするためのロック
        self._drop_count_lock = Lock()

    def enqueue(self, record: logging.LogRecord) -> None:
        """
        ログレコードを非ブロッキング優先でキューに投入する

        Args:
            record (logging.LogRecord): 追加するログレコード
        """

        # まずは完全非ブロッキングでキュー投入を試みる
        is_enqueued = self._enqueue_non_blocking(record)
        if is_enqueued is True:
            # 正常投入時も、以前のドロップ集計があれば通知する
            self._emit_drop_summary_if_needed()
            return

        # キューが飽和している場合は、重要度に応じて扱いを変える
        ## INFO / DEBUG はイベントループ保護を優先してドロップする
        ## WARNING / ERROR は短時間だけ再試行し、極力取りこぼさない
        if record.levelno >= logging.WARNING:
            try:
                # 高優先度ログだけ、ごく短時間だけブロッキング再試行する
                log_queue = cast(Queue[logging.LogRecord], self.queue)
                log_queue.put(record, block=True, timeout=0.005)
                self._emit_drop_summary_if_needed()
                return
            except Full:
                # 再試行しても満杯の場合はドロップ集計へ回す
                pass

        # ドロップしたログ件数をレベル別に加算する
        with self._drop_count_lock:
            if record.levelno >= logging.WARNING:
                self._dropped_warning_error_count += 1
            else:
                self._dropped_info_debug_count += 1
        # 一定間隔で集約警告を出す
        self._emit_drop_summary_if_needed()

    def _enqueue_non_blocking(self, record: logging.LogRecord) -> bool:
        """
        ログレコードをブロッキングなしで投入する

        Args:
            record (logging.LogRecord): 追加するログレコード

        Returns:
            bool: キュー投入に成功した場合は True
        """

        try:
            log_queue = cast(Queue[logging.LogRecord], self.queue)
            log_queue.put_nowait(record)
            return True
        except Full:
            return False

    def _emit_drop_summary_if_needed(self) -> None:
        """
        ドロップ件数がある場合に一定間隔で集約警告を投入する
        """

        with self._drop_count_lock:
            # 現在のドロップ件数をスナップショットとして取得する
            dropped_info_debug_count = self._dropped_info_debug_count
            dropped_warning_error_count = self._dropped_warning_error_count
            current_time = time.monotonic()
            elapsed_seconds = current_time - self._last_drop_report_time
            # 通知間隔を満たし、かつドロップ件数が 1 件以上ある場合のみ通知対象とする
            should_report = (
                (dropped_info_debug_count + dropped_warning_error_count) > 0
                and elapsed_seconds >= self.drop_report_interval_seconds
            )
            if should_report is False:
                return

            # 集約通知に進む時点でカウンタをリセットする
            self._dropped_info_debug_count = 0
            self._dropped_warning_error_count = 0
            self._last_drop_report_time = current_time

        # 集約通知は通常ログと同じ経路で扱えるよう LogRecord として構築する
        summary_record = logging.LogRecord(
            name='uvicorn',
            level=logging.WARNING,
            pathname=__file__,
            lineno=0,
            msg=(
                'Async logging queue dropped records. '
                f'dropped_info_debug: {dropped_info_debug_count}, '
                f'dropped_warning_error: {dropped_warning_error_count}'
            ),
            args=(),
            exc_info=None,
        )
        # 集約通知自体が投入できなかった場合は、ドロップ件数を戻して次回通知へ繰り越す
        if self._enqueue_non_blocking(summary_record) is False:
            with self._drop_count_lock:
                self._dropped_info_debug_count += dropped_info_debug_count
                self._dropped_warning_error_count += dropped_warning_error_count


def InitializeAsyncLogging() -> QueueListener | None:
    """
    Uvicorn ロガーを QueueHandler + QueueListener 構成に置き換える

    Returns:
        QueueListener | None: 初期化に成功した場合は QueueListener、不要な場合は None
    """

    # 既存の Uvicorn ロガーを取得し、現在のハンドラ構成を退避する
    uvicorn_logger = logging.getLogger('uvicorn')
    existing_handlers = list(uvicorn_logger.handlers)
    if len(existing_handlers) == 0:
        # ハンドラが未設定なら差し替え不要なので終了する
        return None

    # 既存フォーマッタや既存ハンドラをそのまま活かし、書き込みだけ別スレッドへ逃がす
    ## INFO 全件ログは維持しつつ、イベントループでのファイル I/O 待機を削減する
    log_queue: Queue[logging.LogRecord] = Queue(maxsize=20000)
    queue_handler = NonBlockingQueueHandler(log_queue)
    queue_handler.setLevel(logging.DEBUG)
    uvicorn_logger.handlers = [queue_handler]

    # 実際のハンドラ実行は QueueListener 側へ移譲する
    queue_listener = QueueListener(log_queue, *existing_handlers, respect_handler_level=True)
    queue_listener.start()
    return queue_listener


def ShutdownAsyncLogging(queue_listener: QueueListener | None) -> None:
    """
    QueueListener を安全に停止する

    Args:
        queue_listener (QueueListener | None): 停止対象の QueueListener
    """

    if queue_listener is None:
        return
    # プロセス終了時に残ログを可能な範囲で flush しつつ停止する
    queue_listener.stop()


# Uvicorn を起動する前に Uvicorn のロガーを使えるようにする
logging.config.dictConfig(LOGGING_CONFIG)
# QueueHandler + QueueListener でログ書き込みを非同期化する
active_queue_listener = InitializeAsyncLogging()
# プロセス終了時に QueueListener を確実に停止する
atexit.register(ShutdownAsyncLogging, active_queue_listener)

# ロガーを取得
logger = logging.getLogger('uvicorn')


def debug(message: Any, *args: Any, exc_info: BaseException | bool | None = None) -> None:
    """
    デバッグログを出力する (スクリプトパス・行番号を出力しない)

    Args:
        message (Any): ログメッセージ
    """
    if CONFIG.ENVIRONMENT == 'Develop':
        logger.setLevel(logging.DEBUG)
        logger.debug(message, *args, exc_info=exc_info, stacklevel=2)
        logger.setLevel(logging.INFO)


def info(message: Any, *args: Any, exc_info: BaseException | bool | None = None) -> None:
    """
    情報ログを出力する

    Args:
        message (Any): ログメッセージ
    """
    logger.info(message, *args, exc_info=exc_info, stacklevel=2)


def warning(message: Any, *args: Any, exc_info: BaseException | bool | None = None) -> None:
    """
    警告ログを出力する

    Args:
        message (Any): ログメッセージ
    """
    logger.warning(message, *args, exc_info=exc_info, stacklevel=2)


def error(message: Any, *args: Any, exc_info: BaseException | bool | None = None) -> None:
    """
    エラーログを出力する

    Args:
        message (Any): ログメッセージ
    """
    logger.error(message, *args, exc_info=exc_info, stacklevel=2)
