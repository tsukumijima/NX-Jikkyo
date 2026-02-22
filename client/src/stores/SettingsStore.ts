
import { defineStore } from 'pinia';

import { IClientSettings, IMutedCommentKeywords } from '@/services/Settings';


// 選択可能な画質の種類
export type LiveStreamingQuality = '1080p-60fps' | '1080p' | '810p' | '720p' | '540p' | '480p' | '360p' | '240p';
export const LIVE_STREAMING_QUALITIES: LiveStreamingQuality[] = ['1080p'];
export type VideoStreamingQuality = '1080p-60fps' | '1080p' | '810p' | '720p' | '540p' | '480p' | '360p' | '240p';
export const VIDEO_STREAMING_QUALITIES: VideoStreamingQuality[] = ['1080p-60fps', '1080p', '810p', '720p', '540p', '480p', '360p', '240p'];

/**
 * LocalStorage に保存される NX-Jikkyo の設定データ
 * IClientSettings とは異なり、同期対象外の設定キーも含まれる
 */
export interface ILocalClientSettings extends IClientSettings {
    showed_panel_last_time: boolean;
    pinned_channel_ids: string[];
    panel_display_state: 'RestorePreviousState' | 'AlwaysDisplay' | 'AlwaysFold';
    tv_panel_active_tab: 'Program' | 'Channel' | 'Comment';
    video_panel_active_tab: 'RecordedProgram' | 'Comment';
    show_player_background_image: boolean;
    tv_channel_sort_by_jikkyo_force: boolean;
    tv_channel_up_down_buttons_reverse: boolean;
    tv_channel_selection_requires_alt_key: boolean;
    tv_streaming_quality: LiveStreamingQuality;
    tv_streaming_quality_cellular: LiveStreamingQuality;
    tv_data_saver_mode: boolean;
    tv_data_saver_mode_cellular: boolean;
    tv_low_latency_mode: boolean;
    tv_low_latency_mode_cellular: boolean;
    video_streaming_quality: VideoStreamingQuality;
    video_streaming_quality_cellular: VideoStreamingQuality;
    video_data_saver_mode: boolean;
    video_data_saver_mode_cellular: boolean;
    caption_font: string;
    always_border_caption_text: boolean;
    specify_caption_opacity: boolean;
    caption_opacity: number;
    tv_show_superimpose: boolean;
    video_show_superimpose: boolean;
    tv_show_data_broadcasting: boolean;
    enable_internet_access_from_data_broadcasting: boolean;
    capture_save_mode: 'Browser' | 'UploadServer' | 'Both';
    capture_caption_mode: 'VideoOnly' | 'CompositingCaption' | 'Both';
    capture_copy_to_clipboard: boolean;
    prefer_posting_to_nicolive: boolean;
    comment_speed_rate: number;
    comment_font_size: number;
    close_comment_form_after_sending: boolean;
    comment_delay_seconds: number;
    mute_nicolive_comments: boolean;
    mute_nxjikkyo_comments: boolean;
    mute_vulgar_comments: boolean;
    mute_abusive_discriminatory_prejudiced_comments: boolean;
    mute_big_size_comments: boolean;
    mute_fixed_comments: boolean;
    mute_colored_comments: boolean;
    mute_consecutive_same_characters_comments: boolean;
    mute_comment_keywords_normalize_alphanumeric_width_case: boolean;
    muted_comment_keywords: IMutedCommentKeywords[];
    muted_niconico_user_ids: string[];
}

/**
 * LocalStorage に保存される NX-Jikkyo の設定データのデフォルト値
 * IClientSettings とは異なり、同期対象外の設定キーも含まれる
 */
export const ILocalClientSettingsDefault: ILocalClientSettings = {

    // ***** 設定画面から直接変更できない設定値 *****

    // 前回視聴画面を開いた際にパネルが表示されていたかどうか (同期無効)
    showed_panel_last_time: true,
    // ***** 設定 → 全般 *****

    // ピン留めしているチャンネルの ID (ex: gr011) が入るリスト
    pinned_channel_ids: [],
    // デフォルトのパネルの表示状態 (Default: 前回の状態を復元する)
    panel_display_state: 'RestorePreviousState',
    // テレビをみるときにデフォルトで表示されるパネルのタブ (Default: コメントタブ)
    tv_panel_active_tab: 'Comment',
    // ビデオをみるときにデフォルトで表示されるパネルのタブ (Default: コメントタブ)
    video_panel_active_tab: 'Comment',
    // コメントプレイヤーに背景画像を表示する (Default: オン)
    show_player_background_image: true,
    // チャンネル一覧を実況勢いが強い順に並び替える (Default: オフ)
    tv_channel_sort_by_jikkyo_force: false,
    // チャンネル切り替えボタンとショートカットキーの上下方向をテレビリモコン準拠にする (Default: オフ)
    tv_channel_up_down_buttons_reverse: false,
    // チャンネル選局のキーボードショートカットを Alt or Option + 数字キー/テンキーに変更する (Default: オフ)
    tv_channel_selection_requires_alt_key: false,

    // ***** 設定 → 画質 *****

    // テレビのデフォルトのストリーミング画質 (Wi-Fi 回線時) (Default: 1080p) (同期無効)
    tv_streaming_quality: '1080p',
    // テレビのデフォルトのストリーミング画質 (モバイル回線時) (Default: 480p) (同期無効)
    tv_streaming_quality_cellular: '480p',
    // テレビを通信節約モードで視聴する (Wi-Fi 回線時)  (Default: オフ) (同期無効)
    tv_data_saver_mode: false,
    // テレビを通信節約モードで視聴する (モバイル回線時)  (Default: オン) (同期無効)
    tv_data_saver_mode_cellular: true,
    // テレビを低遅延で視聴する (Wi-Fi 回線時)  (Default: 低遅延で視聴する) (同期無効)
    tv_low_latency_mode: true,
    // テレビを低遅延で視聴する (モバイル回線時)  (Default: 低遅延で視聴しない) (同期無効)
    tv_low_latency_mode_cellular: false,

    // ビデオのデフォルトのストリーミング画質 (Wi-Fi 回線時) (Default: 1080p) (同期無効)
    video_streaming_quality: '1080p',
    // ビデオのデフォルトのストリーミング画質 (モバイル回線時) (Default: 480p) (同期無効)
    video_streaming_quality_cellular: '480p',
    // ビデオを通信節約モードで視聴する (Wi-Fi 回線時)  (Default: オフ) (同期無効)
    video_data_saver_mode: false,
    // ビデオを通信節約モードで視聴する (モバイル回線時)  (Default: オン) (同期無効)
    video_data_saver_mode_cellular: true,

    // ***** 設定 → 字幕 *****

    // 字幕のフォント (Default: Windows TV 丸ゴシック)
    caption_font: 'Windows TV MaruGothic',
    // 字幕の文字を常に縁取って描画する (Default: 常に縁取る)
    always_border_caption_text: true,
    // 字幕の不透明度を指定する (Default: 指定しない)
    specify_caption_opacity: false,
    // 字幕の不透明度 (Default: 50%)
    caption_opacity: 0.5,
    // テレビをみるときに文字スーパーを表示する (Default: 表示する)
    tv_show_superimpose: true,
    // ビデオをみるときに文字スーパーを表示する (Default: 表示しない)
    video_show_superimpose: false,

    // ***** 設定 → データ放送 *****

    // テレビをみるときにデータ放送機能を利用する (Default: 表示する) (同期無効)
    tv_show_data_broadcasting: true,

    // データ放送からのインターネットアクセスを有効にする (Default: 無効) (同期無効)
    enable_internet_access_from_data_broadcasting: false,

    // ***** 設定 → キャプチャ *****

    // キャプチャの保存先 (Default: NX-Jikkyo サーバーにアップロード)
    capture_save_mode: 'UploadServer',
    // 字幕が表示されているときのキャプチャの保存モード (Default: 映像のみのキャプチャと、字幕を合成したキャプチャを両方保存する)
    capture_caption_mode: 'Both',
    // キャプチャをクリップボードにコピーする (Default: 無効) (同期無効)
    capture_copy_to_clipboard: false,

    // ***** 設定 → ニコニコ実況 *****

    // 可能であればニコニコ実況にコメントする (Default: オン)
    prefer_posting_to_nicolive: true,
    // コメントの速さ (Default: 1倍)
    comment_speed_rate: 1,
    // コメントのフォントサイズ (Default: 34px)
    comment_font_size: 34,
    // コメント送信後にコメント入力フォームを閉じる (Default: オフ)
    close_comment_form_after_sending: false,
    // コメント表示の遅延秒数 (Default: 0秒)
    comment_delay_seconds: 0,

    // ***** 設定 → ニコニコ実況 (ミュート設定) *****

    // 本家ニコニコ実況に投稿されたコメントをミュートする (Default: ミュートしない)
    mute_nicolive_comments: false,
    // NX-Jikkyo に投稿されたコメントをミュートする (Default: ミュートしない)
    mute_nxjikkyo_comments: false,
    // 露骨な表現を含むコメントをミュートする (Default: ミュートしない)
    mute_vulgar_comments: false,
    // 罵倒や誹謗中傷、差別的な表現、政治的に偏った表現を含むコメントをミュートする (Default: ミュートする)
    mute_abusive_discriminatory_prejudiced_comments: true,
    // 文字サイズが大きいコメントをミュートする (Default: ミュートする)
    mute_big_size_comments: true,
    // 映像の上下に固定表示されるコメントをミュートする (Default: ミュートしない)
    mute_fixed_comments: false,
    // 色付きのコメントをミュートする (Default: ミュートしない)
    mute_colored_comments: false,
    // 8文字以上同じ文字が連続しているコメントをミュートする (Default: ミュートしない)
    mute_consecutive_same_characters_comments: false,
    // ミュート対象キーワード内の英数字・記号を、大文字小文字や全角半角の違いを無視して判定する (Default: オン)
    mute_comment_keywords_normalize_alphanumeric_width_case: true,
    // ミュート済みのコメントのキーワードが入るリスト
    muted_comment_keywords: [],
    // ミュート済みのニコニコユーザー ID が入るリスト
    muted_niconico_user_ids: [],
};

/**
 * LocalStorage の NX-Jikkyo-Settings キーから生の設定データを取得する
 * 返されるデータはノーマライズされていない生データで、最新であるかや ILocalClientSettings と一致するかは保証されない
 * @returns 生の設定データ
 */
export function getLocalStorageSettings(): {[key: string]: any} {
    const settings = localStorage.getItem('NX-Jikkyo-Settings');
    if (settings !== null) {
        return JSON.parse(settings);
    } else {
        // もし LocalStorage に NX-Jikkyo-Settings キーがまだない場合、あらかじめデフォルトの設定値を保存しておく
        const default_settings = structuredClone(ILocalClientSettingsDefault);
        setLocalStorageSettings(default_settings);
        return default_settings;
    }
}

/**
 * LocalStorage の NX-Jikkyo-Settings キーに設定データを JSON にシリアライズして保存する
 * @param settings 設定データ
 */
export function setLocalStorageSettings(settings: ILocalClientSettings): void {
    localStorage.setItem('NX-Jikkyo-Settings', JSON.stringify(settings));
}

/**
 * 与えられた生の設定データにソート・足りない設定キーの補完・不要な設定キーの削除を行って返す
 * @param settings 生の設定データ
 * @returns ノーマライズされた設定データ (LocalClientSettings と厳密に一致する)
 */
export function getNormalizedLocalClientSettings(settings: {[key: string]: any}): ILocalClientSettings {

    // (名前が変わった、廃止されたなどの理由で) 現在の ILocalClientSettingsDefault に存在しない設定キーを排除した上でソート
    // ソートされていないと設定データの比較がうまくいかない
    const normalized_settings: Partial<ILocalClientSettings> = {};
    for (const default_settings_key of Object.keys(ILocalClientSettingsDefault)) {
        if (default_settings_key in settings) {
            normalized_settings[default_settings_key] = settings[default_settings_key];
        } else {
            // 後のバージョンで追加されたなどの理由で現状の NX-Jikkyo-Settings に存在しない設定キーの場合
            // その設定キーのデフォルト値をディープコピーして取得する
            // (配列などの参照型を直接代入すると ILocalClientSettingsDefault が汚染される恐れがあるため)
            normalized_settings[default_settings_key] = structuredClone(ILocalClientSettingsDefault[default_settings_key]);
        }
    }

    return normalized_settings as ILocalClientSettings;
}

/**
 * 設定データを共有するストア
 */
const useSettingsStore = defineStore('settings', {
    state: () => {

        // ref: https://www.vuemastery.com/blog/refresh-proof-your-pinia-stores/

        // LocalStorage から生の設定データを取得する
        const settings = getLocalStorageSettings();

        // 生の設定データに対してソート・足りない設定キーの補完・不要な設定キーの削除を行う
        const normalized_settings = getNormalizedLocalClientSettings(settings);

        // この状態の新しい設定データを LocalStorage に保存する
        setLocalStorageSettings(normalized_settings);

        // 設定データを Store の state のデフォルト値として返す
        return {
            settings: normalized_settings,
        };
    },
    actions: {

        /**
         * エクスポートした JSON ファイルから設定データをインポートする (既存の設定はすべて上書きされる)
         * @param file エクスポートした JSON ファイル
         * @returns インポートに成功したかどうか
         */
        async importClientSettings(file: File): Promise<boolean> {

            // JSON ファイルを読み込む
            const settings_json = await file.text();

            // JSON ファイルをパースする
            let settings = {};
            try {
                settings = JSON.parse(settings_json);
            } catch (error) {
                return false;
            }

            // 生の設定データに対してソート・足りない設定キーの補完・不要な設定キーの削除を行う
            const normalized_settings = getNormalizedLocalClientSettings(settings);

            // この状態の新しい設定データを LocalStorage に保存し、Store の state に反映する
            // このとき、既存の設定データはすべて上書きされる
            setLocalStorageSettings(normalized_settings);
            this.settings = normalized_settings;

            return true;
        },

        /**
         * 設定データを初期状態にリセットする
         */
        async resetClientSettings(): Promise<void> {
            // デフォルト値の設定データを LocalStorage に保存し、Store の state に反映する
            const default_settings = structuredClone(ILocalClientSettingsDefault);
            setLocalStorageSettings(default_settings);
            this.settings = default_settings;
        }
    }
});

export default useSettingsStore;
