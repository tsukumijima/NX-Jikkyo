import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from tortoise import connections
from tortoise.backends.base.client import TransactionalDBClient
from tortoise.transactions import in_transaction

from app import logging


TransactionResultType = TypeVar('TransactionResultType')
# DB ダウン時にドライバ層から返る代表的なメッセージ断片を保持する
## 例外型だけでは取りこぼすケースがあるため、メッセージ判定を併用する
DATABASE_CONNECTION_UNAVAILABLE_MESSAGES: list[str] = [
    "Can't connect to MySQL server",
    'Lost connection to MySQL server',
    'Connection refused',
]


def IsDatabaseConnectionUnavailableError(exception: Exception) -> bool:
    """
    一時的な DB 接続断に起因する例外かどうかを判定する

    Args:
        exception (Exception): 判定対象の例外

    Returns:
        bool: 一時的な DB 接続断に起因する場合は True
    """

    current_exception: BaseException | None = exception
    # __cause__ / __context__ を辿る回数の上限
    ## 無限ループを避けつつ、十分な深さで原因例外を探索する
    traversal_count = 0
    max_traversal_count = 8
    while current_exception is not None and traversal_count < max_traversal_count:
        # ドライバ差分を吸収するため、接続断で出やすい組み込み例外をまず判定する
        if isinstance(current_exception, ConnectionRefusedError | TimeoutError | ConnectionError):
            return True

        # ラッパー例外に包まれても検知できるよう、文字列メッセージでも判定する
        current_exception_message = str(current_exception)
        for unavailable_message in DATABASE_CONNECTION_UNAVAILABLE_MESSAGES:
            if unavailable_message in current_exception_message:
                return True

        # 直近原因へ辿って再判定する
        current_exception = current_exception.__cause__ or current_exception.__context__
        traversal_count += 1
    return False


def HasStaleTransactionConnectionContext() -> bool:
    """
    現在コンテキスト上の接続が壊れた TransactionWrapper かどうかを判定する

    Returns:
        bool: 壊れた TransactionWrapper が残っている場合は True
    """

    # Tortoise ORM の TransactionWrapper は _parent を持つ
    ## ただし pool acquire に失敗した壊れた wrapper は _connection が None のまま残る
    current_connection = connections.get('default')
    parent_connection = getattr(current_connection, '_parent', None)
    wrapped_connection = getattr(current_connection, '_connection', None)

    # TransactionWrapper は _parent を持ち、pool から acquire できていない場合は _connection が None のまま残る
    return parent_connection is not None and wrapped_connection is None


def RecoverStaleTransactionConnectionContext() -> bool:
    """
    壊れた TransactionWrapper が残っている場合に、親接続へ差し戻して復旧する

    Returns:
        bool: 復旧処理を実行した場合は True
    """

    # 現在コンテキストに残っている接続情報を確認する
    current_connection = connections.get('default')
    parent_connection = getattr(current_connection, '_parent', None)
    wrapped_connection = getattr(current_connection, '_connection', None)

    # wrapper が健全か、そもそも wrapper ではない場合は何もしない
    if parent_connection is None or wrapped_connection is not None:
        return False

    # 壊れた wrapper を捨て、親接続を current context に戻す
    connections.set('default', parent_connection)
    return True


async def RunTransactionWithReconnectRetry(
    operation: Callable[[TransactionalDBClient], Awaitable[TransactionResultType]],
    operation_name: str,
    max_retry_attempts: int = 3,
    retry_wait_seconds: float = 0.2,
) -> TransactionResultType:
    """
    トランザクション開始時の接続異常を検知した場合に、接続を再取得して再試行する

    Args:
        operation (Callable[[TransactionalDBClient], Awaitable[TransactionResultType]]): トランザクション内で実行する処理
        operation_name (str): ログ出力用の操作名
        max_retry_attempts (int, optional): 最大リトライ回数. Defaults to 3.
        retry_wait_seconds (float, optional): リトライ前の待機秒数. Defaults to 0.2.

    Returns:
        TransactionResultType: operation の戻り値
    """

    # トランザクション開始時の失敗は再試行で回復する余地があるため、限定的にリトライする
    for retry_count in range(max_retry_attempts):
        # 直前失敗で壊れた wrapper が残っている場合を先に回復する
        if RecoverStaleTransactionConnectionContext() is True:
            logging.warning(
                f'{operation_name}: Recovered stale transaction connection context before starting transaction.',
            )

        try:
            async with in_transaction() as connection:
                return await operation(connection)
        except Exception as ex:
            # DB ダウン系のエラーは、短い backoff で再試行して吸収する
            is_database_unavailable_error = IsDatabaseConnectionUnavailableError(ex)
            is_last_retry = retry_count >= (max_retry_attempts - 1)
            if is_database_unavailable_error is True:
                if is_last_retry is True:
                    raise

                # 障害復旧直後の突発負荷を避けるため、試行回数に応じて待機時間をわずかに伸ばす
                retry_wait_seconds_for_unavailable_db = min(retry_wait_seconds * (retry_count + 1), 1.0)
                logging.warning(
                    f'{operation_name}: Database is temporarily unavailable. Retrying... '
                    f'attempt: {retry_count + 1}/{max_retry_attempts}',
                    exc_info = ex,
                )
                await asyncio.sleep(retry_wait_seconds_for_unavailable_db)
                continue

            # DB ダウン以外でも、壊れた TransactionWrapper が残っているケースだけは再試行対象にする
            is_retryable_error = HasStaleTransactionConnectionContext()
            if is_retryable_error is False or is_last_retry is True:
                raise

            logging.warning(
                f'{operation_name}: Failed to start transaction due to stale connection context. Retrying... '
                f'attempt: {retry_count + 1}/{max_retry_attempts}',
                exc_info = ex,
            )

            # 念のためここでも context 回復を実行してから再試行する
            RecoverStaleTransactionConnectionContext()
            await asyncio.sleep(retry_wait_seconds)

    # for ループ内ですべて return / raise / continue されるため、ここは理論上到達しない
    assert False, f'{operation_name}: Unreachable control flow in transaction retry loop.'
