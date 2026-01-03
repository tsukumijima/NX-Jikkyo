
import logging
import logging.config
from typing import Any

from app.config import CONFIG
from app.constants import LOGGING_CONFIG


# Uvicorn を起動する前に Uvicorn のロガーを使えるようにする
logging.config.dictConfig(LOGGING_CONFIG)

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
