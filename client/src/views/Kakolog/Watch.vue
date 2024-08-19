<template>
    <Watch :playback_mode="'Video'" />
</template>
<script lang="ts">

import { mapStores } from 'pinia';
import { defineComponent } from 'vue';

import Watch from '@/components/Watch/Watch.vue';
import Message from '@/message';
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

            // 終了日時が開始日時より前の場合はエラー
            if (kakolog_end_dayjs < kakolog_start_dayjs) {
                Message.error('指定された終了日時が開始日時より前です。');
                this.$router.push({path: '/not-found/'});
                return;
            }

            // 終了日時が未来の日付の場合はエラー
            if (kakolog_end_dayjs > dayjs()) {
                Message.error('指定された終了日時が未来の日付です。');
                this.$router.push({path: '/not-found/'});
                return;
            }

            // 開始日時と終了日時が同じ場合はエラー
            if (kakolog_start_dayjs.isSame(kakolog_end_dayjs)) {
                Message.error('指定された開始日時と終了日時が同じです。');
                this.$router.push({path: '/not-found/'});
                return;
            }

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
            recorded_program.title = `${channel.name}【ニコニコ実況${kakolog_start_dayjs.isAfter('2024-06-09') ? '+NX-Jikkyo' : ''}】${display_date.format('YYYY年MM月DD日')}`;
            recorded_program.description = '';
            recorded_program.detail = {
                '過去ログ再生について': (
                    '過去ログ再生機能では、ニコニコ実況 過去ログ API (https://jikkyo.tsukumijima.net) に保存されている、' +
                    '2009年11月から現在までのほぼすべての過去ログコメントを再生できます。\n\n' +
                    `現在は、Ch:${channel.channel_number} ${channel.name} の ${display_date.format('YYYY年MM月DD日 (dd)')} ${display_date.format('HH:mm')} 〜 ${kakolog_end_dayjs.format('HH:mm')} の過去ログコメントを、時系列に再生しています。`
                ),
                'NX-Jikkyo について': (
                    'NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。\n' +
                    'ニコニコ実況に投稿されたコメントも、NX-Jikkyo のコメントと一緒にまとめて再生できます。'
                ),
            };
            recorded_program.start_time = kakolog_start_dayjs.toISOString();
            recorded_program.end_time = kakolog_end_dayjs.toISOString();
            recorded_program.duration = kakolog_end_dayjs.diff(kakolog_start_dayjs, 'second');
            this.playerStore.recorded_program = recorded_program;

            // 現在表示中の過去ログのタイトルと概要を更新
            const title = `過去ログ再生 - Ch:${channel.channel_number} ${channel.name} ${display_date.format('YYYY年MM月DD日')} ${display_date.format('HH:mm')} 〜 ${kakolog_end_dayjs.format('HH:mm')} | NX-Jikkyo : ニコニコ実況避難所`;
            const description = '過去ログ再生機能では、ニコニコ実況 過去ログ API (https://jikkyo.tsukumijima.net) に保存されている、' +
                '2009年11月から現在までのほぼすべての過去ログコメントを再生できます。';
            document.title = title;
            const description_meta = document.querySelector('meta[name="description"]');
            if (description_meta) {
                description_meta.setAttribute('content', description);
            }
            const og_title_meta = document.querySelector('meta[property="og:title"]');
            if (og_title_meta) {
                og_title_meta.setAttribute('content', title);
            }
            const og_description_meta = document.querySelector('meta[property="og:description"]');
            if (og_description_meta) {
                og_description_meta.setAttribute('content', description);
            }
            const twitter_title_meta = document.querySelector('meta[name="twitter:title"]');
            if (twitter_title_meta) {
                twitter_title_meta.setAttribute('content', title);
            }
            const twitter_description_meta = document.querySelector('meta[name="twitter:description"]');
            if (twitter_description_meta) {
                twitter_description_meta.setAttribute('content', description);
            }

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
