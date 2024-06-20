<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <div class="px-5 py-8" style="width: 100%; max-width: 850px; margin: 0 auto; line-height: 1.65;">
                <h1>過去ログ再生</h1>
                <p class="mt-4 text-text-darken-1">
                    <strong><a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> に保存されている、2009年11月から現在までの 旧ニコニコ実況・ニコ生統合後の新ニコニコ実況・NX-Jikkyo のすべての過去ログを、チャンネルと日時範囲を指定して再生できます。</strong><br>
                </p>
                <v-select class="mt-8" color="primary" variant="outlined" hide-details label="実況チャンネル"
                    :items="jikkyo_channel_items" v-model="jikkyo_channel_id">
                </v-select>
                <div class="mt-9" style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px;">
                    <v-text-field type="date" color="primary" variant="outlined" label="開始日付" class="datetime-field" v-model="start_date">
                    </v-text-field>
                    <v-text-field type="time" color="primary" variant="outlined" label="開始時刻" class="datetime-field" v-model="start_time">
                    </v-text-field>
                </div>
                <div class="d-flex justify-space-around">
                    <div class="d-flex" style="column-gap: 8px;">
                        <v-btn variant="flat" color="background-lighten-2" height="46" style="font-size: 16px;"
                            @click="addMinutes(-30)">
                            －30分
                        </v-btn>
                        <v-btn variant="flat" color="background-lighten-2" height="46" style="font-size: 16px;"
                            @click="addMinutes(-5)">
                            －5分
                        </v-btn>
                    </div>
                    <v-btn variant="flat" color="secondary" width="54" height="46"
                        v-tooltip.top="'開始日時を終了日時に反映する'"
                        @click="end_date = start_date; end_time = start_time">
                        <Icon icon="fluent:chevron-double-down-16-filled" height="40px" />
                    </v-btn>
                    <div class="d-flex" style="column-gap: 8px;">
                        <v-btn variant="flat" color="background-lighten-2" height="46" style="font-size: 16px;"
                            @click="addMinutes(5)">
                            ＋5分
                        </v-btn>
                        <v-btn variant="flat" color="background-lighten-2" height="46" style="font-size: 16px;"
                            @click="addMinutes(30)">
                            ＋30分
                        </v-btn>
                    </div>
                </div>
                <div class="mt-6" style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px;">
                    <v-text-field type="date" color="primary" variant="outlined" label="終了日付" class="datetime-field" v-model="end_date">
                    </v-text-field>
                    <v-text-field type="time" color="primary" variant="outlined" label="終了時刻" class="datetime-field" v-model="end_time">
                    </v-text-field>
                </div>
                <div class="mt-2 d-flex justify-space-around">
                    <v-btn variant="flat" color="secondary" height="46">
                        <Icon icon="fluent:receipt-play-20-regular" height="32px" />
                        <span class="ml-2" style="font-size: 17px;">過去ログを再生開始</span>
                    </v-btn>
                </div>
            </div>
        </main>
    </div>
</template>
<script lang="ts" setup>

import { ref } from 'vue';

import HeaderBar from '@/components/HeaderBar.vue';
import Navigation from '@/components/Navigation.vue';
import useChannelsStore from '@/stores/ChannelsStore';
import { dayjs } from '@/utils';

// 実況チャンネルの選択肢を生成
const jikkyo_channel_items = ref<{ title: string; value: string }[]>([]);
const channels_store = useChannelsStore();
channels_store.update().then(() => {
    const channels = [...channels_store.channels_list['GR'], ...channels_store.channels_list['BS']];
    jikkyo_channel_items.value = channels.map((channel) => ({
        title: `${channel.id}: ${channel.name}`,
        value: channel.id,
    }));
});

// 実況チャンネル ID
const jikkyo_channel_id = ref('jk1');

// 現在日時を取得し、分と秒を0に設定
const now = dayjs().minute(0).second(0);

// 開始日時（終了日時の1時間前）
const start_date = ref(now.subtract(1, 'hour').format('YYYY-MM-DD'));
const start_time = ref(now.subtract(1, 'hour').format('HH:mm'));

// 終了日時（現在日時の分と秒を0にしたもの）
const end_date = ref(now.format('YYYY-MM-DD'));
const end_time = ref(now.format('HH:mm'));

// -30分/-5分/+5分/+30分 を終了日時両方に反映する
// もちろん日付の繰り上がり/繰り下がりに対応する
function addMinutes(minutes: number) {

    // 現在の終了日時を取得
    const current_end = dayjs(`${end_date.value} ${end_time.value}`);

    // 指定された分数を加算
    const new_end = current_end.add(minutes, 'minute');

    // 新しい終了日時を設定
    end_date.value = new_end.format('YYYY-MM-DD');
    end_time.value = new_end.format('HH:mm');
}

</script>
<style lang="scss">

.datetime-field input[type="date"],
.datetime-field input[type="time"] {
    font-size: 18.5px;
}

.datetime-field input[type="date"]::-webkit-calendar-picker-indicator,
.datetime-field input[type="time"]::-webkit-calendar-picker-indicator {
    position: absolute;
    top: 17px;
    right: 16px;
    bottom: 0;
    width: 20px;
    height: 20px;
}

</style>
<style lang="scss" scoped>

blockquote {
    border-left: 3px solid rgb(var(--v-theme-secondary));
    background-color: rgb(var(--v-theme-background-lighten-1));
    padding: 12px 16px;
    border-radius: 4px;
}
hr {
    border-color: rgb(var(--v-theme-text-darken-2));
}

</style>
