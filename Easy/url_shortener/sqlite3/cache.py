import threading
import time
from collections import OrderedDict # a dictionary that remembers order
from typing import Optional

CACHE_TTL = 300 # seconds a cached link may be reused
class TTLCache:
    """A thread-safe cache. An entry leaves when it's too old (TTL) or when we're out of room (LRU)."""
    def __init__(self, max_items: int = 10_000, ttl: float = CACHE_TTL): # The underscores in 10_000 are permitted in Python numeric literals. They improve readability. Python treats 10_000 exactly like 10000.
        self.max_items = max_items
        self.ttl = ttl
        self._data = OrderedDict() # key -> (expires_at, value); the END holds the most recently used
        self._lock = threading.Lock() # preventing simultaneous access -- FastAPI runs `def` endpoints on several threads at once

    def get(self, key:str) -> Optional[str]:
        with self._lock:
            # Access or modify the cache
            item = self._data.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= time.monotonic():
                del self._data[key]
                return None
            self._data.move_to_end(key)
            return value
    def set(self, key:str, value:str, ttl: Optional[float] = None) -> None:
        ttl = self.ttl if ttl is None else ttl
        with self._lock:
            self._data[key] = (time.monotonic() + ttl, value)
            self._data.move_to_end(key)
            while len(self._data) > self.max_itmes:
                self._data.popitem(last=False) # the FRONT is the least recently used: evict it
    def delete(self, key:str):
        with self._lock:
            self._data.pop(key, None)

cache = TTLCache()    