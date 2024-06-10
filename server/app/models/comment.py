
# Type Hints を指定できるように
# ref: https://stackoverflow.com/a/33533514/17124142
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model as TortoiseModel


class Channel(TortoiseModel):
    """
    実況チャンネルを表す Tortoise ORM モデル (マスタデータ)
    jk1: NHK総合 みたいな
    """

    # データベース上のテーブル名
    class Meta(TortoiseModel.Meta):
        table: str = 'channels'

    # ID は (jk)1, (jk)2 のような固定値で、初回起動時に登録される
    id = fields.IntField(pk=True, generated=False)
    # チャンネル名
    name = fields.CharField(255)
    # チャンネルの説明
    description = fields.TextField()
    # スレッド一覧
    threads: fields.ReverseRelation[Thread]


class Thread(TortoiseModel):
    """
    コメントのスレッドを表す Tortoise ORM モデル
    各チャンネルごとに毎日4時に新しいスレッドが開始され、翌朝4時に終了する
    各チャンネルで同時に開催されるスレッドは1つだけ (ニコニコ実況の仕様に準拠)
    """

    # データベース上のテーブル名
    class Meta(TortoiseModel.Meta):
        table: str = 'threads'

    # ID は自動でインクリメントされる
    id = fields.IntField(pk=True)
    # スレッドが開催されているチャンネル ID
    channel = fields.ForeignKeyField('models.Channel', related_name='threads')
    channel_id: int
    # スレッド開始日時
    start_at = fields.DatetimeField(auto_now_add=True)
    # スレッド終了日時
    end_at = fields.DatetimeField(null=True)
    # スレッドの放送時間長
    duration = fields.IntField()
    # スレッドのタイトル
    title = fields.CharField(255)
    # スレッドの説明
    description = fields.TextField()


class Comment(TortoiseModel):
    """
    ニコニコ実況互換のコメントを表す Tortoise ORM モデル
    """

    # データベース上のテーブル名
    class Meta(TortoiseModel.Meta):
        table: str = 'comments'

    # ID は自動でインクリメントされる
    id = fields.IntField(pk=True)
    # コメントのスレッド ID
    thread = fields.ForeignKeyField('models.Thread', related_name='comments')
    thread_id: int
    # コメント番号（コメ番）
    # ex: 46712
    no = fields.IntField()
    # スレッド開始からのコメントの再生位置（10ミリ秒単位）
    # ex: 7201727
    vpos = fields.IntField()
    # コメント投稿日時
    # ex: 1717426821.46713 (UNIX タイムスタンプ換算)
    # 実際にニコ生互換のレスポンスで返す際は数値の date と小数点以下の date_usec に分割される
    date = fields.DatetimeField(auto_now=True)
    # コメントのコマンド（184, red naka big など / 歴史的経緯で mail というフィールドながらコマンドが入る）
    # ex: 184 white naka medium
    mail = fields.CharField(255, default='')
    # ユーザー ID（コマンドに 184 が指定されている場合は匿名化される）
    # ex: z7edP-AgH-4reNetV-sFtPDN0fk
    user_id = fields.CharField(255)
    # コメントしたユーザーがプレミアム会員であれば true
    premium = fields.BooleanField(default=False)
    # 匿名コメントであれば true
    anonymity = fields.BooleanField(default=False)
    # コメント本文（XML 形式では chat 要素自体の値）
    content = fields.TextField()


class ChannelResponse(BaseModel):
    """
    チャンネル情報のレスポンスの Pydantic モデル
    """
    id: str
    name: str
    description: str
    threads: list[ThreadResponse]

class ThreadResponse(BaseModel):
    """
    スレッド情報のレスポンスの Pydantic モデル
    """
    id: int
    start_at: datetime
    end_at: datetime
    duration: int
    title: str
    description: str
    jikkyo_force: int | None
    viewers: int
    comments: int
