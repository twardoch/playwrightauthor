# this_file: src/playwrightauthor/session_runtime.py
"""Share Playwright's sync driver within one thread while contexts stay isolated."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from threading import local
from typing import Any

_runtime = local()


@contextmanager
def sync_driver(factory: Callable[[], Any]) -> Iterator[Any]:
    """Playwright forbids nested sync drivers; stop only after the last session."""
    if getattr(_runtime, "users", 0) == 0:
        _runtime.driver = factory().start()
        _runtime.users = 0
    _runtime.users += 1
    try:
        yield _runtime.driver
    finally:
        _runtime.users -= 1
        if _runtime.users == 0:
            driver, _runtime.driver = _runtime.driver, None
            driver.stop()
