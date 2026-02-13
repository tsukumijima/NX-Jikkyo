
import pkgutil
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from redis.asyncio.client import Redis

from app.config import CONFIG


# バージョン
VERSION = '1.13.2'

# 日本標準時 (JST, UTC+9) の ZoneInfo
## このサーバーは主に日本向けのサービスのため、日時は JST で統一して扱う
JST = ZoneInfo('Asia/Tokyo')

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
## サーバーログのアーカイブ（日付別ログ）を格納するサブディレクトリ
## ログディレクトリ直下にアーカイブが大量に並ぶとノイズになるため、サブディレクトリに分離する
LOGS_ARCHIVES_DIR = LOGS_DIR / 'archives'
## サーバーログのアーカイブの保持期限 (日数)
## 30 日を超えたアーカイブログを自動削除する
SERVER_LOG_ARCHIVE_RETENTION_DAYS: int | None = 30
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
            ## maxsize はプロセスあたりの MySQL 接続プール上限で、デフォルト 5 だとメインプロセスの
            ## StreamNicoliveComments タスク (10チャンネル分) や CacheChannelResponses でプール競合が発生しやすいため 15 に引き上げている
            ## 5 プロセス × 15 = 最大 75 接続で、MySQL の max_connections=80 の範囲内に収まる
            f'mysql://{CONFIG.MYSQL_USER}:{CONFIG.MYSQL_PASSWORD}@nx-jikkyo-mysql:3306/{CONFIG.MYSQL_DATABASE}?connect_timeout=3&pool_recycle=1800&maxsize=15'
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
            'format': '[%(asctime)s.%(msecs)03d] %(levelprefix)s %(message)s',
        },
        'default_file': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s.%(msecs)03d] %(levelprefix)s %(message)s',
            'use_colors': False,  # ANSI エスケープシーケンスを出力しない
        },
        # サーバーログ (デバッグ) 用のログフォーマッター
        'debug': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s.%(msecs)03d] %(levelprefix)s %(pathname)s:%(lineno)s:\n'
            '                                %(message)s',
        },
        'debug_file': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s.%(msecs)03d] %(levelprefix)s %(pathname)s:%(lineno)s:\n'
            '                                %(message)s',
            'use_colors': False,  # ANSI エスケープシーケンスを出力しない
        },
        # アクセスログ用のログフォーマッター
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s.%(msecs)03d] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        'access_file': {
            '()': 'uvicorn.logging.AccessFormatter',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'format': '[%(asctime)s.%(msecs)03d] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
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
            'class': 'app.utils.log_rotation.DailyRotatingFileHandler',
            'filename': NX_JIKKYO_SERVER_LOG_PATH,
            'encoding': 'utf-8',
            'retention_days': SERVER_LOG_ARCHIVE_RETENTION_DAYS,
        },
        ## サーバーログ (デバッグ) は標準エラー出力と server/logs/NX-Jikkyo-Server.log の両方に出力する
        'debug': {
            'formatter': 'debug',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'debug_file': {
            'formatter': 'debug_file',
            'class': 'app.utils.log_rotation.DailyRotatingFileHandler',
            'filename': NX_JIKKYO_SERVER_LOG_PATH,
            'encoding': 'utf-8',
            'retention_days': SERVER_LOG_ARCHIVE_RETENTION_DAYS,
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

# マスタデータとして扱う実況チャンネル情報
## app.py の RegisterMasterChannels() で channels テーブルへ反映するソースオブジェクト
## WebSocket 側の既知チャンネル判定でも同じ定義を使い、重複定義による不整合を防ぐ
MASTER_CHANNEL_INFOS: dict[str, dict[str, str]] = {
    'jk1': {'name': 'NHK総合'},
    'jk2': {'name': 'NHK Eテレ'},
    'jk4': {'name': '日本テレビ'},
    'jk5': {'name': 'テレビ朝日'},
    'jk6': {'name': 'TBSテレビ'},
    'jk7': {'name': 'テレビ東京'},
    'jk8': {'name': 'フジテレビ'},
    'jk9': {'name': 'TOKYO MX'},
    'jk10': {'name': 'テレ玉'},
    'jk11': {'name': 'tvk'},
    'jk12': {'name': 'チバテレビ'},
    'jk13': {'name': 'サンテレビ'},
    'jk14': {'name': 'KBS京都'},
    'jk101': {'name': 'NHK BS'},
    'jk103': {'name': 'NHK BSプレミアム4K'},
    'jk141': {'name': 'BS日テレ'},
    'jk151': {'name': 'BS朝日'},
    'jk161': {'name': 'BS-TBS'},
    'jk171': {'name': 'BSテレ東'},
    'jk181': {'name': 'BSフジ'},
    'jk191': {'name': 'WOWOW PRIME'},
    'jk192': {'name': 'WOWOW LIVE'},
    'jk193': {'name': 'WOWOW CINEMA'},
    'jk200': {'name': 'BS10'},  # 旧 BSJapanext
    'jk201': {'name': 'BS10スターチャンネル'},
    'jk211': {'name': 'BS11'},
    'jk222': {'name': 'BS12'},
    'jk236': {'name': 'BSアニマックス'},
    'jk252': {'name': 'WOWOW PLUS'},
    'jk260': {'name': 'BS松竹東急'},
    'jk263': {'name': 'BSJapanext'},  # 後方互換性のために維持。WebSocket 接続時は jk200 にリダイレクト
    'jk265': {'name': 'BSよしもと'},
    'jk333': {'name': 'AT-X'},
}

# NX-Jikkyo が提供している実況チャンネル ID の集合
## MASTER_CHANNEL_INFOS から機械的に生成し、参照側での重複定義を避ける
KNOWN_JIKKYO_CHANNEL_IDS: frozenset[int] = frozenset(
    int(channel_id.replace('jk', ''))
    for channel_id in MASTER_CHANNEL_INFOS
)
