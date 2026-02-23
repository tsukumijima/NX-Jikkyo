# NX-Jikkyo と KonomiTV の差異リファレンス

NX-Jikkyo は KonomiTV のフォークであり、ニコニコ実況避難所に特化したシンプルなウェブアプリケーション。
KonomiTV は録画番組管理・予約・Twitter 統合・番組表などを備えた多機能な TV 視聴システム。

---

## 目次

- [1. NX-Jikkyo で削除された機能](#1-nx-jikkyo-で削除された機能)
- [2. NX-Jikkyo で独自に追加された機能](#2-nx-jikkyo-で独自に追加された機能)
- [3. ファイル構成の差異](#3-ファイル構成の差異)
- [4. IClientSettings の差異](#4-iclientsettings-の差異)
- [5. アーキテクチャの差異](#5-アーキテクチャの差異)
- [6. NX-Jikkyo のハック的実装](#6-nx-jikkyo-のハック的実装)
- [7. 移植時の注意点パターン集](#7-移植時の注意点パターン集)

---

## 1. NX-Jikkyo で削除された機能

### 認証・ユーザー管理
- ユーザー登録/ログイン機能（Login.vue, Register.vue）
- アカウント設定（Account.vue）
- アクセストークンによる認証（Bearer トークン）
- サーバー側のユーザー管理 API

### 録画・予約関連
- 録画番組視聴（Videos システム: Home, Search, Programs, Watch）
- 予約管理（Reservations システム）
- シリーズ管理（Series サービス）

### ユーザーコンテンツ管理
- マイリスト（Mylist）
- 視聴履歴（WatchedHistory）
- マイページ（MyPage）

### 番組表
- TimeTable（番組表画面とコンポーネント群）

### Twitter 統合
- Twitter サービス（Twitter.ts）、ストア（TwitterStore.ts）
- Twitter パネル（Tweet, Timeline, Search, Captures コンポーネント）
- ハッシュタグ管理関連設定

### プレイヤー拡張機能
- キャプチャ機能（CaptureManager, Captures サービス）
- データ放送（LiveDataBroadcastingManager, DataBroadcasting 設定画面）
- L 字画面クロップ（LShapedScreenCropSettings）
- MediaSession API 統合
- ライブイベント管理
- Web Workers（CaptureCompositor, LivePSIArchivedDataDecoder）

### サーバー設定・メンテナンス
- サーバー設定画面（Settings/Server.vue）
- メンテナンスサービス
- ServerSettingsStore

### 設定同期
- サーバーとの双方向設定同期（sync_settings, syncClientSettingsToServer/FromServer）
- `last_synced_at` による同期時刻管理
- 3秒ごとのポーリング同期

---

## 2. NX-Jikkyo で独自に追加された機能

### 過去ログ再生
- `Kakolog/Index.vue` — 過去ログ検索画面
- `Kakolog/Watch.vue` — 過去ログ再生画面

### 独自設定項目
- `comment_delay_seconds: number` — コメント表示遅延秒数
- `mute_nicolive_comments: boolean` — 本家ニコニコ実況コメントのミュート
- `mute_nxjikkyo_comments: boolean` — NX-Jikkyo コメントのミュート

### ニコニコアカウント連携方式
- KonomiTV: サーバー側ユーザーアカウントにログイン → ニコニコアカウント連携
- NX-Jikkyo: `NX-Niconico-User` Cookie に Base64 エンコードした JSON で直接保存（サーバーアカウント不要）

### About ページ
- `About.vue` — NX-Jikkyo の情報ページ

---

## 3. ファイル構成の差異

### NX-Jikkyo にない KonomiTV のファイル

**Views:**
- Videos/ (Home, Search, Programs, Watch)
- TimeTable.vue
- Reservations/ (Home, Reservations)
- Mylist.vue, WatchedHistory.vue, MyPage.vue
- Login.vue, Register.vue
- Settings/ (Account, Quality, Caption, DataBroadcasting, Capture, Twitter, Server)

**Components:**
- Breadcrumbs.vue, SPHeaderBar.vue
- Settings/AccountManageSettings.vue, TimeTableSettings.vue, ServerLogDialog.vue
- Reservations/ (4コンポーネント)
- TimeTable/ (5コンポーネント)
- Videos/ (RecordedProgram, RecordedProgramList, Dialogs/)
- Watch/LShapedScreenCropSettings.vue
- Watch/Panel/ (Remocon, Series, Twitter/ 4コンポーネント)

**Services:**
- Captures.ts, Maintenance.ts, ReservationConditions.ts, Reservations.ts, Series.ts, Twitter.ts

**Player Managers:**
- CaptureManager.ts, LiveDataBroadcastingManager.ts, LiveEventManager.ts, MediaSessionManager.ts

**Stores:**
- TwitterStore.ts, TimeTableStore.ts, ServerSettingsStore.ts

**Workers:**
- LivePSIArchivedDataDecoder.ts, CaptureCompositor.ts (+Proxy)

**Utils:**
- Semaphore.ts, TimeTableUtils.ts

### デフォルト値の差異

| 設定項目 | NX-Jikkyo | KonomiTV |
|---|---|---|
| `tv_panel_active_tab` | `'Comment'` | `'Program'` |
| `video_panel_active_tab` | `'Comment'` | `'RecordedProgram'` |
| `close_comment_form_after_sending` | `false` | `true` |
| `mute_vulgar_comments` | `false` | `true` |

---

## 4. IClientSettings の差異

### NX-Jikkyo のパネルタブ型
```typescript
tv_panel_active_tab: 'Program' | 'Channel' | 'Comment';
video_panel_active_tab: 'RecordedProgram' | 'Comment';
```

### KonomiTV のパネルタブ型
```typescript
tv_panel_active_tab: 'Program' | 'Channel' | 'Comment' | 'Twitter';
video_panel_active_tab: 'RecordedProgram' | 'Series' | 'Comment' | 'Twitter';
```

### KonomiTV にのみある設定項目（抜粋）
- `last_synced_at`, `sync_settings` — 設定同期
- `saved_twitter_hashtags`, `fold_panel_after_sending_tweet`, `reset_hashtag_when_program_switches`, `auto_add_watching_channel_hashtag`, `twitter_active_tab`, `tweet_hashtag_position`, `tweet_capture_watermark_position` — Twitter 関連
- `mylist`, `watched_history`, `video_watched_history_max_count` — ユーザーコンテンツ
- `timetable_*` — 番組表関連
- `capture_filename_pattern` — キャプチャ
- `use_pure_black_player_background`, `use_28hour_clock`, `show_original_broadcast_time_during_playback` — UI

### 同期無効コメントについて
NX-Jikkyo の IClientSettings には KonomiTV から引き継いだ「同期無効」コメント（`// tv_streaming_quality: 同期無効` など）が残っているが、これは単なる削除漏れである。NX-Jikkyo にはサーバー同期機能自体が存在せず、実装予定もない（同期機能にはサーバー側のユーザー管理機能が必要であり、コストが高いため）。これらのコメントはすでに Settings.ts から削除済み。

### ILocalClientSettings から削除済みのフィールド

以下のフィールドは KonomiTV には存在するが、NX-Jikkyo のデータ放送機能削除に伴い `ILocalClientSettings` 型定義と `ILocalClientSettingsDefault` デフォルト値の両方から除去済み。バックポート時に再混入させないよう注意。

- `tv_show_data_broadcasting: boolean` — テレビ視聴時にデータ放送機能を利用するかどうか
- `enable_internet_access_from_data_broadcasting: boolean` — データ放送からのインターネットアクセスを有効にするかどうか

---

## 5. アーキテクチャの差異

### チャンネル ID フォーマット

NX-Jikkyo と KonomiTV ではチャンネル ID の形式が根本的に異なる。

| プロジェクト | GR チャンネル ID | BS チャンネル ID |
|---|---|---|
| KonomiTV | `gr011` など（5文字、`gr` prefix + 3桁番号） | `bs211` など（5文字、`bs` prefix + 3桁番号） |
| NX-Jikkyo | `jk1`〜`jk9`（3〜4文字、ニコニコ実況 GR 系） | `jk101`〜`jk999`（5文字、ニコニコ実況 BS 系） |

`ChannelUtils.ts` の `getChannelType()` が `id.length <= 4` で GR/BS を判別しているのは、NX-Jikkyo の ID フォーマットに対して正しい実装（`Channels.ts` でも同じロジックを使用）。KonomiTV の `gr`/`bs` prefix 判別とは異なるが、バグではない。差分調査時に誤検知しやすいパターンなので注意。

### ルーティング
- NX-Jikkyo: `/` → TV Home（直接）、`/watch/`、`/log/`、`/about/`、`/settings/`
- KonomiTV: `/` → `/tv/` リダイレクト、`/tv/watch/`、`/videos/`、`/timetable/`、`/reservations/`、`/login/`、`/register/`

### 設定保存
- NX-Jikkyo: LocalStorage のみ（`NX-Jikkyo-Settings` キー）
- KonomiTV: LocalStorage + サーバー同期（`KonomiTV-Settings` キー）

### View Transitions
- NX-Jikkyo: `/watch/` で無効化
- KonomiTV: `/tv/watch/` と `/videos/watch/` で無効化

### CSS クラス
- `settings__item--sync-disabled`: KonomiTV でサーバー同期が無効な設定項目に適用。NX-Jikkyo には同期機能がないため不要。

---

## 6. NX-Jikkyo のハック的実装

NX-Jikkyo は最低限の工数で KonomiTV の機能を流用するため、多くのハック的な実装を含んでいる。
移植時にはこれらの仕組みを理解した上で、壊さないように注意する必要がある。

### 6.1 過去ログ再生 — KonomiTV の録画再生基盤の流用

NX-Jikkyo の過去ログ再生機能は、KonomiTV の録画番組視聴機能 (`Videos/Watch.vue`) のインフラをほぼそのまま流用して実装されている。
KonomiTV の共有視聴コンポーネント (`Watch.vue`) が `playback_mode` プロパティ (`'Live'` / `'Video'`) で動作を分岐する仕組みを利用し、
`Kakolog/Watch.vue` が `playback_mode="Video"` を指定することで録画再生と同じ UI・コンポーネント群を再利用している。

```
KonomiTV Videos/Watch.vue (録画番組視聴画面)
    → playback_mode="Video" で共有コンポーネント Watch を使用
                ↓ NX-Jikkyo はこの仕組みをそのまま流用
NX-Jikkyo Kakolog/Watch.vue (過去ログ再生画面)
    → playback_mode="Video" で同じ共有コンポーネント Watch を使用
```

流用されるコンポーネント・サービス:
- `components/Watch/Watch.vue` — `playback_mode` で Live/Video の表示を分岐
- `components/Watch/Panel.vue` — パネルのタブ構成を `playback_mode` で分岐
- `components/Watch/Panel/RecordedProgram.vue` — 番組情報パネル（過去ログ再生時の情報表示に使用）
- `components/Watch/Panel/Comment.vue` — ライブ時は `DynamicScroller`、ビデオ時は `VirtuaList` + シーク機能で分岐
- `services/player/PlayerController.ts` — `playback_mode` で映像ソース・コメント取得・キープアライブなどの処理を分岐

### 6.2 IRecordedProgram のモック生成

KonomiTV では `IRecordedProgram` はサーバーの録画番組データベースから取得されるが、NX-Jikkyo にはサーバー側に録画番組の概念がない。
`Kakolog/Watch.vue` では、ユーザーが指定した過去ログの日時範囲とチャンネル情報から、メモリ上に仮想的な `IRecordedProgram` オブジェクトをモック生成して `PlayerStore` に渡している。

```typescript
// Kakolog/Watch.vue での IRecordedProgram モック生成
const recorded_program = structuredClone(IRecordedProgramDefault);
recorded_program.id = -100;  // 特殊 ID でモック番組であることを識別
recorded_program.channel = channel;
recorded_program.recorded_video.recording_start_time = kakolog_start_dayjs.toISOString();
recorded_program.recorded_video.recording_end_time = kakolog_end_dayjs.toISOString();
recorded_program.title = `${channel.name}【ニコニコ実況+NX-Jikkyo】${display_date.format('YYYY年MM月DD日')}`;
recorded_program.start_time = kakolog_start_dayjs.toISOString();
recorded_program.end_time = kakolog_end_dayjs.toISOString();
recorded_program.duration = kakolog_end_dayjs.diff(kakolog_start_dayjs, 'second');
this.playerStore.recorded_program = recorded_program;
```

このモック `IRecordedProgram` には実際の録画ファイル情報 (`recorded_video.file_path` など) は存在しない。
共有コンポーネント群は `recorded_program` の `title`, `start_time`, `end_time`, `channel` などのフィールドのみ参照するため、これで動作する。

### 6.3 過去ログコメント取得 — クライアント側から外部 API 直接呼び出し

KonomiTV の `Videos.fetchVideoJikkyoComments()` はサーバー側で過去ログを取得する仕組みだが、
NX-Jikkyo ではクライアント側からニコニコ実況過去ログ API (`jikkyo.tsukumijima.net/api/kakolog/`) に直接アクセスするように書き換えられている。

```typescript
// KonomiTV: サーバー経由
static async fetchVideoJikkyoComments(video_id: number): Promise<IJikkyoComments> {
    const response = await APIClient.get(`/videos/${video_id}/jikkyo`);
    // ...
}

// NX-Jikkyo: クライアントから外部 API に直接アクセス
static async fetchVideoJikkyoComments(recorded_program: IRecordedProgram): Promise<IJikkyoComments> {
    const start_time = new Date(recorded_program.start_time).getTime() / 1000;
    const end_time = new Date(recorded_program.end_time).getTime() / 1000;
    const jikkyo_id = recorded_program.channel!.id;
    const kakolog_api_url = `https://jikkyo.tsukumijima.net/api/kakolog/${jikkyo_id}?starttime=${start_time}&endtime=${end_time}&format=json`;
    const response = await APIClient.get(kakolog_api_url, { timeout: 30000 });
    // ...
}
```

シグネチャも `video_id: number` → `recorded_program: IRecordedProgram` に変更されている。

### 6.4 Cookie ベースのニコニコアカウント連携

KonomiTV ではサーバー側のユーザーアカウントシステムを通じてニコニコアカウントと連携するが、
NX-Jikkyo にはユーザーアカウント機能がないため、`NX-Niconico-User` Cookie に Base64 エンコードした JSON を保存するハック的な方式を採用している。

```typescript
// NX-Jikkyo の Users.fetchUser() — Cookie からユーザー情報を読み取る
static async fetchUser(): Promise<IUser> {
    const niconico_user_cookie = getCookie('NX-Niconico-User');
    if (!niconico_user_cookie) {
        return {...IUserDefault};
    }
    try {
        const niconico_user = JSON.parse(Base64.decode(niconico_user_cookie));
        return {
            niconico_user_id: niconico_user.niconico_user_id,
            niconico_user_name: niconico_user.niconico_user_name,
            niconico_user_premium: niconico_user.niconico_user_premium,
        };
    } catch (error) {
        return {...IUserDefault};
    }
}
```

KonomiTV のコードで `user_store.user === null` が「KonomiTV にログインしていない」を意味する箇所は、
NX-Jikkyo では Cookie が存在しない = 「ニコニコアカウント未連携」を意味するように読み替える必要がある。

### 6.5 video_panel_active_tab と video 系設定の残存

NX-Jikkyo にはKonomiTV の録画番組視聴機能は存在しないが、過去ログ再生機能が `playback_mode="Video"` を利用する関係で、
`video_panel_active_tab`、`video_show_superimpose`、`video_data_saver_mode` といった video 系設定が残存している。
これらは過去ログ再生時に共有コンポーネントから参照されるため、削除すると動作しなくなる。

### 6.6 PlayerController の playback_mode 分岐

`PlayerController.ts` は `playback_mode` フラグで以下のように処理を大きく分岐している。

| 処理 | Live | Video（過去ログ） |
|---|---|---|
| 映像ソース | HLS/mpegts ストリーミング | なし（モック） |
| コメント取得 | `LiveCommentManager` で WebSocket リアルタイム取得 | `Videos.fetchVideoJikkyoComments()` で一括取得 |
| コメント送信 | `LiveCommentManager` で WebSocket 送信 | エラーメッセージ返却（送信不可） |
| mpegts.js 初期化 | 必須 | スキップ |
| キープアライブ | 不要 | 必須（過去ログ API セッション維持） |
| `LiveCommentManager` | PlayerManager に追加 | 追加しない |

### 6.7 KakologState.ts — Provide/Inject による状態管理

過去ログ検索画面 (`Kakolog/Index.vue`) の UI 状態（チャンネル・開始日時・終了日時）は、Pinia ストアではなく Vue 3 の Provide/Inject パターン (`KakologState.ts`) で管理されている。
グローバル状態にする必要がなく、`Index.vue` のスコープ内でのみ共有されるため。

---

## 7. 移植時の注意点パターン集

### パターン A: 機能の新規追加移植
KonomiTV で新しく追加された設定項目や UI を NX-Jikkyo に移植する場合。
- IClientSettings に型定義を追加
- SettingsStore にデフォルト値を追加
- 対応する Settings View の UI を追加
- `settings__item--sync-disabled` クラスは NX-Jikkyo では不要

### パターン B: 既存機能の改良移植
KonomiTV で既存機能が改良された場合。
- diff を確認し、NX-Jikkyo で削除済みの機能への参照がないか確認
- Twitter, Videos, Reservations, TimeTable 関連のコードは除外
- ユーザーアカウント関連（`is_logged_in`, `access_token`, `user_store.user` のログインチェック）は除外
- 設定同期関連（`sync_settings`, `last_synced_at`, `syncClientSettings*`）は除外

### パターン C: デッドコードの検出と除去
KonomiTV から移植した際に混入するデッドコードのパターン。
- アクセストークン関連（`getAccessToken`, `saveAccessToken`, `deleteAccessToken`）
- ユーザー認証チェック（`is_logged_in` チェックで機能をガードするコード）
- Twitter 関連の型定義や処理分岐
- キャプチャ関連のインポートや処理
- データ放送関連の処理
- サーバー設定同期のロジック

### パターン D: LocalStorage ベースの設定
NX-Jikkyo では DPlayer の設定（コメント表示/非表示、無制限表示、透明度）が LocalStorage に直接保存される。
KonomiTV の同等設定を移植する際は、LocalStorage からの読み取りと書き込みを手動で実装する必要がある。
- `dplayer-danmaku-show` — コメント表示/非表示
- `dplayer-danmaku-unlimited` — コメント無制限表示
- `dplayer-danmaku-opacity` — コメント透明度

### パターン E: ニコニコアカウント連携
NX-Jikkyo では `NX-Niconico-User` Cookie で連携情報を管理。
- KonomiTV の `Users.fetchUser()` → API アクセス
- NX-Jikkyo の `Users.fetchUser()` → Cookie 読み取り
- KonomiTV で `user_store.user === null` のチェックが「ログインしていない」を意味するコードは、NX-Jikkyo では「ニコニコアカウント連携がない」を意味するように変換が必要

### パターン F: structuredClone によるデフォルト値の保護
SettingsStore のデフォルト値にオブジェクトや配列が含まれる場合、`structuredClone()` を使用してディープコピーする必要がある。
共有参照による意図しない状態変更を防ぐため。

### パターン G: コメントアウトされたコードの整理

NX-Jikkyo で不要になった処理がコメントアウトのまま残されている場合の整理方針。

- **削除すべきケース**: 対応するフィールドや変数も削除されており、単なるコードの残骸になっている場合。`destroy()` 内の cleanup コードだけが残っている場合も削除対象。
- **理由コメントへの変換が適切なケース**: 「なぜこの処理が NX-Jikkyo では不要か」を将来のバックポート担当者に伝える価値がある場合。

`PlayerController.ts` に存在した代表的なコメントアウトパターン（現在は理由コメントに変換済み）:
- RomSound（文字スーパー内蔵音）のロード: NX-Jikkyo にはデータ放送機能がないため不要
- mpegts.js バッファ詰まり対策の強制シーク (`live_force_seek`): ライブ視聴で映像ストリーミングがないため不要
- Keep-Alive API リクエスト (`video_keep_alive`): 過去ログ再生にサーバー側ビデオストリーム API がないため不要
