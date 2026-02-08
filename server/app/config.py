
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    アプリケーションの設定を表す Pydantic モデル
    .env ファイルから自動で設定を読み込む
    """

    model_config = SettingsConfigDict(
        env_file = Path(__file__).resolve().parent.parent.parent / '.env',
        env_file_encoding = 'utf-8',
        env_ignore_empty=True,
        extra='ignore',
    )

    # 基本
    ENVIRONMENT: Literal['Develop', 'Production'] = 'Develop'
    SERVER_PORT: int = 5610
    SPECIFIED_SERVER_PORT: int = 5610  # 実際は .env 内の環境変数としては存在せず、便宜上の値
    SUB_SERVER_PROCESS_COUNT: int = 0

    # データベース接続
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # ニコニコ連携
    NICONICO_OAUTH_CLIENT_ID: str
    NICONICO_OAUTH_CLIENT_SECRET: str


# ref: https://github.com/pydantic/pydantic/blob/main/docs/visual_studio_code.md#basesettings-and-ignoring-pylancepyright-errors
CONFIG = Config.model_validate({})
