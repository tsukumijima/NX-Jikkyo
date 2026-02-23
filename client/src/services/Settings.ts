
/**
 * ミュート対象のコメントのキーワードのインターフェイス
 */
export interface IMutedCommentKeywords {
    match: 'partial' | 'forward' | 'backward' | 'exact' | 'regex';
    pattern: string;
}

/**
 * サーバーに保存されるクライアント設定を表すインターフェース
 * サーバー側の app.config.ClientSettings で定義されているものと同じ
 */
export interface IClientSettings {
    // showed_panel_last_time: 同期無効
    pinned_channel_ids: string[];
    panel_display_state: 'RestorePreviousState' | 'AlwaysDisplay' | 'AlwaysFold';
    tv_panel_active_tab: 'Program' | 'Channel' | 'Comment';
    video_panel_active_tab: 'RecordedProgram' | 'Comment';
    show_player_background_image: boolean;
    tv_channel_sort_by_jikkyo_force: boolean;
    tv_channel_up_down_buttons_reverse: boolean;
    tv_channel_selection_requires_alt_key: boolean;
    // tv_streaming_quality: 同期無効
    // tv_streaming_quality_cellular: 同期無効
    // tv_data_saver_mode: 同期無効
    // tv_data_saver_mode_cellular: 同期無効
    // tv_low_latency_mode: 同期無効
    // tv_low_latency_mode_cellular: 同期無効
    // video_streaming_quality: 同期無効
    // video_streaming_quality_cellular: 同期無効
    // video_data_saver_mode: 同期無効
    // video_data_saver_mode_cellular: 同期無効
    caption_font: string;
    always_border_caption_text: boolean;
    specify_caption_opacity: boolean;
    caption_opacity: number;
    tv_show_superimpose: boolean;
    video_show_superimpose: boolean;
    // tv_show_data_broadcasting: 同期無効
    // enable_internet_access_from_data_broadcasting: 同期無効
    capture_save_mode: 'Browser' | 'UploadServer' | 'Both';
    capture_caption_mode: 'VideoOnly' | 'CompositingCaption' | 'Both';
    // capture_copy_to_clipboard: 同期無効
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
