
from fastapi import APIRouter

from app.models.comment import (
    Channel,
    ChannelResponse,
)


# ルーター
router = APIRouter(
    tags = ['Comments'],
    prefix = '/api/v1',
)


@router.get(
    '/channels',
    summary = 'チャンネル情報 API',
    response_description = 'チャンネル情報。',
    response_model = list[ChannelResponse],
)
async def ChannelsAPI():
    channels = await Channel.all().order_by('id')
    response = [
        ChannelResponse(
            id=f'jk{channel.id}',
            name=channel.name,
            description=channel.description
        )
        for channel in channels
    ]
    return response

