
import hashlib

from starlette.websockets import WebSocket


def GenerateClientID(websocket: WebSocket) -> str:
    """
    WebSocket 接続時の HTTP リクエストヘッダーに含まれる情報からフィンガープリントを生成し、
    ある程度一意にユーザーを特定できるクライアント ID を生成する

    基本荒らしや不快なコメントをコメント ID 単位で一発ミュートできるようにするためのもの
    NX-Jikkyo 以外のサードパーティークライアントからのアクセスでは Cookie での識別ができないため
    完全には固定できず、IP アドレスや User-Agent の変更により随時変動する

    Args:
        websocket (WebSocket): WebSocket 接続情報

    Returns:
        str: クライアント ID
    """

    # Cookie に NX-User-ID が含まれていればそれを取得し、単体でユーザーを識別できるため単独でハッシュ化する
    ## NX-Jikkyo の公式 SPA アプリからアクセスした場合は常にセットされているはず
    if 'NX-User-ID' in websocket.cookies:
        return hashlib.sha1(websocket.cookies['NX-User-ID'].encode('utf-8')).hexdigest()

    # Cookie に _ga キーが含まれていればそれを取得し、単体でユーザーを識別できるため単独でハッシュ化する
    ## Google アナリティクスによって設定される _ga という名前の Cookie はユーザー識別用の ID で、
    ## ユーザーが Cookie を消去するか有効期限に達するまで永続的に設定される
    ## なお _ga_MK1R3QRD5D のような名前の Cookie はリロードごとに変更されるので、
    ## Cookie 全体をフィンガープリントに突っ込むと一意性が失われるため注意
    ## https://www.bbccss.com/explanation-of-cookie-values-used-by-ga4.html
    if '_ga' in websocket.cookies:
        return hashlib.sha1(websocket.cookies['_ga'].encode('utf-8')).hexdigest()

    # HTTP リクエスト元の IP アドレスを取得
    ## NX-Jikkyo は Cloudflare と nginx を挟んでのデプロイを想定しているので、
    ## cf-connecting-ip, x-real-ip, x-forwarded-for (一番左側) の順で取得を試し、
    ## どのヘッダーも設定されていなければ何もリバースプロキシを挟んでいないものと判断して直接取得する
    ip_address: str = ''
    if websocket.headers.get('cf-connecting-ip') is not None:
        ip_address = websocket.headers.get('cf-connecting-ip', '')
    elif websocket.headers.get('x-real-ip') is not None:
        ip_address = websocket.headers.get('x-real-ip', '')
    elif websocket.headers.get('x-forwarded-for') is not None:
        # X-Forwarded-For は複数の IP アドレスが含まれる場合があるので、最左端の IP アドレスを取得する
        ip_address = websocket.headers.get('x-forwarded-for', '').split(',')[0]
    elif websocket.client is not None:
        ip_address = websocket.client.host

    # User-Agent が指定されていればそれを取得
    user_agent: str = ''
    if websocket.headers.get('user-agent') is not None:
        user_agent = websocket.headers.get('user-agent', '')

    # CF-Ray が指定されていれば、- 区切りの右側の3レターコードを取得
    ##  Cloudflare が設定するヘッダーで、CF-Ray は 8957e991ee938d28-KIX のような値になる
    ## - 以降の文字列は Cloudflare のデータセンターの位置を示す  日本の場合、NRT が東京、KIX が大阪を示しているらしい
    ## これを使うことでユーザーが大まかに関東と関西どちらに住んでいるかが分かる
    cf_ray_data_center: str = ''
    if websocket.headers.get('cf-ray') is not None:
        cf_ray = websocket.headers.get('cf-ray', '')
        if '-' in cf_ray:
            cf_ray_data_center = cf_ray.split('-')[1]

    # CF-IPCountry が指定されていればそれを取得
    ## Cloudflare が設定するヘッダーで、値は ISO 3166-1 のコードで表される
    ## JP は日本、US は米国、CN は中国、KR は韓国など
    cf_ip_country: str = ''
    if websocket.headers.get('cf-ipcountry') is not None:
        cf_ip_country = websocket.headers.get('cf-ipcountry', '')

    # Accept-Encoding が指定されていればそれを取得
    ## Accept-Encoding の値はブラウザや HTTP クライアントによって微妙に異なるため、
    ## 単体では意味をなさないが、他の情報と組み合わせるとフィンガープリントの精度を向上できる
    accept_encoding: str = ''
    if websocket.headers.get('accept-encoding') is not None:
        accept_encoding = websocket.headers.get('accept-encoding', '')

    # Accept-Language が指定されていればそれを取得
    ## Accept-Language の値はユーザーのブラウザ設定次第で異なるため、
    ## 単体では意味をなさないが、他の情報と組み合わせるとフィンガープリントの精度を向上できる
    accept_language: str = ''
    if websocket.headers.get('accept-language') is not None:
        accept_language = websocket.headers.get('accept-language', '')

    # Sec-WebSocket-Extensions が指定されていればそれを取得
    ## 通常のブラウザは "permessage-deflate; client_max_window_bits" という値を設定する
    ## 外部ソフトからのアクセスの場合、WebSocket クライアントの実装次第ではこの値が設定されないことを識別に利用する
    sec_websocket_extensions: str = ''
    if websocket.headers.get('sec-websocket-extensions') is not None:
        sec_websocket_extensions = websocket.headers.get('sec-websocket-extensions', '')

    # 取得した情報を : で結合してフィンガープリントを生成
    fingerprint: str = ':'.join([
        ip_address,
        user_agent,
        cf_ray_data_center,
        cf_ip_country,
        accept_encoding,
        accept_language,
        sec_websocket_extensions,
    ])

    # フィンガープリントを SHA-1 でハッシュ化して返す
    ## MD5 よりかは安全にしたいが、SHA-256 は桁が長すぎるため
    return hashlib.sha1(fingerprint.encode('utf-8')).hexdigest()
