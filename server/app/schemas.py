
import httpx
from pydantic import BaseModel

from app.constants import API_REQUEST_HEADERS, HTTPX_CLIENT
from app.config import CONFIG


class NiconicoUser(BaseModel):
    """
    ニコニコ生放送にアクセスするためのニコニコアカウントとの連携情報を表す Pydantic モデル
    """

    niconico_user_id: int
    niconico_user_name: str
    niconico_user_premium: bool
    niconico_access_token: str
    niconico_refresh_token: str

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
