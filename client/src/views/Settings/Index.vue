<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <v-card class="settings-container d-flex px-5 py-5 mx-auto" elevation="0" width="100%" max-width="1000">
                <nav class="settings-navigation">
                    <h1 class="mt-2" style="font-size: 24px;">設定</h1>
                    <v-btn variant="flat" class="settings-navigation__button mt-6" to="/settings/general">
                        <Icon icon="fa-solid:sliders-h" width="26px" style="padding: 0 3px;" />
                        <span class="ml-4">全般</span>
                    </v-btn>
                    <!-- <v-btn variant="flat" class="settings-navigation__button" to="/settings/account">
                        <Icon icon="fluent:person-20-filled" width="26px" />
                        <span class="ml-4">アカウント</span>
                    </v-btn> -->
                    <v-btn variant="flat" class="settings-navigation__button" to="/settings/jikkyo">
                        <Icon icon="bi:chat-left-text-fill" width="26px" style="padding: 0 2px;" />
                        <span class="ml-4">実況</span>
                    </v-btn>
                    <v-btn variant="flat" class="settings-navigation__button settings-navigation__button--version"
                        :class="{'settings-navigation__button--version-highlight': versionStore.is_update_available}"
                        href="https://github.com/tsukumijima/NXJikkyo">
                        <Icon icon="fluent:info-16-regular" width="26px" />
                        <span class="ml-4">
                            version {{versionStore.client_version}}{{versionStore.is_update_available ? ' (Update Available)' : ''}}
                        </span>
                    </v-btn>
                </nav>
            </v-card>
        </main>
    </div>
</template>
<script lang="ts">

import { mapStores } from 'pinia';
import { defineComponent } from 'vue';

import HeaderBar from '@/components/HeaderBar.vue';
import Navigation from '@/components/Navigation.vue';
import useVersionStore from '@/stores/VersionStore';

export default defineComponent({
    name: 'Settings-Index',
    components: {
        HeaderBar,
        Navigation,
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

.settings-container {
    background: rgb(var(--v-theme-background)) !important;
    width: 100%;
    min-width: 0;
    @include smartphone-horizontal {
        padding: 16px 20px !important;
    }
    @include smartphone-horizontal-short {
        padding: 16px 16px !important;
    }
    @include smartphone-vertical {
        padding: 16px 16px !important;
    }

    .settings-navigation {
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        width: 100%;
        transform: none !important;
        visibility: visible !important;

        .settings-navigation__button {
            justify-content: left !important;
            width: 100%;
            height: 54px;
            margin-bottom: 6px;
            border-radius: 6px;
            font-size: 16px;
            color: rgb(var(--v-theme-text)) !important;
            background: rgb(var(--v-theme-background-lighten-1)) !important;

            &--version {
                display: none;
                @include smartphone-vertical {
                    display: flex;
                }
                &-highlight {
                    color: rgb(var(--v-theme-secondary-lighten-1)) !important;
                }
            }
        }

        h1 {
            @include smartphone-horizontal {
                font-size: 22px !important;
            }
        }
    }
}

</style>
