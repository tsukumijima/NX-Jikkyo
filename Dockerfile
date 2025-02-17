
# Python の公式イメージをベースにする
FROM python:3.13.1-bookworm

# タイムゾーンを東京に設定
ENV TZ=Asia/Tokyo

# apt-get に対話的に設定を確認されないための設定
ENV DEBIAN_FRONTEND=noninteractive

# Poetry をインストール
RUN python -m pip install poetry

# Poetry の依存パッケージリストだけをコピー
WORKDIR /code/server/
COPY ./server/pyproject.toml ./server/poetry.lock ./server/poetry.toml /code/server/

# 依存パッケージを poetry でインストール
RUN python -m poetry install --only main --no-root

# サーバーのソースコードをコピー
COPY ./server/ /code/server/

# NX-Jikkyo サーバーを起動
ENTRYPOINT ["/code/server/.venv/bin/python", "NX-Jikkyo.py"]
