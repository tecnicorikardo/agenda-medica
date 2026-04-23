from __future__ import annotations

from pydantic import BaseModel
from pydantic.config import ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

