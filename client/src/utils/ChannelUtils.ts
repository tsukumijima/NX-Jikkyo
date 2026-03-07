
import type { ChannelType } from '@/services/Channels';


/**
 * チャンネル周りのユーティリティ
 */
export class ChannelUtils {

    /**
     * display_channel_id からチャンネルタイプを取得する
     * @param display_channel_id display_channel_id
     * @returns チャンネルタイプ (不正な display_channel_id の場合は null)
     */
    static getChannelType(display_channel_id: string): ChannelType | null {
        // try {
        //     const result = display_channel_id.match('(?<channel_type>[a-z]+)[0-9]+')!.groups!.channel_type.toUpperCase();
        //     switch (result) {
        //         case 'GR': return 'GR';
        //         case 'BS': return 'BS';
        //         case 'CS': return 'CS';
        //         case 'CATV': return 'CATV';
        //         case 'SKY': return 'SKY';
        //         case 'STARDIGIO': return 'STARDIGIO';
        //         // 正規表現ではエラーになっていないが、ChannelType のいずれにもマッチしない
        //         default: return null;
        //     }
        // } catch (e) {
        //     // 何かしらエラーが発生したということは display_channel_id が不正
        //     return null;
        // }

        // jk99x チャンネルは特設チャンネルで、特別に GR チャンネルとして扱う
        return display_channel_id.length <= 4 || display_channel_id.startsWith('jk99') ? 'GR' : 'BS';
    }


    /**
     * チャンネルの実況勢いから「多」「激多」「祭」を取得する
     * ref: https://ja.wikipedia.org/wiki/%E3%83%8B%E3%82%B3%E3%83%8B%E3%82%B3%E5%AE%9F%E6%B3%81
     * @param jikkyo_force チャンネルの実況勢い
     * @returns normal（普通）or many（多）or so-many（激多）or festival（祭）
     */
    static getChannelForceType(jikkyo_force: number | null): 'normal' | 'many' | 'so-many' | 'festival' {

        // 実況勢いが null（=対応する実況チャンネルがない）
        if (jikkyo_force === null) return 'normal';

        // 実況勢いが 500 コメント以上（祭）
        if (jikkyo_force >= 500) return 'festival';
        // 実況勢いが 200 コメント以上（激多）
        if (jikkyo_force >= 200) return 'so-many';
        // 実況勢いが 100 コメント以上（多）
        if (jikkyo_force >= 100) return 'many';

        // それ以外
        return 'normal';
    }

}
