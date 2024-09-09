
import base64
import httpx
import json
from fastapi import APIRouter
from fastapi import Query
from fastapi import Request
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from pydantic import BaseModel
from typing import Annotated

from app import logging
from app.constants import API_REQUEST_HEADERS, HTTPX_CLIENT
from app.config import CONFIG
from app.utils.OAuthCallbackResponse import OAuthCallbackResponse


# ルーター
## https://app.konomi.tv/api/redirect/niconico のコールバック先 URL が /app/niconico/callback 固定なので、
## この API だけ /v1/ を外している
router = APIRouter(
    tags = ['Niconico'],
    prefix = '/api/niconico',
)


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


@router.get(
    '/auth',
    summary = 'ニコニコ OAuth 認証 URL 発行 API',
    response_model = ThirdpartyAuthURL,
    response_description = 'ユーザーにアプリ連携してもらうための認証 URL。',
)
async def NiconicoAuthURLAPI(
    request: Request,
):
    """
    ニコニコアカウントと連携するための認証 URL を取得する。<br>
    認証 URL をブラウザで開くとアプリ連携の許可を求められ、ユーザーが許可すると /api/v1/niconico/callback に戻ってくる。

    JWT エンコードされたアクセストークンがリクエストの Authorization: Bearer に設定されていないとアクセスできない。<br>
    """

    # クライアント (フロントエンド) の URL を Origin ヘッダーから取得
    ## Origin ヘッダーがリクエストに含まれていない場合はこの API サーバーの URL を使う
    client_url = request.headers.get('Origin', f'https://{request.url.netloc}').rstrip('/') + '/'
    print(client_url)

    # コールバック URL を設定
    ## ニコニコ API の OAuth 連携では、事前にコールバック先の URL を運営側に設定しておく必要がある
    ## 一方 KonomiTV サーバーの URL はまちまちなので、コールバック先の URL を一旦 https://app.konomi.tv/api/redirect/niconico に集約する
    ## この API は、リクエストを認証 URL の "state" パラメーター内で指定された KonomiTV サーバーの NiconicoAuthCallbackAPI にリダイレクトする
    ## 最後に KonomiTV サーバーがリダイレクトを受け取ることで、コールバック対象の URL が定まらなくても OAuth 連携ができるようになる
    ## ref: https://github.com/tsukumijima/KonomiTV-API
    callback_url = 'https://app.konomi.tv/api/redirect/niconico'

    # リクエストの Authorization ヘッダーで渡されたログイン中ユーザーの JWT アクセストークンを取得
    # このトークンをコールバック先の NiconicoAuthCallbackAPI に渡し、ログイン中のユーザーアカウントとニコニコアカウントを紐づける
    _, user_access_token = get_authorization_scheme_param(request.headers.get('Authorization'))

    # コールバック後の NiconicoAuthCallbackAPI に渡す state の値
    state = {
        # リダイレクト先の KonomiTV サーバー
        'server': f'{"https" if client_url.startswith("https") else "http"}://{request.url.netloc}/',
        # スマホ・タブレットでの NiconicoAuthCallbackAPI のリダイレクト先 URL
        'client': client_url,
        # ログイン中ユーザーの JWT アクセストークン
        'user_access_token': user_access_token,
    }

    # state は URL パラメータとして送らないといけないので、JSON エンコードしたあと Base64 でエンコードする
    state_base64 = base64.b64encode(json.dumps(state, ensure_ascii=False).encode('utf-8')).decode('utf-8')

    # 末尾の = はニコニコ側でリダイレクトされる際に変に URL エンコードされる事があるので、削除する
    state_base64 = state_base64.replace('=', '')

    # 利用するスコープを指定
    scope = '%20'.join([
        'offline_access',
        'openid',
        'profile',
        'user.authorities.relives.watch.get',
        'user.authorities.relives.watch.interact',
        'user.premium',
    ])

    # 認証 URL を作成
    authorization_url = (
        f'https://oauth.nicovideo.jp/oauth2/authorize?response_type=code&'
        f'scope={scope}&client_id={CONFIG.NICONICO_OAUTH_CLIENT_ID}&redirect_uri={callback_url}&state={state_base64}'
    )

    return {'authorization_url': authorization_url}


@router.get(
    '/callback',
    summary = 'ニコニコ OAuth コールバック API',
    response_class = OAuthCallbackResponse,
    response_description = 'ユーザーアカウントにニコニコアカウントのアクセストークン・リフレッシュトークンが登録できたことを示す。',
)
async def NiconicoAuthCallbackAPI(
    client: Annotated[str, Query(description='OAuth 連携元の KonomiTV クライアントの URL 。')],
    user_access_token: Annotated[str, Query(description='コールバック元から渡された、ユーザーの JWT アクセストークン。')],
    code: Annotated[str | None, Query(description='コールバック元から渡された認証コード。OAuth 認証が成功したときのみセットされる。')] = None,
    error: Annotated[str | None, Query(description='このパラメーターがセットされているとき、OAuth 認証がユーザーによって拒否されたことを示す。')] = None,
):
    """
    ニコニコの OAuth 認証のコールバックを受け取り、ログイン中のユーザーアカウントとニコニコアカウントを紐づける。
    """

    # スマホ・タブレット向けのリダイレクト先 URL を生成
    redirect_url = f'{client.rstrip("/")}/settings/jikkyo'

    # "error" パラメーターがセットされている
    # OAuth 認証がユーザーによって拒否されたことを示しているので、401 エラーにする
    if error is not None:

        # 401 エラーを送出
        ## コールバック元から渡されたエラーメッセージをそのまま表示する
        logging.error('[NiconicoRouter][NiconicoAuthCallbackAPI] Authorization was denied')
        return OAuthCallbackResponse(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = f'Authorization was denied ({error})',
            redirect_to = redirect_url,
        )

    # なぜか code がない
    if code is None:
        logging.error('[NiconicoRouter][NiconicoAuthCallbackAPI] Authorization code does not exist')
        return OAuthCallbackResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = 'Authorization code does not exist',
            redirect_to = redirect_url,
        )
    try:

        # 認証コードを使い、ニコニコ OAuth のアクセストークンとリフレッシュトークンを取得
        token_api_url = 'https://oauth.nicovideo.jp/oauth2/token'
        async with HTTPX_CLIENT() as httpx_client:
            token_api_response = await httpx_client.post(
                url = token_api_url,
                headers = {**API_REQUEST_HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'},
                data = {
                    'grant_type': 'authorization_code',
                    'client_id': CONFIG.NICONICO_OAUTH_CLIENT_ID,
                    'client_secret': CONFIG.NICONICO_OAUTH_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': 'https://app.konomi.tv/api/redirect/niconico',
                },
            )

        # ステータスコードが 200 以外
        if token_api_response.status_code != 200:
            logging.error(f'[NiconicoRouter][NiconicoAuthCallbackAPI] Failed to get access token (HTTP Error {token_api_response.status_code})')
            return OAuthCallbackResponse(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = f'Failed to get access token (HTTP Error {token_api_response.status_code})',
                redirect_to = redirect_url,
            )

        token_api_response_json = token_api_response.json()

    # 接続エラー（サーバーメンテナンスやタイムアウトなど）
    except (httpx.NetworkError, httpx.TimeoutException):
        logging.error('[NiconicoRouter][NiconicoAuthCallbackAPI] Failed to get access token (Connection Timeout)')
        return OAuthCallbackResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = 'Failed to get access token (Connection Timeout)',
            redirect_to = redirect_url,
        )

    # アクセストークンとリフレッシュトークンを取得
    ## アクセストークンは1時間で有効期限が切れるので、適宜リフレッシュトークンで再取得する
    niconico_access_token = str(token_api_response_json['access_token'])
    niconico_refresh_token = str(token_api_response_json['refresh_token'])

    # ニコニコアカウントのユーザー ID を取得
    # ユーザー ID は id_token の JWT の中に含まれている
    id_token_jwt = jwt.get_unverified_claims(token_api_response_json['id_token'])
    niconico_user_id = int(id_token_jwt.get('sub', 0))

    try:

        # ニコニコアカウントのユーザー情報を取得
        ## 3秒応答がなかったらタイムアウト
        user_api_url = f'https://nvapi.nicovideo.jp/v1/users/{niconico_user_id}'
        async with HTTPX_CLIENT() as httpx_client:
            # X-Frontend-Id がないと INVALID_PARAMETER になる
            user_api_response = await httpx_client.get(user_api_url, headers={**API_REQUEST_HEADERS, 'X-Frontend-Id': '6'})

        # ステータスコードが 200 以外
        if user_api_response.status_code != 200:
            logging.error(f'[NiconicoRouter][NiconicoAuthCallbackAPI] Failed to get user information (HTTP Error {user_api_response.status_code})')
            return OAuthCallbackResponse(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = f'Failed to get user information (HTTP Error {user_api_response.status_code})',
                redirect_to = redirect_url,
            )

        # ユーザー名
        niconico_user_name = str(user_api_response.json()['data']['user']['nickname'])
        # プレミアム会員かどうか
        niconico_user_premium = bool(user_api_response.json()['data']['user']['isPremium'])

    # 接続エラー（サーバー再起動やタイムアウトなど）
    except (httpx.NetworkError, httpx.TimeoutException):
        logging.error('[NiconicoRouter][NiconicoAuthCallbackAPI] Failed to get user information (Connection Timeout)')
        return OAuthCallbackResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = 'Failed to get user information (Connection Timeout)',
            redirect_to = redirect_url,
        )

    # 取得したニコニコアカウントとの連携情報を NiconicoUser に格納
    niconico_user = NiconicoUser(
        niconico_user_id = niconico_user_id,
        niconico_user_name = niconico_user_name,
        niconico_user_premium = niconico_user_premium,
        niconico_access_token = niconico_access_token,
        niconico_refresh_token = niconico_refresh_token,
    )

    # OAuth 連携が正常に完了したことを伝えるレスポンスを作成
    response =  OAuthCallbackResponse(
        status_code = status.HTTP_200_OK,
        detail = 'Success',
        redirect_to = redirect_url,
    )

    # Cookie に NX-Niconico-User を設定
    response.set_cookie(
        key = 'NX-Niconico-User',
        value = base64.b64encode(niconico_user.model_dump_json().encode('utf-8')).decode('utf-8'),
        max_age = 315360000,  # 10年間の有効期限 (秒単位)
        httponly = False,  # JavaScript からアクセスできるようにする
        samesite = 'lax',  # CSRF 攻撃を防ぐ
    )

    return response
