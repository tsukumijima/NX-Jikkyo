
import hashlib
import pathlib
import time
import xml.etree.ElementTree as ET
from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Request,
    Response,
    status,
)
from fastapi.responses import FileResponse
from tortoise import connections
from tortoise import timezone
from typing import Annotated, cast, Literal
from zoneinfo import ZoneInfo

from app.constants import (
    LOGO_DIR,
    REDIS_CLIENT,
    REDIS_KEY_JIKKYO_FORCE_COUNT,
    REDIS_KEY_VIEWER_COUNT,
    VERSION,
)
from app.models.comment import (
    ChannelResponse,
    ThreadResponse,
)


# ルーター
router = APIRouter(
    tags = ['Channels'],
    prefix = '/api/v1',
)

# チャンネル情報のキャッシュ
__channels_cache: list[ChannelResponse] | None = None
__channels_cache_expiry: float | None = None


@router.get(
    '/channels',
    summary = 'チャンネル情報 API',
    response_description = 'チャンネル情報。',
    response_model = list[ChannelResponse],
)
async def ChannelsAPI():
    """
    全チャンネルの情報と、各チャンネルごとの全スレッドの情報を一括で取得する。
    """

    global __channels_cache, __channels_cache_expiry

    # キャッシュが有効であればそれを返す
    ## 下記クエリはかなり重いので、できるだけキャッシュを返したい
    if __channels_cache is not None and __channels_cache_expiry is not None and time.time() < __channels_cache_expiry:
        return __channels_cache

    # ID 昇順、スレッドは新しい順でチャンネルを取得
    connection = connections.get('default')
    channels = await connection.execute_query_dict(
        '''
        SELECT
            c.id,
            c.name,
            c.description,
            t.id AS thread_id,
            t.start_at,
            t.end_at,
            t.duration,
            t.title,
            t.description AS thread_description,
            cc.max_no AS comments_count
        FROM channels c
        LEFT JOIN threads t ON c.id = t.channel_id
        LEFT JOIN comment_counters cc ON t.id = cc.thread_id
        ORDER BY c.id ASC, t.start_at ASC
        '''
    )

    response: list[ChannelResponse] = []
    current_channel_id: int | None = None
    current_channel_name: str | None = None
    current_channel_description: str | None = None
    threads: list[ThreadResponse] = []
    for row in channels:
        if current_channel_id != row['id']:
            if current_channel_id is not None:
                response.append(ChannelResponse(
                    id = f'jk{current_channel_id}',
                    name = cast(str, current_channel_name),
                    description = cast(str, current_channel_description),
                    threads = threads,
                ))
            current_channel_id = cast(int, row['id'])
            current_channel_name = cast(str, row['name'])
            current_channel_description = cast(str, row['description'])
            threads = []

        # タイムゾーン情報を付加した datetime に変換する
        start_at = row['start_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
        end_at = row['end_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))

        # スレッドの現在のステータスを算出する
        now = timezone.now()
        status: Literal['ACTIVE', 'UPCOMING', 'PAST']
        if start_at <= now <= end_at:
            status = 'ACTIVE'
        elif start_at > now:
            status = 'UPCOMING'
        else:
            status = 'PAST'

        # ステータスが ACTIVE (放送中) のスレッドのみ、当該チャンネルに対応する実況勢いカウントを取得
        ## スコア (UNIX タイムスタンプ) が現在時刻から 60 秒以内の範囲のエントリの数が実況勢いとなる
        if status == 'ACTIVE':
            current_time = time.time()
            jikkyo_force_count = await REDIS_CLIENT.zcount(f'{REDIS_KEY_JIKKYO_FORCE_COUNT}:jk{current_channel_id}', current_time - 60, current_time)
        else:
            jikkyo_force_count = None

        # ステータスが ACTIVE (放送中) のスレッドのみ、当該チャンネルに対応する同時接続数カウントを取得
        if status == 'ACTIVE':
            viewer_count = int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, f'jk{current_channel_id}') or 0)
        else:
            viewer_count = None

        # スレッド情報を追加
        threads.append(ThreadResponse(
            id = cast(int, row['thread_id']),
            start_at = start_at,
            end_at = end_at,
            duration = cast(int, row['duration']),
            title = cast(str, row['title']),
            description = cast(str, row['thread_description']),
            status = status,
            jikkyo_force = jikkyo_force_count,
            viewers = viewer_count,
            comments = cast(int, row['comments_count']),
        ))

    if current_channel_id is not None:
        response.append(ChannelResponse(
            id = f'jk{current_channel_id}',
            name = cast(str, current_channel_name),
            description = cast(str, current_channel_description),
            threads = threads,
        ))

    # キャッシュを更新 (10秒間有効)
    __channels_cache = response
    __channels_cache_expiry = time.time() + 10

    return response


@router.get(
    '/channels/xml',
    summary = 'namami・旧ニコニコ実況互換用チャンネル情報 API',
    response_class = Response,
    responses = {
        status.HTTP_200_OK: {
            'description': 'namami・旧ニコニコ実況互換用のチャンネル情報。',
            'content': {'application/xml': {}},
        }
    }
)
async def ChannelsXMLAPI():
    """
    namami・旧ニコニコ実況互換用のチャンネル情報を XML 形式で返す。<br>
    NicoJK.ini の channelsUri= に指定する用途を想定。
    """

    channels_response = await ChannelsAPI()

    root = ET.Element('channels', status='ok')

    for channel in channels_response:
        channel_id_num = int(channel.id.replace('jk', ''))
        if channel_id_num < 100:
            channel_element = ET.SubElement(root, 'channel')
        else:
            channel_element = ET.SubElement(root, 'bs_channel')

        ET.SubElement(channel_element, 'id').text = str(channel_id_num)
        if channel_id_num < 100:
            ET.SubElement(channel_element, 'no').text = str(channel_id_num)
        ET.SubElement(channel_element, 'name').text = channel.name
        ET.SubElement(channel_element, 'video').text = channel.id

        # アクティブな最初のスレッドの情報のみを返す
        # 通常アクティブなスレッドは1つだけのはずだが…
        active_threads = [thread for thread in channel.threads if thread.status == 'ACTIVE']
        if active_threads:
            thread = active_threads[0]
            thread_element = ET.SubElement(channel_element, 'thread')
            ET.SubElement(thread_element, 'id').text = str(thread.id)
            ET.SubElement(thread_element, 'last_res').text = ''  # 常に空文字列
            ET.SubElement(thread_element, 'force').text = str(thread.jikkyo_force)
            ET.SubElement(thread_element, 'viewers').text = str(thread.viewers)
            ET.SubElement(thread_element, 'comments').text = str(thread.comments)

    xml_str = ET.tostring(root, encoding='utf-8', method='xml')
    return Response(content=xml_str, media_type='application/xml; charset=UTF-8')


@router.get(
    '/channels/{channel_id}/logo',
    summary = 'チャンネルロゴ API',
    response_class = Response,
    responses = {
        status.HTTP_200_OK: {
            'description': 'チャンネルロゴ。',
            'content': {'image/png': {}},
        }
    }
)
def ChannelLogoAPI(
    request: Request,
    channel_id: Annotated[str, Path(description='チャンネル ID 。ex: jk101')],
):
    """
    指定されたチャンネルに紐づくロゴを取得する。
    """

    def GetETag(logo_data: bytes) -> str:
        """ ロゴデータのバイナリから ETag を生成する """
        return hashlib.sha256(logo_data).hexdigest()

    # HTTP レスポンスヘッダーの Cache-Control の設定
    ## 1ヶ月キャッシュする
    CACHE_CONTROL = 'public, no-transform, immutable, max-age=2592000'

    # ***** 同梱のロゴを利用（存在する場合）*****

    def ValidateAndResolvePath(base_dir: pathlib.Path, relative_path: str) -> pathlib.Path:
        """ ベースディレクトリ内の相対パスを検証し、正規化されたパスを返す """
        resolved_path = (base_dir / relative_path).resolve()
        if not resolved_path.is_relative_to(base_dir):
            raise HTTPException(status_code=400, detail='Invalid path traversal attempt.')
        return resolved_path

    # 同梱されているロゴがあれば取得する
    logo_path = ValidateAndResolvePath(LOGO_DIR, f'{channel_id}.png')

    # Path.exists() が同期的なので、あえて同期 API で実装している
    if logo_path.exists():

        # リクエストに If-None-Match ヘッダが存在し、ETag が一致する場合は 304 を返す
        ## ETag はロゴファイルのパスとバージョン情報のハッシュから生成する
        etag = GetETag(f'{logo_path}{VERSION}'.encode())
        if request.headers.get('If-None-Match') == etag:
            return Response(status_code=304)

        # ロゴデータを返す
        return FileResponse(logo_path, headers={
            'Cache-Control': CACHE_CONTROL,
            'ETag': etag,
        })

    # ***** デフォルトのロゴ画像を利用 *****

    # 同梱のロゴファイルも Mirakurun や EDCB からのロゴもない場合は、デフォルトのロゴ画像を返す
    return FileResponse(LOGO_DIR / 'default.png', headers={
        'Cache-Control': CACHE_CONTROL,
        'ETag': GetETag('default'.encode()),
    })


@router.get(
    '/channels/total-viewers',
    summary = '全チャンネルの同時接続数カウントの合計を返す API',
    response_model = dict,
    responses = {
        status.HTTP_200_OK: {
            'description': '全チャンネルの同時接続数カウントの合計。',
            'content': {'application/json': {}},
        },
    },
)
async def GetTotalViewers():
    """
    全チャンネルの同時接続数カウントの合計を返す。ほぼデバッグ&負荷検証用。
    """
    channels = await ChannelsAPI()
    total_viewers = sum(
        thread.viewers for channel in channels for thread in channel.threads if thread.viewers is not None
    )
    return {'total_viewers': total_viewers}
