
import asyncio
import traceback
from datetime import datetime, timedelta
from time import time
from typing import Any, Literal
from urllib.parse import quote
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from app import logging
from app.constants import HTTPX_CLIENT
from app.utils.TSInformation import TSInformation


class ProgramInfo(BaseModel):
    # TVer から取得したタイトル (フル)
    title: str
    # 番組開始時刻 (常に Asia/Tokyo の datetime)
    start_at: datetime
    # 番組終了時刻 (常に Asia/Tokyo の datetime)
    end_at: datetime
    # 番組長 (秒単位)
    duration: int
    # ジャンル名
    genre: str | None = None

class TVerBroadcasterInfo(BaseModel):
    # ota: 地上波 / bs: BS
    type: Literal['ota', 'bs']
    # area: 放送範囲 (東京なら 23 など)
    area: int
    # ブロードキャスター ID
    broadcaster_id: int

# ニコニコ実況 ID から Tver API 上の放送局情報への変換マップ
JIKKYO_ID_TO_TVER_BROADCASTER_INFO_MAP: dict[str, TVerBroadcasterInfo] = {
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
    'jk13': TVerBroadcasterInfo(type='ota', area=42, broadcaster_id=593),
    'jk14': TVerBroadcasterInfo(type='ota', area=41, broadcaster_id=588),
    'jk101': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=1),
    'jk141': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=5),
    'jk151': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=8),
    'jk161': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=11),
    'jk171': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=14),
    'jk181': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=17),
    'jk191': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=20),
    'jk192': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=21),
    'jk193': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=22),
    'jk200': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=23),
    'jk201': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=24),
    'jk211': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=26),
    'jk222': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=27),
    'jk236': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=31),
    'jk252': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=39),
    'jk260': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=260),
    'jk263': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=263),
    'jk265': TVerBroadcasterInfo(type='bs', area=23, broadcaster_id=265),
}

# ジャンル ID からジャンル文字列への変換マップ
GENRE_ID_TO_GENRE_NAME_MAP: dict[int, str] = {
    0x0: 'ニュース・報道',
    0x1: 'スポーツ',
    0x2: '情報・ワイドショー',
    0x3: 'ドラマ',
    0x4: '音楽',
    0x5: 'バラエティ',
    0x6: '映画',
    0x7: 'アニメ・特撮',
    0x8: 'ドキュメンタリー・教養',
    0x9: '劇場・公演',
    0xA: '趣味・教育',
    0xB: '福祉',
    0xE: '拡張',
    0xF: 'その他',
}

# キャッシュの TTL (秒)
CACHE_TTL = 60 * 30  # 30分
# キャッシュのマップ
CACHE: dict[str, tuple[Any, float]] = {}


async def GetNowAndNextProgramInfos() -> dict[str, tuple[ProgramInfo | None, ProgramInfo | None]]:
    """
    TVer の番組表 API から、実況 ID に対応する現在放送中・次に放送される番組情報を取得する

    Returns:
        dict[str, tuple[ProgramInfo | None, ProgramInfo | None]]: 実況 ID に対応する現在放送中・次に放送される番組情報
    """

    # 5:00 より前は前日の番組表を取得する
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    if now.hour < 5:
        date = (now - timedelta(days=1)).strftime('%Y/%m/%d')
    else:
        date = now.strftime('%Y/%m/%d')

    async def fetch_programs(area: int, type_: str) -> dict[str, Any]:
        url = f'https://service-api.tver.jp/api/v1/callEPGv2?date={quote(date)}&area={area}&type={type_}'

        current_time = time()
        if url in CACHE:
            cached_data, expiration_time = CACHE[url]
            if current_time < expiration_time:
                return cached_data

        try:
            async with HTTPX_CLIENT() as client:
                response = await client.get(url, headers={
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'ja',
                    'origin': 'https://tver.jp',
                    'referer': 'https://tver.jp/',
                    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                    'x-tver-platform-type': 'web',
                })
                response.raise_for_status()
                response_json = response.json()
                logging.info(f'Successfully fetched programs from TVer API (type: {type_}, area: {area})')
                CACHE[url] = (response_json, current_time + CACHE_TTL)
                return response_json
        except Exception as e:
            logging.error(f'An error occurred while calling the TVer API: {e}')
            logging.error(traceback.format_exc())
            return {}

    def get_current_and_next_programs(programs: list[dict[str, Any]]) -> tuple[ProgramInfo | None, ProgramInfo | None]:
        current_program: ProgramInfo | None = None
        next_program: ProgramInfo | None = None

        for program in programs:
            try:
                start_at = datetime.fromtimestamp(program['startAt'], ZoneInfo('Asia/Tokyo'))
                end_at = datetime.fromtimestamp(program['endAt'], ZoneInfo('Asia/Tokyo'))

                if start_at <= now < end_at or (now < start_at and next_program is None):
                    title = TSInformation.formatString(program['title'])

                    # アイコン情報を追加
                    icons = []
                    if program['icon']['new']:
                        icons.append('[新]')
                    if program['icon']['revival']:
                        icons.append('[再]')
                    if program['icon']['last']:
                        icons.append('[終]')
                    if icons:
                        title = f"{''.join(icons)}{title}"

                    # ジャンルは "0xA" のようになぜか16進数表記の文字列で入っているので、適切に int に変換してからジャンル名にする
                    genre = None
                    if program.get('genre'):
                        genre_id = int(program['genre'], 16)
                        genre = GENRE_ID_TO_GENRE_NAME_MAP.get(genre_id)

                    program_info = ProgramInfo(
                        title=title,
                        start_at=start_at,
                        end_at=end_at,
                        duration=int((end_at - start_at).total_seconds()),
                        genre=genre,
                    )

                    if start_at <= now < end_at:
                        current_program = program_info
                    else:
                        next_program = program_info

                if current_program and next_program:
                    break
            except Exception as e:
                logging.error(f'An error occurred while processing the program information: {e}')
                logging.error(traceback.format_exc())
                continue

        return current_program, next_program

    results = {}
    tasks = []
    for type_ in ['ota', 'bs']:
        areas = set(info.area for info in JIKKYO_ID_TO_TVER_BROADCASTER_INFO_MAP.values() if info.type == type_)
        tasks.extend(fetch_programs(area, type_) for area in areas)

    responses = await asyncio.gather(*tasks)
    for response in responses:
        try:
            for content in response.get('result', {}).get('contents', []):
                broadcaster_id = int(content['broadcaster']['id'])
                for jk_id, info in JIKKYO_ID_TO_TVER_BROADCASTER_INFO_MAP.items():
                    if info.broadcaster_id == broadcaster_id:
                        results[jk_id] = get_current_and_next_programs(content.get('programs', []))
        except Exception as e:
            logging.error(f'An error occurred while processing the response: {e}')
            logging.error(traceback.format_exc())
            continue

    return results


if __name__ == '__main__':
    import os
    async def main():
        results = await GetNowAndNextProgramInfos()
        terminal_width = os.get_terminal_size().columns
        print('=' * terminal_width)
        for jk_id, (current_program, next_program) in results.items():
            print(f'チャンネル: {jk_id}')
            print('-' * terminal_width)
            if current_program:
                print(f'現在の番組: {current_program.title}')
                print(f'  開始時刻: {current_program.start_at.strftime("%Y-%m-%d %H:%M:%S")} 終了時刻: {current_program.end_at.strftime("%Y-%m-%d %H:%M:%S")}')
                print(f'  長さ: {current_program.duration // 60}分 ジャンル: {current_program.genre or "不明"}')
            else:
                print('現在の番組: なし')
            print('-' * terminal_width)
            if next_program:
                print(f'次の番組: {next_program.title}')
                print(f'  開始時刻: {next_program.start_at.strftime("%Y-%m-%d %H:%M:%S")} 終了時刻: {next_program.end_at.strftime("%Y-%m-%d %H:%M:%S")}')
                print(f'  長さ: {next_program.duration // 60}分 ジャンル: {next_program.genre or "不明"}')
            else:
                print('次の番組: なし')
            print('=' * terminal_width)
    asyncio.run(main())
