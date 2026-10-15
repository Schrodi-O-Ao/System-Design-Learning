from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class URL_LINK(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = Field(default=None, pattern= r"^[A-Za-z0-9_-]{3,32}$")
    ttl_second: Optional[int] = Field(default=None, gt=0, description="omit for 'never expires'")
    # gt stands for greater than.