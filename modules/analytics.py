from __future__ import annotations
import time
from contextlib import contextmanager


@contextmanager
def timer():
    start = time.perf_counter()
    result = {"elapsed_sec": None}
    yield result
    result["elapsed_sec"] = round(time.perf_counter() - start, 4)
