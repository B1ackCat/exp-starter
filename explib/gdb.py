from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from pwn import gdb as pwngdb

_CURRENT_IO: ContextVar[Any] = ContextVar("explib_current_io", default=None)


@contextmanager
def bind_io(io):
    token = _CURRENT_IO.set(io)
    try:
        yield
    finally:
        _CURRENT_IO.reset(token)


def gdb(script="", *, io=None, **kwargs):
    """Attach GDB.

    If `io` is omitted, uses the active exploit context.
    """
    target = io if io is not None else _CURRENT_IO.get()
    if target is None:
        raise RuntimeError("gdb(): no active io; pass io=... explicitly")

    kwargs.setdefault("gdbscript", script)
    return pwngdb.attach(target, **kwargs)
