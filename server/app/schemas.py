
import base64
import json
from typing import ClassVar

import httpx2 as httpx
from fastapi import Response
from pydantic import BaseModel

from app.config import CONFIG
from app.constants import API_REQUEST_HEADERS, HTTPX_CLIENT


class NiconicoUser(BaseModel):
    """
    ニコニコ生放送にアクセスするためのニコニコアカウントとの連携情報を表す Pydantic モデル
    """

    niconico_user_id: int
    niconico_user_name: str
    niconico_user_premium: bool
    niconico_access_token: str
    niconico_refresh_token: str

    # NX-Jikkyo はユーザーアカウントを持たないため、ニコニコアカウントとの連携情報はブラウザの Cookie に保存する
    # 表示用の連携情報 (ユーザー ID・ユーザー名・プレミアム会員かどうか) を保存する Cookie の名前
    ## クライアントの JavaScript から読み取って画面に表示するため、HttpOnly を付けない
    USER_COOKIE_NAME: ClassVar[str] = 'NX-Niconico-User'
    # ニコニコのアクセストークン・リフレッシュトークンを保存する Cookie の名前
    ## サーバー側でしか使わないので、XSS で盗まれないよう HttpOnly を付けて JavaScript から読めないようにする
    TOKEN_COOKIE_NAME: ClassVar[str] = 'NX-Niconico-Token'
    # 連携情報を保存する Cookie の有効期限 (10年間、秒単位)
    COOKIE_MAX_AGE: ClassVar[int] = 315360000

    @classmethod
    def fromCookies(cls, cookies: dict[str, str]) -> tuple['NiconicoUser | None', bool]:
        """
        リクエストの Cookie から、ニコニコアカウントとの連携情報を読み取る
        以前はトークンも表示用の連携情報と一緒に NX-Niconico-User Cookie (JavaScript から読める) に保存していたため、
        トークンの Cookie がない場合は、NX-Niconico-User Cookie に含まれているトークンを読み取る

        Args:
            cookies (dict[str, str]): リクエストの Cookie

        Returns:
            tuple[NiconicoUser | None, bool]: 連携情報 (未連携の場合は None) と、以前の形式の Cookie から読み取ったかどうか

        Raises:
            ValueError: Cookie の値が Base64 や JSON として不正な場合や、連携情報として必要な値が欠けている場合
        """

        # 表示用の連携情報の Cookie がない場合は、未連携として扱う
        ## 以前のクライアントは連携解除の際に NX-Niconico-User Cookie だけを削除していたため、
        ## トークンの Cookie だけが残っていても、そのトークンは使わない
        user_cookie = cookies.get(cls.USER_COOKIE_NAME)
        if not user_cookie:
            return None, False
        user_json = json.loads(base64.b64decode(user_cookie).decode('utf-8'))
        if not isinstance(user_json, dict):
            raise ValueError(f'{cls.USER_COOKIE_NAME} cookie is not JSON object.')

        # トークンの Cookie がある場合は、表示用の連携情報と合わせて連携情報とする
        token_cookie = cookies.get(cls.TOKEN_COOKIE_NAME)
        if token_cookie:
            token_json = json.loads(base64.b64decode(token_cookie).decode('utf-8'))
            if not isinstance(token_json, dict):
                raise ValueError(f'{cls.TOKEN_COOKIE_NAME} cookie is not JSON object.')
            niconico_user = cls.model_validate({
                'niconico_user_id': user_json.get('niconico_user_id'),
                'niconico_user_name': user_json.get('niconico_user_name'),
                'niconico_user_premium': user_json.get('niconico_user_premium'),
                'niconico_access_token': token_json.get('niconico_access_token'),
                'niconico_refresh_token': token_json.get('niconico_refresh_token'),
            })
            return niconico_user, False

        # トークンの Cookie がない場合は、以前の形式の NX-Niconico-User Cookie に含まれているトークンを使う
        ## 新しい形式の NX-Niconico-User Cookie にはトークンが含まれないため、その場合は ValidationError (ValueError) になる
        return cls.model_validate(user_json), True

    @classmethod
    def deleteCookies(cls, response: Response) -> None:
        """
        ニコニコアカウントとの連携情報を保存している Cookie をすべて削除する

        Args:
            response (Response): Cookie を削除するレスポンス
        """

        response.delete_cookie(key=cls.USER_COOKIE_NAME, samesite='lax')
        response.delete_cookie(key=cls.TOKEN_COOKIE_NAME, httponly=True, samesite='lax')

    def setCookies(self, response: Response) -> None:
        """
        ニコニコアカウントとの連携情報を、表示用の連携情報の Cookie とトークンの Cookie に分けて保存する

        Args:
            response (Response): Cookie を設定するレスポンス
        """

        # 表示用の連携情報は、クライアントの JavaScript から読めるように HttpOnly を付けずに保存する
        user_json = self.model_dump_json(include={'niconico_user_id', 'niconico_user_name', 'niconico_user_premium'})
        response.set_cookie(
            key = self.USER_COOKIE_NAME,
            value = base64.b64encode(user_json.encode('utf-8')).decode('utf-8'),
            max_age = self.COOKIE_MAX_AGE,
            httponly = False,  # JavaScript からアクセスできるようにする
            samesite = 'lax',  # CSRF 攻撃を防ぐ
        )

        # トークンは、XSS で盗まれないよう HttpOnly を付けて保存する
        token_json = self.model_dump_json(include={'niconico_access_token', 'niconico_refresh_token'})
        response.set_cookie(
            key = self.TOKEN_COOKIE_NAME,
            value = base64.b64encode(token_json.encode('utf-8')).decode('utf-8'),
            max_age = self.COOKIE_MAX_AGE,
            httponly = True,  # JavaScript からアクセスできないようにする
            samesite = 'lax',  # CSRF 攻撃を防ぐ
        )

    async def refreshNiconicoAccessToken(self) -> None:
        """
        このユーザーに紐づくニコニコアカウントのアクセストークンを、リフレッシュトークンで更新する

        Raises:
            Exception: アクセストークンの更新に失敗した場合 (例外に含まれるエラーメッセージを API レスポンスで返す想定)
        """

        try:

            # リフレッシュトークンを使い、ニコニコ OAuth のアクセストークンとリフレッシュトークンを更新
            token_api_url = 'https://oauth.nicovideo.jp/oauth2/token'
            async with HTTPX_CLIENT() as client:
                token_api_response = await client.post(
                    url = token_api_url,
                    headers = {**API_REQUEST_HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'},
                    data = {
                        'grant_type': 'refresh_token',
                        'client_id': CONFIG.NICONICO_OAUTH_CLIENT_ID,
                        'client_secret': CONFIG.NICONICO_OAUTH_CLIENT_SECRET,
                        'refresh_token': self.niconico_refresh_token,
                    },
                )

            # ステータスコードが 200 以外
            if token_api_response.status_code != 200:
                error_code = ''
                try:
                    error_code = f' ({token_api_response.json()["error"]})'
                except Exception:
                    pass
                raise Exception(f'アクセストークンの更新に失敗しました。(HTTP Error {token_api_response.status_code}{error_code})')

            token_api_response_json = token_api_response.json()

        # 接続エラー（サーバーメンテナンスやタイムアウトなど）
        except (httpx.NetworkError, httpx.TimeoutException):
            raise Exception('アクセストークンの更新リクエストがタイムアウトしました。')

        # 取得したアクセストークンとリフレッシュトークンをユーザーアカウントに設定
        ## 仕様上リフレッシュトークンに有効期限はないが、一応このタイミングでリフレッシュトークンも更新することが推奨されている
        self.niconico_access_token = str(token_api_response_json['access_token'])
        self.niconico_refresh_token = str(token_api_response_json['refresh_token'])

        try:
            # ついでなので、このタイミングでユーザー情報を取得し直す
            ## 頻繁に変わるものでもないとは思うけど、一応再ログインせずとも同期されるようにしておきたい
            ## 3秒応答がなかったらタイムアウト
            user_api_url = f'https://nvapi.nicovideo.jp/v1/users/{self.niconico_user_id}'
            async with HTTPX_CLIENT() as client:
                # X-Frontend-Id がないと INVALID_PARAMETER になる
                user_api_response = await client.get(user_api_url, headers={**API_REQUEST_HEADERS, 'X-Frontend-Id': '6'})

            if user_api_response.status_code == 200:
                # ユーザー名
                self.niconico_user_name = str(user_api_response.json()['data']['user']['nickname'])
                # プレミアム会員かどうか
                self.niconico_user_premium = bool(user_api_response.json()['data']['user']['isPremium'])

        # 接続エラー（サーバー再起動やタイムアウトなど）
        except (httpx.NetworkError, httpx.TimeoutException):
            pass  # 取れなくてもセッション取得に支障はないのでパス


# ***** ニコニコ実況連携 *****

class JikkyoWebSocketInfo(BaseModel):
    # 視聴セッション維持用 WebSocket API の URL (NX-Jikkyo)
    watch_session_url: str | None
    # 視聴セッション維持用 WebSocket API の URL (ニコニコ生放送)
    nicolive_watch_session_url: str | None = None
    # 視聴セッション維持用 WebSocket API のエラー情報 (ニコニコ生放送)
    nicolive_watch_session_error: str | None = None
    # コメント受信用 WebSocket API の URL (NX-Jikkyo)
    comment_session_url: str | None
    # 現在は NX-Jikkyo のみ存在するニコニコ実況チャンネルかどうか
    is_nxjikkyo_exclusive: bool

class ThirdpartyAuthURL(BaseModel):
    authorization_url: str
