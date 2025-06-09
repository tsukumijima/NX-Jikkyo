
# Type Hints を指定できるように
# ref: https://stackoverflow.com/a/33533514/17124142
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from bs4 import Tag
from fastapi import Request
from typing import cast, ClassVar

from app import logging
from app import schemas
from app.constants import API_REQUEST_HEADERS, HTTPX_CLIENT


class Jikkyo:
    """ ニコニコ実況関連のクライアント実装 (KonomiTV から部分的に移植) """

    # 旧来の実況チャンネル ID とニコニコチャンネル ID のマッピング
    ## 現在アクティブ (実況可能) なニコニコ実況チャンネルがここに記載されている
    ## id が None のチャンネルは NX-Jikkyo にのみ存在する実況チャンネル
    JIKKYO_CHANNEL_ID_MAP: ClassVar[dict[str, str | None]] = {
        'jk1': 'ch2646436',
        'jk2': 'ch2646437',
        'jk4': 'ch2646438',
        'jk5': 'ch2646439',
        'jk6': 'ch2646440',
        'jk7': 'ch2646441',
        'jk8': 'ch2646442',
        'jk9': 'ch2646485',
        'jk10': None,
        'jk11': None,
        'jk12': None,
        'jk13': 'ch2649860',
        'jk14': None,
        'jk101': 'ch2647992',
        'jk103': None,
        'jk141': None,
        'jk151': None,
        'jk161': None,
        'jk171': None,
        'jk181': None,
        'jk191': None,
        'jk192': None,
        'jk193': None,
        'jk211': 'ch2646846',
        'jk222': None,
        'jk236': None,
        'jk252': None,
        'jk260': None,
        'jk263': None,
        'jk265': None,
        'jk333': None,
    }


    def __init__(self, jikkyo_channel_id: str) -> None:
        """
        ニコニコ実況クライアントを初期化する

        Args:
            jikkyo_channel_id (str): 実況チャンネル ID (ex: jk101)
        """

        # 実況チャンネル ID (ex: jk101) を取得
        self.jikkyo_id: str = jikkyo_channel_id

        # 実況チャンネル ID に対応するニコニコチャンネル ID を取得する
        # ニコニコチャンネル ID が存在しない実況チャンネルは NX-Jikkyo にのみ存在する
        if (self.jikkyo_id in Jikkyo.JIKKYO_CHANNEL_ID_MAP) and \
           (Jikkyo.JIKKYO_CHANNEL_ID_MAP[self.jikkyo_id] is not None):
            self.nicochannel_id: str | None = Jikkyo.JIKKYO_CHANNEL_ID_MAP[self.jikkyo_id]
        else:
            self.nicochannel_id: str | None = None


    async def fetchWebSocketInfo(self,
        request: Request,
        current_user: schemas.NiconicoUser | None,
    ) -> tuple[schemas.JikkyoWebSocketInfo, schemas.NiconicoUser | None]:
        """
        ニコニコ実況・NX-Jikkyo とコメントを送受信するための WebSocket API の情報を取得する
        2024/08/05 以降の新ニコニコ生放送でコメントサーバーが刷新された影響で、従来 KonomiTV で実装していた
        「ブラウザから直接ニコ生の WebSocket API に接続しコメントを送受信する」手法が使えなくなったため、
        デフォルトでは NX-Jikkyo の旧ニコニコ生放送互換 WebSocket API (視聴セッション・コメントセッション) の URL を返す
        ログイン中かつニコニコアカウントと連携している場合のみ、ニコ生の WebSocket API (視聴セッションのみ) の URL も返す
        最終的にどちらの「視聴セッション維持用 WebSocket API」に接続するか (=どちらにコメントを送信するか) はフロントエンドの裁量で決められる
        いずれの場合でも、「コメント受信用 WebSocket API」には常に NX-Jikkyo の WebSocket API を利用する

        Args:
            current_user (User | None): ログイン中のユーザーのモデルオブジェクト

        Returns:
            schemas.JikkyoWebSocketInfo: ニコニコ実況・NX-Jikkyo とコメントを送受信するための WebSocket API の情報
        """

        # 現在は NX-Jikkyo のみ存在するニコニコ実況チャンネルかどうかを表すフラグ
        ## 実況チャンネル ID に対応するニコニコチャンネル ID が存在しない場合、NX-Jikkyo 固有のニコニコ実況チャンネルと判定する (jk141 など)
        is_nxjikkyo_exclusive = self.nicochannel_id is None

        # ネットワーク ID + サービス ID に対応するニコニコ実況チャンネルがない場合
        ## 実況チャンネルが昔から存在しない CS や、2020年12月のニコニコ実況リニューアルで廃止された BS スカパーのチャンネルなどが該当
        if self.jikkyo_id is None:
            return (
                schemas.JikkyoWebSocketInfo(
                    watch_session_url = None,
                    nicolive_watch_session_url = None,
                    nicolive_watch_session_error = None,
                    comment_session_url = None,
                    is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
                ),
                current_user,
            )

        # scheme はそのままだと多段プロキシの場合に ws:// になってしまうので、
        # X-Forwarded-Proto ヘッダから scheme を取得してから URI を組み立てる
        scheme = request.headers.get('X-Forwarded-Proto', request.url.scheme).replace('http', 'ws')

        # NX-Jikkyo の旧ニコニコ生放送「視聴セッション維持用 WebSocket API」互換の WebSocket API の URL を生成
        watch_session_url = f'{scheme}://{request.url.netloc}/api/v1/channels/{self.jikkyo_id}/ws/watch'

        # NX-Jikkyo の旧ニコニコ生放送「コメント受信用 WebSocket API」互換の WebSocket API の URL を生成
        comment_session_url = f'{scheme}://{request.url.netloc}/api/v1/channels/{self.jikkyo_id}/ws/comment'

        # 現在は NX-Jikkyo のみ存在するニコニコ実況チャンネル or 未ログイン or ニコニコアカウントと連携していない場合は、
        # ニコ生側の「視聴セッション維持用 WebSocket API」の URL は取得せず、そのまま NX-Jikkyo の WebSocket API の URL のみを返す
        if is_nxjikkyo_exclusive is True or current_user is None or not all([
            current_user.niconico_user_id,
            current_user.niconico_user_name,
            current_user.niconico_access_token,
            current_user.niconico_refresh_token,
        ]):
            return (
                schemas.JikkyoWebSocketInfo(
                    watch_session_url = watch_session_url,
                    nicolive_watch_session_url = None,
                    nicolive_watch_session_error = None,
                    comment_session_url = comment_session_url,
                    is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
                ),
                current_user,
            )

        # ログイン中かつニコニコアカウントと連携している場合のみ、ニコ生側の「視聴セッション維持用 WebSocket API」の URL を取得する
        ## 2024/08/05 以降も「視聴セッション維持用 WebSocket API」は一部変更の上で継続運用されており、コメント送信インターフェイスも変わらない
        ## この「視聴セッション維持用 WebSocket API」に接続できれば、NX-Jikkyo の代わりに本家ニコニコ実況にコメントを投稿できる
        ## この「視聴セッション維持用 WebSocket API」を取得できなかった場合は、NX-Jikkyo の WebSocket API の URL のみを返す
        ## このとき、フロントエンドではユーザーの設定に関わらず、フォールバックとして NX-Jikkyo の「視聴セッション維持用 WebSocket API」に接続する

        try:
            # 実況チャンネル ID に対応するニコニコチャンネルで現在放送中のニコニコ生放送番組の ID を取得する
            nicolive_program_id = None
            async with HTTPX_CLIENT() as client:
                response = await client.get(f'https://ch.nicovideo.jp/{self.nicochannel_id}/live')
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                live_now = soup.find('div', id='live_now')
                if live_now:
                    live_link = live_now.find('a', href=lambda href: bool(href and href.startswith('https://live.nicovideo.jp/watch/lv')))  # type: ignore
                    if live_link:
                        nicolive_program_id = cast(str, cast(Tag, live_link).get('href')).split('/')[-1]

            # 何らかの理由で放送中のニコニコ生放送番組が取得できなかった
            ## メンテナンス中などで実況番組が放送されていないか、ニコニコチャンネルの HTML 構造が変更された可能性が高い
            if nicolive_program_id is None:
                logging.warning(f'[fetchWebSocketInfo][{self.nicochannel_id}] Failed to get currently broadcasting nicolive program id.')
                return (
                    schemas.JikkyoWebSocketInfo(
                        watch_session_url = watch_session_url,
                        nicolive_watch_session_url = None,
                        nicolive_watch_session_error = '現在放送中のニコニコ実況番組が見つかりませんでした。',
                        comment_session_url = comment_session_url,
                        is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
                    ),
                    current_user,
                )

            # 視聴セッションの WebSocket URL を取得する
            ## レスポンスで取得できる WebSocket に接続すると、ログイン中のユーザーに紐づくニコニコアカウントでコメントできる
            wsendpoint_api_url = (
                'https://api.live2.nicovideo.jp/api/v1/wsendpoint?'
                f'nicoliveProgramId={nicolive_program_id}&userId={current_user.niconico_user_id}'
            )

            async def get_session():  # 使い回せるように関数化
                async with HTTPX_CLIENT() as client:
                    return await client.get(
                        url = wsendpoint_api_url,
                        headers = {**API_REQUEST_HEADERS, 'Authorization': f'Bearer {current_user.niconico_access_token}'},
                    )
            wsendpoint_api_response = await get_session()

            # ステータスコードが 401 (Unauthorized)
            ## アクセストークンの有効期限が切れているため、リフレッシュトークンでアクセストークンを更新してからやり直す
            if wsendpoint_api_response.status_code == 401:
                try:
                    await current_user.refreshNiconicoAccessToken()
                except Exception as ex:
                    # アクセストークンのリフレッシュに失敗した
                    logging.warning(f'[fetchWebSocketInfo][{self.nicochannel_id}] Failed to refresh niconico access token. ({ex.args[0]})')
                    return (
                        schemas.JikkyoWebSocketInfo(
                            watch_session_url = watch_session_url,
                            nicolive_watch_session_url = None,
                            nicolive_watch_session_error = ex.args[0],
                            comment_session_url = comment_session_url,
                            is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
                        ),
                        current_user,
                    )
                wsendpoint_api_response = await get_session()

            # ステータスコードが 200 以外
            if wsendpoint_api_response.status_code != 200:
                error_code = ''
                try:
                    error_code = f' ({wsendpoint_api_response.json()["meta"]["errorCode"]})'
                except Exception:
                    pass
                logging.warning(f'[fetchWebSocketInfo][{self.nicochannel_id}] Failed to get nicolive watch session url. '
                              f'({wsendpoint_api_response.status_code}{error_code})')
                return (
                    schemas.JikkyoWebSocketInfo(
                        watch_session_url = watch_session_url,
                        nicolive_watch_session_url = None,
                        nicolive_watch_session_error = (
                            '現在、ニコニコ生放送でエラーが発生しています。'
                            f'(HTTP Error {wsendpoint_api_response.status_code}{error_code})'
                        ),
                        comment_session_url = comment_session_url,
                        is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
                    ),
                    current_user,
                )

        # 接続エラー（サーバー再起動やタイムアウトなど）
        except (httpx.NetworkError, httpx.TimeoutException):
            logging.warning(f'[fetchWebSocketInfo][{self.nicochannel_id}] Failed to connect to nicolive.')
            return (
                schemas.JikkyoWebSocketInfo(
                    watch_session_url = watch_session_url,
                    nicolive_watch_session_url = None,
                    nicolive_watch_session_error = 'ニコニコ生放送に接続できませんでした。ニコニコで障害が発生している可能性があります。',
                    comment_session_url = comment_session_url,
                    is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
                ),
                current_user,
            )

        # NX-Jikkyo のに加え、ニコ生側の「視聴セッション維持用 WebSocket API」の URL も併せて返す
        return (
            schemas.JikkyoWebSocketInfo(
                watch_session_url = watch_session_url,
                nicolive_watch_session_url = wsendpoint_api_response.json()['data']['url'],
                nicolive_watch_session_error = None,
                comment_session_url = comment_session_url,
                is_nxjikkyo_exclusive = is_nxjikkyo_exclusive,
            ),
            current_user,
        )
