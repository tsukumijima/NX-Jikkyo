---
name: konomitv-to-nx-jikkyo-porter
description: >
  KonomiTV の最新開発版で追加・改良された機能を NX-Jikkyo に移植（バックポート）するためのガイド。
  NX-Jikkyo は KonomiTV のフォークだが、ユーザーアカウント管理・Twitter 統合・録画番組管理・番組表など
  多数の機能が削除されており、単純なコピーでは動作しない。このスキルは両プロジェクト間の差異を把握した上で、
  適切に移植を行うワークフローを提供する。
  以下のようなタスクで使用する:
  (1) KonomiTV の新機能や改良を NX-Jikkyo にバックポートする
  (2) KonomiTV から移植した際に混入したデッドコードを検出・除去する
  (3) KonomiTV と NX-Jikkyo の差分を確認・把握する
---

# KonomiTV → NX-Jikkyo 移植ガイド

## 概要

NX-Jikkyo は KonomiTV をフォークして作られたニコニコ実況避難所向けの TV 視聴アプリケーション。
KonomiTV が持つ多機能（ユーザーアカウント管理・録画番組・予約・Twitter 統合・番組表・設定同期など）から、
ライブ視聴とニコニコ実況コメントに必要な機能だけを残したシンプルな構成になっている。

KonomiTV 側で行われた機能改良を NX-Jikkyo に移植する際は、削除済み機能への参照を除外しつつ、
NX-Jikkyo 固有のアーキテクチャ（Cookie ベースのニコニコアカウント連携など）に適合させる必要がある。

両プロジェクト間の差異の詳細は [references/nx-jikkyo-differences.md](references/nx-jikkyo-differences.md) を参照。

## 移植ワークフロー

KonomiTV の変更を NX-Jikkyo に移植する手順は以下の通り。

1. **変更内容の把握**: KonomiTV 側の diff を確認し、変更されたファイルと変更内容を理解する
2. **移植可否の判定**: 変更が NX-Jikkyo で削除済みの機能に関連するか判定する（後述の「除外すべき機能」参照）
3. **対応ファイルの特定**: KonomiTV のファイルパスを NX-Jikkyo の対応パスに変換する（後述の「パス変換ルール」参照）
4. **差異の吸収**: NX-Jikkyo 固有の違いを考慮して変更を適用する（後述の「適応パターン」参照）
5. **デッドコード確認**: 移植したコードに NX-Jikkyo では不要な参照が残っていないか確認する
6. **ビルド検証**: `yarn lint` と `yarn typecheck` でエラーがないことを確認する

## NX-Jikkyo 固有のハック的実装

NX-Jikkyo は最低限の工数で KonomiTV から機能を流用しているため、以下のハック的実装が存在する。
移植時にこれらを壊さないよう注意が必要。詳細は [references/nx-jikkyo-differences.md](references/nx-jikkyo-differences.md) のセクション 6 を参照。

- **過去ログ再生 = KonomiTV の録画再生基盤の流用**: `Kakolog/Watch.vue` が `playback_mode="Video"` で共有コンポーネント群 (`Watch.vue`, `Panel.vue`, `Comment.vue`, `RecordedProgram.vue`, `PlayerController.ts`) を再利用。KonomiTV の録画番組視聴画面 (`Videos/Watch.vue`) と同じインフラで動作する
- **IRecordedProgram のモック生成**: 過去ログの日時範囲から仮想的な `IRecordedProgram` を `id = -100` でメモリ上に構築し `PlayerStore` に渡す
- **過去ログコメントの外部 API 直接呼び出し**: `Videos.fetchVideoJikkyoComments()` のシグネチャを `video_id` → `recorded_program` に変更し、クライアント側から `jikkyo.tsukumijima.net` の過去ログ API に直接アクセス
- **Cookie ベースのニコニコアカウント連携**: サーバー側ユーザーアカウントの代わりに `NX-Niconico-User` Cookie (Base64 JSON) で連携情報を保持
- **video 系設定の残存**: 過去ログ再生が `playback_mode="Video"` を使うため、`video_panel_active_tab` や `video_show_superimpose` などの video 系設定を削除できない

## 除外すべき機能

以下の機能は NX-Jikkyo に存在しないため、これらに関連する変更は移植対象外とする。

- **ユーザーアカウント管理**: ログイン/登録/アカウント設定、Bearer トークン認証、`is_logged_in` チェック
- **Twitter 統合**: Twitter サービス/ストア/パネル、ハッシュタグ管理、ツイート連携
- **録画番組管理**: Videos システム（ただし `Videos.ts` の `fetchVideoJikkyoComments()` は過去ログ再生で使用されるため残存）、シリーズ管理
- **予約管理**: Reservations システム
- **番組表**: TimeTable システム
- **ユーザーコンテンツ**: マイリスト、視聴履歴、マイページ
- **設定同期**: サーバーとの双方向同期、`sync_settings`、`last_synced_at`、`syncClientSettings*`
- **プレイヤー拡張**: キャプチャ機能、データ放送、L 字画面クロップ、MediaSession、ライブイベント管理
- **サーバー管理**: サーバー設定画面、メンテナンスサービス

## パス変換ルール

KonomiTV と NX-Jikkyo でルーティングが異なるため、ファイルパスの対応関係に注意が必要。

| KonomiTV | NX-Jikkyo | 備考 |
|---|---|---|
| `views/TV/Home.vue` | `views/TV/Home.vue` | 同一 |
| `views/TV/Watch.vue` | `views/TV/Watch.vue` | 同一 |
| `views/Videos/Watch.vue` | `views/Kakolog/Watch.vue` | 録画再生基盤を過去ログ再生に流用 |
| `views/Settings/Jikkyo.vue` | `views/Settings/Jikkyo.vue` | 同一 |
| `views/Settings/General.vue` | `views/Settings/General.vue` | 同一 |
| `views/Login.vue` | *(存在しない)* | 移植不要 |
| `views/Register.vue` | *(存在しない)* | 移植不要 |
| `views/Settings/Account.vue` | *(存在しない)* | 移植不要 |
| `views/Settings/Twitter.vue` | *(存在しない)* | 移植不要 |
| `views/Settings/Server.vue` | *(存在しない)* | 移植不要 |
| `views/Videos/*`（Watch 以外） | *(存在しない)* | 移植不要 |
| `services/Videos.ts` | `services/Videos.ts` | シグネチャ変更あり（外部 API 直接呼び出し） |
| `components/Watch/*` | `components/Watch/*` | 同一（playback_mode で Live/Video 分岐） |

ルーターのパスも異なる:
- KonomiTV: `/tv/watch/:id` → NX-Jikkyo: `/watch/:id`
- KonomiTV: `/tv/` → NX-Jikkyo: `/`
- KonomiTV: `/videos/watch/:video_id` → NX-Jikkyo: `/log/:display_channel_id/:kakolog_period_id`

## 適応パターン

### A. 設定項目の移植

KonomiTV で新しい設定項目が追加された場合の対応手順。

1. `client/src/services/Settings.ts` の `IClientSettings` に型定義を追加
2. `client/src/stores/SettingsStore.ts` にデフォルト値を追加
   - オブジェクトや配列のデフォルト値には `structuredClone()` を使用すること
3. 対応する Settings View にUI を追加
   - KonomiTV の `settings__item--sync-disabled` CSS クラスは NX-Jikkyo では不要（同期機能がないため）
4. `tv_panel_active_tab` の型に `'Twitter'` が含まれていないか確認（NX-Jikkyo では除外済み）
5. `video_panel_active_tab` の型に `'Series'` や `'Twitter'` が含まれていないか確認（NX-Jikkyo では除外済み）

### B. ニコニコアカウント連携関連の移植

KonomiTV と NX-Jikkyo ではニコニコアカウント連携の仕組みが根本的に異なる。

- KonomiTV: サーバー側ユーザーアカウントにログイン → `Users.fetchUser()` が API を呼び出す
- NX-Jikkyo: `NX-Niconico-User` Cookie から直接読み取り → `Users.fetchUser()` が Cookie をパースする

移植時のポイント:
- KonomiTV で `user_store.user === null` が「ログインしていない」を意味するコードは、NX-Jikkyo では「ニコニコアカウント未連携」として扱う
- `is_logged_in` のチェックで機能をガードするコードは NX-Jikkyo では不要（ガードを除去するか、ニコニコ連携チェックに書き換える）
- Bearer トークン関連の処理（`getAccessToken`, Authorization ヘッダー）は NX-Jikkyo には存在しない

### C. LocalStorage ベースの設定（DPlayer 設定）

NX-Jikkyo では DPlayer の設定が LocalStorage に直接保存される。
KonomiTV の同等設定を Settings 画面に追加する場合、以下のキーとの連携が必要。

- `dplayer-danmaku-show` — コメント表示/非表示 (boolean)
- `dplayer-danmaku-unlimited` — コメント無制限表示 (boolean)
- `dplayer-danmaku-opacity` — コメント透明度 (number: 0〜1)

Settings View の `created()` で LocalStorage から読み取り、`watch` で LocalStorage に書き戻す実装が必要。

### D. デッドコードの検出

KonomiTV からコードを移植した後、以下のパターンのデッドコードが混入していないか確認する。

- **インポート**: 存在しないモジュール（`TwitterStore`, `Captures`, `Series` など）のインポート
- **型参照**: `'Twitter'`, `'Series'` など NX-Jikkyo に存在しないリテラル型の参照
- **認証ガード**: `is_logged_in` や `access_token` による条件分岐
- **同期処理**: `syncClientSettings*` の呼び出しや `last_synced_at` の参照
- **API 呼び出し**: NX-Jikkyo のサーバーに存在しないエンドポイントへのリクエスト

## リファレンス

両プロジェクト間の差異の完全なリストは [references/nx-jikkyo-differences.md](references/nx-jikkyo-differences.md) を参照。
以下の情報が含まれる:

- NX-Jikkyo で削除された全機能の一覧
- NX-Jikkyo で独自に追加された機能
- ファイル構成の詳細な差異
- IClientSettings の型定義とデフォルト値の差異
- アーキテクチャの差異（ルーティング、設定保存方式など）
- 移植時の注意点パターン集
