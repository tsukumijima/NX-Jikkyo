
import logging
import logging.config
from typing import Any

from app.config import CONFIG
from app.constants import LOGGING_CONFIG


# Uvicorn を起動する前に Uvicorn のロガーを使えるようにする
logging.config.dictConfig(LOGGING_CONFIG)

# ロガーを取得
logger = logging.getLogger('uvicorn')
logger_debug = logging.getLogger('uvicorn.debug')


def debug(message: Any) -> None:
    """
    デバッグログを出力する

    Args:
        message (Any): ログメッセージ
    """
    if CONFIG.ENVIRONMENT == 'Develop':
        logger_debug.debug(message, stacklevel=2)


def debug_simple(message: Any) -> None:
    """
    デバッグログを出力する (スクリプトパス・行番号を出力しない)

    Args:
        message (Any): ログメッセージ
    """
    if CONFIG.ENVIRONMENT == 'Develop':
        logger.setLevel(logging.DEBUG)
        logger.debug(message, stacklevel=2)
        logger.setLevel(logging.INFO)


def info(message: Any) -> None:
    """
    情報ログを出力する

    Args:
        message (Any): ログメッセージ
    """
    logger.info(message, stacklevel=2)


def warning(message: Any) -> None:
    """
    警告ログを出力する

    Args:
        message (Any): ログメッセージ
    """
    logger.warning(message, stacklevel=2)


def error(message: Any) -> None:
    """
    エラーログを出力する

    Args:
        message (Any): ログメッセージ
    """
    logger.error(message, stacklevel=2)
