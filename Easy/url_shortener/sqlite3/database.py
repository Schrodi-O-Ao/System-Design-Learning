import sqlite3

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'short.db'

# If your db code expects a string:
DB_PATH_STR = str(BASE_DIR / 'short.db')

def init_db() -> None:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("""
    CREATE TABLE IF NOT EXISTS links( 
    short_url   PRIMARY KEY,    -- PRIMARY KEY = must be unique + automatically indexed
    long_url    TEXT NOT NULL,
    create_at   REAL NOT NULL,
    expires_at  REAL            -- NULL means "never expires"
    )   
    """)
    connection.commit()
    connection.close()

def get_db():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

init_db()