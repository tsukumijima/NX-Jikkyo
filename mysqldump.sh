#!/bin/bash

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# .env ファイルから MYSQL_PASSWORD を取得
MYSQL_PASSWORD=$(grep -oP '(?<=MYSQL_PASSWORD=).+' .env)

# mysqldump コマンドを実行
docker compose exec nx-jikkyo-mysql /bin/bash -c "mysqldump -u root -p$MYSQL_PASSWORD nx-jikkyo_db" > ./backup/$(date +'%Y%m%d_%H%M%S').sql
