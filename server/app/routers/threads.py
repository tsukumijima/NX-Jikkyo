
from fastapi import (
    APIRouter,
    HTTPException,
    Path,
)
from tortoise import timezone
from typing import Annotated, Literal

from app.models.comment import (
    Comment,
    CommentResponse,
    Thread,
    ThreadWithCommentsResponse,
)


# ルーター
router = APIRouter(
    tags = ['Threads'],
    prefix = '/api/v1',
)


@router.get(
    '/threads/{thread_id}',
    summary = 'スレッド取得 API',
    response_description = 'スレッド情報とスレッド内の全コメント。',
    response_model = ThreadWithCommentsResponse,
)
async def ThreadAPI(thread_id: Annotated[int, Path(description='スレッド ID 。')]):
    """
    指定されたスレッドの情報と、スレッド内の全コメントを取得する。
    """

    # スレッドが存在するか確認
    thread = await Thread.filter(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail='Thread not found.')

    # スレッドの現在のステータスを算出する
    now = timezone.now()
    status: Literal['ACTIVE', 'UPCOMING', 'PAST']
    if thread.start_at <= now <= thread.end_at:
        status = 'ACTIVE'
    elif thread.start_at > now:
        status = 'UPCOMING'
    else:
        status = 'PAST'

    # スレッドの全コメントをコメ番順に取得
    comments = await Comment.filter(thread_id=thread_id).order_by('no').all()

    # コメントを変換
    comment_responses: list[CommentResponse] = []
    for comment in comments:
        comment_responses.append(CommentResponse(
            id = comment.id,
            thread_id = comment.thread_id,
            no = comment.no,
            vpos = comment.vpos,
            date = comment.date,
            mail = comment.mail,
            user_id = comment.user_id,
            premium = comment.premium,
            anonymity = comment.anonymity,
            content = comment.content,
        ))

    # スレッド情報とコメント情報を返す
    thread_response = ThreadWithCommentsResponse(
        id = thread.id,
        channel_id = f'jk{thread.channel_id}',
        start_at = thread.start_at,
        end_at = thread.end_at,
        duration = thread.duration,
        title = thread.title,
        description = thread.description,
        status = status,
        jikkyo_force = None,
        viewers = None,
        comments = comment_responses,
    )

    return thread_response
