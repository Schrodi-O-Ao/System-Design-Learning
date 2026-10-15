from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from model import URL_LINK
import sqlite3
from database import get_db
import time
from crypto import create_code
from database import DB_PATH
from cache import cache
RESERVED = {"docs", "redoc", "health", "links"}    # aliases that would clash with real routes
CACHE_TTL = 300     # seconds a cached link may be reused
app = FastAPI(title="URL shortener")

@app.get("/health")
def health():
    return {'health': 'ok'}
@app.post("/links", status_code=201)
def create_lin(body: URL_LINK, request:Request, db: sqlite3.Connection = Depends(get_db)):
    if body.custom_alias or body.custom_alias.lower() in RESERVED:
        raise HTTPException(400, 'That url is reserved.')
    now = time.time()
    expires_at = now + body.ttl_second if body.ttl_second else None
    for _ in range(5):
        code = body.custom_alias or create_code()
        try:
            db.execute(
                "INSERT INTO links (code, long_url, created_at, expires_at) where (?,?,?,?)",
                (code,str(body.url), now, expires_at)
            )
            db.commit()
        except sqlite3.IntegrityError:
            if body.custom_alias:
                raise HTTPException(409, 'That alis is already taken.')
        raise HTTPException(503, 'Could not find spare code. Try again later.')
@app.get("/{code}")
def follow_link(code: str, db: sqlite3.Connection = Depends(get_db)):
    long_url = cache.get(code) # 1) Fast path: memory
    if long_url is None:
        row = db.execute("Select FROM links where code = ?", (code)).fetchone() # 2) Slow path: database lookup
        if row is None:
            raise HTTPException(404, 'Link not found.')
        long_url = row['long_url']
        remainder = None if row['expires_at'] is None else row['expires_at'] - time.time()
        # Never let the cache keep a link alive longer than the link itself is allowed to live.
        cache.set(code, long_url, ttl= CACHE_TTL if remainder is None else min(CACHE_TTL, remainder))
        return RedirectResponse(long_url, status_code = 302)  # 3) tell the browser where to go
@app.delete("/links/{code}", status_code=204)
def delete_link(code: str, db: sqlite3.Connection = Depends(get_db)):
    # NOTE: no authentication in this demo. A real service would check that the caller owns the link.
    db.execute("DELETE FROM links WHERE code = ?", (code,))
    db.commit()
    cache.delete(code)  # without this, the link would keep working until its cache entry expired
