<template>
    <Watch :playback_mode="'Video'" />
</template>
<script lang="ts">

import { mapStores } from 'pinia';
import { defineComponent } from 'vue';

import Watch from '@/components/Watch/Watch.vue';
import { IChannel } from '@/services/Channels';
import PlayerController from '@/services/player/PlayerController';
import { IRecordedProgramDefault } from '@/services/Videos';
import useChannelsStore from '@/stores/ChannelsStore';
import usePlayerStore from '@/stores/PlayerStore';
import useSettingsStore from '@/stores/SettingsStore';
import Utils, { dayjs } from '@/utils';

// PlayerController のインスタンス
// data() 内に記述すると再帰的にリアクティブ化され重くなる上リアクティブにする必要自体がないので、グローバル変数にしている
let player_controller: PlayerController | null = null;

export default defineComponent({
    name: 'Kakolog-Watch',
    components: {
        Watch,
    },
    computed: {
        ...mapStores(usePlayerStore, useSettingsStore),
    },
    // 開始時に実行
    created() {

        // 下記以外の視聴画面の開始処理は Watch コンポーネントの方で自動的に行われる

        // 再生セッションを初期化
        this.init();
    },
    methods: {

        // 再生セッションを初期化する
        async init() {

            // 再生対象の過去ログの実況チャンネルの ID
            const display_channel_id = this.$route.params.display_channel_id as string;

            // 再生対象の過去ログの期間を示す ID (ex: 20191002213500-20191002215600)
            const kakolog_period_id = this.$route.params.kakolog_period_id as string;

            // それぞれ過去ログ開始日時と終了日時の dayjs に変換
            const kakolog_start_dayjs = dayjs(kakolog_period_id.split('-')[0]);
            const kakolog_end_dayjs = dayjs(kakolog_period_id.split('-')[1]);

            // 再生対象の過去ログの実況チャンネル情報を取得
            const channels_store = useChannelsStore();
            await channels_store.update();
            let channel: IChannel | null = null;
            if (display_channel_id.length <= 4) {
                // 地上波
                channel = channels_store.channels_list['GR'].find(channel => channel.id === display_channel_id) ?? null;
            } else {
                // BS
                channel = channels_store.channels_list['BS'].find(channel => channel.id === display_channel_id) ?? null;
            }
            if (channel === null) {
                this.$router.push({path: '/not-found/'});
                return;
            }

            // 録画番組情報をモックして錬成
            await Utils.sleep(0.1);
            const display_date = kakolog_start_dayjs.hour() < 4 ? kakolog_start_dayjs.subtract(1, 'day') : kakolog_start_dayjs;
            const recorded_program = structuredClone(IRecordedProgramDefault);
            recorded_program.id = -100;
            recorded_program.channel = channel;
            recorded_program.recorded_video.recording_start_time = kakolog_start_dayjs.toISOString();
            recorded_program.recorded_video.recording_end_time = kakolog_end_dayjs.toISOString();
            recorded_program.recording_start_margin = 0;
            recorded_program.recording_end_margin = 0;
            recorded_program.title = `${channel.name}【ニコニコ実況】${display_date.format('YYYY年MM月DD日')}`;
            recorded_program.description = `
                NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。<br>
                <div class="mt-1"></div>
                このページでは、ニコニコ実況 過去ログ API に保存されている、2009年11月から現在までの 旧ニコニコ実況・ニコ生統合後の新ニコニコ実況・NX-Jikkyo の過去ログを再生できます。
                <div class="mt-1"></div>
                現在は Ch:${channel.channel_number} ${channel.name} に ${display_date.format('YYYY年MM月DD日')} ${display_date.format('HH:mm')} 〜 ${kakolog_end_dayjs.format('HH:mm')} の期間に投稿されたコメントの過去ログを時系列に再生しています。
            `;
            recorded_program.start_time = kakolog_start_dayjs.toISOString();
            recorded_program.end_time = kakolog_end_dayjs.toISOString();
            recorded_program.duration = kakolog_end_dayjs.diff(kakolog_start_dayjs, 'second');
            this.playerStore.recorded_program = recorded_program;

            // PlayerController を初期化
            player_controller = new PlayerController('Video');
            await player_controller.init();
        },

        // 再生セッションを破棄する
        async destroy() {

            this.playerStore.recorded_program = IRecordedProgramDefault;

            // PlayerController を破棄
            if (player_controller !== null) {
                await player_controller.destroy();
                player_controller = null;
            }
        }
    }
});

</script>
