<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <div class="px-5 py-8" style="width: 100%; max-width: 860px; margin: 0 auto; line-height: 1.65;">
                <h1>過去ログ再生</h1>
                <p class="mt-4 text-text-darken-1">
                    <strong><a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> に保存されている、2009年11月から現在までの 旧ニコニコ実況 (2009/11/28 ~ 2020/12/15)・ニコ生統合後の新ニコニコ実況 (2020/12/15 ~ 2024/06/08)・NX-Jikkyo (2024/06/10 ~)・ニコニコ実況 (Re:仮) (2024/07/20 ~ 2024/08/05)・暫定復旧版ニコニコ実況 (2024/08/05 ~ 2024/08/22)・本復旧後のニコニコ実況 (2024/08/22 ~) のほぼすべての過去ログを、チャンネルと日時範囲を指定して再生できます。</strong><br>
                </p>
                <p class="mt-2 text-text-darken-1">
                    十数年分もの膨大な過去ログデータには、当時の世相が色濃く反映された、その時代を生きた「生の声」が、まるでタイムカプセルのように刻まれています。<br>
                    たまには昔のコメントを眺めて懐かしんだり、録画番組をコメント付きで楽しんでみては？
                </p>
                <v-select class="mt-8 datetime-field" color="primary" variant="outlined" hide-details label="実況チャンネル"
                    :items="jikkyo_channel_items" v-model="jikkyo_channel_id">
                </v-select>
                <div class="mt-3 d-flex align-center justify-space-between">
                    <span v-if="is_restored_from_local_storage" class="text-text-darken-1" style="font-size: 14px;">
                        前回の設定を復元しています
                    </span>
                    <span v-else></span>
                    <v-btn variant="text" color="primary" size="small" @click="resetToCurrentDateTime()">
                        現在日時にリセット
                    </v-btn>
                </div>
                <div class="mt-8" style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px;">
                    <v-text-field type="date" class="datetime-field" color="primary" variant="outlined" label="開始日付"
                        min="2009-11-26" :max="dayjs().format('YYYY-MM-DD')" v-model="start_date">
                    </v-text-field>
                    <v-text-field type="time" class="datetime-field" color="primary" variant="outlined" label="開始時刻"
                        v-model="start_time">
                    </v-text-field>
                </div>
                <div class="d-flex justify-space-around" style="font-family: 'Open Sans','YakuHanJPs','Twemoji','Hiragino Sans','Noto Sans JP',sans-serif;">
                    <div class="d-flex" style="column-gap: 8px;">
                        <v-btn variant="flat" color="background-lighten-2" height="46" class="px-2" style="font-size: 15px;"
                            @click="addMinutes(-30)">
                            －30分
                        </v-btn>
                        <v-btn variant="flat" color="background-lighten-2" height="46" class="px-2" style="font-size: 15px;"
                            @click="addMinutes(-5)">
                            －5分
                        </v-btn>
                    </div>
                    <v-btn variant="flat" color="secondary" height="46" class="px-2"
                        v-ftooltip.top="'開始日時を終了日時に設定'"
                        @click="end_date = start_date; end_time = start_time">
                        <Icon icon="fluent:chevron-double-down-16-filled" height="40px" />
                    </v-btn>
                    <div class="d-flex" style="column-gap: 8px;">
                        <v-btn variant="flat" color="background-lighten-2" height="46" class="px-2" style="font-size: 15px;"
                            @click="addMinutes(5)">
                            ＋5分
                        </v-btn>
                        <v-btn variant="flat" color="background-lighten-2" height="46" class="px-2" style="font-size: 15px;"
                            @click="addMinutes(30)">
                            ＋30分
                        </v-btn>
                    </div>
                </div>
                <div class="mt-6" style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px;">
                    <v-text-field type="date" class="datetime-field" color="primary" variant="outlined" label="終了日付"
                        min="2009-11-26" :max="dayjs().format('YYYY-MM-DD')" v-model="end_date">
                    </v-text-field>
                    <v-text-field type="time" class="datetime-field" color="primary" variant="outlined" label="終了時刻"
                        v-model="end_time">
                    </v-text-field>
                </div>
                <div class="mt-2 d-flex justify-space-around">
                    <v-btn variant="flat" color="secondary" height="54" @click="playKakolog()">
                        <Icon icon="fluent:receipt-play-20-regular" height="32px" />
                        <span class="ml-2" style="font-size: 17px;">過去ログを再生</span>
                    </v-btn>
                </div>
            </div>
        </main>
    </div>
</template>
<script lang="ts" setup>

import { ref } from 'vue';
import { useRouter } from 'vue-router';

import HeaderBar from '@/components/HeaderBar.vue';
import Navigation from '@/components/Navigation.vue';
import Message from '@/message';
import useChannelsStore from '@/stores/ChannelsStore';
import { dayjs } from '@/utils';
import {
    resetKakologFormStateToCurrentDateTime,
    useKakologState,
    validateKakologFormState,
} from '@/views/Kakolog/KakologState';

const router = useRouter();

// 実況チャンネルの選択肢を生成
const jikkyo_channel_items = ref<{ title: string; value: string }[]>([]);
const channels_store = useChannelsStore();
channels_store.update().then(() => {
    const channels = [...channels_store.channels_list['GR'], ...channels_store.channels_list['BS']];
    jikkyo_channel_items.value = channels.map((channel) => ({
        title: `Ch:${channel.channel_number} (${channel.id}) : ${channel.name}`,
        value: channel.id,
    }));
});

// useKakologState から状態を取得
const kakolog_state = useKakologState();
const {
    jikkyo_channel_id,
    start_date,
    start_time,
    end_date,
    end_time,
    is_restored_from_local_storage,
} = kakolog_state;

// フォームを現在日時ベースのデフォルト値に戻す
function resetToCurrentDateTime() {
    resetKakologFormStateToCurrentDateTime(kakolog_state);
}

// -30分/-5分/+5分/+30分 を終了日時両方に反映する
// もちろん日付の繰り上がり/繰り下がりに対応する
function addMinutes(minutes: number) {

    // 現在の終了日時を取得
    const current_end = dayjs(`${end_date.value} ${end_time.value}`);

    // Invalid Date の場合は無視
    if (!current_end.isValid()) {
        return;
    }

    // 指定された分数を加算
    const new_end = current_end.add(minutes, 'minute');

    // 新しい終了日時を設定
    end_date.value = new_end.format('YYYY-MM-DD');
    end_time.value = new_end.format('HH:mm');
}

function playKakolog() {

    const form = {
        jikkyo_channel_id: jikkyo_channel_id.value,
        start_date: start_date.value,
        start_time: start_time.value,
        end_date: end_date.value,
        end_time: end_time.value,
    };

    const validation_error = validateKakologFormState(form);
    if (validation_error !== null) {
        Message.error(validation_error);
        return;
    }

    const start_datetime = dayjs(`${form.start_date} ${form.start_time}`);
    const end_datetime = dayjs(`${form.end_date} ${form.end_time}`);

    // 開始日時-終了日時の ID を 20191002213500-20191002215600 のようなフォーマットで組み立てる
    const id = `${start_datetime.format('YYYYMMDDHHmmss')}-${end_datetime.format('YYYYMMDDHHmmss')}`;
    router.push({ path: `/log/${jikkyo_channel_id.value}/${id}` });
}

</script>
<style lang="scss">

.datetime-field input[type="date"],
.datetime-field input[type="time"] {
    display: block !important;
    font-size: 18.5px;
    font-family: 'Open Sans', 'YakuHanJPs', 'Twemoji', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
}
.datetime-field .v-select__selection-text {
    font-family: 'Open Sans', 'YakuHanJPs', 'Twemoji', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
}

.datetime-field input[type="date"]::-webkit-calendar-picker-indicator {
    width: 20px;
    height: 20px;
    cursor: pointer;
}
.datetime-field input[type="time"]::-webkit-calendar-picker-indicator {
    width: 20px;
    height: 20px;
    cursor: pointer;
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
