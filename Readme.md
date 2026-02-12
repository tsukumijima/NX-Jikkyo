
# NX-Jikkyo

**NX-Jikkyo:** Nico Nico Jikkyo Alternative

## About

**NX-Jikkyo は、[サイバー攻撃の影響で 2024/06/08 〜 08/05 まで停止していた](https://blog.nicovideo.jp/niconews/225099.html) ニコニコ実況に代わる、ニコニコ実況民のための避難所であり、[ニコニコ生放送互換の WebSocket API](server/app/routers/websocket.py) を備えるコメントサーバーです。** 2024/06/10 から運営しています。

ニコニコ実況が復旧した現在では、**「ニコニコ実況の Web 版非公式コメントビューア」＋「公式にない実況チャンネルを補完するコメントサーバー」** として運営を続けています。

> [!NOTE]
> [API ドキュメント](https://nx-jikkyo.tsukumijima.net/api/v1/docs) もあります。

### 対応チャンネル

地上波 9 局・BS/CS を含む計 38 チャンネルに対応しています (jk1 〜 jk333) 。

### 対応サードパーティーアプリ

NX-Jikkyo の WebSocket API を利用してコメント取得・表示が可能なアプリです。

- **[jkcommentviewer](https://air.fem.jp/jkcommentviewer/)** v2.3.7.3 以降
- **[TVTest](https://github.com/DBCTRADO/TVTest) + [NicoJK](https://github.com/xtne6f/NicoJK/releases)** master-240613 以降
- **[TVTComment](https://github.com/noriokun4649/TVTComment)** v3.0.1 以降
- **[KonomiTV](https://github.com/tsukumijima/KonomiTV/releases)** 0.10.1 以降

## Architecture

### 技術スタック

| レイヤー | 技術 |
|:--|:--|
| **フロントエンド** | Vue 3 + Vuetify 3 + TypeScript + Vite + Pinia |
| **バックエンド** | Python 3.13 + FastAPI + Uvicorn + Tortoise ORM |
| **データベース** | MySQL 8.0 |
| **キャッシュ** | Redis 6.2 |
| **リバースプロキシ** | Caddy 2 (Let's Encrypt 自動 TLS + ロードバランシング) |
| **コンテナ** | Docker Compose |

### フロントエンド

フロントエンドは **Vue 3 (Composition API) + Vuetify 3 (Material Design) + TypeScript** で構築された SPA (Single Page Application) で、**[KonomiTV](https://github.com/tsukumijima/KonomiTV) 0.10.0 時点の大半のソースコードを流用して開発されています。**

当時はとにかく一刻も早くリリースすべく開発を急ぐ必要があったという経緯ゆえではありますが、コードはお世辞にも無茶苦茶でデッドコードも多いです。  
その後も KonomiTV での改良に合わせて、不定期で KonomiTV 側の改良のバックポートを行っています。

KonomiTV のプレイヤーロジック（[DPlayer](https://github.com/tsukumijima/DPlayer) ベース）をそのまま動画再生処理だけを無効化し、コメント再生だけを行わせる形で実現しています。  
PWA (Progressive Web App) にも対応しており、PC のデスクトップやスマホのホーム画面からアプリのように起動できます。[Android 版アプリ](https://play.google.com/store/apps/details?id=net.tsukumijima.nxjikkyo.android) もあります。

主な依存ライブラリは [client/package.json](client/package.json) を参照してください。

### バックエンド

バックエンドは **Python 3.13 + FastAPI** で構築された非同期 Web サーバーです。Uvicorn (uvloop) 上で動作し、マルチプロセス構成 (メイン + サブプロセス × N) でリクエストを処理します。  
こちらのソースコードも、KonomiTV のサーバー API の設計に寄せて開発されています。

Caddy リバースプロキシがラウンドロビン方式で各ワーカープロセス (ポート 5610 〜 5613) にリクエストを分散します。WebSocket の長時間接続に対応するため、タイムアウトは 24 時間に設定されています。

主な依存ライブラリは [server/pyproject.toml](server/pyproject.toml) を参照してください。

### ニコニコ実況コメントのリアルタイム連携

ニコニコ実況の各チャンネルに投稿されたコメントを NX-Jikkyo のサーバー側で [NDGRClient](https://github.com/tsukumijima/NDGRClient) を使いリアルタイム受信し、NX-Jikkyo のデータベースに通常のコメントとして「投稿」することで、ニコニコ実況のコメントをリアルタイム表示しています。

さらに、NX-Jikkyo のフロントエンドには、ニコニコ実況（ニコニコ生放送）とアプリ連携し、直接コメントを投稿する機能もあります。  
この機能を使えば、NX-Jikkyo を事実上ニコニコ実況の非公式コメントサーバーとして利用できます。

- ニコニコ実況からのコメントは、ユーザー ID に `nicolive:` プレフィックスが付与されます
- NX-Jikkyo に投稿されたコメントには `nicolive:` プレフィックスは付きません
- クライアント側でニコニコ実況のコメントと NX-Jikkyo のコメントを区別して表示・ミュートできます

### WebSocket API

NX-Jikkyo は、**niwavided 旧コメントサーバー (サイバー攻撃前のニコニコ生放送で使用されていたコメントサーバー) の WebSocket API と互換性があります。**

ニコ生統合後の新ニコニコ実況対応クライアントであれば、ニコ生視聴ページに埋め込まれている JSON (`embedded-data`) 内の `site.relive.webSocketUrl` から取得していた接続先 WebSocket の URL を `wss://nx-jikkyo.tsukumijima.net/api/v1/channels/(jk1,jk9,jk141, etc.)/ws/watch` に差し替えるだけで、NX-Jikkyo に対応できるはずです。

WebSocket API は 2 つの独立したエンドポイントで構成されています。

#### 視聴セッション WebSocket (`/api/v1/channels/{channel_id}/ws/watch`)

ニコ生互換の視聴セッション管理を行います。統計情報（視聴者数・コメント数）の取得、サーバー時刻同期、コメント投稿、コメント受信用 WebSocket の接続情報 (`room` メッセージ) の取得が可能です。

**クライアント → サーバー:**
| メッセージ | 説明 |
|:--|:--|
| `startWatching` | 視聴開始 |
| `keepSeat` | 座席維持 (30 秒ごと) |
| `pong` | ハートビート応答 |
| `postComment` | コメント投稿 (`text`, `vpos`, `isAnonymous`, `color`, `position`, `size`, `font`) |

**サーバー → クライアント:**
| メッセージ | 説明 |
|:--|:--|
| `serverTime` | サーバー時刻 (45 秒ごと) |
| `seat` | 座席確保情報 (`keepIntervalSec`) |
| `schedule` | スレッド放送時刻 (`begin`, `end`) |
| `room` | コメントサーバー接続情報 (`uri`, `threadId`, `yourPostKey`, `vposBaseTime`) |
| `statistics` | 統計情報 (`viewers`, `comments`, `adPoints`, `giftPoints`) (60 秒ごと) |
| `ping` | キープアライブ (30 秒ごと) |
| `postCommentResult` | コメント投稿結果 |
| `disconnect` | 切断通知 (`END_PROGRAM` / `SERVICE_TEMPORARILY_UNAVAILABLE`) |

#### コメントセッション WebSocket (`/api/v1/channels/{channel_id}/ws/comment`)

ニコ生互換のコメント受信セッションです。リアルタイムコメント受信と過去ログコメント取得に対応しています。

**コメント (`chat`) の JSON 形式:**
```json
{
  "chat": {
    "thread": "123456",
    "no": 5678,
    "vpos": 7201727,
    "date": 1704067200,
    "date_usec": 123456,
    "mail": "184 white naka medium",
    "user_id": "z7edP-AgH...",
    "premium": 1,
    "anonymity": 1,
    "yourpost": 1,
    "content": "コメント本文"
  }
}
```

`premium`, `anonymity`, `yourpost` は値が 0 の場合、本家ニコ生の仕様に合わせてフィールド自体が省略されます。

### プロジェクト構成

```
NX-Jikkyo/
├── client/                       # フロントエンド (Vue 3 + Vuetify 3 + TypeScript)
│   ├── src/
│   │   ├── components/           # Vue コンポーネント
│   │   │   └── Watch/            # 視聴画面関連コンポーネント
│   │   ├── views/                # ページコンポーネント
│   │   │   ├── TV/               # ライブ実況視聴画面
│   │   │   ├── Kakolog/          # 過去ログ再生画面
│   │   │   └── Settings/         # 設定画面
│   │   ├── services/             # API 通信層
│   │   │   └── player/           # プレイヤー関連 (KonomiTV ベース)
│   │   │       └── managers/     # PlayerManager 群
│   │   │           ├── LiveCommentManager.ts    # コメント管理
│   │   │           ├── KeyboardShortcutManager.ts
│   │   │           └── DocumentPiPManager.ts
│   │   ├── stores/               # Pinia ストア (状態管理)
│   │   ├── utils/                # ユーティリティ関数
│   │   └── plugins/              # Vue プラグイン (Vuetify 等)
│   ├── package.json
│   └── vite.config.ts
├── server/                       # バックエンド (Python 3.13 + FastAPI)
│   ├── NX-Jikkyo.py              # エントリーポイント (Typer CLI)
│   ├── app/
│   │   ├── app.py                # FastAPI アプリケーション定義
│   │   ├── config.py             # 設定管理 (Pydantic Settings)
│   │   ├── constants.py          # 定数 (チャンネル情報・Redis キー等)
│   │   ├── schemas.py            # Pydantic & TypedDict スキーマ定義
│   │   ├── models/
│   │   │   └── comment.py        # ORM モデル (Channel, Thread, Comment)
│   │   ├── routers/
│   │   │   ├── channels.py       # チャンネル API
│   │   │   ├── threads.py        # スレッド/コメント API
│   │   │   ├── websocket.py      # WebSocket API (ニコ生互換)
│   │   │   └── niconico.py       # ニコニコ OAuth API
│   │   ├── utils/
│   │   │   ├── Jikkyo.py         # ニコニコ実況連携 (NDGRClient)
│   │   │   ├── comment_counter_cache.py  # コメ番キャッシュ (Redis Lua)
│   │   │   └── transaction.py    # DB トランザクション (自動リトライ)
│   │   └── migrations/           # Aerich マイグレーション
│   ├── pyproject.toml            # Poetry 依存管理・タスク定義
│   └── static/logos/             # チャンネルロゴ
├── docker-compose.yaml           # Docker Compose 構成定義
├── Dockerfile                    # コンテナビルド定義
├── Caddyfile                     # Caddy リバースプロキシ設定
├── my.cnf                        # MySQL パフォーマンスチューニング設定
├── .env.example                  # 環境変数テンプレート
└── mysqldump.sh                  # MySQL バックアップスクリプト
```

### REST API エンドポイント

| エンドポイント | 説明 |
|:--|:--|
| `GET /api/v1/channels` | チャンネル一覧取得 (`full=True` で全スレッド取得) |
| `GET /api/v1/channels/xml` | XML 互換チャンネル情報 (NicoJK.ini 対応) |
| `GET /api/v1/channels/{channel_id}/threads` | チャンネルのスレッド履歴 |
| `GET /api/v1/channels/{channel_id}/logo` | チャンネルロゴ (PNG) |
| `GET /api/v1/channels/{channel_id}/jikkyo` | ニコニコ実況 WebSocket 情報 |
| `GET /api/v1/threads/{thread_id}` | スレッド情報と全コメント取得 |
| `WS /api/v1/channels/{channel_id}/ws/watch` | 視聴セッション WebSocket |
| `WS /api/v1/channels/{channel_id}/ws/comment` | コメントセッション WebSocket |
| `GET /api/niconico/auth` | ニコニコ OAuth 認証 URL 発行 |
| `GET /api/niconico/callback` | ニコニコ OAuth コールバック |

## Development

### 前提条件

- **Docker** & **Docker Compose**
- **Python 3.13** + **[Poetry](https://python-poetry.org/)**
- **Node.js** + **Yarn** (フロントエンド開発時)

### セットアップ

```bash
# .env を作成
cp .env.example .env
```

### 環境変数 (.env)

| 変数名 | デフォルト値 | 説明 |
|:--|:--|:--|
| `ENVIRONMENT` | `Develop` | 環境 (`Develop` / `Production`) |
| `SERVER_PORT` | `5610` | FastAPI メインサーバーポート |
| `SUB_SERVER_PROCESS_COUNT` | `3` | メインサーバープロセスの他に起動するサブサーバープロセスの個数 |
| `CADDY_HTTP_PORT` | `80` | Caddy HTTP ポート |
| `CADDY_HTTPS_PORT` | `443` | Caddy HTTPS ポート |
| `MYSQL_USER` | `nx-jikkyo_user` | MySQL ユーザー名 |
| `MYSQL_PASSWORD` | `nx-jikkyo_password` | MySQL パスワード |
| `MYSQL_DATABASE` | `nx-jikkyo_db` | MySQL データベース名 |
| `NICONICO_OAUTH_CLIENT_ID` | - | ニコニコ OAuth クライアント ID |
| `NICONICO_OAUTH_CLIENT_SECRET` | - | ニコニコ OAuth クライアントシークレット |

### Server

```bash
# VSCode 上での Python の補完が効くように、別途ローカルに Poetry で管理している依存ライブラリをインストールする必要がある
## 実際に NX-Jikkyo サーバーの動作に使われるのは Docker イメージビルド時にインストールされたライブラリの方
## 両者は同期しないので、Poetry でライブラリを追加・更新した際は忘れずにローカル環境で poetry install --no-root を実行すること
cd server
poetry install --no-root
```

以下のコマンドは内部的に Docker Compose 上で実行されます。  
MySQL / Redis コンテナは NX-Jikkyo (Uvicorn) と同時に起動します (サーバーを立ち下げても MySQL / Redis コンテナは停止しないので注意) 。

```bash
# サーバーを起動
#  http://localhost:5610 でアクセス可能
poetry run task serve

# サーバーを起動 (ホットリロード)
# server/app/ 配下のコード変更を検知して自動的にサーバーを再起動する
poetry run task dev
```

その他の開発コマンドは以下の通りです。

```bash
# Aerich (マイグレーションツール) を使う
poetry run task aerich --help

# コード品質チェック (Ruff + Pyright)
poetry run task lint

# 型チェックのみ (Pyright)
poetry run task typecheck

# MySQL のバックアップを取る
./mysqldump.sh

# MySQLTuner を実行する場合 (別途 MySQLTuner のダウンロードが必要)
~/mysqltuner.pl --host $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' nx-jikkyo-mysql) --user root --pass nx-jikkyo_password --forcemem 8192 --forceswap 2048
```

### Client

```bash
cd client

# 依存ライブラリをインストール
yarn install

# フロントエンド開発サーバーを起動 (ホットリロード)
# http://localhost:5710 でアクセス可能
yarn dev

# フロントエンドをビルド
# client/dist/ にビルド成果物が出力される (Docker イメージから参照される)
yarn build

# コード品質チェック (ESLint)
yarn lint
```

### Docker Compose 構成

| サービス | イメージ | 説明 |
|:--|:--|:--|
| `nx-jikkyo` | `python:3.13.1-bookworm` ベース | FastAPI メインアプリケーション (Uvicorn) |
| `nx-jikkyo-mysql` | `mysql:8.0` | データベース |
| `nx-jikkyo-redis` | `redis:6.2` | キャッシュ・Pub/Sub |
| `nx-jikkyo-caddy` | `caddy:2-alpine` | リバースプロキシ (TLS 終端・ロードバランシング) |

## License

[MIT License](License.txt)
