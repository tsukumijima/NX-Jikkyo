#!/bin/bash

# Usage: ./misc/BumpVersion.sh
# NX-Jikkyo の各所に書かれているバージョンを更新するスクリプト

# シェルスクリプトの実行時にエラーが発生したらスクリプトを終了する
set -Eeuo pipefail

# NX-Jikkyo のルートディレクトリに移動
cd "$(dirname "$0")"
cd ..
cd ..

# 引数の数をチェック
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <New NX-Jikkyo version: 1.0.0 etc.>"
    exit 1
fi

# 新しいバージョンを変数に格納
new_version=$1

# server/app/constants.py のバージョンを更新
sed -i "s/^VERSION = '.*'/VERSION = '$new_version'/" server/app/constants.py

# client/package.json のバージョンを更新
sed -i "s/^\s*\"version\": \".*\"/    \"version\": \"$new_version\"/" client/package.json

# server/pyproject.toml のバージョンを更新
sed -i "s/^version = \".*\"/version = \"$new_version\"/" server/pyproject.toml

# この状態でクライアントをビルドする
(cd client && yarn build)

# Git にコミット
git add .
git commit -m "Release: version $new_version"

echo "Updated version to $new_version."

