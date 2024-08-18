

import { createRouter, createWebHistory } from 'vue-router';

import Utils from '@/utils';


// Vue Router v4
// ref: https://router.vuejs.org/guide/

const router = createRouter({

    // ルーティングのベース URL
    history: createWebHistory(import.meta.env.BASE_URL),

    // ルーティング設定
    routes: [
        {
            path: '/',
            name: 'TV Home',
            component: () => import('@/views/TV/Home.vue'),
            meta: {
                title: 'NX-Jikkyo : ニコニコ実況避難所',
                description: 'サイバー攻撃で鯖落ちしていたニコニコ実況に代わる避難所です。お気に入りのアプリを使い続けながら、今まで通りテレビを楽しく快適に実況できます。',
            },
        },
        {
            path: '/watch/:display_channel_id',
            name: 'TV Watch',
            component: () => import('@/views/TV/Watch.vue'),
            meta: {
                title: 'テレビ実況 - コメント再生中 | NX-Jikkyo : ニコニコ実況避難所',
                description: 'サイバー攻撃で鯖落ちしていたニコニコ実況に代わる避難所です。お気に入りのアプリを使い続けながら、今まで通りテレビを楽しく快適に実況できます。',
            },
        },
        {
            path: '/log/',
            name: 'Kakolog',
            component: () => import('@/views/Kakolog/Index.vue'),
            meta: {
                title: '過去ログ再生 | NX-Jikkyo : ニコニコ実況避難所',
                description: 'ニコニコ実況 過去ログ API に保存されている、2009年11月から現在までの 旧ニコニコ実況 (2009/11/28 ~ 2020/12/15)・ニコ生統合後の新ニコニコ実況 (2020/12/15 ~ 2024/06/08)・NX-Jikkyo (2024/06/10 ~)・ニコニコ実況 (Re:仮) (2024/07/20 ~ 2024/08/05)・暫定復旧版ニコニコ実況 (2024/08/05 ~ 2024/08/22)・本復旧後のニコニコ実況 (2024/08/22 ~) のすべての過去ログを、チャンネルと日時範囲を指定して再生できます。',
            },
        },
        {
            path: '/log/:display_channel_id/:kakolog_period_id',
            name: 'Kakolog Watch',
            component: () => import('@/views/Kakolog/Watch.vue'),
            meta: {
                title: '過去ログ再生 - コメント再生中 | NX-Jikkyo : ニコニコ実況避難所',
                description: 'ニコニコ実況 過去ログ API に保存されている、2009年11月から現在までの 旧ニコニコ実況 (2009/11/28 ~ 2020/12/15)・ニコ生統合後の新ニコニコ実況 (2020/12/15 ~ 2024/06/08)・NX-Jikkyo (2024/06/10 ~)・ニコニコ実況 (Re:仮) (2024/07/20 ~ 2024/08/05)・暫定復旧版ニコニコ実況 (2024/08/05 ~ 2024/08/22)・本復旧後のニコニコ実況 (2024/08/22 ~) のすべての過去ログを、チャンネルと日時範囲を指定して再生できます。',
            },
        },
        {
            path: '/about/',
            name: 'About',
            component: () => import('@/views/About.vue'),
            meta: {
                title: 'NX-Jikkyo とは | NX-Jikkyo : ニコニコ実況避難所',
                description: 'NX-Jikkyo のサイトについての情報です。',
            },
        },
        {
            path: '/settings/',
            name: 'Settings Index',
            component: () => import('@/views/Settings/Index.vue'),
            beforeEnter: (to, from, next) => {
                // スマホ縦画面・スマホ横画面・タブレット縦画面では設定一覧画面を表示する（画面サイズの関係）
                if (Utils.isSmartphoneVertical() || Utils.isSmartphoneHorizontal() || Utils.isTabletVertical()) {
                    next();  // 通常通り遷移
                    return;
                }
                // それ以外の画面サイズでは全般設定にリダイレクト
                next({path: '/settings/general/'});
            },
            meta: {
                title: '設定 | NX-Jikkyo : ニコニコ実況避難所',
                description: 'NX-Jikkyo の設定を変更できます。',
            },
        },
        {
            path: '/settings/general',
            name: 'Settings General',
            component: () => import('@/views/Settings/General.vue'),
            meta: {
                title: '設定 - 全般 | NX-Jikkyo : ニコニコ実況避難所',
                description: 'NX-Jikkyo の全般の設定を変更できます。',
            },
        },
        // {
        //     path: '/settings/account',
        //     name: 'Settings Account',
        //     component: () => import('@/views/Settings/Account.vue'),
        // },
        {
            path: '/settings/jikkyo',
            name: 'Settings Jikkyo',
            component: () => import('@/views/Settings/Jikkyo.vue'),
            meta: {
                title: '設定 - コメント/実況 | NX-Jikkyo : ニコニコ実況避難所',
                description: 'NX-Jikkyo のコメント/実況の設定を変更できます。',
            },
        },
        // {
        //     path: '/login/',
        //     name: 'Login',
        //     component: () => import('@/views/Login.vue'),
        // },
        // {
        //     path: '/register/',
        //     name: 'Register',
        //     component: () => import('@/views/Register.vue'),
        // },
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            component: () => import('@/views/NotFound.vue'),
            meta: {
                title: '404 Not Found | NX-Jikkyo : ニコニコ実況避難所',
                description: 'お探しのページは存在しないか、鋭意開発中です。',
            },
        },
    ],

    // ページ遷移時のスクロールの挙動の設定
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            // 戻る/進むボタンが押されたときは保存されたスクロール位置を使う
            return savedPosition;
        } else {
            // それ以外は常に先頭にスクロールする
            return {top: 0, left: 0};
        }
    }
});

// タイトルと概要を動的に変更
router.beforeEach((to) => {
    const title = (to.meta.title || 'NX-Jikkyo') as string;
    const description = (to.meta.description || 'サイバー攻撃で鯖落ちしていたニコニコ実況に代わる避難所です。お気に入りのアプリを使い続けながら、今まで通りテレビを楽しく快適に実況できます。') as string;
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
});

// ルーティングの変更時に View Transitions API を適用する
// ref: https://developer.mozilla.org/ja/docs/Web/API/View_Transitions_API
router.beforeResolve((to, from, next) => {
    // View Transition API を適用しないルートの prefix
    // to と from の両方のパスがこの prefix で始まる場合は View Transition API を適用しない
    const no_transition_routes = [
        '/watch/',
    ];
    if (document.startViewTransition && !no_transition_routes.some((route) => to.path.startsWith(route) && from.path.startsWith(route))) {
        document.startViewTransition(() => {
            next();
        });
    } else {
        next();
    }
});

export default router;
