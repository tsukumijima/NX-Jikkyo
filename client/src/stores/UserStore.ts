
import { defineStore } from 'pinia';

import Users, { IUser } from '@/services/Users';


/**
 * ニコニコアカウントの連携状態を共有するストア
 * NX-Jikkyo では KonomiTV のようなユーザーアカウント管理機能はないが、
 * ニコニコアカウント連携の状態を UI 全体で共有するために UserStore を利用している
 */
const useUserStore = defineStore('user', {
    state: () => ({

        // ニコニコアカウント連携状態を含むユーザー情報
        user: null as IUser | null,
    }),
    getters: {

        /**
         * ニコニコアカウントのユーザーアイコンの URL (ニコニコアカウントと連携されている場合のみ)
         */
        user_niconico_icon_url(): string | null {
            if (this.user === null || this.user.niconico_user_id === null) {
                return null;
            }
            const user_id = this.user.niconico_user_id.toString();
            // ユーザー ID が 4 桁以下の場合は '0' 、5 桁以上の場合は一万位より上の値を使う
            const user_id_prefix = user_id.length <= 4 ? '0' : user_id.slice(0, -4);
            return `https://secure-dcdn.cdn.nimg.jp/nicoaccount/usericon/${user_id_prefix}/${user_id}.jpg`;
        }
    },
    actions: {

        /**
         * ニコニコアカウントの連携状態を取得する
         * NX-Niconico-User Cookie から連携情報を読み取る
         * すでに取得済みの情報がある場合は Cookie の再読み取りを行わずにそれを返す
         * @param force 強制的に Cookie を再読み取りする場合は true
         * @returns ニコニコアカウント連携状態を含むユーザー情報
         */
        async fetchUser(force: boolean = false): Promise<IUser> {

            // すでにユーザー情報がある場合はそれを返す
            // force が true の場合は無視される
            if (this.user !== null && force === false) {
                return this.user;
            }

            // NX-Niconico-User Cookie からニコニコアカウント連携情報を取得する
            const user = await Users.fetchUser();
            this.user = user;

            return this.user;
        },
    }
});

export default useUserStore;
