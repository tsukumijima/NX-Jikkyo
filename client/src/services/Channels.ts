
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
    id: 'NID0-SID0',
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
                remocon_id: -1,
                channel_number: channel.id.length <= 4 ? ('00' + channel.id.replaceAll('jk', '')).slice(-2) + '1' : channel.id.replaceAll('jk', ''),
                type: channel.id.length <= 4 ? 'GR' : 'BS',
                name: channel.name,
                jikkyo_force: null,
                is_display: true,
                is_subchannel: false,
                is_radiochannel: false,
                is_watchable: true,
                viewer_count: 0,
                program_present: (() => {
                    const program: IProgram = {
                        id: channel.threads[0].id.toString(),
                        channel_id: channel.id,
                        network_id: -1,
                        service_id: -1,
                        event_id: -1,
                        title: channel.threads[0].title,
                        description: channel.threads[0].description,
                        detail: {},
                        start_time: channel.threads[0].start_at,
                        end_time: channel.threads[0].end_at,
                        duration: channel.threads[0].duration,
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
                    const program: IProgram = {
                        id: channel.threads[1].id.toString(),
                        channel_id: channel.id,
                        network_id: -1,
                        service_id: -1,
                        event_id: -1,
                        title: channel.threads[1].title,
                        description: channel.threads[1].description,
                        detail: {},
                        start_time: channel.threads[1].start_at,
                        end_time: channel.threads[1].end_at,
                        duration: channel.threads[1].duration,
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
        return {
            is_success: true,
            audience_token: `${Utils.api_base_url.replaceAll('http', 'ws')}/channels/${channel_id}/ws/watch`,
            detail: '',
        };
    }
}

export default Channels;
