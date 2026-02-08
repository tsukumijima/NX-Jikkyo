import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from tortoise import connections
from tortoise.backends.base.client import TransactionalDBClient
from tortoise.transactions import in_transaction

from app import logging


TransactionResultType = TypeVar('TransactionResultType')

def HasStaleTransactionConnectionContext() -> bool:
    """
    現在コンテキスト上の接続が壊れた TransactionWrapper かどうかを判定する

    Returns:
        bool: 壊れた TransactionWrapper が残っている場合は True
    """

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

    current_connection = connections.get('default')
    parent_connection = getattr(current_connection, '_parent', None)
    wrapped_connection = getattr(current_connection, '_connection', None)

    if parent_connection is None or wrapped_connection is not None:
        return False

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

    for retry_count in range(max_retry_attempts):
        if RecoverStaleTransactionConnectionContext() is True:
            logging.warning(
                f'{operation_name}: Recovered stale transaction connection context before starting transaction.',
            )

        try:
            async with in_transaction() as connection:
                return await operation(connection)
        except Exception as ex:
            is_retryable_error = HasStaleTransactionConnectionContext()
            is_last_retry = retry_count >= (max_retry_attempts - 1)
            if is_retryable_error is False or is_last_retry is True:
                raise

            logging.warning(
                f'{operation_name}: Failed to start transaction due to stale connection context. Retrying... '
                f'attempt: {retry_count + 1}/{max_retry_attempts}',
                exc_info = ex,
            )

            RecoverStaleTransactionConnectionContext()
            await asyncio.sleep(retry_wait_seconds)

    raise RuntimeError(f'{operation_name}: Failed to execute transaction after retries.')
