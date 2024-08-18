<template>
    <header class="header">
        <router-link v-ripple class="nx-jikkyo-logo ml-3 ml-md-6" to="/">
            <img class="nx-jikkyo-logo__image" src="/assets/images/logo.svg" height="35" alt="NX-Jikkyo">
        </router-link>
        <div class="subtitle ml-2 pt-1 d-flex align-center text-text-darken-1"
            style="font-size: 15px; user-select: none;">
            <div class="mr-2" style="font-size: 17px;">|</div>
            Nico Nico Jikkyo Alternative
        </div>
        <v-spacer></v-spacer>
        <v-btn v-if="isButtonDisplay" variant="flat" color="background-lighten-3" class="pwa-install-button"
            @click="pwaInstallHandler.install()">
            <Icon icon="material-symbols:install-desktop-rounded" height="20px" class="mr-1" />
            アプリとしてインストール
        </v-btn>
    </header>
</template>
<script lang="ts" setup>

import { pwaInstallHandler } from 'pwa-install-handler';
import { onMounted, ref } from 'vue';

const isButtonDisplay = ref(false);

onMounted(() => {
    pwaInstallHandler.addListener((canInstall) => {
        isButtonDisplay.value = canInstall;
    });
});

</script>
<style lang="scss" scoped>

.header {
    position: fixed;
    display: flex;
    align-items: center;
    width: 100%;
    height: 65px;
    padding: 4px 16px;
    background: rgb(var(--v-theme-background-lighten-1));
    box-shadow: 0px 5px 5px -3px rgb(0 0 0 / 20%),
                0px 8px 10px 1px rgb(0 0 0 / 14%),
                0px 3px 14px 2px rgb(0 0 0 / 12%);
    z-index: 10;

    @include smartphone-horizontal {
        width: 210px;
        height: 48px;
        justify-content: center;
        .v-spacer {
            display: none;
        }
    }
    @include smartphone-horizontal-short {
        width: 190px;
    }
    @include smartphone-vertical {
        display: none;
    }

    .spacer {
        @include smartphone-horizontal {
            display: none;
        }
    }

    .nx-jikkyo-logo {
        display: block;
        padding: 12px 8px;
        border-radius: 8px;
        @include smartphone-horizontal {
            margin: 0 !important;
        }

        &__image {
            display: block;
            @include smartphone-horizontal {
                height: 19.5px;
            }
        }
    }

    .subtitle {
        @include smartphone-horizontal {
            display: none !important;
        }
    }

    .pwa-install-button {
        @include smartphone-horizontal {
            display: none !important;
        }
        @media (display-mode: standalone) {
            display: none !important;
        }
    }
}

</style>
