

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
                title: 'テレビ実況 | NX-Jikkyo',
                description: 'サイバー攻撃で最低7月末まで鯖落ち中のニコニコ実況に代わる避難所です。お気に入りのソフトを使い続けながら、今まで通りテレビを楽しく実況できます。',
            },
        },
        {
            path: '/watch/:display_channel_id',
            name: 'TV Watch',
            component: () => import('@/views/TV/Watch.vue'),
            meta: {
                title: 'テレビ実況 - コメント再生 | NX-Jikkyo',
                description: 'サイバー攻撃で最低7月末まで鯖落ち中のニコニコ実況に代わる避難所です。お気に入りのソフトを使い続けながら、今まで通りテレビを楽しく実況できます。',
            },
        },
        {
            path: '/about/',
            name: 'About',
            component: () => import('@/views/About.vue'),
            meta: {
                title: 'NX-Jikkyo とは | NX-Jikkyo',
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
                title: '設定 | NX-Jikkyo',
                description: 'NX-Jikkyo の設定を変更できます。',
            },
        },
        {
            path: '/settings/general',
            name: 'Settings General',
            component: () => import('@/views/Settings/General.vue'),
            meta: {
                title: '設定 - 全般 | NX-Jikkyo',
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
                title: '設定 - コメント/実況 | NX-Jikkyo',
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
                title: '404 Not Found | NX-Jikkyo',
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
    document.title = (to.meta.title || 'NX-Jikkyo') as string;
    const default_description = 'サイバー攻撃で最低7月末まで鯖落ち中のニコニコ実況に代わる避難所です。お気に入りのソフトを使い続けながら、今まで通りテレビを楽しく実況できます。';
    const description_meta = document.querySelector('meta[name="description"]')!;
    if (description_meta) {
        description_meta.setAttribute('content', (to.meta.description || default_description) as string);
    } else {
        const meta = document.createElement('meta');
        meta.name = 'description';
        meta.content = (to.meta.description || default_description) as string;
        document.head.appendChild(meta);
    }
});

// ルーティングの変更時に View Transitions API を適用する
// ref: https://developer.mozilla.org/ja/docs/Web/API/View_Transitions_API
router.beforeResolve((to, from, next) => {
    // View Transition API を適用しないルートの prefix
    // to と from の両方のパスがこの prefix で始まる場合は View Transition API を適用しない
    const no_transition_routes = [
        '/watch/',
        '/videos/watch/',
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
