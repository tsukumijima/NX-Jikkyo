

import DPlayer from 'dplayer';
import { watch } from 'vue';

import router from '@/router';
import PlayerManager from '@/services/player/PlayerManager';
import useChannelsStore from '@/stores/ChannelsStore';
import usePlayerStore from '@/stores/PlayerStore';
import useSettingsStore from '@/stores/SettingsStore';
import Utils from '@/utils';


/**
 * キーボードショートカットの定義
 * 一部の特殊なキーコンビネーションは表現しきれないため、キーボードイベント発生時の条件分岐で直接実装している
 */
interface ShortcutDefinition {
    // 適用対象の再生モード (Live: ライブ視聴のみ, Video: ビデオ視聴のみ, Both: 両方に適用)
    mode: 'Live' | 'Video' | 'Both';
    // トリガー対象のキー (KeyboardEvent.code)
    key: string;
    // キーリピートを許可するかどうか
    repeat: boolean;
    // Ctrl キーの同時押しが必要かどうか
    // Mac では Ctrl キーではなく Cmd キーで判定される
    ctrl: boolean;
    // Shift キーの同時押しが必要かどうか
    shift: boolean;
    // Alt キーの同時押しが必要かどうか
    // Mac では Alt キーではなく Option キーで判定される
    alt: boolean;
    // キーが押されたときに実行する関数
    handler: () => void;
}


/**
 * 視聴画面全体のキーボードショートカットイベントを管理する PlayerManager
 */
class KeyboardShortcutManager implements PlayerManager {

    // ユーザー操作により DPlayer 側で画質が切り替わった際、この PlayerManager の再起動が必要かどうかを PlayerController に示す値
    public readonly restart_required_when_quality_switched = false;

    // DPlayer のインスタンス
    // 設計上コンストラクタ以降で変更すべきでないため readonly にしている
    private readonly player: DPlayer;

    // 再生モード (Live: ライブ視聴, Video: ビデオ視聴)
    private readonly playback_mode: 'Live' | 'Video';

    // キーボードショートカットをバインドする Document オブジェクト
    private readonly document: Document;

    // キーボードショートカットイベントをキャンセルする AbortController
    private abort_controller: AbortController | null = null;

    /**
     * コンストラクタ
     * @param player DPlayer のインスタンス
     * @param playback_mode 再生モード (Live: ライブ視聴, Video: ビデオ視聴)
     * @param document キーボードショートカットをバインドする Document オブジェクト
     */
    constructor(player: DPlayer, playback_mode: 'Live' | 'Video', document: Document = window.document) {
        this.player = player;
        this.playback_mode = playback_mode;
        this.document = document;
    }


    /**
     * キーボードショートカットイベントをブラウザに登録する
     */
    public async init(): Promise<void> {
        const channels_store = useChannelsStore();
        const player_store = usePlayerStore();
        const settings_store = useSettingsStore();

        // キーボードショートカットイベントをキャンセルする AbortController を生成
        this.abort_controller = new AbortController();

        // 視聴画面のルート要素を取得
        const route_container_element = document.querySelector<HTMLDivElement>('.route-container')!;

        // キャプチャボタンの HTML 要素を取得
        // KeyboardShortcutManager より先に CaptureManager が初期化されていることが前提
        const capture_button_element = this.player.container.querySelector<HTMLDivElement>('.dplayer-capture-icon')!;
        const comment_capture_button_element = this.player.container.querySelector<HTMLDivElement>('.dplayer-comment-capture-icon')!;

        // ツイート送信フォーム / ツイート送信ボタンの HTML 要素を取得
        // Twitter パネルコンポーネントが視聴画面に追加されていることが前提
        const tweet_form_element = document.querySelector<HTMLDivElement>('.tweet-form__textarea')!;
        const tweet_button_element = document.querySelector<HTMLButtonElement>('.tweet-button')!;

        // データ放送リモコンの各ボタンの HTML 要素を取得
        // データ放送リモコンコンポーネントが視聴画面に追加されていることが前提
        // ビデオ視聴時はデータ放送リモコンコンポーネントが表示されないためすべて null になる
        const remocon_data_button = document.querySelector<HTMLDivElement>('.remote-control-button-data');
        const remocon_back_button = document.querySelector<HTMLDivElement>('.remote-control-button-back');
        const remocon_select_button = document.querySelector<HTMLDivElement>('.remote-control-button-select');
        const remocon_up_button = document.querySelector<HTMLDivElement>('.remote-control-button-up');
        const remocon_left_button = document.querySelector<HTMLDivElement>('.remote-control-button-left');
        const remocon_right_button = document.querySelector<HTMLDivElement>('.remote-control-button-right');
        const remocon_down_button = document.querySelector<HTMLDivElement>('.remote-control-button-down');
        const remocon_blue_button = document.querySelector<HTMLDivElement>('.remote-control-button-blue');
        const remocon_red_button = document.querySelector<HTMLDivElement>('.remote-control-button-red');
        const remocon_green_button = document.querySelector<HTMLDivElement>('.remote-control-button-green');
        const remocon_yellow_button = document.querySelector<HTMLDivElement>('.remote-control-button-yellow');

        // 一般的なキーボードショートカットの定義
        // 一部の特殊なキーコンビネーションは表現しきれないため、キーボードイベント発生時の条件分岐で直接実装している
        const shortcuts: ShortcutDefinition[] = [

            // ***** 全般 *****

            // ↑: ライブ視聴: 前のチャンネルに切り替える
            {mode: 'Live', key: 'ArrowUp', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                player_store.is_zapping = true;  // ザッピング状態にする
                router.push({path: `/tv/watch/${channels_store.channel.previous.display_channel_id}`});
            }},

            // ↓: ライブ視聴: 次のチャンネルに切り替える
            {mode: 'Live', key: 'ArrowDown', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                player_store.is_zapping = true;  // ザッピング状態にする
                router.push({path: `/tv/watch/${channels_store.channel.next.display_channel_id}`});
            }},

            // /(？): キーボードショートカットの一覧を表示する
            {mode: 'Both', key: 'Slash', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                player_store.shortcut_key_modal = !player_store.shortcut_key_modal;  // 表示状態を反転
            }},

            // ***** プレイヤー *****

            // Space: 再生 / 一時停止の切り替え
            {mode: 'Both', key: 'Space', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                this.player.toggle();
            }},

            // F: フルスクリーンの切り替え
            {mode: 'Both', key: 'KeyF', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                this.player.fullScreen.toggle();
            }},

            // E: Picture-in-Picture の表示切り替え
            {mode: 'Both', key: 'KeyE', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                if (document.pictureInPictureEnabled) {
                    this.player.template.pipButton.click();
                }
            }},

            // D: コメントの表示切り替え
            {mode: 'Both', key: 'KeyD', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                this.player.template.showDanmaku.click();
                if (this.player.template.showDanmakuToggle.checked) {
                    this.player.notice(`${this.player.tran('Show comment')}`);
                } else {
                    this.player.notice(`${this.player.tran('Hide comment')}`);
                }
            }},

            // M: ライブ視聴: コメント入力フォームにフォーカスする
            // ビデオ視聴ではコメント送信自体ができないため有効化しない
            {mode: 'Live', key: 'KeyM', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                this.player.controller.show();
                this.player.comment!.show();
                player_store.event_emitter.emit('SetControlDisplayTimer', {});
                window.setTimeout(() => this.player.template.commentInput.focus(), 100);
            }},

            // ***** パネル *****

            // P: パネルの表示切り替え
            {mode: 'Both', key: 'KeyP', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                player_store.is_panel_display = !player_store.is_panel_display;  // 表示状態を反転
            }},

            // K: ライブ視聴: 番組情報タブを表示する
            {mode: 'Live', key: 'KeyK', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                player_store.tv_panel_active_tab = 'Program';
            }},

            // L: ライブ視聴: チャンネルタブを表示する
            {mode: 'Live', key: 'KeyL', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                player_store.tv_panel_active_tab = 'Channel';
            }},

            // ;(＋): コメントタブを表示する
            {mode: 'Both', key: 'Semicolon', repeat: false, ctrl: false, shift: false, alt: false, handler: () => {
                if (this.playback_mode === 'Live') {
                    player_store.tv_panel_active_tab = 'Comment';
                } else {
                    player_store.video_panel_active_tab = 'Comment';
                }
            }},
        ];

        // ドキュメント全体のキーボードショートカットイベント
        // this.document に対してイベントを登録することで、メインウインドウ配下以外の Document にも対応できる
        let last_key_pressed_at = 0;  // 最終押下時刻
        this.document.addEventListener('keydown', (event: KeyboardEvent) => {

            // 日本語 IME による入力中は無視
            // event.keyCode === 229 は日本語 IME 変換確定時に発火するらしい (謎のテクニック)
            if (event.isComposing === true || event.keyCode === 229) {
                return;
            }

            // キーリピート (押しっぱなし) 状態かを検知
            let is_repeat = false;
            if (event.repeat) {
                is_repeat = true;
            }
            // キーリピート状態は event.repeat を見る事でだいたい検知できるが、最初の何回かは検知できないこともある
            // そこで、0.05 秒以内に連続して発火したキーイベントをキーリピートとみなす
            const now = Utils.time();
            if (now - last_key_pressed_at < 0.05) {
                is_repeat = true;
            }
            last_key_pressed_at = now;  // 最終押下時刻を更新

            // Ctrl or Cmd (Mac) キーが押されているかどうか
            // Mac では Ctrl キーではなく Cmd キーで判定される
            const is_ctrl_or_cmd_pressed = (Utils.isMacOS() === true ? event.metaKey : event.ctrlKey);
            // Shift キーが押されているかどうか
            const is_shift_pressed = event.shiftKey;
            // Alt or Option キーが押されているかどうか
            // Mac では Alt キーではなく Option キーで判定される
            const is_alt_pressed = event.altKey;

            // 現在パネル上でアクティブなタブ
            const panel_active_tab = this.playback_mode === 'Live' ? player_store.tv_panel_active_tab : player_store.video_panel_active_tab;

            // 現在フォーム (input or textarea) にフォーカスがあるかどうか
            const is_form_focused = (document.activeElement instanceof HTMLInputElement ||
                                     document.activeElement instanceof HTMLTextAreaElement);

            // ***** 特殊な処理を行うキーボードショートカットの処理 *****

            // 1~9, 0, -(=), ^(~): (ライブ視聴のみ) 押されたキーに対応するチャンネルに切り替える
            // チャンネル選局のキーボードショートカットを Alt or Option + 数字キー/テンキーに変更する設定が有効なときは、
            // Alt or Option キーが押されていることを条件に追加する
            // フォーカスが input or textarea にあるときは誤動作防止のため無効化
            if ((this.playback_mode === 'Live') &&
                (is_repeat === false) &&
                (is_ctrl_or_cmd_pressed === false) &&
                (is_alt_pressed === (settings_store.settings.tv_channel_selection_requires_alt_key === true)) &&
                (is_form_focused === false)) {

                // ***** 数字キーでチャンネルを切り替える *****

                // Shift キーが同時押しされていたら BS チャンネルの方を選局する
                const switch_channel_type = is_shift_pressed ? 'BS' : 'GR';

                // 切り替えるチャンネルのリモコン ID
                // リモコン ID に当てはまるキーが押下していなければ null のままになる
                let switch_remocon_id: number | null = null;

                // 1～9キー
                if (['Digit1', 'Digit2', 'Digit3', 'Digit4', 'Digit5', 'Digit6', 'Digit7', 'Digit8', 'Digit9'].includes(event.code)) {
                    switch_remocon_id = Number(event.code.replace('Digit', ''));
                }
                // 0キー: 10に割り当て
                if (event.code === 'Digit0') switch_remocon_id = 10;
                // -キー: 11に割り当て
                if (event.code === 'Minus') switch_remocon_id = 11;
                // ^キー: 12に割り当て
                if (event.code === 'Equal') switch_remocon_id = 12;
                // 1～9キー (テンキー)
                if (['Numpad1', 'Numpad2', 'Numpad3', 'Numpad4', 'Numpad5', 'Numpad6', 'Numpad7', 'Numpad8', 'Numpad9'].includes(event.code)) {
                    switch_remocon_id = Number(event.code.replace('Numpad', ''));
                }
                // 0キー (テンキー): 10に割り当て
                if (event.code === 'Numpad0') switch_remocon_id = 10;

                // この時点でリモコン ID が取得できている場合のみ実行
                if (switch_remocon_id !== null) {

                    // 切り替え先のチャンネルを取得する
                    const switch_channel = channels_store.getChannelByRemoconID(switch_channel_type, switch_remocon_id);

                    // チャンネルが取得できていれば、ルーティングをそのチャンネルに置き換える
                    // 押されたキーに対応するリモコン ID のチャンネルがない場合や、現在と同じチャンネル ID の場合は何も起こらない
                    if (switch_channel !== null && switch_channel.display_channel_id !== channels_store.display_channel_id) {
                        router.push({path: `/tv/watch/${switch_channel.display_channel_id}`});

                        // 既定のキーボードショートカットイベントをキャンセルして終了
                        event.preventDefault();
                        event.stopPropagation();
                        return;
                    }
                }
            }

            // Ctrl + M: (ライブ視聴のみ) コメント入力フォームを閉じる
            // コメント入力フォームが表示されているときのみ有効
            // コメント入力フォームにフォーカスが当たっている場合も実行する
            if ((this.playback_mode === 'Live') &&
                (event.code === 'KeyM') &&
                (is_repeat === false) &&
                (is_ctrl_or_cmd_pressed === true) &&
                (is_shift_pressed === false) &&
                (is_alt_pressed === false) &&
                (this.player.template.controller.classList.contains('dplayer-controller-comment')) &&
                (is_form_focused === false || document.activeElement === this.player.template.commentInput)) {

                // コメント入力フォームを閉じる
                this.player.comment!.hide();

                // 既定のキーボードショートカットイベントをキャンセルして終了
                event.preventDefault();
                event.stopPropagation();
                return;
            }

            // ***** 一般的なキーボードショートカットの処理 *****

            // フォーカスが input or textarea にあるとき、上記以外のキーボードショートカットを無効化
            if (is_form_focused === true) {
                return;
            }

            // キーボードショートカットの定義を走査して、該当するものがあれば実行
            for (const shortcut of shortcuts) {

                // 適用対象の再生モード が Both ではなく、初期化時の再生モードと一致しない
                if (shortcut.mode !== 'Both' && shortcut.mode !== this.playback_mode) {
                    continue;
                }
                // キーが一致しない
                if (shortcut.key !== event.code) {
                    continue;
                }
                // キーリピートを許可しない設定のショートカットで、キーリピート状態である
                // キーリピートを許可する設定のショートカットでは、キーリピート状態かに関わらず実行する
                if (shortcut.repeat === false && is_repeat === true) {
                    continue;
                }
                // Ctrl or Cmd (Mac) キーの同時押しが必要かどうかが一致しない
                if (shortcut.ctrl !== is_ctrl_or_cmd_pressed) {
                    continue;
                }
                // Shift キーの同時押しが必要かどうかが一致しない
                if (shortcut.shift !== is_shift_pressed) {
                    continue;
                }
                // Alt or Option キーの同時押しが必要かどうかが一致しない
                if (shortcut.alt !== is_alt_pressed) {
                    continue;
                }

                // キーボードショートカットの実行
                shortcut.handler();

                // 既定のキーボードショートカットイベントをキャンセル
                event.preventDefault();
                event.stopPropagation();

                // 実行条件に一致しキーボードショートカットを実行し終えた時点で、即座にループを抜けて終了する
                return;
            }

        }, { signal: this.abort_controller.signal });

        console.log('[KeyboardShortcutManager] Initialized.');
    }


    /**
     * キーボードショートカットイベントをブラウザから削除する
     */
    public async destroy(): Promise<void> {
        const player_store = usePlayerStore();

        // ライブ視聴: ザッピング中のみ、ザッピングが終わるだけ待ってから非同期でキーボードショートカットイベントをキャンセルする
        // 即座にキーボードショートカットイベントをキャンセルしてしまうと、ザッピングが終わるまでキーボードショートカットが効かなくなってしまう
        if (this.playback_mode === 'Live' && player_store.is_zapping === true) {

            // PlayerController が初期化されているかの状態が変更されたときに実行するイベントを設定
            // false から true に変わったときにザッピングが終わったとみなす
            const unwatch_zapping = watch(() => player_store.is_player_initialized, (new_value, old_value) => {
                if (old_value === false && new_value === true) {
                    // 設定したウォッチャーを両方削除
                    unwatch_zapping();
                    unwatch_watching();
                    // キーボードショートカットイベントをキャンセル
                    if (this.abort_controller !== null) {
                        this.abort_controller.abort();
                        this.abort_controller = null;
                    }
                    console.log('[KeyboardShortcutManager] Destroyed. (Zapping finished)');
                }
            });

            // ザッピング中に視聴画面を離れたときに実行するイベントを設定
            // 設定しておかないと視聴画面を離れてもキーボードショートカットイベントがキャンセルされない
            // true から false に変わったときにザッピングがキャンセルされたとみなす
            const unwatch_watching = watch(() => player_store.is_watching, (new_value, old_value) => {
                if (old_value === true && new_value === false) {
                    // 設定したウォッチャーを両方削除
                    unwatch_zapping();
                    unwatch_watching();
                    // キーボードショートカットイベントをキャンセル
                    if (this.abort_controller !== null) {
                        this.abort_controller.abort();
                        this.abort_controller = null;
                    }
                    console.log('[KeyboardShortcutManager] Destroyed. (Zapping canceled)');
                }
            });

        // ザッピング中でなければ、即座にキーボードショートカットイベントをキャンセル
        } else {
            if (this.abort_controller !== null) {
                this.abort_controller.abort();
                this.abort_controller = null;
            }
            console.log('[KeyboardShortcutManager] Destroyed.');
        }
    }
}

export default KeyboardShortcutManager;
