
import APIClient from './APIClient';

import { IChannel } from '@/services/Channels';
import { CommentUtils } from '@/utils';


/** 録画ファイル情報を表すインターフェース */
export interface IRecordedVideo {
    id: number;
    file_path: string;
    file_hash: string;
    file_size: number;
    recording_start_time: string | null;
    recording_end_time: string | null;
    duration: number;
    container_format: 'MPEG-TS';
    video_codec: 'MPEG-2' | 'H.264' | 'H.265';
    video_codec_profile: 'High' | 'High 10' | 'Main' | 'Main 10' | 'Baseline';
    video_scan_type: 'Interlaced' | 'Progressive';
    video_frame_rate: number;
    video_resolution_width: number;
    video_resolution_height: number;
    primary_audio_codec: 'AAC-LC' | 'HE-AAC' | 'MP2';
    primary_audio_channel: 'Monaural' | 'Stereo' | '5.1ch';
    primary_audio_sampling_rate: number;
    secondary_audio_codec: 'AAC-LC' | 'HE-AAC' | 'MP2' | null;
    secondary_audio_channel: 'Monaural' | 'Stereo' | '5.1ch' | null;
    secondary_audio_sampling_rate: number | null;
    cm_sections: { start_time: number; end_time: number; }[];
}

/** 録画ファイル情報を表すインターフェースのデフォルト値 */
export const IRecordedVideoDefault: IRecordedVideo = {
    id: -1,
    file_path: '',
    file_hash: '',
    file_size: 0,
    recording_start_time: null,
    recording_end_time: null,
    duration: 0,
    container_format: 'MPEG-TS',
    video_codec: 'MPEG-2',
    video_codec_profile: 'High',
    video_scan_type: 'Interlaced',
    video_frame_rate: 29.97,
    video_resolution_width: 1440,
    video_resolution_height: 1080,
    primary_audio_codec: 'AAC-LC',
    primary_audio_channel: 'Stereo',
    primary_audio_sampling_rate: 48000,
    secondary_audio_codec: null,
    secondary_audio_channel: null,
    secondary_audio_sampling_rate: null,
    cm_sections: [],
};

/** 録画番組情報を表すインターフェース */
export interface IRecordedProgram {
    id: number;
    recorded_video: IRecordedVideo;
    recording_start_margin: number;
    recording_end_margin: number;
    is_partially_recorded: boolean;
    channel: IChannel | null;
    network_id: number | null;
    service_id: number | null;
    event_id: number | null;
    series_id: number | null;
    series_broadcast_period_id: number | null;
    title: string;
    series_title: string | null;
    episode_number: string | null;
    subtitle: string | null;
    description: string;
    detail: { [key: string]: string };
    start_time: string;
    end_time: string;
    duration: number;
    is_free: boolean;
    genres: { major: string; middle: string; }[];
    primary_audio_type: string;
    primary_audio_language: string;
    secondary_audio_type: string | null;
    secondary_audio_language: string | null;
}

/** 録画番組情報を表すインターフェースのデフォルト値 */
export const IRecordedProgramDefault: IRecordedProgram = {
    id: -1,
    recorded_video: IRecordedVideoDefault,
    recording_start_margin: 0,
    recording_end_margin: 0,
    is_partially_recorded: false,
    channel: null,
    network_id: null,
    service_id: null,
    event_id: null,
    series_id: null,
    series_broadcast_period_id: null,
    title: '取得中…',
    series_title: null,
    episode_number: null,
    subtitle: null,
    description: '取得中…',
    detail: {},
    start_time: '2000-01-01T00:00:00+09:00',
    end_time: '2000-01-01T00:00:00+09:00',
    duration: 0,
    is_free: true,
    genres: [],
    primary_audio_type: '2/0モード(ステレオ)',
    primary_audio_language: '日本語',
    secondary_audio_type: null,
    secondary_audio_language: null,
};

/** 録画番組情報リストを表すインターフェース */
export interface IRecordedPrograms {
    total: number;
    recorded_programs: IRecordedProgram[];
}

/** 過去ログコメントを表すインターフェース */
export interface IJikkyoComment {
    time: number;
    type: 'top' | 'right' | 'bottom';
    size: 'big' | 'medium' | 'small';
    color: string;
    author: string;
    text: string;
}

/** 過去ログコメントのリストを表すインターフェース */
export interface IJikkyoComments {
    is_success: boolean;
    comments: IJikkyoComment[];
    detail: string;
}


class Videos {

    /**
     * ニコニコ実況の過去ログコメントを取得する
     * KonomiTV と異なり、直接過去ログ API にアクセスさせるように適当に改造してある
     * @param recorded_program 録画番組情報
     * @returns 過去ログコメントのリスト
     */
    static async fetchVideoJikkyoComments(recorded_program: IRecordedProgram): Promise<IJikkyoComments> {

        // API リクエストを実行
        const start_time = new Date(recorded_program.start_time).getTime() / 1000;
        const end_time = new Date(recorded_program.end_time).getTime() / 1000;
        const jikkyo_id = recorded_program.channel!.id;
        const kakolog_api_url = `https://jikkyo.tsukumijima.net/api/kakolog/${jikkyo_id}?starttime=${start_time}&endtime=${end_time}&format=json`;

        const response = await APIClient.get(kakolog_api_url, { timeout: 30000 });

        // エラー処理
        if (response.type === 'error') {
            let detail;
            switch (response.status) {
                case 500:
                    detail = '過去ログ API でサーバーエラーが発生しました。過去ログ API に不具合がある可能性があります。(HTTP Error 500)';
                    break;
                case 503:
                    detail = '現在、過去ログ API は一時的に利用できなくなっています。(HTTP Error 503)';
                    break;
                default:
                    detail = `現在、過去ログ API でエラーが発生しています。(HTTP Error ${response.status})`;
            }
            APIClient.showGenericError(response, detail);
            return {
                is_success: false,
                comments: [],
                detail: detail,
            };
        }

        const kakolog_api_response_json = await response.data as { error?: string; packet: any[] };
        if ('error' in kakolog_api_response_json) {
            return {
                is_success: false,
                comments: [],
                detail: kakolog_api_response_json.error || '過去ログコメントを取得できませんでした。',
            };
        }

        const raw_jikkyo_comments = kakolog_api_response_json.packet as { chat: { content: string; date: string; date_usec: string; deleted: string; mail: string; user_id: string; } }[];
        if (raw_jikkyo_comments.length === 0) {
            return {
                is_success: false,
                comments: [],
                detail: 'この録画番組の過去ログコメントは存在しないか、現在取得中です。',
            };
        }

        const jikkyo_comments = raw_jikkyo_comments.map((raw_jikkyo_comment) => {
            const comment = raw_jikkyo_comment.chat.content;
            if (typeof comment !== 'string' || comment === '' || raw_jikkyo_comment.chat.deleted === '1' || /\/[a-z]+ /.test(comment)) {
                return null;
            }

            const parsed_comment_command = CommentUtils.parseCommentCommand(raw_jikkyo_comment.chat.mail);
            // rekari が true の時は color 内の 16 進数カラーコードの末尾に C0 を付与して半透明にする
            const color = raw_jikkyo_comment.chat.user_id.startsWith('rekari:') ? parsed_comment_command.color + 'C0' : parsed_comment_command.color;
            const position = parsed_comment_command.position;
            const size = parsed_comment_command.size;
            const chat_date = parseInt(raw_jikkyo_comment.chat.date);
            const chat_date_usec = parseInt(raw_jikkyo_comment.chat.date_usec || '0', 10);
            const comment_time = parseFloat(`${chat_date - start_time}.${chat_date_usec}`);
            const comment_data = {
                time: comment_time,
                type: position,
                size: size,
                color: color,
                author: raw_jikkyo_comment.chat.user_id || '',
                text: comment,
            };
            // ミュート対象のコメントをここで除外
            if (CommentUtils.isMutedComment(comment_data.text, comment_data.author, comment_data.color, comment_data.type, comment_data.size)) {
                return null;
            }
            return comment_data;
        }).filter((comment): comment is IJikkyoComment => comment !== null);

        return {
            is_success: true,
            comments: jikkyo_comments,
            detail: '過去ログコメントを取得しました。',
        };
    }
}

export default Videos;
