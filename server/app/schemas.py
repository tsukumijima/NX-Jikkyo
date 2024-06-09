
# Type Hints を指定できるように
# ref: https://stackoverflow.com/a/33533514/17124142
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Annotated


# モデルに関連しない API リクエストの構造を表す Pydantic モデル
## リクエストボティの JSON 構造と一致する



# モデルに関連しない API レスポンスの構造を表す Pydantic モデル
## レスポンスボティの JSON 構造と一致する


