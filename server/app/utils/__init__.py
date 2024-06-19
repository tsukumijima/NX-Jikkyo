
import asyncio
from datetime import datetime, timedelta
from typing import Any, Literal, TypedDict
from zoneinfo import ZoneInfo

from app.constants import HTTPX_CLIENT


class TVerBroadcasterInfo(TypedDict):
    # ota: 地上波 / bs: BS
    type: Literal['ota', 'bs']
    # area: 放送範囲 (東京なら 23 など)
    area: int
    # ブロードキャスター ID
    broadcaster_id: int


# ニコニコ実況 ID から Tver API 上の放送局情報への変換マップ
JIKKYO_ID_TO_TVER_BROADCASTER_INFO: dict[str, TVerBroadcasterInfo] = {
    'jk1': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=120),
    'jk2': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=124),
    'jk4': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=128),
    'jk5': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=138),
    'jk6': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=131),
    'jk7': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=142),
    'jk8': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=134),
    'jk9': TVerBroadcasterInfo(type='ota', area=23, broadcaster_id=399),
    'jk10': TVerBroadcasterInfo(type='ota', area=29, broadcaster_id=426),
    'jk11': TVerBroadcasterInfo(type='ota', area=24, broadcaster_id=404),
    'jk12': TVerBroadcasterInfo(type='ota', area=27, broadcaster_id=417),
    'jk101': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=1),
    'jk141': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=5),
    'jk151': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=8),
    'jk161': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=11),
    'jk171': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=14),
    'jk181': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=17),
    'jk191': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=20),
    'jk192': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=21),
    'jk193': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=22),
    'jk211': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=26),
    'jk222': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=27),
    'jk236': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=31),
    'jk252': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=39),
    'jk260': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=260),
    'jk263': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=263),
    'jk265': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=265),
}

class ProgramInfo(TypedDict):
    # TVer から取得したタイトル (フル)
    title: str
    # 番組開始時刻 (常に Asia/Tokyo の datetime)
    start_at: datetime
    # 番組終了時刻 (常に Asia/Tokyo の datetime)
    end_at: datetime
    # 番組長 (分単位)
    duration_minutes: int


async def GetNowONAirProgramInfos() -> dict[str, ProgramInfo]:
    """
    TVer の番組表 API から、実況 ID に対応する現在放送中の番組情報を取得する

    Returns:
        dict[str, ProgramInfo]: 実況 ID に対応する現在放送中の番組情報
    """

    # 5:00 より前は前日の番組表を取得する
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    if now.hour < 5:
        date = (now - timedelta(days=1)).strftime('%Y/%m/%d')
    else:
        date = now.strftime('%Y/%m/%d')

    async def fetch_programs(area: int, type_: str) -> dict[str, Any]:
        url = f'https://service-api.tver.jp/api/v1/callEPGv2?date={date}&area={area}&type={type_}'
        async with HTTPX_CLIENT() as client:
            response = await client.get(url, headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'x-tver-platform-type': 'web',
            })
            response.raise_for_status()
            return response.json()

    async def get_current_program(programs: list[dict[str, Any]]) -> ProgramInfo | None:
        for program in programs:
            start_at = datetime.fromtimestamp(program['startAt'], ZoneInfo('Asia/Tokyo'))
            end_at = datetime.fromtimestamp(program['endAt'], ZoneInfo('Asia/Tokyo'))
            title = program['title']
            # もし programs['icon']['new'] が True なら "[新]" を title の先頭に付け足す
            if program['icon']['new']:
                title = f'[新]{title}'
            # もし programs['icon']['revival'] が True なら "[再]" を title の先頭に付け足す
            if program['icon']['revival']:
                title = f'[再]{title}'
            # もし programs['icon']['last'] が True なら "[終]" を title の先頭に付け足す
            if program['icon']['last']:
                title = f'[終]{title}'
            # 分単位の番組長を算出
            duration_minutes = int((end_at - start_at).total_seconds() / 60)
            if start_at <= now < end_at:
                return ProgramInfo(
                    title=title,
                    start_at=start_at,
                    end_at=end_at,
                    duration_minutes=duration_minutes,
                )
        return None

    results = {}
    tasks = []
    for type_ in ['ota', 'bs']:
        areas = {info['area'] for info in JIKKYO_ID_TO_TVER_BROADCASTER_INFO.values() if info['type'] == type_}
        for area in areas:
            tasks.append(fetch_programs(area, type_))

    responses = await asyncio.gather(*tasks)
    for response in responses:
        for content in response['result']['contents']:
            broadcaster_id = int(content['broadcaster']['id'])
            for jk_id, info in JIKKYO_ID_TO_TVER_BROADCASTER_INFO.items():
                if info['broadcaster_id'] == broadcaster_id:
                    current_program = await get_current_program(content['programs'])
                    if current_program:
                        results[jk_id] = current_program

    return results
