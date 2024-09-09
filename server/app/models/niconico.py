
from pydantic import BaseModel


class NiconicoUser(BaseModel):
    """
    ニコニコ生放送にアクセスするためのニコニコアカウントとの連携情報を表す Pydantic モデル
    """

    niconico_user_id: int
    niconico_user_name: str
    niconico_user_premium: bool
    niconico_access_token: str
    niconico_refresh_token: str


class ThirdpartyAuthURL(BaseModel):
    authorization_url: str
