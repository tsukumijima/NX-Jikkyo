# NX-Jikkyo — AI エージェント向けドメイン知識ガイド

このファイルはコードからは読み取りにくい設計意図・前提知識をまとめたものです。
NX-Jikkyo のコードを読む・修正する前に必ず一読してください。

---

## サービス概要

NX-Jikkyo はニコニコ実況の補完・拡張サービスです。フロントエンド (client/) は KonomiTV のソースコードを流用して開発されているほか、バックエンドの基本的なファイル構成も KonomiTV のサーバー側コードに寄せて開発されています（DB 設計や API エンドポイントなどは全く異なりますが）。

ニコニコ実況はニコニコ生放送（ニコ生）の公式チャンネル群として運営されており、
テレビ放送を別途見ながら、リアルタイムでコメントを投稿できる仕組みです。
NX-Jikkyo はこれを「JavaScript に対する TypeScript」のようなスーパーセット的なポジションで提供しています。

**ニコ生側が用意している実況チャンネル**（NX-Jikkyo はこれらのミラー兼補完）:
`jk1`, `jk2`, `jk4`, `jk5`, `jk6`, `jk7`, `jk8`, `jk9`, `jk101`, `jk211`（地上波 + NHK BS + BS11）

**NX-Jikkyo 独自のチャンネル**（ニコ生には存在しない、NX が独自にコメントサーバーを提供）:
上記以外の `jk10`, `jk11`, `jk12`... `jk222`, `jk333` など（主に BS・CS 系）

コメント量の多さは **地上波（特に jk1 NHK総合、jk6 TBS など）が圧倒的**で、
BS 系（jk141: BS日テレ、jk222: BS12 など）はアニメ実況くらいでしか盛り上がらない。
NX-Jikkyo の存在意義のメインは「ニコ生がカバーしていない BS・CS 系チャンネルの補完」にある。

これに加えて、ニコ生側のコメント配信プロトコルの大幅変更についていけていないサードパーティーアプリ向けの互換 API の提供としての意味合いもある。  
実際、KonomiTV はニコ生側・NX 側両方のコメントを NX-Jikkyo の WebSocket API から取得して表示している。

より詳細な歴史的経緯は適宜 [About ページ](client/src/views/About.vue) を参照してください。

---

## コメント取り込みの仕組み（重要）

### ニコ生対応チャンネル（jk1/jk2/jk4/jk5/jk6/jk7/jk8/jk9/jk101/jk211）

`NDGRClient`（curl-cffi + HTTP/3）でニコ生の NDGR メッセージサーバーからコメントをリアルタイムストリーミングし、
**専用の 5610 ポートプロセス**（Caddy のロードバランシングから意図的に除外）が DB に書き込む。

`app.py` の `StreamNicoliveComments()` が各チャンネルに対してバックグラウンドタスクとして起動する。
処理フロー（1 コメントにつきシーケンシャル）:
```
NDGRClient.streamComments() の yield
  → await RunTransactionWithReconnectRetry(CreateCommentInTransaction)  # DB 書き込み
  → await UpdateThreadCommentCounterCache(...)                          # Redis コメ番キャッシュ
  → await REDIS_CLIENT.publish(...)                                     # Redis Pub/Sub 配信
```

`async for` ジェネレータのバックプレッシャー構造のため、
**DB 書き込みが詰まると次のコメント受信も止まる**（イベントループ自体はブロックしないが、
ジェネレータの `yield` が戻るまで次の `await comment_queue.get()` に進めない）。

### NX-Jikkyo 独自チャンネル（BS 系など）

WebSocket 経由のユーザー投稿のみ。NDGRClient によるストリーミングは行わない。

### コメント番号（no）の採番

`comment_counters` テーブルで `UPDATE comment_counters SET max_no = max_no + 1 WHERE thread_id = ?` により採番。
thread_id ごとの行ロックが発生する。異なる thread_id 間での競合は通常ない。

---

## スレッド管理

- 1スレッド = 1チャンネルの **JST 04:00 〜 翌日 JST 04:00** の 24 時間分
- **スレッドの切り替わりは毎日 JST 04:00**（ニコ生の実況枠リセットも同じく 04:00）
- VPS 自体の定期再起動も毎日 JST 04:00 に設定（`~/cron.conf` の `0 4 * * * sudo reboot`）
  → MySQL コンテナも含め全てがリセットされる（InnoDB バッファプールのコールドスタート）
  → ただし JST 04:00 はコメント量が最も少ない時間帯なので影響は限定的

---

## データストア設計

### MySQL（メイン DB）

- `comments` テーブル: 全リアルタイムコメント（2026-02 時点で 9300 万行超、約 3.5 GiB）
  - インデックス: `PRIMARY KEY (id)` + `KEY idx_thread_id_id (thread_id, id)` のみ
  - `id` は AUTO_INCREMENT（末尾追記）、`no` はスレッドごとの連番（`comment_counters` で採番）
  - `ORDER BY no ASC` はインデックスが効かない（`idx_thread_id_id` は id 順のため filesort が必要）
  - `ORDER BY id ASC/DESC` はインデックスが効く
- `comment_counters` テーブル: スレッドごとの最新コメ番
- `threads` テーブル: チャンネルごとの 24 時間スレッド情報
- **バッファプール設定の経緯**: 元は 2 GiB → 2026-02-08 に 1 GiB に削減 → 2026-02-13 に 1.28 GiB に調整（削りすぎたため戻した）
  - 現在のバッファプール 1.28 GiB に対してテーブル 3.5 GiB → キャッシュ率 36% と低い
  - SELECT クエリがバッファプールを圧迫すると eviction が発生し、COMMIT も巻き添えになる

### Redis

- コメ番の最新値キャッシュ（`comment_counter_cache`）: DB 書き込み側の採番を高速化
- Pub/Sub（`REDIS_CHANNEL_THREAD_COMMENTS_PREFIX:{thread_id}`）: リアルタイムコメント配信
- 視聴者数・実況勢いカウンター
- **コメントの内容（過去コメント一覧）はキャッシュしていない**
  → `GET /api/v1/threads/{thread_id}` は毎回 DB から全件取得する

### XML ファイル（過去ログ）

- [JKCommentCrawler](https://github.com/tsukumijima/JKCommentCrawler) （別プロジェクト）が生成・管理する
- NX-Jikkyo 側の DB バックアップ + 1ヶ月で消えてしまうニコニコ生放送の過去ログをバックアップ・アーカイブする役割の両方を持っている（NX-Jikkyo 自体はリアルタイム取り込みで、ニコ生側のコメントの取りこぼしが起きうるため）
- DB ではなく XML にしているのは「整合性管理や差分取得が DB だと複雑」という設計判断
- Hugging Face の [KakologArchives](https://huggingface.co/datasets/KakologArchives/KakologArchives) リポジトリに push されている

---

## JKCommentCrawler との連携（重要）

JKCommentCrawler は別リポジトリの CLI ツールで、自宅サーバーの cron で動く。

**主な動作**:
- NDGRClient で直接ニコ生からコメントを取得（これがメイン）
- NXClient 経由で `GET /api/v1/threads/{thread_id}` を叩き、NX-Jikkyo 独自コメントを補完取得
- 両者をマージしてニコ生互換 XML 形式で保存

**NX-Jikkyo をマスターにしていない理由**:
NX-Jikkyo はリアルタイム取り込みで取りこぼしが避けられない構造のため。
ニコ生はプレミアム会員なら 1 ヶ月まで過去ログを参照できるため、NDGRClient で遡れる。

**cron スケジュール**（自宅 PC）:
- `*/5 * * * *`: 当日分を 5 分おきに取得（`cron_minutes`）
- `01,15 00 * * *`, `01,15 12 * * *`: 前日分を `--force` 付きで取得（取りこぼし防止）

**NX-Jikkyo 側への負荷**:
`NXClient.downloadBackwardComments()` が `GET /api/v1/threads/{thread_id}` を呼ぶ。
このエンドポイントは `ORDER BY no ASC` で全コメントを返すため、コメント量が多い
地上波スレッド（jk1〜jk8）では 1 万〜数万行のスキャンが発生する。
バッファプールが不足している状態でこれが走ると、書き込み側の COMMIT も遅延する。

---

## デプロイ構成

```
Docker Compose サービス:
  caddy        → リバースプロキシ・ロードバランサー
  nx-jikkyo    → FastAPI (Uvicorn) × 5 プロセス
  nx-jikkyo-mysql → MySQL 8.0
  nx-jikkyo-redis → Redis 6.2
```

5 プロセスのうち **5610 ポートのプロセスのみが Caddy から除外**され、
NDGRClient によるコメント取り込みと DB 書き込みに専念する。

**デプロイ時の注意（重要）**:
`docker compose up -d --build --force-recreate` は MySQL コンテナも再起動するため、
InnoDB バッファプールがコールドスタートし、コメント詰まりが発生しやすくなる。
アプリコードのみ更新する場合は以下のように nx-jikkyo コンテナのみ再起動すること:
```bash
docker compose up -d --build nx-jikkyo
```

---

## 既知のパフォーマンス課題（2026-02 時点）

1. **`GET /api/v1/threads/{thread_id}` が `ORDER BY no ASC` で全件取得**（`threads.py:53`）
   - インデックス `idx_thread_id_id (thread_id, id)` は `no` のソートに使えない → filesort 発生
   - `ORDER BY id ASC` に変えるだけでインデックスが効くようになる（`no` と `id` はほぼ同順）
   - このエンドポイントに Redis キャッシュを追加する（過去スレッドなら内容不変）のも有効

2. **MySQL のバッファプール不足**
   - テーブル 3.5 GiB に対してバッファプール 1.28 GiB（キャッシュ率 36%）
   - SELECT が走ると eviction → ダーティページフラッシュ → I/O 占有 → COMMIT 遅延
   - 根本解決は古いレコードの削除（JKCommentCrawler の XML にバックアップがあるため安全）

3. **コールドスタート時のコメント詰まり**
   - 再起動後にバッファプールが空の状態でコメントが来ると COMMIT が数十秒単位で遅延
   - `async for` のバックプレッシャーによりコメントが滞留してバーストとして現れる
   - デプロイ時に MySQL を再起動しないことで回避できる

4. **`async for` バックプレッシャー構造**（`app.py` の `StreamNicoliveComments`）
   - 1 コメントの DB 書き込みが完了するまで次のコメント受信が止まる構造的問題
   - asyncio.Queue を間に挟んで受信と書き込みを並行化することで解消できるが実装難度は中程度

---

## KonomiTV との関係

NX-Jikkyo は KonomiTV のフォークだが、以下の機能を意図的に削除している:
- ユーザーアカウント管理
- Twitter/X 統合
- 録画番組管理
- 番組表機能
- その他多数の KonomiTV 固有機能

KonomiTV の最新機能を NX-Jikkyo にバックポートする際は、
削除済み機能との依存関係に注意が必要（`/konomitv-to-nx-jikkyo-porter` スキルを参照）。
