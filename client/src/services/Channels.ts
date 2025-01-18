
import { getCookie } from 'typescript-cookie';

import APIClient from '@/services/APIClient';
import { IProgram, IProgramDefault } from '@/services/Programs';
import Utils from '@/utils';


/** チャンネルタイプの型 */
export type ChannelType = 'GR' | 'BS' | 'CS' | 'CATV' | 'SKY' | 'STARDIGIO';

// チャンネルタイプの型 (実際のチャンネルリストに表示される表現)
export type ChannelTypePretty = 'ピン留め' | '地デジ' | 'BS' | 'CS' | 'CATV' | 'SKY' | 'StarDigio';

/** チャンネル情報を表すインターフェイス */
export interface IChannel {
    id: string;
    display_channel_id: string;
    network_id: number;
    service_id: number;
    transport_stream_id: number | null;
    remocon_id: number;
    channel_number: string;
    type: ChannelType;
    name: string;
    jikkyo_force: number | null;
    is_subchannel: boolean;
    is_radiochannel: boolean;
    is_watchable: boolean,
}

/** 現在放送中のチャンネル情報を表すインターフェイス */
export interface ILiveChannel extends IChannel {
    // 以下はすべて動的に生成される TV ライブストリーミング用の追加カラム
    is_display: boolean;
    viewer_count: number;
    program_present: IProgram | null;
    program_following: IProgram | null;
}

/** 現在放送中のチャンネル情報を表すインターフェイスのデフォルト値 */
export const ILiveChannelDefault: ILiveChannel = {
    id: 'jk0',
    display_channel_id: 'gr000',
    network_id: 0,
    service_id: 0,
    transport_stream_id: null,
    remocon_id: 0,
    channel_number: '---',
    type: 'GR',
    name: '取得中…',
    jikkyo_force: null,
    is_subchannel: false,
    is_radiochannel: false,
    is_watchable: true,
    is_display: true,
    viewer_count: 0,
    program_present: IProgramDefault,
    program_following: IProgramDefault,
};

/** すべてのチャンネルタイプの現在放送中のチャンネルの情報を表すインターフェイス */
export interface ILiveChannelsList {
    GR: ILiveChannel[];
    BS: ILiveChannel[];
    CS: ILiveChannel[];
    CATV: ILiveChannel[];
    SKY: ILiveChannel[];
    STARDIGIO: ILiveChannel[];
}

/** ニコニコ実況の WebSocket API の情報を表すインターフェイス */
export interface IJikkyoWebSocketInfo {
    watch_session_url: string | null;
    nicolive_watch_session_url: string | null;
    nicolive_watch_session_error: string | null;
    comment_session_url: string | null;
    is_nxjikkyo_exclusive: boolean;
}

export interface INXJikkyoChannel {
    id: string;
    name: string;
    program_present: INXJikkyoProgramInfo | null;
    program_following: INXJikkyoProgramInfo | null;
    threads: INXJikkyoThread[];
}

export interface INXJikkyoProgramInfo {
    // TVer から取得したタイトル (フル)
    title: string;
    // 番組開始時刻 (常に Asia/Tokyo の datetime)
    start_at: string;
    // 番組終了時刻 (常に Asia/Tokyo の datetime)
    end_at: string;
    // 番組長 (秒単位)
    duration: number;
    // ジャンル名
    genre: string | null;
}

export interface INXJikkyoThread {
    id: number;
    start_at: string;
    end_at: string;
    duration: number;
    title: string;
    description: string;
    status: string;
    jikkyo_force: number | null;
    viewers: number | null;
    comments: number;
}



class Channels {

    /**
     * すべてのチャンネルの情報を取得する
     * @return すべてのチャンネルの情報
     */
    static async fetchAll(): Promise<ILiveChannelsList | null> {

        /*
        // API リクエストを実行
        const response = await APIClient.get<ILiveChannelsList>('/channels');

        // エラー処理
        if (response.type === 'error') {
            APIClient.showGenericError(response, 'チャンネル情報を取得できませんでした。');
            return null;
        }

        return response.data;
        */

        // API リクエストを実行
        const response = await APIClient.get<INXJikkyoChannel[]>('/channels');

        // エラー処理
        if (response.type === 'error') {
            APIClient.showGenericError(response, 'チャンネル情報を取得できませんでした。');
            return null;
        }

        // KonomiTV からコードを大きく変えるのが面倒なので API インターフェイスをモックして適合させる
        const live_channels_list: ILiveChannelsList = {
            GR: [],
            BS: [],
            CS: [],
            CATV: [],
            SKY: [],
            STARDIGIO: [],
        };

        // まずは放送中のスレッドが存在するチャンネルのみに絞り込む
        const now = new Date();
        const filtered_channels = response.data.filter(channel =>
            channel.threads.some(thread => new Date(thread.start_at) <= now && now <= new Date(thread.end_at))
        );

        // チャンネルごとに ILiveChannel 互換のオブジェクトを生成する
        filtered_channels.forEach((channel) => {

            // 現在放送中のスレッドを取得
            const current_thread = channel.threads.find(thread =>
                new Date(thread.start_at) <= now && now <= new Date(thread.end_at)
            );

            // 次に放送されるスレッドを取得
            const current_thread_index = channel.threads.findIndex(thread =>
                new Date(thread.start_at) <= now && now <= new Date(thread.end_at)
            );
            const next_thread = (current_thread_index !== -1 && current_thread_index + 1 < channel.threads.length)
                ? channel.threads[current_thread_index + 1]
                : null;

            // 番組情報に関しては存在するならスレッド情報ではなく番組情報を優先する
            const live_channel: ILiveChannel = {
                id: channel.id,
                display_channel_id: channel.id,
                network_id: -1,
                service_id: -1,
                transport_stream_id: -1,
                remocon_id: (() => {
                    if (channel.id.length <= 4) {
                        return parseInt(channel.id.replaceAll('jk', ''));
                    } else {
                        switch (channel.id) {
                            case 'jk101':
                                return 1;
                            case 'jk141':
                                return 4;
                            case 'jk151':
                                return 5;
                            case 'jk161':
                                return 6;
                            case 'jk171':
                                return 7;
                            case 'jk181':
                                return 8;
                            case 'jk191':
                                return 9;
                            case 'jk200':
                                return 10;
                            case 'jk211':
                                return 11;
                            case 'jk222':
                                return 12;
                            default:
                                return -1;
                        }
                    }
                })(),
                channel_number: channel.id.length <= 4 ? ('00' + channel.id.replaceAll('jk', '')).slice(-2) + '1' : channel.id.replaceAll('jk', ''),
                type: channel.id.length <= 4 ? 'GR' : 'BS',
                name: channel.name,
                jikkyo_force: current_thread ? current_thread.jikkyo_force : null,
                is_display: true,
                is_subchannel: false,
                is_radiochannel: false,
                is_watchable: true,
                viewer_count: current_thread ? current_thread.comments : 0,
                program_present: current_thread ? {
                    id: current_thread.id.toString(),
                    channel_id: channel.id,
                    network_id: -1,
                    service_id: -1,
                    event_id: -1,
                    title: channel.program_present?.title || current_thread.title,
                    description: `<div class="font-weight-bold">🎧実況枠: ${current_thread.title}</div>`,
                    detail: {
                        'NX-Jikkyo について': (
                            'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。\n' +
                            'ニコニコ実況に投稿されたコメントも、リアルタイムで表示されます。\n\n' +
                            'ひとりだけど、ひとりじゃない。\n' +
                            'テレビの映像は流れませんが、好きな番組をテレビで見ながら、プレイヤーに流れるコメントでワイワイ楽しめます。\n' +
                            'ぜひ感想などを気軽にコメントしてお楽しみください。'
                        ),
                    },
                    start_time: channel.program_present?.start_at || current_thread.start_at,
                    end_time: channel.program_present?.end_at || current_thread.end_at,
                    duration: channel.program_present?.duration || current_thread.duration,
                    is_free: false,
                    genres: channel.program_present?.genre ? [{
                        major: channel.program_present.genre,
                        middle: '',
                    }] : [],
                    video_type: '',
                    video_codec: '',
                    video_resolution: '',
                    primary_audio_type: '',
                    primary_audio_language: '',
                    primary_audio_sampling_rate: '',
                    secondary_audio_type: null,
                    secondary_audio_language: null,
                    secondary_audio_sampling_rate: null,
                } : null,
                program_following: next_thread ? {
                    id: next_thread.id.toString(),
                    channel_id: channel.id,
                    network_id: -1,
                    service_id: -1,
                    event_id: -1,
                    title: channel.program_following?.title || next_thread.title,
                    description: next_thread.description,
                    detail: {},
                    start_time: channel.program_following?.start_at || next_thread.start_at,
                    end_time: channel.program_following?.end_at || next_thread.end_at,
                    duration: channel.program_following?.duration || next_thread.duration,
                    is_free: false,
                    genres: channel.program_following?.genre ? [{
                        major: channel.program_following.genre,
                        middle: '',
                    }] : [],
                    video_type: '',
                    video_codec: '',
                    video_resolution: '',
                    primary_audio_type: '',
                    primary_audio_language: '',
                    primary_audio_sampling_rate: '',
                    secondary_audio_type: null,
                    secondary_audio_language: null,
                    secondary_audio_sampling_rate: null,
                } : null,
            };

            if (channel.id.length <= 4) {
                live_channels_list.GR.push(live_channel);
            } else {
                live_channels_list.BS.push(live_channel);
            }
        });

        return live_channels_list;
    }


    /**
     * 指定したチャンネルの情報を取得する
     * 現状、処理の見直しにより使用されていない
     * @param channel_id チャンネル ID (id or display_channel_id)
     * @return 指定したチャンネルの情報
     */
    static async fetch(channel_id: string): Promise<ILiveChannel | null> {

        // API リクエストを実行
        const response = await APIClient.get<ILiveChannel>(`/channels/${channel_id}`);

        // エラー処理
        if (response.type === 'error') {
            APIClient.showGenericError(response, 'チャンネル情報を取得できませんでした。');
            return null;
        }

        return response.data;
    }


    /**
     * 指定されたチャンネルに対応する、ニコニコ実況・NX-Jikkyo とコメントを送受信するための WebSocket API の情報を取得する
     * @param channel_id チャンネル ID (id or display_channel_id)
     * @return ニコニコ実況・NX-Jikkyo とコメントを送受信するための WebSocket API の情報
     */
    static async fetchWebSocketInfo(channel_id: string): Promise<IJikkyoWebSocketInfo | null> {

        // NX-Niconico-User Cookie を取得
        const niconico_user_cookie = getCookie('NX-Niconico-User');

        // Cookie が存在しない場合は負荷削減のため、常に API にはアクセスせずモックする
        if (!niconico_user_cookie) {
            return {
                watch_session_url: `${Utils.api_base_url.replaceAll('http', 'ws')}/channels/${channel_id}/ws/watch`,
                nicolive_watch_session_url: null,
                nicolive_watch_session_error: null,
                comment_session_url: `${Utils.api_base_url.replaceAll('http', 'ws')}/channels/${channel_id}/ws/comment`,
                is_nxjikkyo_exclusive: false,
            };
        }

        // API リクエストを実行
        const response = await APIClient.get<IJikkyoWebSocketInfo>(`/channels/${channel_id}/jikkyo`);

        // エラー処理
        if (response.type === 'error') {
            APIClient.showGenericError(response, 'コメント送受信用 WebSocket API の情報を取得できませんでした。');
            return null;
        }

        return response.data;
    }
}

export default Channels;
