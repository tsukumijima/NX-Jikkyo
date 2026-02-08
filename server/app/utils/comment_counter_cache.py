from app import logging
from app.constants import (
    REDIS_CLIENT,
    REDIS_KEY_THREAD_COMMENT_COUNTER,
)


# Redis への更新は「投稿パス」「インポートパス」「定期同期パス」から同時に到達する
## 単純な HGET -> 比較 -> HSET では、並行実行時に古い値で上書きされる競合が発生しうる
## Lua script で「現在値より大きい時だけ更新」を 1 コマンドで実行し、単調増加を保証する
THREAD_COMMENT_COUNTER_UPDATE_SCRIPT = """
local cache_key = KEYS[1]
local thread_field = ARGV[1]
local new_comment_no = tonumber(ARGV[2])

local current_comment_no = redis.call('HGET', cache_key, thread_field)
if current_comment_no == false then
    redis.call('HSET', cache_key, thread_field, new_comment_no)
    return new_comment_no
end

current_comment_no = tonumber(current_comment_no)
if current_comment_no < new_comment_no then
    redis.call('HSET', cache_key, thread_field, new_comment_no)
    return new_comment_no
end

return current_comment_no
"""


async def GetThreadCommentCounterCache(thread_id: int) -> int | None:
    """
    Redis からスレッドごとの最新コメ番キャッシュを取得する

    Args:
        thread_id (int): スレッド ID

    Returns:
        int | None: キャッシュが存在する場合は最新コメ番、存在しない場合は None
    """

    # Redis Hash の field は str に統一して扱う
    ## 型を固定しておくことで、他経路からの更新と衝突しにくくする
    cached_comment_counter = await REDIS_CLIENT.hget(REDIS_KEY_THREAD_COMMENT_COUNTER, str(thread_id))
    if cached_comment_counter is None:
        return None

    try:
        # 値が数値として読めることを保証してから返す
        return int(cached_comment_counter)
    except ValueError as ex:
        # 壊れた値は次回も失敗を誘発するため、この場で削除して自己修復を優先する
        logging.warning(
            f'GetThreadCommentCounterCache: Invalid cached comment counter found. thread_id: {thread_id}',
            exc_info = ex,
        )
        await REDIS_CLIENT.hdel(REDIS_KEY_THREAD_COMMENT_COUNTER, str(thread_id))
        return None


async def UpdateThreadCommentCounterCache(thread_id: int, comment_no: int) -> int:
    """
    Redis 上の最新コメ番キャッシュを、与えられたコメ番以上になるように更新する

    Args:
        thread_id (int): スレッド ID
        comment_no (int): 更新候補のコメ番

    Returns:
        int: 更新後に Redis に保存されている最新コメ番
    """

    # Lua script で単調増加更新を原子的に実行する
    ## 返り値は「更新後に Redis に残っている値」で、呼び出し元はそのまま採用できる
    updated_comment_counter = await REDIS_CLIENT.eval(
        THREAD_COMMENT_COUNTER_UPDATE_SCRIPT,
        1,
        REDIS_KEY_THREAD_COMMENT_COUNTER,
        str(thread_id),
        str(comment_no),
    )
    return int(updated_comment_counter)
