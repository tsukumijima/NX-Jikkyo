
import pkgutil
from pathlib import Path
from typing import Any

import httpx
from redis.asyncio.client import Redis

from app.config import CONFIG


# バージョン
VERSION = '1.13.2'

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
        'default': (
            # 接続確立待ちが長引くと WebSocket タスク全体が詰まるため、DB ダウン時は短時間で失敗させる
            ## Tortoise ORM の URL パラメータとして connect_timeout が公式に受理され、aiomysql へ引き渡される
            ## 3 秒は「瞬断時の再試行余地」と「障害時の素早いフォールバック」のバランスを取った値
            ## pool_recycle は長寿命接続を定期的に作り直し、古い接続再利用による失敗率を下げるために指定する
            f'mysql://{CONFIG.MYSQL_USER}:{CONFIG.MYSQL_PASSWORD}@nx-jikkyo-mysql:3306/{CONFIG.MYSQL_DATABASE}?connect_timeout=3&pool_recycle=1800'
        ),
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
    # HTTP/2 を使用する
    http2 = True,
)

# Redis クライアント
REDIS_CLIENT = Redis.from_url('redis://nx-jikkyo-redis', encoding='utf-8', decode_responses=True)
# Redis 上でスレッドに投稿されたコメントを Pub/Sub するチャンネルの Prefix
REDIS_CHANNEL_THREAD_COMMENTS_PREFIX = 'nx-jikkyo:thread_comments'
# Redis 上のチャンネル情報キャッシュのキー
REDIS_KEY_CHANNEL_INFOS_CACHE = 'nx-jikkyo:channel_infos_cache'
# Redis 上の実況勢いカウントのキー
REDIS_KEY_JIKKYO_FORCE_COUNT = 'nx-jikkyo:jikkyo_force_counts'
# Redis 上の同時接続数カウントのキー
REDIS_KEY_VIEWER_COUNT = 'nx-jikkyo:viewer_counts'
# Redis 上のスレッドごとの最新コメ番キャッシュのキー
REDIS_KEY_THREAD_COMMENT_COUNTER = 'nx-jikkyo:thread_comment_counters'
