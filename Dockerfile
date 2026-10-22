
# Python の公式イメージをベースにする
FROM python:3.13.1-bookworm

# タイムゾーンを東京に設定
ENV TZ=Asia/Tokyo

# apt-get に対話的に設定を確認されないための設定
ENV DEBIAN_FRONTEND=noninteractive

# uv をインストール
RUN python -m pip install --no-cache-dir uv

# uv の依存パッケージリストだけをコピー
WORKDIR /code/server/
COPY ./server/pyproject.toml ./server/uv.lock /code/server/

# 依存パッケージを uv でインストール
## 開発用パッケージを除いて仮想環境 (.venv) を作成し、インストール後にキャッシュを削除する
RUN python -m uv sync --frozen --no-dev --python /usr/local/bin/python && \
    python -m uv cache clean

# サーバーのソースコードをコピー
COPY ./server/ /code/server/

# NX-Jikkyo サーバーを起動
ENTRYPOINT ["/code/server/.venv/bin/python", "NX-Jikkyo.py"]
