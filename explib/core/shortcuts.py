from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Mapping
from typing import MutableMapping

from pwn import log, u64


class ShortcutNamespace:
    """Pwntools-style shortcuts exposed into exploit() global scope."""

    def __init__(self, io: Any, elf: Any, libc: Any):
        self.io = io
        self.elf = elf
        self.libc = libc

    @staticmethod
    def to_bytes(value: Any) -> bytes:
        return value if isinstance(value, bytes) else str(value).encode()

    @staticmethod
    def unpack_u64(data: bytes) -> int:
        return u64(data.ljust(8, b"\x00"))

    @staticmethod
    def log_value(key: str, value: Any) -> None:
        log.info(f"{key} @ {value}")

    @classmethod
    def _normalize_delims(cls, delims: Any) -> Any:
        if isinstance(delims, tuple):
            return tuple(cls.to_bytes(d) for d in delims)
        if isinstance(delims, list):
            return [cls.to_bytes(d) for d in delims]
        return cls.to_bytes(delims)

    def send(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.send(self.to_bytes(data), *args, **kwargs)

    def sendline(self, data: Any = b"", *args: Any, **kwargs: Any) -> Any:
        return self.io.sendline(self.to_bytes(data), *args, **kwargs)

    def sendafter(self, delim: Any, data: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.sendafter(
            self.to_bytes(delim), self.to_bytes(data), *args, **kwargs
        )

    def sendlineafter(self, delim: Any, data: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.sendlineafter(
            self.to_bytes(delim), self.to_bytes(data), *args, **kwargs
        )

    def recvuntil(self, delims: Any, *args: Any, **kwargs: Any) -> Any:
        return self.io.recvuntil(self._normalize_delims(delims), *args, **kwargs)

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
            "rvn": self.io.recvn,
            # convenience helpers
            "to_bytes": self.to_bytes,
            "uu64": self.unpack_u64,
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
