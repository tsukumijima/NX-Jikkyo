
import { Base64 } from 'js-base64';
import { getCookie } from 'typescript-cookie';


/**
 * ニコニコアカウント連携状態を含むユーザー情報を表すインターフェイス
 * NX-Jikkyo では KonomiTV のようなユーザーアカウント管理機能はないが、
 * ニコニコアカウント連携状態を保持するために IUser インターフェイスを利用している
 * ニコニコアカウントの連携情報は NX-Niconico-User Cookie (Base64 エンコードされた JSON) に保存される
 */
export interface IUser {
    niconico_user_id: number | null;
    niconico_user_name: string | null;
    niconico_user_premium: boolean | null;
}

/** ニコニコアカウント未連携時のデフォルト IUser */
const IUserDefault: IUser = {
    niconico_user_id: null,
    niconico_user_name: null,
    niconico_user_premium: null,
};


class Users {

    /**
     * 現在のニコニコアカウント連携状態を取得する
     * NX-Niconico-User Cookie から連携情報を読み取り、IUser オブジェクトを返す
     * Cookie が存在しない場合はニコニコアカウント未連携のデフォルト値を返す
     * @returns ニコニコアカウント連携状態を含むユーザー情報
     */
    static async fetchUser(): Promise<IUser> {

        // NX-Niconico-User Cookie を取得
        const niconico_user_cookie = getCookie('NX-Niconico-User');

        // Cookie が存在しない場合はニコニコアカウント未連携のデフォルト値を返す
        if (!niconico_user_cookie) {
            return {...IUserDefault};
        }

        try {
            // Cookie の値を Base64 デコードして JSON としてパース
            const niconico_user = JSON.parse(Base64.decode(niconico_user_cookie));

            // IUser インターフェイスに合わせてデータを返す
            return {
                niconico_user_id: niconico_user.niconico_user_id,
                niconico_user_name: niconico_user.niconico_user_name,
                niconico_user_premium: niconico_user.niconico_user_premium,
            };
        } catch (error) {
            console.error('Failed to parse NX-Niconico-User cookie:', error);
            return {...IUserDefault};
        }
    }
}

export default Users;
