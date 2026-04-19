from contextlib import contextmanager
from typing import Any, Dict, Iterator, Mapping, MutableMapping

from pwn import log, u64


def to_bytes(value: Any) -> bytes:
    return value if isinstance(value, bytes) else str(value).encode()


def unpack_u64(data: bytes) -> int:
    return u64(data.ljust(8, b"\x00"))


class ShortcutNamespace:
    """Pwntools-style shortcuts exposed into exploit() global scope."""

    def __init__(self, io: Any, elf: Any, libc: Any):
        self.io = io
        self.elf = elf
        self.libc = libc

    @staticmethod
    def log_value(key: str, value: Any) -> None:
        log.info(f"{key} @ {value}")

    def send(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.send(to_bytes(data), *args, **kwargs)

    def sendline(self, data: Any = b"", *args: Any, **kwargs: Any) -> Any:
        return self.io.sendline(to_bytes(data), *args, **kwargs)

    def sendafter(self, delim: Any, data: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.sendafter(to_bytes(delim), to_bytes(data), *args, **kwargs)

    def sendlineafter(self, delim: Any, data: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.sendlineafter(to_bytes(delim), to_bytes(data), *args, **kwargs)

    def recvuntil(self, delims: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(delims, (list, tuple)):
            delims = type(delims)(to_bytes(d) for d in delims)
        else:
            delims = to_bytes(delims)
        return self.io.recvuntil(delims, *args, **kwargs)

    def mapping(self) -> Dict[str, Any]:
        return {
            # pwntools-style names
            "send": self.send,
            "sendline": self.sendline,
            "sendafter": self.sendafter,
            "sendlineafter": self.sendlineafter,
            "recv": self.io.recv,
            "recvline": self.io.recvline,
            "recvuntil": self.recvuntil,
            "recvn": self.io.recvn,
            "interactive": self.io.interactive,
            # shorthand aliases
            "s": self.send,
            "sl": self.sendline,
            "sa": self.sendafter,
            "sla": self.sendlineafter,
            "r": self.io.recv,
            "rl": self.io.recvline,
            "ru": self.recvuntil,
            "rn": self.io.recvn,
            # convenience helpers
            "to_bytes": to_bytes,
            "uu64": unpack_u64,
            "lg": self.log_value,
            "e": self.elf,
            "io": self.io,
            "libc": self.libc,
        }


@contextmanager
def bind_names(
    scope: MutableMapping[str, Any], values: Mapping[str, Any]
) -> Iterator[None]:
    missing = object()
    old = {}

    for name, value in values.items():
        old[name] = scope.get(name, missing)
        scope[name] = value

    try:
        yield
    finally:
        for name, value in old.items():
            if value is missing:
                scope.pop(name, None)
            else:
                scope[name] = value
