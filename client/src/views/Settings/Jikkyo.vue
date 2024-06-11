<template>
    <!-- ベース画面の中にそれぞれの設定画面で異なる部分を記述する -->
    <SettingsBase>
        <h2 class="settings__heading">
            <a v-ripple class="settings__back-button" @click="$router.back()">
                <Icon icon="fluent:arrow-left-12-filled" width="25px" />
            </a>
            <Icon icon="bi:chat-left-text-fill" width="19px" />
            <span class="ml-3">コメント/実況</span>
        </h2>
        <div class="settings__content" :class="{'settings__content--loading': is_loading}">
            <div class="settings__item-label mt-0" style="border-left: 3px solid rgb(var(--v-theme-text)); padding-left: 12px;">
                コメントの透明度は、コメントプレイヤー下にある設定アイコン ⚙️ から変更できます。<br>
            </div>
            <div class="settings__item">
                <div class="settings__item-heading">コメントのミュート設定</div>
                <div class="settings__item-label">
                    表示したくないコメントを、映像上やコメントリストに表示しないようにミュートできます。<br>
                </div>
                <div class="settings__item-label mt-2">
                    デフォルトでは、下記のミュート設定がオンになっています。<br>
                    これらのコメントも表示したい方は、適宜オフに設定してください。<br>
                    <ul class="ml-5 mt-2">
                        <li>露骨な表現を含むコメントをミュートする</li>
                        <li>ネガティブな表現、差別的な表現、政治的に偏った表現を含むコメントをミュートする</li>
                        <li>文字サイズが大きいコメントをミュートする</li>
                    </ul>
                </div>
            </div>
            <v-btn class="settings__save-button mt-4" variant="flat" @click="comment_mute_settings_modal = !comment_mute_settings_modal">
                <Icon icon="heroicons-solid:filter" height="19px" />
                <span class="ml-1">コメントのミュート設定を開く</span>
            </v-btn>
            <div class="settings__item">
                <div class="settings__item-heading">コメントの速さ</div>
                <div class="settings__item-label">
                    プレイヤーに流れるコメントの速さを設定します。<br>
                    たとえば 1.2 に設定すると、コメントが 1.2 倍速く流れます。<br>
                </div>
                <v-slider class="settings__item-form" color="primary" show-ticks="always" thumb-label hide-details
                    :step="0.1" :min="0.5" :max="2" v-model="settingsStore.settings.comment_speed_rate">
                </v-slider>
            </div>
            <div class="settings__item">
                <div class="settings__item-heading">コメントの文字サイズ</div>
                <div class="settings__item-label">
                    プレイヤーに流れるコメントの文字サイズの基準値を設定します。<br>
                    実際の文字サイズは画面サイズに合わせて調整されます。デフォルトの文字サイズは 34px です。<br>
                </div>
                <v-slider class="settings__item-form" color="primary" show-ticks="always" thumb-label hide-details
                    :step="1" :min="20" :max="60" v-model="settingsStore.settings.comment_font_size">
                </v-slider>
            </div>
            <div class="settings__item settings__item--switch">
                <label class="settings__item-heading" for="close_comment_form_after_sending">コメント送信後にコメント入力フォームを閉じる</label>
                <label class="settings__item-label" for="close_comment_form_after_sending">
                    この設定をオンにすると、コメントを送信した後に、コメント入力フォームが自動で閉じるようになります。<br>
                    なお、コメント入力フォームが表示されたままだと、大半のショートカットキーが文字入力と競合して使えなくなります。ショートカットキーを頻繁に使う方はオンにしておくのがおすすめです。<br>
                </label>
                <v-switch class="settings__item-switch" color="primary" id="close_comment_form_after_sending" hide-details
                    v-model="settingsStore.settings.close_comment_form_after_sending">
                </v-switch>
            </div>
        </div>
        <CommentMuteSettings :modelValue="comment_mute_settings_modal" @update:modelValue="comment_mute_settings_modal = $event" />
    </SettingsBase>
</template>
<script lang="ts">

import { mapStores } from 'pinia';
import { defineComponent } from 'vue';

import CommentMuteSettings from '@/components/Settings/CommentMuteSettings.vue';
import useSettingsStore from '@/stores/SettingsStore';
import useUserStore from '@/stores/UserStore';
import SettingsBase from '@/views/Settings/Base.vue';

export default defineComponent({
    name: 'Settings-Jikkyo',
    components: {
        SettingsBase,
        CommentMuteSettings,
    },
    data() {
        return {

            // コメントのミュート設定のモーダルを表示するか
            comment_mute_settings_modal: false,

            // ローディング中かどうか
            is_loading: true,
        };
    },
    computed: {
        ...mapStores(useSettingsStore, useUserStore),
    },
    async created() {

        // アカウント情報を更新
        await this.userStore.fetchUser();

        // ローディング状態を解除
        this.is_loading = false;
    }
});

</script>
<style lang="scss" scoped>

.settings__content {
    opacity: 1;
    transition: opacity 0.4s;

    &--loading {
        opacity: 0;
    }
}

.niconico-account {
    display: flex;
    align-items: center;
    height: 120px;
    padding: 20px;
    border-radius: 15px;
    background: rgb(var(--v-theme-background-lighten-2));
    @include tablet-horizontal {
        align-items: normal;
        flex-direction: column;
        height: auto;
        padding: 16px;
    }
    @include tablet-vertical {
        align-items: normal;
        flex-direction: column;
        height: auto;
        padding: 16px;
        .niconico-account-wrapper {
            .niconico-account__info {
                margin-left: 16px !important;
                margin-right: 0 !important;
                &-name-text {
                    font-size: 18.5px;
                }
                &-description {
                    font-size: 13.5px;
                }
            }
        }
    }
    @include smartphone-horizontal {
        align-items: normal;
        flex-direction: column;
        height: auto;
        padding: 16px;
        border-radius: 10px;
        .niconico-account-wrapper {
            .niconico-account__info {
                margin-right: 0 !important;
            }
        }
    }
    @include smartphone-horizontal-short {
        .niconico-account-wrapper {
            .niconico-account__info {
                margin-left: 16px !important;
                &-name-text {
                    font-size: 18px;
                }
                &-description {
                    font-size: 13px;
                }
            }
        }
    }
    @include smartphone-vertical {
        align-items: normal;
        flex-direction: column;
        height: auto;
        padding: 16px 12px;
        border-radius: 10px;
        .niconico-account-wrapper {
            .niconico-account__info {
                margin-left: 12px !important;
                margin-right: 0px !important;
                &-name-text {
                    font-size: 17px;
                }
                &-description {
                    font-size: 13px;
                }
            }
        }
    }

    &--anonymous {
        @include tablet-vertical {
            .niconico-account__login {
                margin-top: 12px;
            }
        }
        @include smartphone-horizontal {
            .niconico-account__login {
                margin-top: 12px;
            }
        }
        @include smartphone-horizontal-short {
            .niconico-account-wrapper {
                svg {
                    display: none;
                }
                .niconico-account__info {
                    margin-left: 0 !important;
                }
            }
        }
        @include smartphone-vertical {
            padding-top: 20px;
            .niconico-account__login {
                margin-top: 16px;
            }
            .niconico-account-wrapper {
                svg {
                    display: none;
                }
                .niconico-account__info {
                    margin-left: 0 !important;
                    margin-right: 0 !important;
                }
            }
        }
    }

    &-wrapper {
        display: flex;
        align-items: center;
        min-width: 0;
        height: 80px;
        @include smartphone-vertical {
            height: 60px;
        }
    }

    &__icon {
        flex-shrink: 0;
        min-width: 80px;
        height: 100%;
        border-radius: 50%;
        object-fit: cover;
        // 読み込まれるまでのアイコンの背景
        background: linear-gradient(150deg, rgb(var(--v-theme-gray)), rgb(var(--v-theme-background-lighten-2)));
        // 低解像度で表示する画像がぼやけないようにする
        // ref: https://sho-log.com/chrome-image-blurred/
        image-rendering: -webkit-optimize-contrast;
        @include smartphone-vertical {
            width: 60px;
            min-width: 60px;
            height: 60px;
        }
    }

    &__info {
        display: flex;
        flex-direction: column;
        min-width: 0;
        margin-left: 20px;
        margin-right: 16px;

        &-name {
            display: inline-flex;
            align-items: center;
            height: 33px;
            @include smartphone-vertical {
                height: auto;
            }

            &-text {
                display: inline-block;
                font-size: 20px;
                color: rgb(var(--v-theme-text));
                font-weight: bold;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;  // はみ出た部分を … で省略
            }
        }

        &-description {
            display: inline-block;
            margin-top: 4px;
            color: rgb(var(--v-theme-text-darken-1));
            font-size: 14px;
        }
    }

    &__login {
        border-radius: 7px;
        font-size: 16px;
        letter-spacing: 0;
        @include tablet-horizontal {
            height: 50px !important;
            margin-top: 12px;
            margin-right: auto;
        }
        @include tablet-vertical {
            height: 42px !important;
            margin-top: 8px;
            margin-right: auto;
            font-size: 14.5px;
        }
        @include smartphone-horizontal {
            height: 42px !important;
            margin-top: 8px;
            margin-right: auto;
            font-size: 14.5px;
        }
        @include smartphone-vertical {
            height: 42px !important;
            margin-top: 16px;
            margin-right: auto;
            font-size: 14.5px;
        }
    }
}

</style>
