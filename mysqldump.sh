#!/bin/bash

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# .env ファイルから MYSQL_PASSWORD を取得
MYSQL_PASSWORD=$(grep -oP '(?<=MYSQL_PASSWORD=).+' .env)

# mysqldump コマンドを実行
## --single-transaction を付けないとダンプ中は全テーブルがロックされ、コメントの書き込みとニコ生からのコメント取り込みが止まる
## テーブルはすべて InnoDB なので、ロックせずにダンプ開始時点の一貫したスナップショットを取得できる
docker compose exec nx-jikkyo-mysql /bin/bash -c "mysqldump --single-transaction -u root -p$MYSQL_PASSWORD nx-jikkyo_db" > ./backup/$(date +'%Y%m%d_%H%M%S').sql
