
/**
 * ミュート対象のコメントのキーワードのインターフェイス
 */
export interface IMutedCommentKeywords {
    match: 'partial' | 'forward' | 'backward' | 'exact' | 'regex';
    pattern: string;
}

/**
 * KonomiTV のサーバーに保存されるクライアント設定を表すインターフェース（KonomiTV との互換性維持のため残存）
 * NX-Jikkyo にはサーバー同期機能がなく、すべての設定は LocalStorage のみに保存される (ILocalClientSettings 参照)
 * KonomiTV ではこのインターフェイスの全フィールドがサーバーと同期される
 * KonomiTV の ILocalClientSettings は IClientSettings を extends しており、NX-Jikkyo もその構成を維持している
 * このインターフェイスに含まれないフィールド (画質・データ放送など) は ILocalClientSettings に直接定義する
 */
export interface IClientSettings {
    pinned_channel_ids: string[];
    panel_display_state: 'RestorePreviousState' | 'AlwaysDisplay' | 'AlwaysFold';
    tv_panel_active_tab: 'Program' | 'Channel' | 'Comment';
    video_panel_active_tab: 'RecordedProgram' | 'Comment';
    show_player_background_image: boolean;
    use_pure_black_player_background: boolean;
    tv_channel_sort_by_jikkyo_force: boolean;
    tv_channel_up_down_buttons_reverse: boolean;
    tv_channel_selection_requires_alt_key: boolean;
    caption_font: string;
    always_border_caption_text: boolean;
    specify_caption_opacity: boolean;
    caption_opacity: number;
    tv_show_superimpose: boolean;
    video_show_superimpose: boolean;
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
