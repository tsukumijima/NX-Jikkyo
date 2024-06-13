
import tortoise.contrib.fastapi
import tortoise.log
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_restful.tasks import repeat_every
from pathlib import Path
from zoneinfo import ZoneInfo

from app import logging
from app.config import CONFIG
from app.constants import (
    CLIENT_DIR,
    DATABASE_CONFIG,
    VERSION,
)
from app.models.comment import (
    Channel,
    Comment,
    CommentCounter,
    Thread,
)
from app.routers import (
    channels,
    threads,
    websocket,
)


# FastAPI を初期化
app = FastAPI(
    title = 'NX-Jikkyo',
    description = 'NX-Jikkyo: Nico Nico Jikkyo Alternatives<br><br>'
        'この API ドキュメントには WebSocket API のドキュメントは掲載されていません。ご了承ください。<br>'
        'ニコ生互換の視聴セッション WebSocket の URL は wss://nx-jikkyo.tsukumijima.net/api/v1/channels/(実況ID, ex: jk211)/ws/watch です。<br>'
        'ニコ生統合後の新ニコニコ実況対応クライアントであれば、ニコ生視聴ページに埋め込まれている JSON (embedded-data) 内の site.relive.webSocketUrl から取得していた接続先 WebSocket の URL を、上記 URL に差し替えるだけで対応できるはずです。',
    version = VERSION,
    openapi_url = '/api/v1/openapi.json',
    docs_url = '/api/v1/docs',
    redoc_url = '/api/v1/redoc',
)

# ルーターを登録
app.include_router(channels.router)
app.include_router(threads.router)
app.include_router(websocket.router)

# CORS の設定
## 開発環境では全てのオリジンからのリクエストを許可
## 本番環境では全てのオリジンからのリクエストを拒否
CORS_ORIGINS = ['*'] if CONFIG.ENVIRONMENT == 'Develop' else []
app.add_middleware(
    CORSMiddleware,
    allow_origins = CORS_ORIGINS,
    allow_methods = CORS_ORIGINS,
    allow_headers = CORS_ORIGINS,
    allow_credentials = True,
)

# 静的ファイルの配信
app.mount('/assets', StaticFiles(directory=CLIENT_DIR / 'assets', html=True))

# ルート以下のルーティング
# ファイルが存在すればそのまま配信し、ファイルが存在しなければ index.html を返す
@app.get('/{file:path}', include_in_schema=False)
async def Root(file: str):

    # ディレクトリトラバーサル対策のためのチェック
    ## ref: https://stackoverflow.com/a/45190125/17124142
    try:
        CLIENT_DIR.joinpath(Path(file)).resolve().relative_to(CLIENT_DIR.resolve())
    except ValueError:
        # URL に指定されたファイルパスが CLIENT_DIR の外側のフォルダを指している場合は、
        # ファイルが存在するかに関わらず一律で index.html を返す
        return FileResponse(CLIENT_DIR / 'index.html', media_type='text/html')

    # ファイルが存在する場合のみそのまま配信
    filepath = CLIENT_DIR / file
    if filepath.is_file():
        # 拡張子から MIME タイプを判定
        if filepath.suffix == '.css':
            mime = 'text/css'
        elif filepath.suffix == '.html':
            mime = 'text/html'
        elif filepath.suffix == '.ico':
            mime = 'image/x-icon'
        elif filepath.suffix == '.js':
            mime = 'application/javascript'
        elif filepath.suffix == '.json':
            mime = 'application/json'
        elif filepath.suffix == '.map':
            mime = 'application/json'
        else:
            mime = 'text/plain'
        return FileResponse(filepath, media_type=mime)

    # デフォルトドキュメント (index.html)
    # URL の末尾にスラッシュがついている場合のみ
    elif (filepath / 'index.html').is_file() and (file == '' or file[-1] == '/'):
        return FileResponse(filepath / 'index.html', media_type='text/html')

    # 存在しない静的ファイルが指定された場合
    else:
        if file.startswith('api/'):
            # パスに api/ が前方一致で含まれているなら、404 Not Found を返す
            return JSONResponse({'detail': 'Not Found'}, status_code = status.HTTP_404_NOT_FOUND)
        else:
            # パスに api/ が前方一致で含まれていなければ、index.html を返す
            return FileResponse(CLIENT_DIR / 'index.html', media_type='text/html')

# Internal Server Error のハンドリング
@app.exception_handler(Exception)
async def ExceptionHandler(request: Request, exc: Exception):
    return JSONResponse(
        {'detail': f'Oops! {type(exc).__name__} did something. There goes a rainbow...'},
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        # FastAPI の謎仕様で CORSMiddleware は exception_handler に対しては効かないので、ここで自前で CORS ヘッダーを付与する
        headers = {'Access-Control-Allow-Origin': CORS_ORIGINS[0] if len(CORS_ORIGINS) > 0 else ''},
    )

# Tortoise ORM の初期化
## Tortoise ORM が利用するロガーを Uvicorn のロガーに差し替える
## ref: https://github.com/tortoise/tortoise-orm/issues/529
tortoise.log.logger = logging.logger
tortoise.log.db_client_logger = logging.logger
## Tortoise ORM を FastAPI に登録する
## ref: https://tortoise-orm.readthedocs.io/en/latest/contrib/fastapi.html
tortoise.contrib.fastapi.register_tortoise(
    app = app,
    config = DATABASE_CONFIG,
    generate_schemas = True,
    add_exception_handlers = True,
)

# 初回のみマスタデータのチャンネル情報を登録
@app.on_event('startup')
async def RegisterMasterChannels():

    # マスタデータのチャンネル情報
    master_channels = {
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
        'jk101': {'name': 'NHK BS'},
        'jk141': {'name': 'BS日テレ'},
        'jk151': {'name': 'BS朝日'},
        'jk161': {'name': 'BS-TBS'},
        'jk171': {'name': 'BSテレ東'},
        'jk181': {'name': 'BSフジ'},
        'jk191': {'name': 'WOWOW PRIME'},
        'jk192': {'name': 'WOWOW LIVE'},
        'jk193': {'name': 'WOWOW CINEMA'},
        'jk211': {'name': 'BS11'},
        'jk222': {'name': 'BS12'},
        'jk236': {'name': 'BSアニマックス'},
        'jk252': {'name': 'WOWOW PLUS'},
        'jk260': {'name': 'BS松竹東急'},
        'jk263': {'name': 'BSJapanext'},
        'jk265': {'name': 'BSよしもと'},
        'jk333': {'name': 'AT-X'},
    }

    # チャンネルが1件も登録されていないか確認
    if await Channel.all().count() == 0:

        # チャンネル情報を登録
        for channel_id, channel_info in master_channels.items():
            await Channel.create(
                id = int(channel_id.replace('jk', '')),
                name = channel_info['name'],
                description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
            )
        logging.info('Master channels have been registered.')

# 1時間に1回、明日分の全実況チャンネルのスレッド予定が DB に登録されているかを確認し、もしなければ登録する
# スレッドは同じ実況チャンネル内では絶対に放送時間が被ってはならないし、基本放送時間は 04:00 〜 翌朝 04:00 の 24 時間
## wait_first を指定していないので起動時にも実行される
@app.on_event('startup')
@repeat_every(seconds=60 * 60, logger=logging.logger)
async def AddThreads():

    # 今日と明日用のスレッドが登録されているかを確認し、もしなければ登録する
    channels = await Channel.all()
    for channel in channels:

        # 今日の日付を取得
        now = datetime.now(ZoneInfo('Asia/Tokyo'))
        today = now.date()
        start_time_today = datetime.combine(today, datetime.min.time(), ZoneInfo('Asia/Tokyo')) + timedelta(hours=4)
        end_time_today = start_time_today + timedelta(hours=24)

        # 今日用のスレッドが既に存在するか確認
        existing_thread_today = await Thread.filter(channel=channel, start_at=start_time_today).first()
        if not existing_thread_today:

            # 今日用のスレッドを作成
            await Thread.create(
                channel = channel,
                start_at = start_time_today,
                end_at = end_time_today,
                duration = int((end_time_today - start_time_today).total_seconds()),
                title = f'{channel.name}【NX-Jikkyo】{today.strftime("%Y年%m月%d日")}',
                description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
            )
            logging.info(f'Thread for {channel.name} on {today.strftime("%Y-%m-%d")} has been registered.')

        # 明日の日付を取得
        tomorrow = today + timedelta(days=1)
        start_time_tomorrow = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=4)
        end_time_tomorrow = start_time_tomorrow + timedelta(hours=24)

        # 明日用のスレッドが既に存在するか確認
        existing_thread_tomorrow = await Thread.filter(channel=channel, start_at=start_time_tomorrow).first()
        if not existing_thread_tomorrow:

            # 明日用のスレッドを作成
            await Thread.create(
                channel = channel,
                start_at = start_time_tomorrow,
                end_at = end_time_tomorrow,
                duration = int((end_time_tomorrow - start_time_tomorrow).total_seconds()),
                title = f'{channel.name}【NX-Jikkyo】{tomorrow.strftime("%Y年%m月%d日")}',
                description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
            )
            logging.info(f'Thread for {channel.name} on {tomorrow.strftime("%Y-%m-%d")} has been registered.')

        # もし現在時刻が 04:00 以前であれば、今日のスレッドを作成
        if now < start_time_today:
            # すでに現在放送中のスレッドがあるかを確認
            existing_thread_now = await Thread.filter(
                channel = channel,
                start_at__lte = now,
                end_at__gte = now
            ).first()
            if not existing_thread_now:
                await Thread.create(
                    channel = channel,
                    start_at = now,
                    end_at = start_time_today,
                    duration = int((start_time_today - now).total_seconds()),
                    title = f'{channel.name}【NX-Jikkyo】{now.strftime("%Y年%m月%d日")}',
                    description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
                )
                logging.info(f'Thread for {channel.name} from {now.strftime("%Y-%m-%d %H:%M:%S")} to {start_time_today.strftime("%Y-%m-%d %H:%M:%S")} has been registered.')

    # 採番テーブルに記録された最大コメ番とスレッドごとのコメント数を同期する
    threads = await Thread.all()
    for thread in threads:
        comment_count = await Comment.filter(thread=thread).count()
        await CommentCounter.update_or_create(
            thread_id = thread.id,
            defaults = {'max_no': comment_count}
        )
    logging.info('Comment counters have been synchronized.')
