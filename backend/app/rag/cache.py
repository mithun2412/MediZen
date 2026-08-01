"""Small thread-safe in-memory LRU caches used by RAG retrieval."""
from __future__ import annotations

from collections import OrderedDict
from threading import RLock
from typing import Generic, TypeVar

T = TypeVar("T")


class LRUCache(Generic[T]):
    def __init__(self, max_size: int = 256) -> None:
        self._values: OrderedDict[str, T] = OrderedDict()
        self._max_size = max_size
        self._lock = RLock()

    def get(self, key: str) -> T | None:
        with self._lock:
            value = self._values.get(key)
            if value is not None:
                self._values.move_to_end(key)
            return value

    def set(self, key: str, value: T) -> None:
        with self._lock:
            self._values[key] = value
            self._values.move_to_end(key)
            while len(self._values) > self._max_size:
                self._values.popitem(last=False)
