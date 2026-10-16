import time
from datetime import datetime
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import DateTime, Float, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from base62 import encode
from cache import LRUCache

DB_URL = "sqlite:///links.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Link(Base):
    """One row per shortened URL. ~500 bytes at production scale."""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    long_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    expires_at: Mapped[float | None] = mapped_column(Float, nullable=True)


Base.metadata.create_all(engine)

# One cache per process, ~100k entries of (code -> long_url).
# Capacity math: 100k x ~250 B = 25 MB — trivially fits in RAM.
cache = LRUCache(capacity=100_000)

app = FastAPI(title="sho.rt — URL shortener")


class CreateLink(BaseModel):
    long_url: str
    custom_alias: str | None = None

    @field_validator("long_url")
    @classmethod
    def check_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("long_url must be an absolute http(s) URL")
        if len(v) > 2048:
            raise ValueError("long_url longer than 2048 characters")
        return v


@app.post("/links", status_code=201)
def create_link(body: CreateLink):
    with SessionLocal() as db:
        if body.custom_alias:
            clash = db.query(Link).filter_by(code=body.custom_alias).first()
            if clash:
                raise HTTPException(409, "alias already taken")
            link = Link(code=body.custom_alias, long_url=body.long_url)
            db.add(link)
        else:
            # The auto-increment id IS the global counter.
            link = Link(code="", long_url=body.long_url)
            db.add(link)
            db.flush()  # assigns link.id without committing yet
            link.code = encode(link.id)  # e.g. 1_000_000 -> "4c92"
        db.commit()
        db.refresh(link)

    cache.set(link.code, link.long_url)  # write-through: fill on create
    return {"code": link.code, "short_url": f"http://sho.rt/{link.code}"}


@app.get("/{code}")
def redirect(code: str):
    # 1) Cache hit — the common case (~98% of traffic)
    long_url = cache.get(code)
    if long_url is None:
        # 2) Cache miss — read the database, then backfill the cache
        with SessionLocal() as db:
            link = db.query(Link).filter_by(code=code).first()
            if link is None:
                raise HTTPException(404, "unknown code")
            if link.expires_at and link.expires_at < time.time():
                db.delete(link)
                db.commit()
                raise HTTPException(404, "expired")
            long_url = link.long_url
        cache.set(code, long_url)

    # 302 = temporary: browsers don't cache it, so we can count clicks.
    return RedirectResponse(long_url, status_code=302)