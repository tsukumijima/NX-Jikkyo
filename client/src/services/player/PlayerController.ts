
import assert from 'assert';

import DPlayer, { DPlayerType } from 'dplayer';
import Hls from 'hls.js';
import mpegts from 'mpegts.js';


import APIClient from '@/services/APIClient';
import DocumentPiPManager from '@/services/player/managers/DocumentPiPManager';
import KeyboardShortcutManager from '@/services/player/managers/KeyboardShortcutManager';
import LiveCommentManager from '@/services/player/managers/LiveCommentManager';
import PlayerManager from '@/services/player/PlayerManager';
import Videos from '@/services/Videos';
import useChannelsStore from '@/stores/ChannelsStore';
import usePlayerStore from '@/stores/PlayerStore';
import useSettingsStore, { LiveStreamingQuality, LIVE_STREAMING_QUALITIES, VideoStreamingQuality } from '@/stores/SettingsStore';
import Utils, { dayjs, PlayerUtils } from '@/utils';


/**
 * 動画プレイヤーである DPlayer に関連するロジックを丸ごとラップするクラスで、再生系ロジックの中核を担う
 * DPlayer の初期化後は DPlayer が発行するイベントなどに合わせ、各イベントハンドラーや PlayerManager を管理する
 *
 * このクラスはコンストラクタで指定されたチャンネル or 録画番組の再生に責任を持つ
 * await destroy() 後に再度 await init() すると、コンストラクタに渡したのと同じチャンネル or 録画番組のプレイヤーを再起動できる
 * 再生対象が他のチャンネル or 録画番組に切り替えられた際は、既存の PlayerController を破棄し、新たに PlayerController を作り直す必要がある
 * 実装上、このクラスのインスタンスは必ずアプリケーション上で1つだけ存在するように実装する必要がある
 */
class PlayerController {

    // ライブ視聴: 低遅延モードオンでの再生バッファ (秒単位)
    // 0.8 秒程度余裕を持たせる
    private static readonly LIVE_PLAYBACK_BUFFER_SECONDS_LOW_LATENCY = 0.8;

    // ライブ視聴: 低遅延モードオフでの再生バッファ (秒単位)
    // 4 秒程度の遅延を許容する
    private static readonly LIVE_PLAYBACK_BUFFER_SECONDS = 4.0;

    // DPlayer のインスタンス
    private player: DPlayer | null = null;

    // それぞれの PlayerManager のインスタンスのリスト
    private player_managers: PlayerManager[] = [];

    // 再生モード (Live: ライブ視聴, Video: ビデオ視聴)
    private readonly playback_mode: 'Live' | 'Video';

    // ライブ視聴: 画質プロファイル
    private readonly tv_streaming_quality: LiveStreamingQuality;
    private readonly tv_data_saver_mode: boolean;
    private readonly tv_low_latency_mode: boolean;

    // ビデオ視聴: 画質プロファイル
    private readonly video_streaming_quality: VideoStreamingQuality;
    private readonly video_data_saver_mode: boolean;

    // ライブ視聴: 許容する HTMLMediaElement の内部再生バッファの秒数
    // 設計上コンストラクタ以降で変更すべきでないため readonly にしている
    private readonly live_playback_buffer_seconds: number;

    // ライブ視聴: mpegts.js のバッファ詰まり対策で定期的に強制シークするインターバルをキャンセルする関数
    private live_force_seek_interval_timer_cancel: (() => void) | null = null;

    // ビデオ視聴: ビデオストリームのアクティブ状態を維持するために Keep-Alive API にリクエストを送るインターバルのキャンセルする関数
    private video_keep_alive_interval_timer_cancel: (() => void) | null = null;

    // setupPlayerContainerResizeHandler() で利用する ResizeObserver
    // 保持しておかないと disconnect() で ResizeObserver を止められない
    private player_container_resize_observer: ResizeObserver | null = null;

    // setControlDisplayTimer() で利用するタイマー ID
    // 保持しておかないと clearTimeout() でタイマーを止められない
    private player_control_ui_hide_timer_id: number = 0;

    // Screen Wake Lock API の WakeLockSentinel のインスタンス
    // 確保した起動ロックを解放するために保持しておく必要がある
    // Screen Wake Lock API がサポートされていない場合やリクエストに失敗した場合は null になる
    private screen_wake_lock: WakeLockSentinel | null = null;

    // RomSound の AudioContext と AudioBuffer のリスト
    private readonly romsounds_context: AudioContext = new AudioContext();
    private readonly romsounds_buffers: AudioBuffer[] = [];

    // 破棄中かどうか
    // 破棄中は destroy() が呼ばれても何もしない
    private destroying = false;

    // 破棄済みかどうか
    private destroyed = false;


    /**
     * コンストラクタ
     * 実際の DPlayer の初期化処理は await init() で行われる
     */
    constructor(playback_mode: 'Live' | 'Video') {

        // 再生モードをセット
        this.playback_mode = playback_mode;

        // ネットワーク回線が Cellular (モバイル回線) であれば、モバイル回線用の画質プロファイルを適用する
        // Wi-Fi or 取得できなかった場合は、通常の画質プロファイルを適用する
        const settings_store = useSettingsStore();
        const network_circuit_type = PlayerUtils.getNetworkCircuitType();
        // ライブ視聴の画質プロファイル
        this.tv_streaming_quality = network_circuit_type === 'Cellular' ?
            settings_store.settings.tv_streaming_quality_cellular : settings_store.settings.tv_streaming_quality;
        this.tv_data_saver_mode = network_circuit_type === 'Cellular' ?
            settings_store.settings.tv_data_saver_mode_cellular : settings_store.settings.tv_data_saver_mode;
        this.tv_low_latency_mode = network_circuit_type === 'Cellular' ?
            settings_store.settings.tv_low_latency_mode_cellular : settings_store.settings.tv_low_latency_mode;
        // ビデオ視聴の画質プロファイル
        this.video_streaming_quality = network_circuit_type === 'Cellular' ?
            settings_store.settings.video_streaming_quality_cellular : settings_store.settings.video_streaming_quality;
        this.video_data_saver_mode = network_circuit_type === 'Cellular' ?
            settings_store.settings.video_data_saver_mode_cellular : settings_store.settings.video_data_saver_mode;

        // 低遅延モードであれば低遅延向けの再生バッファを、そうでなければ通常の再生バッファをセット (秒単位)
        this.live_playback_buffer_seconds = this.tv_low_latency_mode ?
            PlayerController.LIVE_PLAYBACK_BUFFER_SECONDS_LOW_LATENCY : PlayerController.LIVE_PLAYBACK_BUFFER_SECONDS;

        // Safari の Media Source Extensions API の実装はどうもバッファの揺らぎが大きい (?) ようなので、バッファ詰まり対策で
        // さらに 0.3 秒程度余裕を持たせる
        if (Utils.isSafari() === true) {
            this.live_playback_buffer_seconds += 0.3;
        }

        // 01 ~ 14 まですべての RomSound を読み込む
        // (async () => {
        //     for (let index = 1; index <= 14; index++) {
        //         // ArrayBuffer をデコードして AudioBuffer にし、すぐ呼び出せるように貯めておく
        //         // ref: https://ics.media/entry/200427/
        //         const romsound_url = `/assets/romsounds/${index.toString().padStart(2, '0')}.wav`;
        //         const romsound_response = await APIClient.get<ArrayBuffer>(romsound_url, {
        //             baseURL: '',  // BaseURL を明示的にクライアントのルートに設定
        //             responseType: 'arraybuffer',
        //         });
        //         if (romsound_response.type === 'success') {
        //             this.romsounds_buffers.push(await this.romsounds_context.decodeAudioData(romsound_response.data));
        //         }
        //     }
        // })();
    }


    /**
     * DPlayer と PlayerManager を初期化し、再生準備を行う
     */
    public async init(): Promise<void> {
        const channels_store = useChannelsStore();
        const player_store = usePlayerStore();
        const settings_store = useSettingsStore();
        console.log('\u001b[31m[PlayerController] Initializing...');

        // 破棄済みかどうかのフラグを下ろす
        this.destroyed = false;

        // PlayerStore にプレイヤーを初期化したことを通知する
        // 実際にはこの時点ではプレイヤーの初期化は完了していないが、PlayerController.init() を実行したことが通知されることが重要
        // ライブ視聴かつザッピングを経てチャンネルが確定した場合、破棄を遅らせていた以前の PlayerController に紐づく
        // KeyboardShortcutManager がこのタイミングで破棄される
        player_store.is_player_initialized = true;

        // mpegts.js と hls.js を window 直下に入れる
        // こうしないと DPlayer が mpegts.js / hls.js を認識できない
        (window as any).mpegts = mpegts;
        (window as any).Hls = Hls;

        // 文字スーパーの表示設定
        // ライブ視聴とビデオ視聴で設定キーが異なる
        const is_show_superimpose = this.playback_mode === 'Live' ?
            settings_store.settings.tv_show_superimpose : settings_store.settings.video_show_superimpose;

        // この時点で LocalStorage に dplayer-danmaku-opacity キーが存在しなければ、コメントの透明度の既定値を設定する
        // NX-Jikkyo ではコメントのみを流すため 1.0 とする
        if (localStorage.getItem('dplayer-danmaku-opacity') === null) {
            localStorage.setItem('dplayer-danmaku-opacity', '1.0');
        }

        // 無音の音声ファイルを生成
        let audio_url = '';
        if (player_store.recorded_program.id == -100) {
            // データ量を削減するためにできるだけサンプルレートを抑えるのが重要
            // 3000Hz が Web Audio API の限界
            audio_url = this.createSilentAudioBuffer(player_store.recorded_program.duration, 3000, 1);
            console.log('\u001b[31m[PlayerController] audio_url:', audio_url);
        }

        // DPlayer を初期化
        this.player = new DPlayer({
            // DPlayer を配置する要素
            container: document.querySelector<HTMLDivElement>('.watch-player__dplayer')!,
            // テーマカラー
            theme: '#E64F97',
            // 言語 (日本語固定)
            lang: 'ja-jp',
            // ライブモード (ビデオ視聴では無効)
            live: this.playback_mode === 'Live' ? true : false,
            // ライブモードで同期する際の最小バッファサイズ
            liveSyncMinBufferSize: this.live_playback_buffer_seconds - 0.1,
            // ループ再生 (ライブ視聴では無効)
            loop: this.playback_mode === 'Live' ? false : false,
            // 自動再生
            autoplay: true,
            // AirPlay 機能 (うまく動かないため無効化)
            airplay: false,
            // ショートカットキー（こちらで制御するため無効化）
            hotkey: false,
            // スクリーンショット (こちらで制御するため無効化)
            screenshot: false,
            // CORS を有効化
            crossOrigin: 'anonymous',
            // 音量の初期値
            volume: 1.0,

            // 動画の設定
            video: (() => {

                // 画質リスト
                const qualities: DPlayerType.VideoQuality[] = [];

                // ブラウザが H.265 / HEVC の再生に対応していて、かつ通信節約モードが有効なとき
                // API に渡す画質に -hevc のプレフィックスをつける
                let hevc_prefix = '';
                if (PlayerUtils.isHEVCVideoSupported() &&
                    ((this.playback_mode === 'Live' && this.tv_data_saver_mode === true) ||
                     (this.playback_mode === 'Video' && this.video_data_saver_mode === true))) {
                    hevc_prefix = '-hevc';
                }

                // ライブ視聴: チャンネル情報がセットされているはず
                if (this.playback_mode === 'Live') {

                    // ライブストリーミング API のベース URL
                    const streaming_api_base_url = `${Utils.api_base_url}/streams/live/${channels_store.channel.current.display_channel_id}`;

                    // ラジオチャンネルの場合
                    // API が受け付ける画質の値は通常のチャンネルと同じだが (手抜き…)、実際の画質は 48KHz/192kbps で固定される
                    // ラジオチャンネルの場合は、1080p と渡しても 48kHz/192kbps 固定の音声だけの MPEG-TS が配信される
                    if (channels_store.channel.current.is_radiochannel === true) {
                        qualities.push({
                            name: '48kHz/192kbps',
                            type: 'mpegts',
                            url: `${streaming_api_base_url}/1080p/mpegts`,
                        });

                    // 通常のチャンネルの場合
                    } else {

                        // 画質リストを作成
                        for (const quality_name of LIVE_STREAMING_QUALITIES) {
                            qualities.push({
                                // 1080p-60fps のみ、見栄えの観点から表示上 "1080p (60fps)" と表示する
                                name: quality_name === '1080p-60fps' ? '1080p (60fps)' : quality_name,
                                type: 'mpegts',
                                url: `${streaming_api_base_url}/${quality_name}${hevc_prefix}/mpegts`,
                            });
                        }
                    }

                    // デフォルトの画質
                    // ラジオチャンネルのみ常に 48KHz/192kbps に固定する
                    let default_quality: string = this.tv_streaming_quality;
                    if (channels_store.channel.current.is_radiochannel) {
                        default_quality = '48kHz/192kbps';
                    }

                    return {
                        quality: qualities,
                        defaultQuality: default_quality,
                    };

                // ビデオ視聴: 録画番組情報がセットされているはず
                } else {

                    /*
                    // ビデオストリーミング API のベース URL
                    const streaming_api_base_url = `${Utils.api_base_url}/streams/video/${player_store.recorded_program.id}`;

                    // 画質リストを作成
                    for (const quality_name of VIDEO_STREAMING_QUALITIES) {
                        qualities.push({
                            // 1080p-60fps のみ、見栄えの観点から表示上 "1080p (60fps)" と表示する
                            name: quality_name === '1080p-60fps' ? '1080p (60fps)' : quality_name,
                            type: 'hls',
                            url: `${streaming_api_base_url}/${quality_name}${hevc_prefix}/playlist`,
                        });
                    }

                    // デフォルトの画質
                    // 録画ではラジオは考慮しない
                    const default_quality: string = this.video_streaming_quality;

                    return {
                        quality: qualities,
                        defaultQuality: default_quality,
                    };*/

                    return {
                        quality: [{
                            name: 'Silent',
                            type: 'normal',
                            url: audio_url,
                        }],
                        defaultQuality: 'Silent',
                    };
                }
            })(),

            // コメントの設定
            danmaku: {
                // コメントするユーザー名: 便宜上 NX-Jikkyo に固定 (実際には利用されない)
                user: 'NX-Jikkyo',
                // コメントの流れる速度
                speedRate: settings_store.settings.comment_speed_rate,
                // コメントのフォントサイズ
                fontSize: settings_store.settings.comment_font_size,
                // コメント送信後にコメントフォームを閉じるかどうか
                closeCommentFormAfterSend: settings_store.settings.close_comment_form_after_sending,
            },

            // コメント API バックエンドの設定
            apiBackend: {
                // コメント取得時
                read: async (options) => {
                    if (this.playback_mode === 'Live') {
                        // ライブ視聴: 空の配列を返す
                        // ライブ視聴では LiveCommentManager 側でリアルタイムにコメントを受信して直接描画するため、ここでは一旦コメント0件として認識させる
                        options.success([]);
                    } else {
                        // ビデオ視聴: 過去ログコメントを取得して返す
                        const jikkyo_comments = await Videos.fetchVideoJikkyoComments(player_store.recorded_program);
                        if (jikkyo_comments.is_success === false) {
                            // 取得に失敗した場合はコメントリストにエラーメッセージを表示する
                            // ただし「この録画番組の過去ログコメントは存在しないか、現在取得中です。」の場合はエラー扱いしない
                            player_store.video_comment_init_failed_message = jikkyo_comments.detail;
                            if (jikkyo_comments.detail !== 'この録画番組の過去ログコメントは存在しないか、現在取得中です。') {
                                options.error(jikkyo_comments.detail);
                            } else {
                                options.success([]);
                            }
                        } else {
                            // 過去ログコメントを取得できているということは、recording_start_time は null ではないはず
                            const recording_start_time = player_store.recorded_program.recorded_video.recording_start_time!;
                            // コメントリストに取得した過去ログコメントを送る
                            // コメ番は重複している可能性がないとも言い切れないので、別途連番を振る
                            let count = 0;
                            player_store.event_emitter.emit('CommentReceived', {
                                is_initial_comments: true,
                                comments: jikkyo_comments.comments.map((comment) => ({
                                    id: count++,
                                    text: comment.text,
                                    time: dayjs(recording_start_time).add(comment.time, 'seconds').format('MM/DD HH:mm:ss'),
                                    playback_position: comment.time,
                                    user_id: comment.author,
                                    my_post: false,
                                    // NX-Jikkyo で生成されるユーザー ID は SHA-1: 40 文字 (初期に投稿されたコメントのみ UUID v4: 36 文字) のため、
                                    // 35 文字以上であれば確実に NX-Jikkyo に投稿されたコメントであると判断できる
                                    comment_source: comment.author.length >= 35 ? 'NX' : 'ニコ実',
                                })),
                            });
                            options.success(jikkyo_comments.comments);
                        }
                    }
                },
                // コメント送信時
                send: async (options) => {
                    if (this.playback_mode === 'Live') {
                        // ライブ視聴: コメントを送信する
                        // PlayerManager に登録されているはずの LiveCommentManager を探し、コメントを送信する
                        for (const player_manager of this.player_managers) {
                            if (player_manager instanceof LiveCommentManager) {
                                player_manager.sendComment(options);  // options.success() は LiveCommentManager 側で呼ばれる
                                return;
                            }
                        }
                    } else {
                        // ビデオ視聴: 過去ログにはコメントできないのでエラーを返す
                        options.error('録画番組にはコメントできません。');
                    }
                },
            },

            // 字幕の設定
            subtitle: {
                type: 'aribb24',  // aribb24.js を有効化
            },

            // 再生プラグインの設定
            pluginOptions: {
                // mpegts.js
                mpegts: {
                    config: {
                        // Web Worker を有効にする
                        enableWorker: true,
                        // Media Source Extensions API 向けの Web Worker を有効にする
                        // メインスレッドから再生処理を分離することで、低スペック端末で DOM 描画の遅延が影響して映像再生が詰まる問題が解消される
                        // MSE in Workers が使えるかは MediaSource.canConstructInDedicatedWorker が true かどうかで判定できる
                        // MediaSource.canConstructInDedicatedWorker は TypeScript の仕様上型定義の追加が難しいため any で回避している
                        // ref: https://developer.mozilla.org/en-US/docs/Web/API/MediaSource/canConstructInDedicatedWorker_static
                        enableWorkerForMSE: window.MediaSource && (window.MediaSource as any).canConstructInDedicatedWorker === true,
                        // 再生開始まで 2048KB のバッファを貯める (?)
                        // あまり大きくしすぎてもどうも効果がないようだが、小さくしたり無効化すると特に Safari で不安定になる
                        enableStashBuffer: true,
                        stashInitialSize: Math.floor(2048 * 1024),
                        // HTMLMediaElement の内部バッファによるライブストリームの遅延を追跡する
                        // liveBufferLatencyChasing と異なり、いきなり再生時間をスキップするのではなく、
                        // 再生速度を少しだけ上げることで再生を途切れさせることなく遅延を追跡する
                        liveSync: this.tv_low_latency_mode,
                        // 許容する HTMLMediaElement の内部バッファの最大値 (秒単位, 3秒)
                        liveSyncMaxLatency: 3,
                        // HTMLMediaElement の内部バッファ (遅延) が liveSyncMaxLatency を超えたとき、ターゲットとする遅延時間 (秒単位)
                        liveSyncTargetLatency: this.live_playback_buffer_seconds,
                        // ライブストリームの遅延の追跡に利用する再生速度 (x1.1)
                        // 遅延が 3 秒を超えたとき、遅延が playback_buffer_sec を下回るまで再生速度が x1.1 に設定される
                        liveSyncPlaybackRate: 1.1,
                    }
                },
                // hls.js
                hls: {
                    ...Hls.DefaultConfig,
                    // デバッグログを有効化
                    debug: true,
                    // Web Worker を有効にする
                    enableWorker: true,
                    // MediaSource が存在しない場合のみ ManagedMediaSource を利用する
                    preferManagedMediaSource: false,
                    // プレイリスト / セグメントのリクエスト時のタイムアウトを回避する
                    manifestLoadPolicy: {
                        default: {
                            maxTimeToFirstByteMs: 1000000,  // 適当に大きな値を設定
                            maxLoadTimeMs: 1000000,  // 適当に大きな値を設定
                            timeoutRetry: {
                                maxNumRetry: 2,
                                retryDelayMs: 0,
                                maxRetryDelayMs: 0,
                            },
                            errorRetry: {
                                maxNumRetry: 1,
                                retryDelayMs: 1000,
                                maxRetryDelayMs: 8000,
                            },
                        },
                    },
                    playlistLoadPolicy: {
                        default: {
                            maxTimeToFirstByteMs: 1000000,  // 適当に大きな値を設定
                            maxLoadTimeMs: 1000000,  // 適当に大きな値を設定
                            timeoutRetry: {
                                maxNumRetry: 2,
                                retryDelayMs: 0,
                                maxRetryDelayMs: 0,
                            },
                            errorRetry: {
                                maxNumRetry: 2,
                                retryDelayMs: 1000,
                                maxRetryDelayMs: 8000,
                            }
                        }
                    },
                    fragLoadPolicy: {
                        default: {
                            maxTimeToFirstByteMs: 1000000,  // 適当に大きな値を設定
                            maxLoadTimeMs: 1000000,  // 適当に大きな値を設定
                            timeoutRetry: {
                                maxNumRetry: 4,
                                retryDelayMs: 0,
                                maxRetryDelayMs: 0,
                            },
                            errorRetry: {
                                maxNumRetry: 6,
                                retryDelayMs: 1000,
                                maxRetryDelayMs: 8000,
                            }
                        }
                    }
                },
                // aribb24.js
                aribb24: {
                    // 文字スーパーレンダラーを無効にするかどうか
                    disableSuperimposeRenderer: is_show_superimpose === false,
                    // 描画フォント
                    normalFont: `"${settings_store.settings.caption_font}", "Rounded M+ 1m for ARIB", sans-serif`,
                    // 縁取りする色
                    forceStrokeColor: settings_store.settings.always_border_caption_text,
                    // 背景色
                    forceBackgroundColor: (() => {
                        if (settings_store.settings.specify_caption_opacity === true) {
                            const opacity = settings_store.settings.caption_opacity;
                            return `rgba(0, 0, 0, ${opacity})`;
                        } else {
                            return undefined;
                        }
                    })(),
                    // DRCS 文字を対応する Unicode 文字に置換
                    drcsReplacement: true,
                    // 高解像度の字幕 Canvas を取得できるように
                    enableRawCanvas: true,
                    // 縁取りに strokeText API を利用
                    useStroke: true,
                    // Unicode 領域の代わりに私用面の領域を利用 (Windows TV 系フォントのみ)
                    usePUA: (() => {
                        const font = settings_store.settings.caption_font;
                        const context = document.createElement('canvas').getContext('2d')!;
                        context.font = '10px "Rounded M+ 1m for ARIB"';
                        context.fillText('Test', 0, 0);
                        context.font = `10px "${font}"`;
                        context.fillText('Test', 0, 0);
                        if (font.startsWith('Windows TV')) {
                            return true;
                        } else {
                            return false;
                        }
                    })(),
                    // 文字スーパーの PRA (内蔵音再生コマンド) のコールバックを指定
                    PRACallback: async (index: number) => {

                        // 設定で文字スーパーが無効なら実行しない
                        if (is_show_superimpose === false) return;

                        // index に応じた内蔵音を鳴らす
                        // ref: https://ics.media/entry/200427/
                        // ref: https://www.ipentec.com/document/javascript-web-audio-api-change-volume

                        // 自動再生ポリシーに引っかかったなどで AudioContext が一時停止されている場合、一度 resume() する必要がある
                        // resume() するまでに何らかのユーザーのジェスチャーが行われているはず…
                        // なくても動くこともあるみたいだけど、念のため
                        if (this.romsounds_context.state === 'suspended') {
                            await this.romsounds_context.resume();
                        }

                        // index で指定された音声データを読み込み
                        const buffer_source_node = this.romsounds_context.createBufferSource();
                        buffer_source_node.buffer = this.romsounds_buffers[index];

                        // GainNode につなげる
                        const gain_node = this.romsounds_context.createGain();
                        buffer_source_node.connect(gain_node);

                        // 出力につなげる
                        gain_node.connect(this.romsounds_context.destination);

                        // 音量を元の wav の3倍にする (1倍だと結構小さめ)
                        gain_node.gain.value = 3;

                        // 再生開始
                        buffer_source_node.start(0);
                    }
                }
            }
        });

        // デバッグ用にプレイヤーインスタンスも window 直下に入れる
        (window as any).player = this.player;

        // この時点で DPlayer のコンテナ要素に dplayer-mobile クラスが付与されている場合、
        // DPlayer は音量コントロールがないスマホ向けの UI になっている
        // 通常の UI で DPlayer の音量を 1.0 以外に設定した後スマホ向け UI になった場合、DPlayer の音量を変更できず OS の音量を上げるしかなくなる
        // そこで、スマホ向けの UI が表示されている場合のみ常に音量を 1.0 に設定する
        if (this.player.container.classList.contains('dplayer-mobile') === true) {
            // player.volume() を用いることで、単に音量を変更するだけでなく LocalStorage に音量を保存する処理も実行される
            // 第3引数を true に設定すると、通知を表示せずに音量を変更できる
            this.player.volume(1.0, undefined, true);
        }

        // DPlayer 側のコントロール UI 非表示タイマーを無効化（上書き）
        // 無効化しておかないと、PlayerController.setControlDisplayTimer() の処理と競合してしまう
        // 上書き元のコードは https://github.com/tsukumijima/DPlayer/blob/v1.30.2/src/ts/controller.ts#L397-L405 にある
        this.player.controller.setAutoHide = (time: number) => {};

        // DPlayer に動画再生系のイベントハンドラーを登録する
        // this.setupVideoPlaybackHandler();

        // DPlayer のフルスクリーン関係のメソッドを無理やり上書きし、NX-Jikkyo の UI と統合する
        this.setupFullscreenHandler();

        // DPlayer の設定パネルを無理やり拡張し、NX-Jikkyo 独自の項目を追加する
        this.setupSettingPanelHandler();

        // NX-Jikkyo 本体の UI を含むプレイヤー全体のコンテナ要素がリサイズされたときのイベントハンドラーを登録する
        this.setupPlayerContainerResizeHandler();

        // プレイヤーのコントロール UI を表示する (初回実行)
        this.setControlDisplayTimer();

        // UI コンポーネントからプレイヤーに通知メッセージの送信を要求されたときのイベントハンドラーを登録する
        // このイベントは常にアプリケーション上で1つだけ登録されていなければならない
        player_store.event_emitter.off('SendNotification');  // SendNotification イベントの全てのイベントハンドラーを削除
        player_store.event_emitter.on('SendNotification', (event) => {
            if (this.destroyed === true || this.player === null) return;
            this.player.notice(event.message, event.duration, event.opacity, event.color);
        });

        /*
        // PlayerManager からプレイヤーの再起動が必要になったことを通知されたときのイベントハンドラーを登録する
        // このイベントは常にアプリケーション上で1つだけ登録されていなければならない
        // さもなければ使い終わった破棄済みの PlayerController が再起動イベントにより復活し、現在利用中の PlayerController と競合してしまう
        let is_player_restarting = false;  // 現在再起動中かどうか
        player_store.event_emitter.off('PlayerRestartRequired');  // PlayerRestartRequired イベントの全てのイベントハンドラーを削除
        player_store.event_emitter.on('PlayerRestartRequired', async (event) => {

            // すでに破棄済みであれば何もしない
            if (this.destroyed === true || this.player === null) return;
            console.warn('\u001b[31m[PlayerController] PlayerRestartRequired event received. Message: ', event.message);

            // ライブ視聴: iOS 17.0 以下で mpegts.js がサポートされていない場合は再起動できない
            if (this.playback_mode === 'Live' && mpegts.isSupported() !== true) {  // mpegts.js 非対応環境では undefined が返る
                console.warn('\u001b[31m[PlayerController] PlayerRestartRequired event received, but mpegts.js is not supported. Ignored.');
                // iOS 17.0 以下は mpegts.js がサポートされていないため、再生できない
                this.player?.notice('iOS (Safari) 17.0 以下での視聴には対応していません。速やかに iOS を 17.1 以降に更新してください。', -1, undefined, '#FF6F6A');
                return;
            }

            // 既に再起動中であれば何もしない (再起動が重複して行われるのを防ぐ)
            if (is_player_restarting === true) {
                console.warn('\u001b[31m[PlayerController] PlayerRestartRequired event received, but already restarting. Ignored.');
                return;
            }
            is_player_restarting = true;

            // PlayerController 自身を破棄
            await this.destroy();

            // 即座に再起動すると諸々問題があるので、少し待つ
            await Utils.sleep(0.5);

            // PlayerController 自身を再初期化
            // この時点で PlayerRestartRequired のイベントハンドラーは再登録されているはず
            await this.init();

            // プレイヤー側にイベントの発火元から送られたメッセージ (プレイヤーを再起動中である旨) を通知する
            // 再初期化により、作り直した DPlayer が再び this.player にセットされているはず
            // 通知を表示してから PlayerController を破棄すると DPlayer の DOM 要素ごと消えてしまうので、DPlayer を作り直した後に通知を表示する
            assert(this.player !== null);
            if (event.message) {
                // 明示的にエラーメッセージではないことが指定されていればデフォルトの色で通知を表示する
                const color = event.is_error_message === false ? undefined : '#FF6F6A';
                this.player.notice(event.message, undefined, undefined, color);
            }
            is_player_restarting = false;
        });
        */

        // PlayerController.setControlDisplayTimer() の呼び出しを要求されたときのイベントハンドラーを登録する
        // このイベントは常にアプリケーション上で1つだけ登録されていなければならない
        player_store.event_emitter.off('SetControlDisplayTimer');  // SetControlDisplayTimer イベントの全てのイベントハンドラーを削除
        player_store.event_emitter.on('SetControlDisplayTimer', (event) => {
            this.setControlDisplayTimer(event.event, event.is_player_region_event, event.timeout_seconds);
        });

        /*
        // プレイヤー再起動ボタンを DPlayer の UI に追加する (再生が止まった際などに利用する想定)
        // insertAdjacentHTML で .dplayer-icons-right の一番左側に配置する
        this.player.container.querySelector('.dplayer-icons.dplayer-icons-right')!.insertAdjacentHTML('afterbegin', `
            <div class="dplayer-icon dplayer-player-restart-icon" aria-label="プレイヤーを再起動"
                data-balloon-nofocus="" data-balloon-pos="up">
                <span class="dplayer-icon-content">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M12 5V3.21c0-.45-.54-.67-.85-.35l-2.8 2.79c-.2.2-.2.51 0 .71l2.79 2.79c.32.31.86.09.86-.36V7c3.31 0 6 2.69 6 6c0 2.72-1.83 5.02-4.31 5.75c-.42.12-.69.52-.69.95c0 .65.62 1.16 1.25.97A7.991 7.991 0 0 0 20 13c0-4.42-3.58-8-8-8zm-6 8c0-1.34.44-2.58 1.19-3.59c.3-.4.26-.95-.09-1.31c-.42-.42-1.14-.38-1.5.1a7.991 7.991 0 0 0 4.15 12.47c.63.19 1.25-.32 1.25-.97c0-.43-.27-.83-.69-.95C7.83 18.02 6 15.72 6 13z"/></svg>
                </span>
            </div>
        `);
        // PlayerRestartRequired イベントとは異なり、通知メッセージなしで即座に PlayerController を再起動する
        this.player.container.querySelector('.dplayer-player-restart-icon')!.addEventListener('click', async () => {
            await this.destroy();
            await this.init();
            this.player?.notice('プレイヤーを再起動しました。', undefined, undefined, undefined);
        });
        */

        // Screen Wake Lock API を利用して画面の自動スリープを抑制する
        // 待つ必要はないので非同期で実行
        if ('wakeLock' in navigator) {
            navigator.wakeLock.request('screen').then((wake_lock) => {
                this.screen_wake_lock = wake_lock;  // 後で解除するために WakeLockSentinel を保持
                console.log('\u001b[31m[PlayerController] Screen Wake Lock API: Screen Wake Lock acquired.');
            });
        }

        // 各 PlayerManager を初期化・登録
        // ライブ視聴とビデオ視聴で必要な PlayerManager が異なる
        // この初期化順序は意図的 (入れ替えても動作するものもあるが、CaptureManager は KeyboardShortcutManager より先に初期化する必要がある)
        if (this.playback_mode === 'Live') {
            // ライブ視聴時に設定する PlayerManager
            this.player_managers = [
                new LiveCommentManager(this.player),
                new DocumentPiPManager(this.player, this.playback_mode),
                new KeyboardShortcutManager(this.player, this.playback_mode),
            ];
        } else {
            // ビデオ視聴時に設定する PlayerManager
            this.player_managers = [
                new DocumentPiPManager(this.player, this.playback_mode),
                new KeyboardShortcutManager(this.player, this.playback_mode),
            ];
        }

        // 登録されている PlayerManager をすべて初期化
        // これにより各 PlayerManager での実際の処理が開始される
        // 同期処理すると時間が掛かるので、並行して実行する
        await Promise.all(this.player_managers.map((player_manager) => player_manager.init()));

        // NX-Jikkyo では動画自体は再生しないので強制的にバッファリング表示を止める
        player_store.background_url = PlayerUtils.generatePlayerBackgroundURL();
        player_store.is_background_display = true;
        player_store.is_video_buffering = false;

        console.log('\u001b[31m[PlayerController] Initialized.');
    }


    /**
     * 指定された秒数分の無音 WAV を作成し、Blob URL を返す
     * @param duration 秒数
     * @param sample_rate サンプルレート
     * @param num_channels チャンネル数
     * @returns 無音 WAV の Blob URL
     */
    private createSilentAudioBuffer(duration: number, sample_rate: number, num_channels: number): string {

        // 最大1時間 (3600秒) ごとに無音バッファを作成する
        const max_duration = 3600;
        const audio_buffers: AudioBuffer[] = [];

        for (let start = 0; start < duration; start += max_duration) {
            const current_duration = Math.min(max_duration, duration - start);
            const frame_count = Math.floor(current_duration * sample_rate);
            const audio_buffer = new AudioBuffer({
                length: frame_count,
                sampleRate: sample_rate,
                numberOfChannels: num_channels,
            });

            for (let channel = 0; channel < num_channels; channel++) {
                const channel_data = audio_buffer.getChannelData(channel);
                for (let i = 0; i < frame_count; i++) {
                    channel_data[i] = 0;
                }
            }

            audio_buffers.push(audio_buffer);
        }

        const wav_header = new Uint8Array(44);
        const data_view = new DataView(wav_header.buffer);
        data_view.setUint32(0, 0x52494646, false); // "RIFF"
        data_view.setUint32(4, 36 + duration * sample_rate * num_channels * 2, true);
        data_view.setUint32(8, 0x57415645, false); // "WAVE"
        data_view.setUint32(12, 0x666d7420, false); // "fmt "
        data_view.setUint32(16, 16, true);
        data_view.setUint16(20, 1, true);
        data_view.setUint16(22, num_channels, true);
        data_view.setUint32(24, sample_rate, true);
        data_view.setUint32(28, sample_rate * num_channels * 2, true);
        data_view.setUint16(32, num_channels * 2, true);
        data_view.setUint16(34, 16, true);
        data_view.setUint32(36, 0x64617461, false); // "data"
        data_view.setUint32(40, duration * sample_rate * num_channels * 2, true);

        const wav_buffer = new ArrayBuffer(wav_header.length + duration * sample_rate * num_channels * 2);
        const wav_view = new DataView(wav_buffer);
        wav_view.setUint8(0, wav_header[0]);
        for (let i = 0; i < wav_header.length; i++) {
            wav_view.setUint8(i, wav_header[i]);
        }

        let offset = wav_header.length;
        for (const buffer of audio_buffers) {
            for (let channel = 0; channel < num_channels; channel++) {
                const channel_data = buffer.getChannelData(channel);
                for (let i = 0; i < buffer.length; i++) {
                    wav_view.setInt16(offset, channel_data[i] * 0x7FFF, true);
                    offset += 2;
                }
            }
        }

        return URL.createObjectURL(new Blob([wav_buffer], { type: 'audio/wav' }));
    }


    /**
     * ライブ視聴: 現在の DPlayer の再生バッファを再生位置とバッファ秒数の差から取得する
     * ビデオ視聴時と、取得に失敗した場合は 0 を返す
     * @returns バッファ秒数
     */
    private getPlaybackBufferSeconds(): number {
        if (this.player === null) return 0;
        if (this.playback_mode === 'Live') {
            try {
                const buffered_range_count = this.player.video.buffered.length;
                const buffer_remain = this.player.video.buffered.end(buffered_range_count - 1) - this.player.video.currentTime;
                return Utils.mathFloor(buffer_remain, 3);
            } catch (error) {
                return 0;
            }
        } else {
            return 0;
        }
    }


    /**
     * まだ再生が開始できていない場合 (HTMLVideoElement.readyState < HAVE_FUTURE_DATA) に再生状態の復旧を試みる
     * 処理の完了を待つ必要はないので、基本 await せず非同期で実行すべき
     * 基本 Safari だとなぜか再生開始がうまく行かないことが多いので（自動再生まわりが影響してる？）、その対策として用意した処理
     */
    private async recoverPlayback(): Promise<void> {
        assert(this.player !== null);
        const player_store = usePlayerStore();

        // 1 秒待つ
        await Utils.sleep(1);

        // この時点で映像が停止していて、かつ readyState が HAVE_FUTURE_DATA な場合、復旧を試みる
        // Safari ではタイミングによっては this.player.video が null になる場合があるらしいので ? を付ける
        if (player_store.is_video_buffering === true && this.player?.video?.readyState < 3) {
            console.warn('\u001b[31m[PlayerController] Video still buffering. (HTMLVideoElement.readyState < HAVE_FUTURE_DATA) trying to recover.');

            // 一旦停止して、0.25 秒間を置く
            this.player.video.pause();
            await Utils.sleep(0.25);

            // 再度再生を試みる
            try {
                await this.player.video.play();
            } catch (error) {
                assert(this.player !== null);
                console.warn('\u001b[31m[PlayerController] HTMLVideoElement.play() rejected. paused.');
                this.player.pause();
                return;  // 再生開始がリジェクトされた場合はここで終了
            }

            // さらに 0.5 秒待った時点で映像が停止している場合、復旧を試みる
            await Utils.sleep(0.5);
            if (player_store.is_video_buffering === true && this.player?.video?.readyState < 3) {
                console.warn('\u001b[31m[PlayerController] Video still buffering. (HTMLVideoElement.readyState < HAVE_FUTURE_DATA) trying to recover.');

                // 一旦停止して、0.25 秒間を置く
                this.player.video.pause();
                await Utils.sleep(0.25);

                // 再度再生を試みる
                try {
                    await this.player.video.play();
                } catch (error) {
                    assert(this.player !== null);
                    console.warn('\u001b[31m[PlayerController] (retry) HTMLVideoElement.play() rejected. paused.');
                    this.player.pause();
                }
            }
        }
    }


    /**
     * DPlayer に動画再生系のイベントハンドラーを登録する
     * 特にライブ視聴ではここで適切に再生状態の管理 (再生可能かどうか、エラーが発生していないかなど) を行う必要がある
     */
    private setupVideoPlaybackHandler(): void {
        assert(this.player !== null);
        const channels_store = useChannelsStore();
        const player_store = usePlayerStore();

        // ライブ視聴: 再生停止状態かつ現在の再生位置からバッファが 30 秒以上離れていないかを 60 秒おきに監視し、そうなっていたら強制的にシークする
        // mpegts.js の仕様上、MSE 側に未再生のバッファが貯まり過ぎると新規に SourceBuffer が追加できなくなるため、強制的に接続が切断されてしまう
        // 再生停止状態でも定期的にシークすることで、バッファが貯まりすぎないように調節する
        if (this.playback_mode === 'Live') {
            this.live_force_seek_interval_timer_cancel = Utils.setIntervalInWorker(() => {
                if (this.player === null) return;
                if ((this.player.video.paused && this.player.video.buffered.length >= 1) &&
                    (this.player.video.buffered.end(0) - this.player.video.currentTime > 30)) {
                    this.player.sync();
                }
            }, 60 * 1000);
        }

        // ビデオ視聴: ビデオストリームのアクティブ状態を維持するために 5 秒おきに Keep-Alive API にリクエストを送る
        // HLS プレイリストやセグメントのリクエストが行われたタイミングでも Keep-Alive が行われるが、
        // それだけではタイミング次第では十分ではないため、定期的に Keep-Alive を行う
        // Keep-Alive が行われなくなったタイミングで、サーバー側で自動的にビデオストリームの終了処理 (エンコードタスクの停止) が行われる
        if (this.playback_mode === 'Video') {
            this.video_keep_alive_interval_timer_cancel = Utils.setIntervalInWorker(async () => {
                // 画質切り替えでベース URL が変わることも想定し、あえて毎回 API URL を取得している
                if (this.player === null) return;
                const api_quality = PlayerUtils.extractVideoAPIQualityFromDPlayer(this.player);
                await APIClient.put(`${Utils.api_base_url}/streams/video/${player_store.recorded_program.id}/${api_quality}/keep-alive`);
            }, 5 * 1000);
        }

        // 再生/停止されたときのイベント
        // デバイスの通知バーからの制御など、ブラウザの画面以外から動画の再生/停止が行われる事もあるため必要
        const on_play_or_pause = () => {
            if (this.player === null) return;
            player_store.is_video_paused = this.player.video.paused;
            // 停止された場合、ロード中でなければ Progress Circular を非表示にする
            if (this.player.video.paused === true && player_store.is_loading === false) {
                player_store.is_video_buffering = false;
            }
            // まだ設定パネルが表示されていたら非表示にする
            this.player.setting.hide();
            // プレイヤーのコントロール UI を表示する
            this.setControlDisplayTimer();
        };
        this.player.on('play', on_play_or_pause);
        this.player.on('pause', on_play_or_pause);

        // 再生が一時的に止まってバッファリングしているとき/再び再生されはじめたときのイベント
        // バッファリングの Progress Circular の表示を制御する
        this.player.on('waiting', () => {
            // Progress Circular を表示する
            player_store.is_video_buffering = true;
        });
        this.player.on('playing', () => {
            // ロード中 (映像が表示されていない) でなければ Progress Circular を非表示にする
            if (player_store.is_loading === false) {
                player_store.is_video_buffering = false;
            }
            // ライブ視聴: 再生が開始できていない場合に再生状態の復旧を試みる
            if (this.playback_mode === 'Live') {
                this.recoverPlayback();
            }
        });

        // 今回 (DPlayer 初期化直後) と画質切り替え開始時の両方のタイミングで実行する必要がある処理
        // mpegts.js などの DPlayer のプラグインは画質切り替え時に一旦破棄されるため、再度イベントハンドラーを登録する必要がある
        const on_init_or_quality_change = async () => {
            assert(this.player !== null);

            // ローディング中の背景画像をランダムに変更
            player_store.background_url = PlayerUtils.generatePlayerBackgroundURL();

            // 実装上画質切り替え後にそのまま対応できない PlayerManager (LiveDataBroadcastingManager など) をここで再起動する
            // 初回実行時はそもそもまだ PlayerManager が一つも初期化されていないので、何も起こらない
            for (const player_manager of this.player_managers) {
                if (player_manager.restart_required_when_quality_switched === true) {
                    player_manager.destroy().then(() => player_manager.init());  // 非同期で実行
                }
            }

            // ライブ視聴時のみ
            if (this.playback_mode === 'Live') {

                // mpegts.js のエラーログハンドラーを登録
                // 再生中に mpegts.js 内部でエラーが発生した際 (例: デバイスの通信が一時的に切断され、API からのストリーミングが途切れた際) に呼び出される
                // このエラーハンドラーでエラーをキャッチして、PlayerController の再起動を要求する
                // PlayerController 内部なので直接再起動してもいいのだが、PlayerController を再起動させる処理は共通化しておきたい
                this.player.plugins.mpegts?.on(mpegts.Events.ERROR, async (error_type: string, detail: string) => {

                    // DPlayer がすでに破棄されている場合は何もしない
                    if (this.player === null) {
                        return;
                    }

                    // すぐ再起動すると問題があるケースがあるので、少し待機する
                    await Utils.sleep(1);

                    // もしこの時点でオフラインの場合、ネットワーク接続の変更による接続切断の可能性が高いので、オンラインになるまで待機する
                    if (navigator.onLine === false) {
                        this.player.notice('現在ネットワーク接続がありません。オンラインになるまで待機しています…', undefined, undefined, '#FF6F6A');
                        console.warn('\u001b[31m[PlayerController] mpegts.js error event: Network error. Waiting for online...');
                        await Utils.waitUntilOnline();
                    }

                    // PlayerController の再起動を要求する
                    console.error('\u001b[31m[PlayerController] mpegts.js error event:', error_type, detail);
                    player_store.event_emitter.emit('PlayerRestartRequired', {
                        message: `再生中にエラーが発生しました。(${error_type}: ${detail}) プレイヤーを再起動しています…`,
                    });
                });

                // HTMLVideoElement ネイティブの再生時エラーのイベントハンドラーを登録
                // mpegts.js が予期せずクラッシュした場合など、意図せず発生してしまうことがある
                // Offline 以外であれば PlayerController の再起動を要求する
                this.player.on('error', async (event: MediaError) => {

                    // DPlayer がすでに破棄されているか、現在ライブストリームが Offline であれば何もしない
                    if (this.player === null || player_store.live_stream_status === 'Offline') {
                        return;
                    }

                    // すぐ再起動すると問題があるケースがあるので、少し待機する
                    await Utils.sleep(1);

                    // MediaError オブジェクトは場合によっては存在しないことがあるらしい…
                    // 存在しない場合は unknown error として扱う
                    if (this.player.video.error) {
                        console.error('\u001b[31m[PlayerController] HTMLVideoElement error event:', this.player.video.error);
                        player_store.event_emitter.emit('PlayerRestartRequired', {
                            message: `再生中にエラーが発生しました。(Native: ${this.player.video.error.code}: ${this.player.video.error.message}) プレイヤーを再起動しています…`,
                        });
                    } else {
                        player_store.event_emitter.emit('PlayerRestartRequired', {
                            message: '再生中にエラーが発生しました。(Native: unknown error) プレイヤーを再起動しています…',
                        });
                    }
                });

                // 必ず最初はローディング状態とする
                player_store.is_loading = true;

                // 一旦音量をミュートする
                this.player.video.muted = true;

                // 再生準備ができた段階で再生バッファを調整し、再生準備ができた段階でローディング中の背景画像を非表示にするイベントハンドラーを登録
                let on_canplay_called = false;
                const on_canplay = async () => {

                    // 重複実行を回避する
                    if (this.player === null) return;
                    if (on_canplay_called === true) return;
                    this.player.video.oncanplaythrough = null;
                    on_canplay_called = true;

                    // 再生バッファ調整のため、一旦停止させる
                    // this.player.video.pause() を使うとプレイヤーの UI アイコンが停止してしまうので、代わりに playbackRate を使う
                    console.log('\u001b[31m[PlayerController] buffering...');
                    this.player.video.playbackRate = 0;

                    // 再生バッファが live_playback_buffer_seconds を超えるまで 0.1 秒おきに再生バッファをチェックする
                    // 再生バッファが live_playback_buffer_seconds を切ると再生が途切れやすくなるので (特に動きの激しい映像)、
                    // 再生開始までの時間を若干犠牲にして、再生バッファの調整と同期に時間を割く
                    // live_playback_buffer_seconds の値は mpegts.js の liveSyncTargetLatency 設定に渡す値と共通
                    let current_playback_buffer_sec = this.getPlaybackBufferSeconds();
                    while (current_playback_buffer_sec < this.live_playback_buffer_seconds) {
                        await Utils.sleep(0.1);
                        current_playback_buffer_sec = this.getPlaybackBufferSeconds();
                    }

                    // 再生バッファ調整のため一旦停止していた再生を再び開始
                    this.player.video.playbackRate = 1;
                    console.log('\u001b[31m[PlayerController] buffering completed.');

                    // ローディング状態を解除し、映像を表示する
                    player_store.is_loading = false;

                    // バッファリング中の Progress Circular を非表示にする
                    player_store.is_video_buffering = false;

                    // この時点で再生が開始できていない場合、再生状態の復旧を試みる
                    this.recoverPlayback();

                    if (channels_store.channel.current.is_radiochannel === true) {
                        // ラジオチャンネルでは引き続き映像の代わりとしてローディング中の背景画像を表示し続ける
                        player_store.is_background_display = true;
                    } else {
                        // ローディング中の背景画像をフェードアウト
                        player_store.is_background_display = false;
                    }

                    // 再生開始時に音量を徐々に上げる (いきなり再生されるよりも体験が良い)
                    // ミュートを解除した上で即座に音量を 0 に設定し、そこから徐々に上げていく
                    this.player.video.muted = false;
                    this.player.video.volume = 0;
                    // 0.5 秒間かけて 0 から current_volume まで音量を上げる
                    const current_volume = this.player.user.get('volume');  // 0.0 ~ 1.0 の範囲
                    const volume_step = current_volume / 10;
                    for (let i = 0; i < 10; i++) {  // 10 回に分けて音量を上げる
                        await Utils.sleep(0.5 / 10);
                        // 音量が current_volume を超えないようにする
                        // 浮動小数点絡みの問題 (丸め誤差) が出るため小数第3位で切り捨てる
                        this.player.video.volume = Math.min(Utils.mathFloor(this.player.video.volume + volume_step, 3), current_volume);
                    }
                    // 最後に current_volume に設定し直す
                    // 上記ロジックでは丸め誤差の関係で完全に current_volume とは一致しないことがあるため
                    this.player.video.volume = current_volume;
                };
                this.player.video.oncanplaythrough = on_canplay;

                // 万が一 canplaythrough が発火しなかった場合のための処理
                // 非同期で 0.05 秒おきに直接 readyState === HAVE_ENOUGH_DATA かどうかを確認する
                // この処理は先に canplaythrough が発火した場合は実行されない
                (async () => {
                    while (this.player !== null && this.player.video.readyState < 4) {
                        await Utils.sleep(0.05);
                    }
                    // さらに 0.1 秒待ってから実行
                    await Utils.sleep(0.1);
                    if (on_canplay_called === false) {
                        console.warn('\u001b[31m[PlayerController] canplaythrough event not fired. trying to recover.');
                        on_canplay();
                    }
                })();

                // もしライブストリームのステータスが ONAir にも関わらず 15 秒以上バッファリング中で canplaythrough が発火しない場合、
                // ロードに失敗したとみなし PlayerController の再起動を要求する
                await Utils.sleep(15);
                if (this.destroyed === true || this.player === null) return;
                if (player_store.live_stream_status === 'ONAir' && player_store.is_video_buffering === true && on_canplay_called === false) {
                    player_store.event_emitter.emit('PlayerRestartRequired', {
                        message: '再生開始までに時間が掛かっています。プレイヤーを再起動しています…',
                    });
                }

            // ビデオ視聴のみ
            } else {

                // 必ず最初はローディング状態で、背景画像を表示する
                player_store.is_loading = true;
                player_store.is_background_display = true;

                // 再生準備ができた段階でローディング中の背景画像を非表示にするイベントハンドラーを登録
                let on_canplay_called = false;
                const on_canplay = async () => {

                    // 重複実行を回避する
                    if (this.player === null) return;
                    if (on_canplay_called === true) return;
                    this.player.video.oncanplaythrough = null;
                    on_canplay_called = true;

                    // ローディング状態を解除し、映像を表示する
                    player_store.is_loading = false;

                    // バッファリング中の Progress Circular を非表示にする
                    player_store.is_video_buffering = false;

                    // ローディング中の背景画像をフェードアウト
                    player_store.is_background_display = false;
                };
                this.player.video.oncanplaythrough = on_canplay;
            }
        };

        // 初回実行
        on_init_or_quality_change();

        // 画質切り替え開始時のイベント
        this.player.on('quality_start', on_init_or_quality_change);

        // 動画の統計情報の表示/非表示を切り替える隠しコマンドのイベントハンドラーを登録
        // iOS / iPadOS Safari では DPlayer 側の contextmenu が長押ししても発火しないため、代替の表示手段として用意
        // 番組情報タブ内の NEXT >> を 500ms 以内に3回連続でタップすると統計情報の表示/非表示が切り替わる
        // イベントを重複定義しないように、あえて ontouchstart を使う
        let tap_count = 0;
        let last_tap = 0;
        const element = document.querySelector<HTMLDivElement>('.program-info__next');
        if (element !== null) {
            element.ontouchstart = () => {
                if (this.player === null) return;
                const current_time = new Date().getTime();
                const time_difference = current_time - last_tap;
                if (time_difference < 500 && time_difference > 0) {
                    tap_count++;
                    if (tap_count === 3) {
                        this.player.infoPanel.toggle();
                        tap_count = 0;
                    }
                }
                last_tap = current_time;
            };
        }
    }


    /**
     * DPlayer のフルスクリーン関係のメソッドを無理やり上書きし、NX-Jikkyo の UI と統合する
     * 上書き元のコードは https://github.com/tsukumijima/DPlayer/blob/master/src/ts/fullscreen.ts にある
     */
    private setupFullscreenHandler(): void {
        assert(this.player !== null);
        const player_store = usePlayerStore();

        // フルスクリーンにするコンテナ要素 (ページ全体)
        const fullscreen_container = document.body;

        // フルスクリーンかどうか
        this.player.fullScreen.isFullScreen = (type?: DPlayerType.FullscreenType) => {
            return !!(document.fullscreenElement || document.webkitFullscreenElement);
        };

        // フルスクリーンをリクエスト
        this.player.fullScreen.request = (type?: DPlayerType.FullscreenType) => {
            assert(this.player !== null);
            // すでにフルスクリーンだったらキャンセルする
            if (this.player.fullScreen.isFullScreen()) {
                this.player.fullScreen.cancel();
                return;
            }
            // フルスクリーンをリクエスト
            // Safari は webkit のベンダープレフィックスが必要
            fullscreen_container.requestFullscreen = fullscreen_container.requestFullscreen || fullscreen_container.webkitRequestFullscreen;
            if (fullscreen_container.requestFullscreen) {
                fullscreen_container.requestFullscreen();
            } else {
                // フルスクリーンがサポートされていない場合はエラーを表示
                this.player.notice('iPhone Safari は動画のフルスクリーン表示に対応していません。', undefined, undefined, '#FF6F6A');
                return;
            }
            // 画面の向きを横に固定 (Screen Orientation API がサポートされている場合)
            if (screen.orientation) {
                screen.orientation.lock('landscape').catch(() => {});
            }
        };

        // フルスクリーンをキャンセル
        this.player.fullScreen.cancel = (type?: DPlayerType.FullscreenType) => {
            // フルスクリーンを終了
            // Safari は webkit のベンダープレフィックスが必要
            document.exitFullscreen = document.exitFullscreen || document.webkitExitFullscreen;
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
            // 画面の向きの固定を解除
            if (screen.orientation) {
                screen.orientation.unlock();
            }
        };

        // フルスクリーン状態が変化した時のイベントハンドラーを登録
        // 複数のイベントを重複登録しないよう、あえて onfullscreenchange を使う
        const fullscreen_handler = () => {
            assert(this.player !== null);
            player_store.is_fullscreen = this.player.fullScreen.isFullScreen() === true;
        };
        if (fullscreen_container.onfullscreenchange !== undefined) {
            fullscreen_container.onfullscreenchange = fullscreen_handler;
        } else if (fullscreen_container.onwebkitfullscreenchange !== undefined) {
            fullscreen_container.onwebkitfullscreenchange = fullscreen_handler;
        }
    }


    /**
     * DPlayer の設定パネルを無理やり拡張し、NX-Jikkyo 独自の項目を追加する
     */
    private setupSettingPanelHandler(): void {
        assert(this.player !== null);
        const player_store = usePlayerStore();

        // 設定パネルにショートカット一覧を表示するボタンを動的に追加する
        // スマホなどのタッチデバイスでは基本キーボードが使えないため、タッチデバイスの場合はボタンを表示しない
        if (Utils.isTouchDevice() === false) {
            this.player.template.settingOriginPanel.insertAdjacentHTML('beforeend', `
            <div class="dplayer-setting-item dplayer-setting-keyboard-shortcut">
                <span class="dplayer-label">キーボードショートカット</span>
                <div class="dplayer-toggle">
                    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 32 32">
                        <path d="M22 16l-10.105-10.6-1.895 1.987 8.211 8.613-8.211 8.612 1.895 1.988 8.211-8.613z"></path>
                    </svg>
                </div>
            </div>`);

            // ショートカット一覧モーダルを表示するボタンがクリックされたときのイベントハンドラーを登録
            this.player.template.settingOriginPanel.querySelector('.dplayer-setting-keyboard-shortcut')!.addEventListener('click', () => {
                assert(this.player !== null);
                // 設定パネルを閉じる
                this.player.setting.hide();
                // ショートカットキー一覧モーダルを表示する
                player_store.shortcut_key_modal = true;
            });
        }
    }


    /**
     * NX-Jikkyo 本体の UI を含むプレイヤー全体のコンテナ要素がリサイズされたときのイベントハンドラーを登録する
     */
    private setupPlayerContainerResizeHandler(): void {

        // 監視対象のプレイヤー全体のコンテナ要素
        const player_container_element = document.querySelector('.watch-player')!;

        // プレイヤー全体のコンテナ要素がリサイズされた際に発火するイベント
        const resize_handler = () => {

            // コメント描画領域の要素
            if (this.player === null) return;
            const comment_area_element = this.player.danmaku!.container;

            // コメント描画領域の幅から算出した、映像の要素の幅/高さ (px)
            // 実際の映像の要素の幅は BML ブラウザの ShadowDOM 内に入ると正確な算出ができないため、代わりにコメント描画領域の幅を使って算出する
            const video_element_width = comment_area_element.clientWidth;
            const video_element_height = comment_area_element.clientWidth * (9 / 16);

            // プレイヤー全体と映像の高さの差（レターボックス）から、コメント描画領域の高さを狭める必要があるかを判定する
            // 2で割っているのは単体の差を測るため
            if (player_container_element === null || player_container_element.clientHeight === null) return;
            const letter_box_height = (player_container_element.clientHeight - video_element_height) / 2;

            // コメント描画領域の高さがしきい値より小さい場合、コメント描画領域のアスペクト比を狭める
            // しきい値はデバイスの画面サイズや向きによって異なる
            // スマホ縦画面ではコメント描画領域を狭める必要がある上部のヘッダーがないため、しきい値を 0 にする
            const threshold = Utils.isSmartphoneVertical() ? 0 : Utils.isSmartphoneHorizontal() ? 50 : 66;
            if (letter_box_height < threshold) {

                // コメント描画領域に必要な上下マージン
                const comment_area_vertical_margin = (threshold - letter_box_height) * 2;

                // 狭めるコメント描画領域の幅
                // 映像の要素の幅をそのまま利用する
                const comment_area_width = video_element_width;

                // 狭めるコメント描画領域の高さ
                const comment_area_height = video_element_height - comment_area_vertical_margin;

                // 狭めるコメント描画領域のアスペクト比を求める
                // https://tech.arc-one.jp/asepct-ratio/
                const gcd = (x: number, y: number) => {  // 最大公約数を求める関数
                    if (y === 0) return x;
                    return gcd(y, x % y);
                };
                // 幅と高さの最大公約数を求める
                const gcd_result = gcd(comment_area_width, comment_area_height);
                // 幅と高さをそれぞれ最大公約数で割ってアスペクト比を算出
                const comment_area_height_aspect = `${comment_area_width / gcd_result} / ${comment_area_height / gcd_result}`;

                // 一時的に transition を無効化する
                // アスペクト比の設定は連続して行われるが、その際に transition が適用されるとワンテンポ遅れたアニメーションになってしまう
                comment_area_element.style.transition = 'none';

                // コメント描画領域に算出したアスペクト比を設定する
                comment_area_element.style.setProperty('--comment-area-aspect-ratio', comment_area_height_aspect);

                // コメント描画領域に必要な上下マージンを設定する
                comment_area_element.style.setProperty('--comment-area-vertical-margin', `${comment_area_vertical_margin}px`);

                // 0.2秒後に再び transition を有効化する
                // 0.2秒より前にもう一度リサイズイベントが来た場合はタイマーがクリアされるため実行されない
                window.setTimeout(() => comment_area_element.style.transition = '', 0.2 * 1000);

            } else {

                // コメント描画領域に設定したアスペクト比・上下マージンを削除する
                comment_area_element.style.removeProperty('--comment-area-aspect-ratio');
                comment_area_element.style.removeProperty('--comment-area-vertical-margin');
            }
        };

        // 初回実行
        resize_handler();

        // 要素の監視を開始
        this.player_container_resize_observer = new ResizeObserver(resize_handler);
        this.player_container_resize_observer.observe(player_container_element);
    }


    /**
     * 一定の条件に基づいてプレイヤーのコントロール UI の表示状態を切り替える
     * マウスが動いたりタップされた時に実行するタイマー関数で、3秒間何も操作がなければプレイヤーのコントロール UI を非表示にする
     * 本来は View 側に実装すべきだが、プレイヤー側のロジックとも密接に関連しているため PlayerController に実装した
     * @param event マウスやタッチイベント (手動実行する際は省略する)
     * @param is_player_region_event プレイヤー画面の中で発火したイベントなら true に設定する
     * @param timeout_seconds 何も操作がない場合にコントロール UI を非表示にするまでの秒数
     */
    private setControlDisplayTimer(
        event: Event | null = null,
        is_player_region_event: boolean = false,
        timeout_seconds: number = 3,
    ): void {
        const player_store = usePlayerStore();

        // タッチデバイスで mousemove 、あるいはタッチデバイス以外で touchmove か click が発火した時は実行じない
        if (Utils.isTouchDevice() === true  && event !== null && (event.type === 'mousemove')) return;
        if (Utils.isTouchDevice() === false && event !== null && (event.type === 'touchmove' || event.type === 'click')) return;

        // 以前セットされたタイマーを止める
        window.clearTimeout(this.player_control_ui_hide_timer_id);

        // 実行された際にプレイヤーのコントロール UI を非表示にするタイマー関数 (setTimeout に渡すコールバック関数)
        const player_control_ui_hide_timer = () => {

            // 万が一実行されたタイミングですでに DPlayer が破棄されていたら何もしない
            if (this.player === null) return;

            // コメント入力フォームが表示されているときは実行しない
            // タイマーを掛け直してから抜ける
            if (this.player.template.controller.classList.contains('dplayer-controller-comment')) {
                this.player_control_ui_hide_timer_id =
                    window.setTimeout(player_control_ui_hide_timer, timeout_seconds * 1000);  // 3秒後に再実行
                return;
            }

            // コントロールを非表示にする
            player_store.is_control_display = false;

            // プレイヤーのコントロールと設定パネルを非表示にする
            this.player.controller.hide();
            this.player.setting.hide();
        };

        // 万が一実行されたタイミングですでに DPlayer が破棄されていたら何もしない
        if (this.player === null) return;

        // タッチデバイスかつプレイヤー画面の中がタップされたとき
        if (Utils.isTouchDevice() === true && is_player_region_event === true) {

            // DPlayer 側のコントロール UI の表示状態に合わせる
            if (this.player.controller.isShow()) {

                // コントロールを表示する
                player_store.is_control_display = true;

                // プレイヤーのコントロールを表示する
                this.player.controller.show();

                // 3秒間何も操作がなければコントロールを非表示にする
                // 3秒間の間一度でもタッチされればタイマーが解除されてやり直しになる
                this.player_control_ui_hide_timer_id =
                    window.setTimeout(player_control_ui_hide_timer, timeout_seconds * 1000);

            } else {

                // コントロール UI を非表示にする
                player_store.is_control_display = false;

                // DPlayer 側のコントロール UI と設定パネルを非表示にする
                this.player.controller.hide();
                this.player.setting.hide();
            }

        // それ以外の画面がクリックされたとき
        } else {

            // コントロール UI を表示する
            player_store.is_control_display = true;

            // DPlayer 側のコントロール UI を表示する
            this.player.controller.show();

            // 3秒間何も操作がなければコントロールを非表示にする
            // 3秒間の間一度でもマウスが動けばタイマーが解除されてやり直しになる
            this.player_control_ui_hide_timer_id =
                window.setTimeout(player_control_ui_hide_timer, timeout_seconds * 1000);
        }
    }


    /**
     * DPlayer と PlayerManager を破棄し、再生を終了する
     * 常に init() で作成したものが destroy() ですべてクリーンアップされるように実装すべき
     * PlayerController の再起動を行う場合、基本外部から直接 await destroy() と await init() は呼び出さず、代わりに
     * player_store.event_emitter.emit('PlayerRestartRequired', 'プレイヤーを再起動しています…') のようにイベントを発火させるべき
     */
    public async destroy(): Promise<void> {
        const player_store = usePlayerStore();

        // すでに破棄されているのに再度実行してはならない
        if (this.destroyed === true) {
            return;
        }

        // すでに破棄中なら何もしない
        if (this.destroying === true) {
            return;
        }
        this.destroying = true;

        console.log('\u001b[31m[PlayerController] Destroying...');

        // 登録されている PlayerManager をすべて破棄
        // CSS アニメーションの関係上、ローディング状態にする前に破棄する必要がある (特に LiveDataBroadcastingManager)
        // 同期処理すると時間が掛かるので、並行して実行する
        await Promise.all(this.player_managers.map(async (player_manager) => player_manager.destroy()));
        this.player_managers = [];

        // Screen Wake Lock API で確保した起動ロックを解放
        // 起動ロックが確保できていない場合は何もしない
        if (this.screen_wake_lock !== null) {
            this.screen_wake_lock.release();
            this.screen_wake_lock = null;
            console.log('\u001b[31m[PlayerController] Screen Wake Lock API: Screen Wake Lock released.');
        }

        // ローディング中の背景画像を隠す
        player_store.is_background_display = false;

        // 再びローディング状態にする
        player_store.is_loading = true;

        // コメントの取得に失敗した際のエラーメッセージを削除
        player_store.live_comment_init_failed_message = null;
        player_store.video_comment_init_failed_message = null;

        // 映像がフェードアウトするアニメーション (0.2秒) 分待ってから実行
        // この 0.2 秒の間に音量をフェードアウトさせる
        if (this.player !== null) {
            // 0.2 秒間かけて current_volume から 0 まで音量を下げる
            const current_volume = this.player.user.get('volume');  // 0.0 ~ 1.0 の範囲
            const volume_step = current_volume / 10;
            for (let i = 0; i < 10; i++) {  // 10 回に分けて音量を下げる
                await Utils.sleep(0.2 / 10);
                // ごく稀に映像が既に破棄されている or まだ再生開始されていない場合がある (?) ので、その場合は実行しない
                if (this.player && this.player.video) {
                    // 音量が 0 より小さくならないようにする
                    // 浮動小数点絡みの問題 (丸め誤差) が出るため小数第3位で切り捨てる
                    this.player.video.volume = Math.max(Utils.mathFloor(this.player.video.volume - volume_step, 3), 0);
                }
            }
            // 最後に音量を 0 に設定
            // 上記ロジックでは丸め誤差の関係で完全に 0 とは一致しないことがあるため
            this.player.video.volume = 0;
        }

        // タイマーを破棄
        if (this.live_force_seek_interval_timer_cancel !== null) {
            this.live_force_seek_interval_timer_cancel();
            this.live_force_seek_interval_timer_cancel = null;
        }
        if (this.video_keep_alive_interval_timer_cancel !== null) {
            this.video_keep_alive_interval_timer_cancel();
            this.video_keep_alive_interval_timer_cancel = null;
        }
        window.clearTimeout(this.player_control_ui_hide_timer_id);

        // プレイヤー全体のコンテナ要素の監視を停止
        if (this.player_container_resize_observer !== null) {
            this.player_container_resize_observer.disconnect();
            this.player_container_resize_observer = null;
        }

        // DPlayer 本体を破棄
        // なぜか例外が出ることがあるので try-catch で囲む
        if (this.player !== null) {
            // プレイヤーの破棄を実行する前に、DPlayer 側に登録された HTMLVideoElement の error イベントハンドラーを全て削除
            // Safari のみ、削除しておかないと「動画の読み込みに失敗しました」というエラーが発生する
            if (this.player.events.events['error']) {
                this.player.events.events['error'] = [];
            }
            // 通常 this.player.destroy() が実行された後 mpegts.js も自動的に破棄されるのだが、Safari のみ
            // なぜか video.src = '' を実行した後に mpegts.js を破棄するとエラーというか挙動不審になるので、
            // あえて mpegts.js を明示的に先に破棄しておいて Safari の地雷を回避する
            if (this.player.plugins.mpegts) {
                try {
                    this.player.plugins.mpegts.unload();
                    this.player.plugins.mpegts.detachMediaElement();
                    this.player.plugins.mpegts.destroy();
                } catch (e) {
                    // 何もしない
                }
            }
            // 引数に true を指定して、破棄後も DPlayer 側の HTML 要素を保持する
            // これにより、チャンネルを切り替えるなどして再度初期化されるまでの僅かな間もプレイヤーのコントロール UI が表示される (動作はしない)
            // ここで HTML 要素を削除してしまうと、プレイヤーのコントロール UI が一瞬削除されることでちらつきが発生して見栄えが悪い
            // HTML 要素を保持する分、破棄中に描画されていたコメントも残ってしまうので、破棄前にコメントを全て削除する
            this.player.danmaku!.clear();
            try {
                this.player.destroy(true);
            } catch (e) {
                // 何もしない
            }
            this.player = null;
        }

        // 破棄済みかどうかのフラグを立てる
        this.destroying = false;
        this.destroyed = true;

        // PlayerStore にプレイヤーを破棄したことを通知
        player_store.is_player_initialized = false;

        console.log('\u001b[31m[PlayerController] Destroyed.');
    }
}

export default PlayerController;
