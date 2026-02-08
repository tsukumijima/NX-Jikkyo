
import asyncio
import json
import mimetypes
import random
import time
import traceback
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import tortoise.contrib.fastapi
import tortoise.log
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from ndgr_client import NDGRClient
from pydantic import TypeAdapter
from rich.rule import Rule
from rich.style import Style
from starlette.middleware.base import BaseHTTPMiddleware
from tortoise import timezone
from tortoise.backends.base.client import TransactionalDBClient

from app import logging
from app.config import CONFIG
from app.constants import (
    CLIENT_DIR,
    DATABASE_CONFIG,
    LOGS_DIR,
    REDIS_CHANNEL_THREAD_COMMENTS_PREFIX,
    REDIS_CLIENT,
    REDIS_KEY_CHANNEL_INFOS_CACHE,
    REDIS_KEY_JIKKYO_FORCE_COUNT,
    REDIS_KEY_VIEWER_COUNT,
    VERSION,
)
from app.models.comment import (
    Channel,
    ChannelResponse,
    Comment,
    CommentCounter,
    Thread,
)
from app.routers import (
    channels,
    niconico,
    threads,
    websocket,
)
from app.routers.websocket import ConvertToXMLCompatibleCommentResponse
from app.utils.comment_counter_cache import UpdateThreadCommentCounterCache
from app.utils.transaction import (
    IsDatabaseConnectionUnavailableError,
    RunTransactionWithReconnectRetry,
)


# FastAPI を初期化
app = FastAPI(
    title = 'NX-Jikkyo',
    description = 'NX-Jikkyo: Nico Nico Jikkyo Alternative<br><br>'
        'この API ドキュメントには WebSocket API のドキュメントは掲載されていません。ご了承ください。<br>'
        'ニコ生互換の視聴セッション維持用 WebSocket の URL は wss://nx-jikkyo.tsukumijima.net/api/v1/channels/(実況ID, ex: jk211)/ws/watch です。<br>'
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
app.include_router(niconico.router)

# CORS の設定
## 開発環境では全てのオリジンからのリクエストを許可
## 本番環境では全てのオリジンからのリクエストを拒否
CORS_ORIGINS = ['*'] if CONFIG.ENVIRONMENT == 'Develop' else []
app.add_middleware(
    CORSMiddleware,
    allow_origins = CORS_ORIGINS,
    # すべての HTTP メソッドと HTTP ヘッダーを許可
    allow_methods = ['*'],
    allow_headers = ['*'],
    allow_credentials = True,
)

# "NX-User-ID" という名前の Cookie が存在しない場合、新しい UUID を生成して Cookie をセット
class NXUserIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        response = await call_next(request)
        if not request.cookies.get('NX-User-ID'):
            response.set_cookie(
                key = 'NX-User-ID',
                value = str(uuid.uuid4()),
                max_age = 315360000,  # 10年間の有効期限 (秒単位)
                httponly = True,
                samesite = 'lax',
            )
        return response
app.add_middleware(NXUserIDMiddleware)

# 拡張子と MIME タイプの対照表を上書きする
## StaticFiles の内部動作は mimetypes.guess_type() の挙動に応じて変化する
## 一部 Windows 環境では mimetypes.guess_type() が正しく機能しないため、明示的に指定しておく
for suffix, mime_type in [
    ('.css', 'text/css'),
    ('.html', 'text/html'),
    ('.ico', 'image/x-icon'),
    ('.js', 'application/javascript'),
    ('.json', 'application/json'),
    ('.map', 'application/json'),
    ]:
    guess = mimetypes.guess_type(f'foo{suffix}')[0]
    if guess != mime_type:
        mimetypes.add_type(mime_type, suffix)

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
        if filepath.suffix in ['.css', '.html', '.ico', '.js', '.json', '.map']:
            mime = mimetypes.guess_type(f'foo{filepath.suffix}')[0] or 'text/plain'
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


# 以降は指定されたポートが .env に記載の SERVER_PORT と一致する場合 (= メインサーバープロセス) のみ実行
if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT:

    # サーバーの初回起動時のみ、チャンネル情報をマスタデータとして登録
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
            'jk200': {'name': 'BS10'},  # 旧BSJapanext
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

        # 既存のチャンネル情報を取得
        existing_channels = await Channel.all()
        existing_channel_ids = {channel.id for channel in existing_channels}

        # マスタデータのチャンネル情報を登録または更新
        description = ''  # 当面未使用
        for channel_id, channel_info in master_channels.items():
            master_channel_id = int(channel_id.replace('jk', ''))
            if master_channel_id not in existing_channel_ids:
                await Channel.create(
                    id = master_channel_id,
                    name = channel_info['name'],
                    description = description
                )
                logging.info(f'Channel {channel_info["name"]} has been registered.')
            else:
                existing_channel = next(channel for channel in existing_channels if channel.id == master_channel_id)
                if existing_channel.name != channel_info['name'] or existing_channel.description != description:
                    existing_channel.name = channel_info['name']
                    existing_channel.description = description
                    await existing_channel.save()
                    logging.info(f'Channel {channel_info["name"]} has been updated.')
        logging.info('Master channels have been registered or updated.')


    # サーバー起動時にチャンネルごとに同時接続数カウントを 0 にリセット
    ## サーバーは再起動しても Redis サーバーは再起動しない場合があり、そうした状況でカウントの整合性を保つために必要
    async def ResetViewerCount():

        # チャンネルごとに保存された同時接続数カウントをリセット
        for channel in await Channel.all():
            await REDIS_CLIENT.hset(REDIS_KEY_VIEWER_COUNT, f'jk{channel.id}', 0)
            logging.info(f'Viewer count for {channel.name} has been reset.')


    # サーバー起動時にニコニコ実況の各実況チャンネルのコメントのリアルタイムストリーミングを開始
    # ストリーミングで取得したコメントは随時 NX-Jikkyo のコメントとして「投稿」する
    ## この処理はサーバー起動時に 1 回だけ実行される
    async def StartStreamNicoliveComments():

        # ニコニコ実況で実装されている実況チャンネル (jk の prefix なし)
        NICOLIVE_JIKKYO_CHANNELS = [1, 2, 4, 5, 6, 7, 8, 9, 101, 211]

        # 現在アクティブなスレッドの情報を保存する辞書
        active_threads: dict[int, Thread] = {}

        # バックグラウンドタスクの参照を保持する
        background_tasks: list[asyncio.Task[None]] = []

        # ニコニコ実況のコメントをリアルタイムに受信する非同期関数
        async def StreamNicoliveComments(channel_id_int: int) -> None:

            # jk の prefix つきのチャンネル ID
            channel_id = f'jk{channel_id_int}'

            # 既存のログがあれば、肥大化を防ぐためにログファイルを削除
            log_file_path = LOGS_DIR / f'NDGRClient-{channel_id}.log'
            if log_file_path.is_file():
                log_file_path.unlink()

            # NDGRClient を初期化
            ndgr_client = NDGRClient(channel_id, verbose=True, log_path=log_file_path)
            # DB 接続断時のログ連打を抑止するため、最後に DB 接続断エラーをログ出力した時刻を保持する
            last_db_connection_error_log_time = 0.0

            # コメントのストリーミング処理を開始
            ## NDGRClient.streamComments() は通常エンドレスに実行され続ける
            ## 予期せぬエラーで途中終了してしまったときは、エラーログを出力した上で 10 秒後にリトライする
            while True:
                try:
                    async for ndgr_comment in ndgr_client.streamComments():
                        ndgr_client.print(f'[{datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")}] Comment Received. [grey70](ID: {ndgr_comment.id})[/grey70]')
                        ndgr_client.print(str(ndgr_comment))
                        ndgr_client.print(Rule(characters='-', style=Style(color='#E33157')))

                        # 現在のサーバー時刻 (UNIX タイムスタンプ)
                        current_time = time.time()

                        # 現在のサーバー時刻 (datetime)
                        current_time_datetime = timezone.now()

                        # 現在アクティブなスレッドの情報が保存されていないか、放送が終了している場合は、
                        # 現在アクティブなスレッドの情報を取得し、active_threads に保存する
                        if channel_id_int not in active_threads or active_threads[channel_id_int].end_at < current_time_datetime:
                            thread = await Thread.filter(
                                channel_id = channel_id_int,
                                start_at__lte = current_time_datetime,
                                end_at__gte = current_time_datetime,
                            ).first()
                            if not thread:
                                # 今日のスレッドが作成中などの理由でまだスレッドが取得できる状態にないことが原因と思われる
                                ## このコメントは飛ばし、スレッドが取得できるようになったコメントから保存する
                                logging.error(f'StreamNicoliveComments [{channel_id}]: Active thread not found.')
                                continue
                            active_threads[channel_id_int] = thread
                            logging.info(f'StreamNicoliveComments [{channel_id}]: Active thread has been updated.')

                        # 現在アクティブなスレッドの情報を取得
                        active_thread = active_threads[channel_id_int]

                        try:

                            # 受信したコメントデータを XML 互換コメント形式に変換
                            xml_compatible_comment = NDGRClient.convertToXMLCompatibleComment(ndgr_comment)

                            async def CreateCommentInTransaction(connection: TransactionalDBClient) -> Comment:

                                # 採番テーブルに記録されたコメ番をインクリメント
                                await connection.execute_query(
                                    'UPDATE comment_counters SET max_no = max_no + 1 WHERE thread_id = %s',
                                    [active_thread.id]
                                )
                                # インクリメント後のコメ番を取得
                                ## 採番テーブルを使うことでコメ番の重複を防いでいる
                                new_no_result = await connection.execute_query_dict(
                                    'SELECT max_no FROM comment_counters WHERE thread_id = %s',
                                    [active_thread.id]
                                )
                                new_no = new_no_result[0]['max_no']

                                # vpos はスレッドの放送開始時刻から起算した秒 1/100 秒 (10ミリ秒) 単位のタイムスタンプ
                                ## NX-Jikkyo 側でのスレッド放送開始時刻と、NDGR メッセージサーバーから受信したコメント投稿時刻の差分から算出する
                                vpos = int((ndgr_comment.at.timestamp() - active_thread.start_at.timestamp()) * 100)

                                # 新しいコメントを作成
                                ## NDGR メッセージサーバーのコメ番はベストエフォートで一意性が保証されない上齟齬も出るため、当面 NX-Jikkyo 側に合わせている
                                ## vpos はニコニコ実況で運用されているがスレッド開始時刻が両者で異なるため、NX-Jikkyo 側で別途算出した値を入れる
                                ## 本家ニコニコ実況のリセット時刻が今の所わからないのもある
                                return await Comment.create(
                                    thread_id = active_thread.id,  # NX-Jikkyo 側のスレッド ID を入れる
                                    no = new_no,  # NX-Jikkyo 側で算出した値を入れる
                                    vpos = vpos,  # NX-Jikkyo 側で算出した値を入れる
                                    date = ndgr_comment.at,  # NX-Jikkyo 側では自動生成せず、NDGR メッセージサーバーから受信したコメント投稿時刻を入れる
                                    mail = xml_compatible_comment.mail,
                                    user_id = f'nicolive:{xml_compatible_comment.user_id}',
                                    premium = True if xml_compatible_comment.premium == 1 else False,
                                    anonymity = True if xml_compatible_comment.anonymity == 1 else False,
                                    content = xml_compatible_comment.content,
                                )

                            # コメントを DB に登録
                            comment = await RunTransactionWithReconnectRetry(
                                operation = CreateCommentInTransaction,
                                operation_name = f'StreamNicoliveComments [{channel_id}]',
                            )

                            # スレッドごとの最新コメ番キャッシュを更新
                            ## statistics 送信で DB 負荷を下げるため、投稿完了時に最新コメ番を即時反映する
                            try:
                                await UpdateThreadCommentCounterCache(active_thread.id, comment.no)
                            except Exception as ex:
                                # キャッシュ更新失敗でコメント投稿自体を失敗させない
                                ## コメント本体の保存成功を優先し、整合性は後段の再検証・定期同期で回復する
                                logging.warning(
                                    f'StreamNicoliveComments [{channel_id}]: Failed to update thread comment counter cache.',
                                    exc_info = ex,
                                )

                            # ニコ生 XML 互換コメント形式に変換した上で、Redis Pub/Sub でコメントを送信
                            ## この段階ではまだ yourpost フラグを設定してはならない
                            ## yourpost フラグはコメントセッション WebSocket 側で設定しないと、意図しないコメントに yourpost フラグが付与されてしまう
                            await REDIS_CLIENT.publish(
                                channel = f'{REDIS_CHANNEL_THREAD_COMMENTS_PREFIX}:{active_thread.id}',
                                message = json.dumps(ConvertToXMLCompatibleCommentResponse(comment), ensure_ascii=False),
                            )

                            # 実況勢いカウント用の Redis ソート済みセット型にエントリを追加
                            ## スコア (UNIX タイムスタンプ) が現在時刻から 60 秒以内の範囲のエントリの数が実況勢いとなる
                            await REDIS_CLIENT.zadd(f'{REDIS_KEY_JIKKYO_FORCE_COUNT}:{channel_id}', {f'comment:{comment.id}': current_time})

                            # 1/10 の確率で現在時刻から 60 秒以上前のエントリを削除
                            ## 毎回削除する必要はないが (古いエントリが残ったままでもカウントする上では影響しない) 、
                            ## メモリ上に古いエントリが残りすぎないように、定期的に削除する
                            if random.random() < 0.1:
                                await REDIS_CLIENT.zremrangebyscore(f'{REDIS_KEY_JIKKYO_FORCE_COUNT}:{channel_id}', 0, current_time - 60)

                            # ニコニコ実況からのコメントのインポート完了
                            logging.info(f'StreamNicoliveComments [{channel_id}]: User {xml_compatible_comment.user_id} posted a comment.')

                        # 何らかの理由でコメント投稿に失敗した場合はエラーログを出力
                        except Exception as ex:
                            # DB 接続断時は同種エラーが一気に発生するため、ログ出力頻度を抑えつつ短時間待機して再試行する
                            if IsDatabaseConnectionUnavailableError(ex) is True:
                                current_time = time.time()
                                if (current_time - last_db_connection_error_log_time) > 10:
                                    logging.error(
                                        f'StreamNicoliveComments [{channel_id}]: Failed to import comment because database is unavailable.',
                                        exc_info = ex,
                                    )
                                    last_db_connection_error_log_time = current_time
                                # DB 停止中に busy loop で CPU を燃やさないよう、最小限待機してから再試行する。
                                await asyncio.sleep(0.2)
                                continue

                            logging.error(f'StreamNicoliveComments [{channel_id}]: Failed to import comment.')
                            logging.error(traceback.format_exc())

                except Exception:
                    logging.error(f'StreamNicoliveComments [{channel_id}]: Unexpected error occurred while streaming.')
                    logging.error(traceback.format_exc())
                    logging.info(f'StreamNicoliveComments [{channel_id}]: Retrying in 10 seconds...')
                    # NDGRClient を再初期化
                    ndgr_client = NDGRClient(channel_id, verbose=True, log_path=log_file_path)
                    await asyncio.sleep(10)
                else:
                    break  # エラーが発生しなかった場合はループを抜ける

        # ニコニコ実況の各実況チャンネルに対し、バックグラウンドでストリーミングを開始
        ## 一度にアクセスするとアクセス規制を喰らう可能性があるので、0.1 秒ずつ遅らせてタスクを起動する
        for nicolive_jikkyo_channel_id_int in NICOLIVE_JIKKYO_CHANNELS:
            background_tasks.append(asyncio.create_task(StreamNicoliveComments(nicolive_jikkyo_channel_id_int)))
            await asyncio.sleep(0.1)
            logging.info(f'StartStreamNicoliveComments [jk{nicolive_jikkyo_channel_id_int}]: Streaming started.')


    # 10秒に1回、現在のチャンネル情報を DB から取得し、Redis にキャッシュとして格納する
    async def CacheChannelResponses():

        # 最新のチャンネル情報を取得
        channel_responses = await channels.GetChannelResponses()

        # キャッシュを更新
        ## このキャッシュは次回の実行で上書きされるまで永続する
        await REDIS_CLIENT.set(REDIS_KEY_CHANNEL_INFOS_CACHE, TypeAdapter(list[ChannelResponse]).dump_json(channel_responses).decode('utf-8'))
        logging.info('Channel responses cache has been updated.')

        # startup イベントハンドラが完了するまでメインスレッドを待機させる
        ## ここで待機しないと、なぜかタイミング次第ではタスクの完了前にタスクが破棄されてしまうことがある
        ## 必ず発生するわけではないが、一度起きると次の日のスレッドがずっと作成されない致命的な問題になる
        ## おそらくイベントループ関連の稀な症状を引いてしまっているみたいだが、とりあえずこれで直る
        await asyncio.sleep(0.1)


    # 念のため、1時間に1回採番テーブルに記録された最大コメ番とスレッドごとのコメント数を同期する
    async def SyncCommentCounters():

        # 各スレッドの実コメント数を DB から集計し、採番テーブルを補正する
        ## 稀な障害時にカウンタがずれても、定期的に自己修復できるようにしている
        threads = await Thread.all()
        for thread in threads:
            latest_comment = await Comment.filter(thread_id=thread.id).order_by('-no').first()
            latest_comment_no = latest_comment.no if latest_comment is not None else 0
            existing_comment_counter = await CommentCounter.filter(thread_id=thread.id).first()
            synchronized_comment_count = latest_comment_no
            if existing_comment_counter is not None:
                # max_no は採番済みコメ番の最大値として扱い、既存値より小さい値で巻き戻さない
                synchronized_comment_count = max(existing_comment_counter.max_no, latest_comment_no)
                if existing_comment_counter.max_no != synchronized_comment_count:
                    existing_comment_counter.max_no = synchronized_comment_count
                    await existing_comment_counter.save(update_fields=['max_no'])
            else:
                await CommentCounter.create(
                    thread_id = thread.id,
                    max_no = synchronized_comment_count,
                )
            # Redis 側のキャッシュも同じ値に揃える
            ## ランタイムでキャッシュ更新に失敗しても、この同期処理で最終的に回復できる
            try:
                await UpdateThreadCommentCounterCache(thread.id, synchronized_comment_count)
            except Exception as ex:
                # Redis の瞬断で同期ジョブ全体を止めない
                logging.warning(
                    f'SyncCommentCounters: Failed to update thread comment counter cache. thread_id: {thread.id}',
                    exc_info = ex,
                )

        logging.info('Comment counters have been synchronized.')

        # startup イベントハンドラが完了するまでメインスレッドを待機させる
        ## ここで待機しないと、なぜかタイミング次第ではタスクの完了前にタスクが破棄されてしまうことがある
        ## 必ず発生するわけではないが、一度起きると次の日のスレッドがずっと作成されない致命的な問題になる
        ## おそらくイベントループ関連の稀な症状を引いてしまっているみたいだが、とりあえずこれで直る
        await asyncio.sleep(0.1)


    # 1時間に1回、明日分の全実況チャンネルのスレッド予定が DB に登録されているかを確認し、もしなければ登録する
    # スレッドは同じ実況チャンネル内では絶対に放送時間が被ってはならないし、基本放送時間は 04:00 〜 翌朝 04:00 の 24 時間
    async def RegisterThreads():

        # 今日と明日用のスレッドが登録されているかを確認し、もしなければ登録する
        channels = await Channel.all()
        for channel in channels:

            # jk263 (BSJapanext) は jk200 (BS10) のエイリアスなので、新規スレッドは作成しない
            if channel.id == 263:
                continue

            # 今日の日付を取得
            now = timezone.now()
            today = now.date()
            start_time_today = datetime.combine(today, datetime.min.time(), ZoneInfo('Asia/Tokyo')) + timedelta(hours=4)
            end_time_today = start_time_today + timedelta(hours=24)

            # 今日用のスレッドが既に存在するか確認
            existing_thread_today = await Thread.filter(channel=channel, start_at=start_time_today).first()
            if not existing_thread_today:

                # 今日用のスレッドを作成
                thread = await Thread.create(
                    channel = channel,
                    start_at = start_time_today,
                    end_at = end_time_today,
                    duration = int((end_time_today - start_time_today).total_seconds()),
                    title = f'{channel.name}【NX-Jikkyo】{today.strftime("%Y年%m月%d日")}',
                    description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
                )
                await CommentCounter.create(thread_id=thread.id, max_no=0)
                logging.info(f'Thread for {channel.name} on {today.strftime("%Y-%m-%d")} has been registered.')

            # 明日の日付を取得
            tomorrow = today + timedelta(days=1)
            start_time_tomorrow = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=4)
            end_time_tomorrow = start_time_tomorrow + timedelta(hours=24)

            # 明日用のスレッドが既に存在するか確認
            existing_thread_tomorrow = await Thread.filter(channel=channel, start_at=start_time_tomorrow).first()
            if not existing_thread_tomorrow:

                # 明日用のスレッドを作成
                thread = await Thread.create(
                    channel = channel,
                    start_at = start_time_tomorrow,
                    end_at = end_time_tomorrow,
                    duration = int((end_time_tomorrow - start_time_tomorrow).total_seconds()),
                    title = f'{channel.name}【NX-Jikkyo】{tomorrow.strftime("%Y年%m月%d日")}',
                    description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
                )
                await CommentCounter.create(thread_id=thread.id, max_no=0)
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
                    thread = await Thread.create(
                        channel = channel,
                        start_at = now,
                        end_at = start_time_today,
                        duration = int((start_time_today - now).total_seconds()),
                        title = f'{channel.name}【NX-Jikkyo】{now.strftime("%Y年%m月%d日")}',
                        description = 'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。'
                    )
                    await CommentCounter.create(thread_id=thread.id, max_no=0)
                    logging.info(f'Thread for {channel.name} from {now.strftime("%Y-%m-%d %H:%M:%S")} to {start_time_today.strftime("%Y-%m-%d %H:%M:%S")} has been registered.')

        logging.info('Thread registration has been completed.')

        # startup イベントハンドラが完了するまでメインスレッドを待機させる
        ## ここで待機しないと、なぜかタイミング次第ではタスクの完了前にタスクが破棄されてしまうことがある
        ## 必ず発生するわけではないが、一度起きると次の日のスレッドがずっと作成されない致命的な問題になる
        ## おそらくイベントループ関連の稀な症状を引いてしまっているみたいだが、とりあえずこれで直る
        await asyncio.sleep(0.1)

    # APScheduler を初期化
    scheduler = AsyncIOScheduler()

    # サーバー起動時に APScheduler のジョブを登録
    @app.on_event('startup')
    async def StartScheduler():
        """ APScheduler のジョブを登録して開始する """

        # 初回起動時に実行する処理群
        await RegisterMasterChannels()
        await ResetViewerCount()
        await StartStreamNicoliveComments()

        # 各定期実行ジョブを登録
        scheduler.add_job(
            CacheChannelResponses,
            'interval',
            seconds = 10,  # 10秒ごとに実行
            id = 'cache_channel_responses',
            replace_existing = True,
        )
        scheduler.add_job(
            SyncCommentCounters,
            'interval',
            hours = 1,  # 1時間ごとに実行
            id = 'sync_comment_counters',
            replace_existing = True,
        )
        scheduler.add_job(
            RegisterThreads,
            'interval',
            hours = 1,  # 1時間ごとに実行
            id = 'register_threads',
            replace_existing = True,
        )

        # ジョブを起動時に一度実行
        await CacheChannelResponses()
        await SyncCommentCounters()
        await RegisterThreads()

        # スケジューラーを開始
        scheduler.start()


    # サーバー終了時に APScheduler を停止
    @app.on_event('shutdown')
    async def StopScheduler():
        """ APScheduler を停止する """
        scheduler.shutdown()
