from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict


class URLCreate(BaseModel):
    target_url: HttpUrl


class URLInfo(BaseModel):
    target_url: str
    short_code: str
    clicks: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
