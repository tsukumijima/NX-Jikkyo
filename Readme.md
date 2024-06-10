
# NX-Jikkyo

💠 **NX-Jikkyo:** Nico Nico Jikkyo Alternatives

## Server

## Development

```bash
# .env を作成
cp .env.example .env

# JWT シークレットを生成
## .env 内の JWT_SECRET_KEY に設定する
python -c 'import secrets; print(secrets.token_hex(32))'

# ローカルの Docker 環境に proxy-network という名前でネットワークを作成
## 開発環境だけならなくてもいいのだが、本番環境では異なる Docker Compose 構成 (=nginx) から
## NX-Jikkyo の HTTP サーバーにアクセスできるようにするために必要
## 開発環境と本番環境で諸々分けるのが面倒なので、開発環境でも作成しておく必要がある
docker network create proxy-network

# VSCode 上での Python の補完が効くように、別途ローカルに Poetry で管理している依存ライブラリをインストールする必要がある
## 実際に NX-Jikkyo サーバーの動作に使われるのは Docker イメージビルド時にインストールされたライブラリの方
## 両者は同期しないので、Poetry でライブラリを追加・更新した際は忘れずにローカル環境で poetry install --no-root を実行すること
cd server
poetry install --no-root

# 以下のコマンドは内部的に Docker Compose 上で実行される
# MySQL コンテナは NX-Jikkyo (Uvicorn) と同時に起動する (サーバーを立ち下げても MySQL コンテナは停止しないので注意)

# サーバーを起動
poetry run task serve

# サーバーを起動 (ホットリロード)
poetry run task dev

# Aerich (マイグレーションツール) を使う
poetry run task aerich --help
```
