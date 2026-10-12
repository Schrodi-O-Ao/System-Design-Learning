import sqlite3

DB_PATH = 'short.db'

def init_db() -> None:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("""
    CREATE IF NOT EXIST links,
    short_url   PRIMARY KEY,
    long_url    TEXT NOT NULL,
    create_at   REAL NOT NULL,
    expires_at  REAL   
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