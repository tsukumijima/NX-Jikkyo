
import httpx
import pkgutil
from passlib.context import CryptContext
from pathlib import Path
from typing import Any

from app.config import CONFIG


# バージョン
VERSION = '1.2.1'

# ベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# クライアントの静的ファイルがあるディレクトリ
CLIENT_DIR = BASE_DIR.parent / 'client/dist'

# データディレクトリ
DATA_DIR = BASE_DIR / 'data'

# スタティックディレクトリ
STATIC_DIR = BASE_DIR / 'static'
## ロゴファイルがあるディレクトリ
LOGO_DIR = STATIC_DIR / 'logos'

# ログディレクトリ
LOGS_DIR = BASE_DIR / 'logs'
## NX-Jikkyo のサーバーログのパス
NX_JIKKYO_SERVER_LOG_PATH = LOGS_DIR / 'NX-Jikkyo-Server.log'
## NX-Jikkyo のアクセスログのパス
NX_JIKKYO_ACCESS_LOG_PATH = LOGS_DIR / 'NX-Jikkyo-Access.log'

# データベース (Tortoise ORM) の設定
__model_list = [name for _, name, _ in pkgutil.iter_modules(path=['app/models'])]
DATABASE_CONFIG = {
    'timezone': 'Asia/Tokyo',
    'connections': {
        'default': f'mysql://{CONFIG.MYSQL_USER}:{CONFIG.MYSQL_PASSWORD}@nx-jikkyo-mysql:3306/{CONFIG.MYSQL_DATABASE}',
    },
    'apps': {
        'models': {
            'models': [f'app.models.{name}' for name in __model_list] + ['aerich.models'],
            'default_connection': 'default',
        }
    }
}

# Uvicorn のロギング設定
## この dictConfig を Uvicorn に渡す (NX-Jikkyo 本体のロギング設定は app.logging に別で存在する)
## Uvicorn のもとの dictConfig を参考にして作成した
## ref: https://github.com/encode/uvicorn/blob/0.18.2/uvicorn/config.py#L95-L126
LOGGING_CONFIG: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # サーバーログ用のログフォーマッター
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s] %(levelprefix)s %(message)s',
        },
        'default_file': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s] %(levelprefix)s %(message)s',
            'use_colors': False,  # ANSI エスケープシーケンスを出力しない
        },
        # サーバーログ (デバッグ) 用のログフォーマッター
        'debug': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s] %(levelprefix)s %(pathname)s:%(lineno)s:\n'
                '                                %(message)s',
        },
        'debug_file': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s] %(levelprefix)s %(pathname)s:%(lineno)s:\n'
                '                                %(message)s',
            'use_colors': False,  # ANSI エスケープシーケンスを出力しない
        },
        # アクセスログ用のログフォーマッター
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        'access_file': {
            '()': 'uvicorn.logging.AccessFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            'use_colors': False,  # ANSI エスケープシーケンスを出力しない
        },
    },
    'handlers': {
        ## サーバーログは標準エラー出力と server/logs/NX-Jikkyo-Server.log の両方に出力する
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'default_file': {
            'formatter': 'default_file',
            'class': 'logging.FileHandler',
            'filename': NX_JIKKYO_SERVER_LOG_PATH,
            'mode': 'a',
            'encoding': 'utf-8',
        },
        ## サーバーログ (デバッグ) は標準エラー出力と server/logs/NX-Jikkyo-Server.log の両方に出力する
        'debug': {
            'formatter': 'debug',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'debug_file': {
            'formatter': 'debug_file',
            'class': 'logging.FileHandler',
            'filename': NX_JIKKYO_SERVER_LOG_PATH,
            'mode': 'a',
            'encoding': 'utf-8',
        },
        ## アクセスログは標準出力と server/logs/NX-Jikkyo-Access.log の両方に出力する
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'access_file': {
            'formatter': 'access_file',
            'class': 'logging.FileHandler',
            'filename': NX_JIKKYO_ACCESS_LOG_PATH,
            'mode': 'a',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'uvicorn': {'level': 'INFO', 'handlers': ['default', 'default_file']},
        'uvicorn.debug': {'level': 'DEBUG', 'handlers': ['debug', 'debug_file'], 'propagate': False},
        'uvicorn.access': {'level': 'INFO', 'handlers': ['access', 'access_file'], 'propagate': False},
        'uvicorn.error': {'level': 'INFO'},
    },
}

# パスワードハッシュ化のための設定
PASSWORD_CONTEXT = CryptContext(
    schemes = ['bcrypt'],
    deprecated = 'auto',
)

# 外部 API に送信するリクエストヘッダー
## NX-Jikkyo の User-Agent を指定
API_REQUEST_HEADERS: dict[str, str] = {
    'User-Agent': f'NX-Jikkyo/{VERSION}',
}

# NX-Jikkyo で利用する httpx.AsyncClient の設定
## httpx.AsyncClient 自体は一度使ったら再利用できないので、httpx.AsyncClient を返す関数にしている
HTTPX_CLIENT = lambda: httpx.AsyncClient(
    # NX-Jikkyo の User-Agent を指定
    headers = API_REQUEST_HEADERS,
    # リダイレクトを追跡する
    follow_redirects = True,
    # 3 秒応答がない場合はタイムアウトする
    timeout = 3.0,
)
