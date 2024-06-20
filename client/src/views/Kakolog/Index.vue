<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <div class="px-5 py-8" style="width: 100%; max-width: 850px; margin: 0 auto; line-height: 1.65;">
                <h1>過去ログ再生</h1>
                <p class="mt-4 text-text-darken-1">
                    <strong><a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> に保存されている、2009年11月から現在までの 旧ニコニコ実況・ニコ生統合後の新ニコニコ実況・NX-Jikkyo のすべての過去ログから、チャンネルと日付時刻を選択して再生できます。</strong><br>
                </p>
                <div class="mt-8" style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px;">
                    <v-text-field type="date" color="primary" variant="outlined" label="開始日時" class="datetime-field">
                    </v-text-field>
                    <v-text-field type="time" color="primary" variant="outlined" label="開始時刻" class="datetime-field">
                    </v-text-field>
                </div>
                <div class="mt-6" style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px;">
                    <v-text-field type="date" color="primary" variant="outlined" label="終了日時" class="datetime-field">
                    </v-text-field>
                    <v-text-field type="time" color="primary" variant="outlined" label="終了時刻" class="datetime-field">
                    </v-text-field>
                </div>
            </div>
        </main>
    </div>
</template>
<script lang="ts" setup>

import HeaderBar from '@/components/HeaderBar.vue';
import Navigation from '@/components/Navigation.vue';

</script>
<style lang="scss">

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
