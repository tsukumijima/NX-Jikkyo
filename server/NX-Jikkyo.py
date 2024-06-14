#!/usr/bin/env python

import asyncio
import logging
import time
import typer
import uvicorn
import subprocess
import sys
import warnings
from aerich import Command
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError
from uvicorn.supervisors.watchfilesreload import WatchFilesReload

from app.config import CONFIG
from app.constants import (
    NX_JIKKYO_ACCESS_LOG_PATH,
    NX_JIKKYO_SERVER_LOG_PATH,
    BASE_DIR,
    DATABASE_CONFIG,
    LOGGING_CONFIG,
    VERSION,
)


# passlib が送出する bcrypt のバージョン差異による警告を無視
# ref: https://github.com/pyca/bcrypt/issues/684
logging.getLogger('passlib').setLevel(logging.ERROR)

# aerich テーブルが既に存在する警告を無視
warnings.filterwarnings('ignore', message='Table \'aerich\' already exists')

cli = typer.Typer()

def version(value: bool):
    if value is True:
        typer.echo(f'NX-Jikkyo version {VERSION}')
        raise typer.Exit()

@cli.command(help='NX-Jikkyo: Nico Nico Jikkyo Alternatives')
def main(
    port: int = typer.Option(CONFIG.SERVER_PORT, '--port', help='Server port number.'),
    reload: bool = typer.Option(False, '--reload', help='Start Uvicorn in auto-reload mode.'),
    version: bool = typer.Option(None, '--version', callback=version, is_eager=True, help='Show version information.'),
):

    # 指定されたポートを設定
    CONFIG.SPECIFIED_SERVER_PORT = port

    # 指定されたポートが .env に記載の SERVER_PORT と一致する場合 (= メインサーバープロセス) のみ
    if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT:

        # 自分が実行されたコマンドラインと同一だが --port オプションでポートがインクリメントされているサブプロセスを起動する
        ## 例えば SERVER_PORT が 3100 なら 3101, 3102 ... と起動する
        for count in range(CONFIG.SUB_SERVER_PROCESS_COUNT):
            subprocess.Popen([sys.executable, __file__, '--port', str(port + count + 1)])

        # 前回のログをすべて削除する
        try:
            if NX_JIKKYO_SERVER_LOG_PATH.exists():
                NX_JIKKYO_SERVER_LOG_PATH.unlink()
            if NX_JIKKYO_ACCESS_LOG_PATH.exists():
                NX_JIKKYO_ACCESS_LOG_PATH.unlink()
        except PermissionError:
            pass

    # サブサーバープロセスの場合、メインプロセスでやってるマイグレーションが終わってないなどの
    # 諸問題を避けるために5秒待ってから起動する
    else:
        time.sleep(5)

    # ここでロガーをインポートする
    ## 前回のログを削除する前でないと正しく動作しない
    from app import logging

    # バージョン情報をログに出力
    logging.info(f'NX-Jikkyo version {VERSION} (Port {CONFIG.SPECIFIED_SERVER_PORT})')

    # Aerich でデータベースをアップグレードする
    ## 特にデータベースのアップグレードが必要ない場合は何も起こらない
    async def UpgradeDatabase():
        command = Command(tortoise_config=DATABASE_CONFIG, app='models', location='./app/migrations/')
        try:
            await command.init()
        except DBConnectionError:
            # ここで DBConnectionError が発生する場合、
            ## まだ MySQL 側でユーザー・データベース・テーブルが自動作成されていない可能性があるので、30秒待機する
            ## 初回は DB 用のバイナリファイルの作成とかもあるからか意外とかなり時間がかかる
            logging.info('Waiting 30 seconds for MySQL to be ready...')
            time.sleep(30)
            # 再度初期化を試みる
            await command.init()
        migrated = await command.upgrade(run_in_transaction=True)
        await Tortoise.close_connections()
        if not migrated:
            logging.info('No database migration is required.')
        else:
            for version_file in migrated:
                logging.info(f'Successfully migrated to {version_file}.')

    # 指定されたポートが .env に記載の SERVER_PORT と一致する場合 (= メインサーバープロセス) のみ実行
    if CONFIG.SPECIFIED_SERVER_PORT == CONFIG.SERVER_PORT:
        asyncio.run(UpgradeDatabase())

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
