#!/usr/bin/env python

import asyncio
import atexit
import os
import subprocess
import sys
import threading
import time
import warnings

import aiomysql
import typer
import uvicorn
from aerich import Command
from redis.asyncio.client import Redis
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError
from uvicorn.supervisors.watchfilesreload import WatchFilesReload

from app.config import CONFIG
from app.constants import (
    BASE_DIR,
    DATABASE_CONFIG,
    LOGGING_CONFIG,
    NX_JIKKYO_ACCESS_LOG_PATH,
    VERSION,
)
from app.utils.log_rotation import SplitServerLogByDate


# aerich テーブルが既に存在する警告を無視
warnings.filterwarnings('ignore', message='Table \'aerich\' already exists')

cli = typer.Typer()

def version(value: bool):
    if value is True:
        typer.echo(f'NX-Jikkyo version {VERSION}')
        raise typer.Exit()

@cli.command(help='NX-Jikkyo: Nico Nico Jikkyo Alternative')
def main(
    port: int = typer.Option(CONFIG.SERVER_PORT, '--port', help='Server port number.'),
    reload: bool = typer.Option(False, '--reload', help='Start Uvicorn in auto-reload mode.'),
    version: bool = typer.Option(None, '--version', callback=version, is_eager=True, help='Show version information.'),
):
    # 指定されたポートを設定
    CONFIG.SPECIFIED_SERVER_PORT = port
    # メインサーバープロセスが起動したサブサーバープロセスを port ごとに管理する
    ## 落ちたサブサーバープロセスだけをピンポイントで再生成できるように dict で保持する
    sub_server_processes: dict[int, subprocess.Popen[bytes]] = {}
    # シャットダウン時に監視スレッドを止めるためのイベント
    stop_sub_server_supervisor = threading.Event()

    # 指定されたポートが .env に記載の SERVER_PORT と一致する場合 (= メインサーバープロセス) のみ
    if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT:

        # 自分が実行されたコマンドラインと同一だが --port オプションでポートがインクリメントされているサブプロセスを起動する
        ## 例えば SERVER_PORT が 5610 なら 5611, 5612 ... と起動する
        for count in range(CONFIG.SUB_SERVER_PROCESS_COUNT):
            sub_server_port = port + count + 1
            sub_server_processes[sub_server_port] = subprocess.Popen([sys.executable, __file__, '--port', str(sub_server_port)])

        # 前回のアクセスログを削除する
        ## サーバーログは起動時分割で過去日付をアーカイブ化するため、ここでは削除しない
        try:
            if NX_JIKKYO_ACCESS_LOG_PATH.exists():
                NX_JIKKYO_ACCESS_LOG_PATH.unlink()
        except PermissionError:
            pass

    # サーバーログに過去日付のエントリが含まれている場合、日付別アーカイブに分割する
    ## DailyRotatingFileHandler がファイルを開く前に分割を完了させるために、ロガーの初期化前に実行する必要がある
    ## メインサーバープロセスのみで実行し、サブプロセスとの競合を避ける
    if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT:
        SplitServerLogByDate()

    # ここでロガーをインポートする
    ## ローテーション分割を実施した後でないと正しく動作しない
    from app import logging

    # バージョン情報をログに出力
    logging.info(f'NX-Jikkyo version {VERSION} (Port {CONFIG.SPECIFIED_SERVER_PORT})')
    # 実行中プロセスの役割を明示し、運用時にメイン/サブのどちらが出しているログかを判別しやすくする
    ## 機能上の挙動は変更せず、解析容易性のみを向上させる
    process_role = 'main' if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT else 'sub'
    logging.info(
        f'NX-Jikkyo process started. role: {process_role}, pid: {os.getpid()}, '
        f'ppid: {os.getppid()}, port: {CONFIG.SPECIFIED_SERVER_PORT}'
    )

    async def WaitForDependencyServices(
        role: str,
        retry_interval_seconds: float = 5.0,
    ) -> None:
        """
        MySQL / Redis が利用可能になるまで待機する
        """

        async def IsMySQLReady() -> bool:
            # MySQL がアプリケーション用資格情報で接続可能か確認する
            ## healthcheck の mysqladmin ping だけでは「TCP ポートが開いた」以上の保証にならないため、
            ## 実際にアプリケーション本体と同じ資格情報で接続できることを利用可能条件にする
            connection = None
            try:
                connection = await aiomysql.connect(
                    host='nx-jikkyo-mysql',
                    port=3306,
                    user=CONFIG.MYSQL_USER,
                    password=CONFIG.MYSQL_PASSWORD,
                    db=CONFIG.MYSQL_DATABASE,
                    connect_timeout=3,
                    autocommit=True,
                    charset='utf8mb4',
                )
                return True
            except Exception:
                return False
            finally:
                if connection is not None:
                    connection.close()

        async def IsRedisReady() -> bool:
            # エントリーポイントでの確認時のみ、共有の REDIS_CLIENT を使わない
            ## asyncio.run() で作られた一時イベントループに接続オブジェクトがぶら下がると、
            ## 後段の Uvicorn のイベントループから再利用した際に
            ## "Future attached to a different loop" が起きてしまう
            redis_client = Redis.from_url('redis://nx-jikkyo-redis', encoding='utf-8', decode_responses=True)
            try:
                # Redis は PING が通れば少なくともコマンド受付状態までは到達しているとみなせる
                await redis_client.ping()
                return True
            except Exception:
                return False
            finally:
                await redis_client.close()

        attempt = 1
        while True:
            # どちらか片方だけ先に起動しても意味がないため、両方をまとめて確認する
            is_mysql_ready, is_redis_ready = await asyncio.gather(
                IsMySQLReady(),
                IsRedisReady(),
            )
            if is_mysql_ready is True and is_redis_ready is True:
                if attempt == 1:
                    logging.info(f'Dependency service check passed immediately. role: {role}')
                else:
                    logging.info(f'All dependency services are available. role: {role}, attempts: {attempt}')
                return

            # 何が未準備なのかを毎回ログに残しておくと、障害時に MySQL 側なのか Redis 側なのかを
            # docker compose logs だけで即座に切り分けやすい
            not_ready_dependencies: list[str] = []
            if is_mysql_ready is False:
                not_ready_dependencies.append('MySQL')
            if is_redis_ready is False:
                not_ready_dependencies.append('Redis')

            logging.info(
                f'Waiting for dependency services to become available. role: {role}, '
                f'not_available: {", ".join(not_ready_dependencies)}, attempt: {attempt}',
            )
            attempt += 1
            await asyncio.sleep(retry_interval_seconds)

    # 全サーバープロセス共通で、MySQL / Redis が利用可能になるのを待つ
    asyncio.run(WaitForDependencyServices(role=process_role))

    # Aerich でデータベースをアップグレードする
    ## 特にデータベースのアップグレードが必要ない場合は何も起こらない
    async def UpgradeDatabase():
        command = Command(tortoise_config=DATABASE_CONFIG, app='models', location='./app/migrations/')
        migration_attempt = 1
        while True:
            try:
                # 依存サービスが利用可能になった後でも、まれに DB 初期化とマイグレーション実行のタイミングがずれる可能性が否定できないため、
                # command.init() 自体にも短い間隔でリトライを入れておく
                await command.init()
                break
            except DBConnectionError:
                logging.info(
                    f'Waiting 5 seconds for database migration initialization... '
                    f'attempt: {migration_attempt}',
                )
                migration_attempt += 1
                await asyncio.sleep(5)
        migrated = await command.upgrade(run_in_transaction=True)
        await Tortoise.close_connections()
        if not migrated:
            logging.info('No database migration is required.')
        else:
            for version_file in migrated:
                logging.info(f'Successfully migrated to {version_file}.')

    def SuperviseSubServerProcesses() -> None:
        # PID 1 が生きている限り Docker の restart policy は発火しないため、
        ## サブサーバープロセスの異常終了だけはアプリケーション内で面倒を見る
        while stop_sub_server_supervisor.is_set() is False:
            for sub_server_port, process in list(sub_server_processes.items()):
                return_code = process.poll()
                if return_code is None:
                    continue

                # poll() 済みの子プロセスを wait() で回収し、ゾンビ化を防ぐ
                process.wait()
                logging.warning(
                    f'Sub server process exited unexpectedly. Restarting... '
                    f'port: {sub_server_port}, return_code: {return_code}',
                )
                sub_server_processes[sub_server_port] = subprocess.Popen(
                    [sys.executable, __file__, '--port', str(sub_server_port)]
                )
            stop_sub_server_supervisor.wait(5)

    # 指定されたポートが .env に記載の SERVER_PORT と一致する場合 (= メインサーバープロセス) のみ実行
    if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT:
        # 必要な場合にマイグレーション処理を実行
        asyncio.run(UpgradeDatabase())
        # サブサーバープロセスの監視は Uvicorn 本体とは独立したデーモンスレッドで回し続ける
        ## 監視対象は 5611-5614 のサブだけで、5610 のメイン自身はこのスレッドでは扱わない
        threading.Thread(
            target=SuperviseSubServerProcesses,
            name='sub-server-supervisor',
            daemon=True,
        ).start()
        # メインプロセス終了時に監視スレッドも確実に止める
        atexit.register(lambda: stop_sub_server_supervisor.set())
    else:
        # マイグレーション処理の完了を待機して競合を避ける
        ## マイグレーション処理はメインサーバープロセスのみが実行するため、サブサーバープロセスでは少しだけ待ってからスタートアップに進む
        time.sleep(5)

    # Uvicorn の設定
    server_config = uvicorn.Config(
        # 起動するアプリケーション
        app = 'app.app:app',
        # リッスンするアドレス
        host = '0.0.0.0',
        # リッスンするポート番号
        port = port,
        # 自動リロードモードモードで起動するか
        reload = reload,
        # リロードするフォルダ
        reload_dirs = str(BASE_DIR / 'app') if reload else None,
        # ロギングの設定
        log_config = LOGGING_CONFIG,
        # インターフェイスとして ASGI3 を選択
        interface = 'asgi3',
        # HTTP プロトコルの実装として httptools を選択
        http = 'httptools',
        # イベントループの実装として uvloop を選択
        loop = 'uvloop',
        # ストリーミング配信中にサーバーシャットダウンを要求された際、強制的に接続を切断するまでの秒数
        timeout_graceful_shutdown = 1,
    )

    # Uvicorn のサーバーインスタンスを初期化
    server = uvicorn.Server(server_config)

    # Uvicorn を起動
    ## 自動リロードモードと通常時で呼び方が異なる
    ## ここで終了までブロッキングされる（非同期 I/O のエントリーポイント）
    ## ref: https://github.com/encode/uvicorn/blob/0.18.2/uvicorn/main.py#L568-L575
    if server_config.should_reload:
        # 自動リロードモード
        sock = server_config.bind_socket()
        WatchFilesReload(server_config, target=server.run, sockets=[sock]).run()
    else:
        # 通常時
        server.run()


if __name__ == '__main__':
    cli()
