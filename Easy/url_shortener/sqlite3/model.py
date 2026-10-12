from pydantic import BaseModel, Field, HttpUrl


class URL(BaseModel):
    url: HttpUrl