
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

/** ニコニコ実況のセッション情報を表すインターフェイス */
export interface IJikkyoSession {
    is_success: boolean;
    audience_token: string | null;
    detail: string;
}


export interface INXJikkyoChannel {
    id: string;
    name: string;
    description: string;
    threads: INXJikkyoThread[];
}

export interface INXJikkyoThread {
    id: number;
    start_at: string;
    end_at: string;
    duration: number;
    title: string;
    description: string;
    jikkyo_force: number | null;
    viewers: number;
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

        response.data.forEach((channel) => {
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
                jikkyo_force: channel.threads[0].jikkyo_force,
                is_display: true,
                is_subchannel: false,
                is_radiochannel: false,
                is_watchable: true,
                viewer_count: channel.threads[0].comments, // 敢えて累計視聴者数の代わりに累計コメント数を入れている
                program_present: (() => {
                    const now = new Date();
                    const current_thread = channel.threads.find(thread =>
                        new Date(thread.start_at) <= now && now <= new Date(thread.end_at)
                    );
                    if (!current_thread) return null;

                    const program: IProgram = {
                        id: current_thread.id.toString(),
                        channel_id: channel.id,
                        network_id: -1,
                        service_id: -1,
                        event_id: -1,
                        title: current_thread.title,
                        description: current_thread.description,
                        detail: {},
                        start_time: current_thread.start_at,
                        end_time: current_thread.end_at,
                        duration: current_thread.duration,
                        is_free: false,
                        genres: [],
                        video_type: '',
                        video_codec: '',
                        video_resolution: '',
                        primary_audio_type: '',
                        primary_audio_language: '',
                        primary_audio_sampling_rate: '',
                        secondary_audio_type: null,
                        secondary_audio_language: null,
                        secondary_audio_sampling_rate: null,
                    };
                    return program;
                })(),
                program_following: (() => {
                    const now = new Date();
                    const current_thread_index = channel.threads.findIndex(thread =>
                        new Date(thread.start_at) <= now && now <= new Date(thread.end_at)
                    );
                    if (current_thread_index === -1 || current_thread_index + 1 >= channel.threads.length) return null;

                    const next_thread = channel.threads[current_thread_index + 1];
                    const program: IProgram = {
                        id: next_thread.id.toString(),
                        channel_id: channel.id,
                        network_id: -1,
                        service_id: -1,
                        event_id: -1,
                        title: next_thread.title,
                        description: next_thread.description,
                        detail: {},
                        start_time: next_thread.start_at,
                        end_time: next_thread.end_at,
                        duration: next_thread.duration,
                        is_free: false,
                        genres: [],
                        video_type: '',
                        video_codec: '',
                        video_resolution: '',
                        primary_audio_type: '',
                        primary_audio_language: '',
                        primary_audio_sampling_rate: '',
                        secondary_audio_type: null,
                        secondary_audio_language: null,
                        secondary_audio_sampling_rate: null,
                    };
                    return program;
                })(),
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
     * 指定したチャンネルに紐づくニコニコ実況のセッション情報を取得する
     * @param channel_id チャンネル ID (id or display_channel_id)
     * @return 指定したチャンネルに紐づくニコニコ実況のセッション情報
     */
    static async fetchJikkyoSession(channel_id: string): Promise<IJikkyoSession | null> {

        // // API リクエストを実行
        // const response = await APIClient.get<IJikkyoSession>(`/channels/${channel_id}/jikkyo`);

        // // エラー処理
        // if (response.type === 'error') {
        //     APIClient.showGenericError(response, 'ニコニコ実況のセッション情報を取得できませんでした。');
        //     return null;
        // }

        // return response.data;

        // 常にモックする
        // ただそれだと早すぎて色々バグる？ので、0.5s だけ遅らせる
        await Utils.sleep(0.5);
        return {
            is_success: true,
            audience_token: `${Utils.api_base_url.replaceAll('http', 'ws')}/channels/${channel_id}/ws/watch`,
            detail: '',
        };
    }
}

export default Channels;
