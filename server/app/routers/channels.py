
import base64
import hashlib
import pathlib
import time
import xml.etree.ElementTree as ET
from async_lru import alru_cache
from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from pydantic import TypeAdapter
from tortoise import connections
from tortoise import timezone
from typing import Annotated, cast, Literal
from zoneinfo import ZoneInfo

from app import logging
from app import schemas
from app.constants import (
    LOGO_DIR,
    REDIS_CLIENT,
    REDIS_KEY_CHANNEL_INFOS_CACHE,
    REDIS_KEY_JIKKYO_FORCE_COUNT,
    REDIS_KEY_VIEWER_COUNT,
    VERSION,
)
from app.models.comment import (
    ChannelResponse,
    ThreadResponse,
    ThreadWithoutStatisticsResponse,
)
from app.utils.Jikkyo import Jikkyo
from app.utils.TVer import GetNowAndNextProgramInfos


# ルーター
router = APIRouter(
    tags = ['Channels'],
    prefix = '/api/v1',
)


async def GetChannelResponses(full: bool = False) -> list[ChannelResponse]:
    """
    データベースから最新のチャンネル情報リストを取得する

    Args:
        full (bool, optional): チャンネルに紐づく全スレッドの情報を取得するかどうか。省略時は最新4日分のスレッドだけ取得する

    Returns:
        list[ChannelResponse]: チャンネル情報リスト
    """

    # ID 昇順、スレッドは古い順でチャンネルを取得
    ## full が False の時は、最新4日分のスレッドだけ取得する
    ## WHERE 1=1 は動的に WHERE 句を組み立てるためのダミー句
    query = '''
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
        WHERE c.id != 263
    '''
    if not full:
        query += ' AND t.start_at >= DATE_SUB(NOW(), INTERVAL 4 DAY)'
    query += ' ORDER BY c.id ASC, t.start_at ASC'
    channels = await connections.get('default').execute_query_dict(query)

    # 現在放送中・次の放送予定の番組情報を取得
    program_infos = await GetNowAndNextProgramInfos()

    # jk200 のアクティブなスレッド情報を取得 (jk263 用)
    now = timezone.now()
    active_thread_jk200 = None
    for row in channels:
        if row['id'] == 200:  # jk200
            start_at = row['start_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
            end_at = row['end_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
            if start_at <= now <= end_at:
                active_thread_jk200 = row
                break

    channel_responses: list[ChannelResponse] = []
    current_channel_id: int | None = None
    current_channel_name: str | None = None
    threads: list[ThreadResponse] = []
    for row in channels:
        if current_channel_id != row['id']:
            if current_channel_id is not None:
                channel_responses.append(ChannelResponse(
                    id = f'jk{current_channel_id}',
                    name = cast(str, current_channel_name),
                    program_present = program_infos.get(f'jk{current_channel_id}', (None, None))[0],
                    program_following = program_infos.get(f'jk{current_channel_id}', (None, None))[1],
                    threads = threads,
                ))
            current_channel_id = cast(int, row['id'])
            current_channel_name = cast(str, row['name'])
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

        description = cast(str, row['thread_description'])

        # スレッド情報を追加
        threads.append(ThreadResponse(
            id = cast(int, row['thread_id']),
            start_at = start_at,
            end_at = end_at,
            duration = cast(int, row['duration']),
            title = cast(str, row['title']),
            description = description,
            status = status,
            jikkyo_force = jikkyo_force_count,
            viewers = viewer_count,
            comments = cast(int, row['comments_count']),
        ))

    # 最後のチャンネルの情報を追加
    if current_channel_id is not None:
        channel_responses.append(ChannelResponse(
            id = f'jk{current_channel_id}',
            name = cast(str, current_channel_name),
            program_present = program_infos.get(f'jk{current_channel_id}', (None, None))[0],
            program_following = program_infos.get(f'jk{current_channel_id}', (None, None))[1],
            threads = threads,
        ))

    # jk263 の情報を追加（アクティブなスレッドと明日のスレッドの情報を jk200 から取得）
    threads_jk263: list[ThreadResponse] = []

    # アクティブなスレッドの情報を jk200 から取得
    if active_thread_jk200 is not None:
        start_at = active_thread_jk200['start_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
        end_at = active_thread_jk200['end_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
        threads_jk263.append(ThreadResponse(
            id = cast(int, active_thread_jk200['thread_id']),
            start_at = start_at,
            end_at = end_at,
            duration = cast(int, active_thread_jk200['duration']),
            title = cast(str, active_thread_jk200['title']),
            description = cast(str, active_thread_jk200['thread_description']),
            status = 'ACTIVE',
            jikkyo_force = await REDIS_CLIENT.zcount(f'{REDIS_KEY_JIKKYO_FORCE_COUNT}:jk200', time.time() - 60, time.time()),
            viewers = int(await REDIS_CLIENT.hget(REDIS_KEY_VIEWER_COUNT, 'jk200') or 0),
            comments = cast(int, active_thread_jk200['comments_count']),
        ))

    # 明日のスレッドの情報を jk200 から取得
    for row in channels:
        if row['id'] == 200:  # jk200
            start_at = row['start_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
            if start_at > now:  # 未来のスレッド
                threads_jk263.append(ThreadResponse(
                    id = cast(int, row['thread_id']),
                    start_at = start_at,
                    end_at = row['end_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo')),
                    duration = cast(int, row['duration']),
                    title = cast(str, row['title']),
                    description = cast(str, row['thread_description']),
                    status = 'UPCOMING',
                    jikkyo_force = None,
                    viewers = None,
                    comments = cast(int, row['comments_count']),
                ))

    # チャンネルレスポンスを ID でソートし直す
    # jk263 を適切な位置（jk260 と jk265 の間）に挿入
    channel_responses.append(ChannelResponse(
        id = 'jk263',
        name = 'BSJapanext',
        program_present = program_infos.get('jk200', (None, None))[0],  # jk200 の番組情報を使用
        program_following = program_infos.get('jk200', (None, None))[1],  # jk200 の番組情報を使用
        threads = threads_jk263,
    ))
    channel_responses.sort(key=lambda x: int(x.id.replace('jk', '')))

    return channel_responses


@alru_cache(maxsize=1, ttl=10)
async def GetRedisCachedChannelResponses() -> list[ChannelResponse]:
    """
    スケジューラーによって定期的に Redis にキャッシュされた、最新のチャンネル情報リストを取得する
    /api/v1/channels の負荷軽減のため、実行結果は 10 秒間メモリ上にキャッシュされる (インメモリ -> Redis の多段キャッシュ構成)

    Returns:
        list[ChannelResponse]: チャンネル情報リスト
    """

    # Redis からキャッシュを取得
    ## キャッシュは app.py で定義のスケジューラーで 10 秒おきに定期更新されているので、基本常に新鮮なキャッシュが存在するはず
    cached_channels = await REDIS_CLIENT.get(REDIS_KEY_CHANNEL_INFOS_CACHE)
    if cached_channels is not None:
        return TypeAdapter(list[ChannelResponse]).validate_json(cached_channels)

    # 万が一キャッシュが存在しない場合のみ、直接取得し一時的にキャッシュしてから返す (フェイルセーフ)
    ## この時に作成される一時キャッシュの有効期限は 10 秒とし、万が一スケジューラーが動作していない場合でも最新のデータが返されることを保証する
    channel_responses = await GetChannelResponses()
    await REDIS_CLIENT.set(REDIS_KEY_CHANNEL_INFOS_CACHE, TypeAdapter(list[ChannelResponse]).dump_json(channel_responses).decode('utf-8'), ex=10)
    logging.warning('[GetRedisCachedChannelResponses] Channel responses cache is missing. Temporary cache is created.')
    return channel_responses


@alru_cache(maxsize=1, ttl=10)
async def GetRedisCachedChannelResponsesXML() -> Response:
    """
    スケジューラーによって定期的に Redis にキャッシュされた、最新のチャンネル情報リストを XML に変換したものを取得する
    /api/v1/channels/xml の負荷軽減のため、実行結果は 10 秒間メモリ上にキャッシュされる (インメモリ -> Redis の多段キャッシュ構成)

    Returns:
        Response: XML 形式のチャンネル情報リストのレスポンス
    """

    channels_response = await GetRedisCachedChannelResponses()

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
    '/channels',
    summary = 'チャンネル情報 API',
    response_description = 'チャンネル情報。',
    response_model = list[ChannelResponse],
)
async def ChannelsAPI(
    full: Annotated[bool, Query(description='チャンネルに紐づく全スレッドの情報を取得するかどうか。省略時は最新4日分のスレッドだけ取得する。')] = False,
):
    """
    全チャンネルの情報と、各チャンネルごとの全スレッドの情報を一括で取得する。
    """

    # 全チャンネルの情報を取得する場合のみ、キャッシュを使わずデータベースから直接取得する
    if full is True:
        return await GetChannelResponses(full=True)

    # それ以外の場合はメモリ (メモリに存在しない場合は Redis) からチャンネル情報リストを取得する
    return await GetRedisCachedChannelResponses()


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

    # メモリから XML 形式のチャンネル情報リストを取得する
    return await GetRedisCachedChannelResponsesXML()


@router.get(
    '/channels/{channel_id}/threads',
    summary = 'チャンネルスレッド情報 API',
    response_model = list[ThreadWithoutStatisticsResponse],
)
async def ChannelThreadsAPI(
    channel_id: Annotated[str, Path(description='チャンネル ID 。ex: jk101')],
):
    """
    指定されたチャンネルに紐づく、過去すべてのスレッド情報を新しい順に取得する。<br>
    API 軽量化のため、実況勢いやコメント数などの統計情報、スレッドに投稿されたコメントはレスポンスに含まれない。<br>
    スレッドに投稿されたコメントを取得したいときは、別途 /api/v1/threads/{thread_id} にリクエストする必要がある。
    """

    # チャンネル ID から数値部分を抽出
    try:
        channel_id_num = int(channel_id.replace('jk', ''))
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid channel ID format.')

    # 現在時刻を取得
    now = timezone.now()

    # SQL クエリを最適化して必要な情報のみを取得
    query = '''
        SELECT
            id,
            start_at,
            end_at,
            title,
            description
        FROM threads
        WHERE channel_id = %s
        ORDER BY start_at DESC
    '''

    # クエリを実行
    threads = await connections.get('default').execute_query_dict(query, [channel_id_num])

    # スレッド情報をレスポンス形式に変換
    thread_responses: list[ThreadWithoutStatisticsResponse] = []
    for thread in threads:

        # タイムゾーン情報を付加した datetime に変換する
        start_at = thread['start_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))
        end_at = thread['end_at'].replace(tzinfo=ZoneInfo('Asia/Tokyo'))

        # スレッドのステータスを算出
        if start_at <= now <= end_at:
            status = 'ACTIVE'
        elif start_at > now:
            status = 'UPCOMING'
        else:
            status = 'PAST'

        # スレッド情報をレスポンス形式に変換
        thread_responses.append(ThreadWithoutStatisticsResponse(
            id = thread['id'],
            start_at = thread['start_at'],
            end_at = thread['end_at'],
            title = thread['title'],
            description = thread['description'],
            status = status,
        ))

    return thread_responses


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
    '/channels/{channel_id}/jikkyo',
    summary = 'ニコニコ実況 WebSocket URL API',
    response_description = 'ニコニコ実況コメント送受信用 WebSocket API の情報。',
    response_model = schemas.JikkyoWebSocketInfo,
)
async def ChannelJikkyoWebSocketInfoAPI(
    request: Request,
    channel_id: Annotated[str, Path(description='チャンネル ID 。ex: jk101')],
):
    """
    指定されたチャンネルに対応する、ニコニコ実況コメント送受信用 WebSocket API の情報を取得する。
    """

    # Cookie から NiconicoUser を取得
    niconico_user = None
    niconico_user_cookie = request.cookies.get('NX-Niconico-User')
    if niconico_user_cookie:
        try:
            niconico_user_json = base64.b64decode(niconico_user_cookie).decode('utf-8')
            niconico_user = schemas.NiconicoUser.model_validate_json(niconico_user_json)
        except Exception:
            logging.warning('[ChannelJikkyoWebSocketInfoAPI] Failed to parse NX-Niconico-User cookie.')

    # ニコニココメント送受信用 WebSocket API の情報を取得する
    jikkyo = Jikkyo(channel_id)
    jikkyo_websocket_info, updated_niconico_user = await jikkyo.fetchWebSocketInfo(request, niconico_user)

    # レスポンスを作成
    response = JSONResponse(content=jikkyo_websocket_info.model_dump())

    # 更新された NiconicoUser が存在する場合、Cookie を更新
    if updated_niconico_user is not None:
        response.set_cookie(
            key = 'NX-Niconico-User',
            value = base64.b64encode(updated_niconico_user.model_dump_json().encode('utf-8')).decode('utf-8'),
            max_age = 315360000,  # 10年間の有効期限 (秒単位)
            httponly = False,  # JavaScript からアクセスできるようにする
            samesite = 'lax',  # CSRF 攻撃を防ぐ
        )

    return response


@router.get(
    '/channels/total-viewers',
    summary = '全チャンネルの同時接続数カウント・実況勢い (コメント数/分) の合計を返す API',
    response_model = dict,
    responses = {
        status.HTTP_200_OK: {
            'description': '全チャンネルの同時接続数カウント・実況勢い (コメント数/分) の合計。',
            'content': {'application/json': {}},
        },
    },
)
async def GetTotalViewers():
    """
    全チャンネルの同時接続数カウント・実況勢い (コメント数/分) の合計を返す。ほぼデバッグ&負荷検証用。
    """
    channels = await ChannelsAPI()
    total_viewers = 0
    total_jikkyo_force = 0
    for channel in channels:
        for thread in channel.threads:
            if thread.viewers is not None:
                total_viewers += thread.viewers
            if thread.jikkyo_force is not None:
                total_jikkyo_force += thread.jikkyo_force
    return {
        'total_viewers': total_viewers,
        'total_jikkyo_force': total_jikkyo_force,
    }
