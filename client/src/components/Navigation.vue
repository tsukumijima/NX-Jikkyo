<template>
    <div>
        <div class="navigation-container elevation-8">
            <nav class="navigation">
                <div class="navigation-scroll">
                    <router-link v-ripple class="navigation__link" active-class="navigation__link--active" to="/"
                        :class="{'navigation__link--active': $route.path.startsWith('/')}">
                        <Icon class="navigation__link-icon" icon="fluent:tv-20-regular" width="26px" />
                        <span class="navigation__link-text">テレビ実況</span>
                    </router-link>
                    <v-spacer></v-spacer>
                    <router-link v-ripple class="navigation__link" active-class="navigation__link--active" to="/settings/"
                        :class="{'navigation__link--active': $route.path.startsWith('/settings')}">
                        <Icon class="navigation__link-icon" icon="fluent:settings-20-regular" width="26px" />
                        <span class="navigation__link-text">設定</span>
                    </router-link>
                    <a v-ripple class="navigation__link" active-class="navigation__link--active" href="https://github.com/tsukumijima/NX-Jikkyo"
                        :class="{
                            'navigation__link--develop-version': versionStore.is_client_develop_version,
                            'navigation__link--highlight': versionStore.is_update_available,
                        }"
                        v-tooltip.top="versionStore.is_update_available ?
                            `アップデートがあります (version ${versionStore.latest_version})` : ''">
                        <Icon class="navigation__link-icon" icon="fluent:info-16-regular" width="26px" />
                        <span class="navigation__link-text">version {{versionStore.client_version}}</span>
                    </a>
                </div>
            </nav>
        </div>
        <BottomNavigation />
    </div>
</template>
<script lang="ts">

import { mapStores } from 'pinia';
import { defineComponent } from 'vue';

import BottomNavigation from '@/components/BottomNavigation.vue';
import useVersionStore from '@/stores/VersionStore';

export default defineComponent({
    name: 'Navigation',
    components: {
        BottomNavigation,
    },
    computed: {
        ...mapStores(useVersionStore),
    },
    async created() {
        await this.versionStore.fetchServerVersion();
    }
});

</script>
<style lang="scss" scoped>

.navigation-container {
    flex-shrink: 0;
    width: 220px;  // .navigation を fixed にするため、浮いた分の幅を確保する
    background: rgb(var(--v-theme-background-lighten-1));
    @include smartphone-horizontal {
        width: 210px;
    }
    @include smartphone-horizontal-short {
        width: 190px;
    }
    @include smartphone-vertical {
        display: none;
    }

    .navigation {
        position: fixed;
        width: 220px;
        top: 65px;  // ヘッダーの高さ分
        left: 0px;
        // スマホ・タブレットのブラウザでアドレスバーが完全に引っ込むまでビューポートの高さが更新されず、
        // その間下に何も背景がない部分ができてしまうのを防ぐ
        bottom: -100px;
        padding-bottom: 100px;
        background: rgb(var(--v-theme-background-lighten-1));
        z-index: 1;
        @include smartphone-horizontal {
            top: 48px;
            width: 210px;
        }
        @include smartphone-horizontal-short {
            width: 190px;
        }

        .navigation-scroll {
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 22px 12px;
            overflow-y: auto;
            @include smartphone-horizontal {
                padding: 10px 12px;
            }
            @include smartphone-horizontal-short {
                padding: 10px 8px;
            }
            &::-webkit-scrollbar-track {
                background: rgb(var(--v-theme-background-lighten-1));
            }

            .navigation__link {
                display: flex;
                align-items: center;
                flex-shrink: 0;
                height: 52px;
                padding-left: 16px;
                margin-top: 4px;
                border-radius: 11px;
                font-size: 16px;
                color: rgb(var(--v-theme-text));
                transition: background-color 0.15s;
                text-decoration: none;
                user-select: none;
                @include smartphone-horizontal {
                    height: 40px;
                    padding-left: 12px;
                    border-radius: 9px;
                    font-size: 15px;
                }

                &:hover {
                    background: rgb(var(--v-theme-background-lighten-2));
                }
                &:first-of-type {
                    margin-top: 0;
                }
                &--active {
                    color: rgb(var(--v-theme-primary));
                    background: #e64f8840;
                    &:hover {
                        background: #e64f8840;
                    }
                }
                &--highlight {
                    color: rgb(var(--v-theme-secondary-lighten-1));
                }
                &--develop-version {
                    font-size: 15px;
                    @include smartphone-horizontal {
                        font-size: 14.5px;
                    }
                }

                .navigation__link-icon {
                    margin-right: 14px;
                    @include smartphone-horizontal {
                        margin-right: 10px;
                    }
                }
            }
        }
    }
}

</style>
