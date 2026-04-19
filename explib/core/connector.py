import sys
from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple

from pwn import log, process, remote


@dataclass(frozen=True)
class Connector:
    """Connection metadata and connection factory for exploit runs."""

    elf: Any
    libc: Optional[Any] = None
    ld: Optional[Any] = None
    remote_host: Optional[str] = None
    remote_port: Optional[int] = None
    local_argv: Tuple[str, ...] = ()

    def __post_init__(self):
        has_host = self.remote_host is not None
        has_port = self.remote_port is not None
        if has_host != has_port:
            raise ValueError("remote_host and remote_port must be set together")

    def connect(self):
        if self.remote_host is not None and self.remote_port is not None:
            log.info(f"Running remote @ {self.remote_host}:{self.remote_port}...")
            return remote(self.remote_host, self.remote_port)

        log.info("Running local...")
        argv = [self.elf.path, *self.local_argv]
        return process(argv)

    @classmethod
    def from_cli(
        cls,
        elf: Any,
        libc: Optional[Any] = None,
        ld: Optional[Any] = None,
        argv: Optional[Sequence[str]] = None,
    ) -> "Connector":
        args = list(sys.argv if argv is None else argv) or ["ex.py"]
        user_args = args[1:]
        inferred_libc = libc if libc is not None else getattr(elf, "libc", None)

        remote_args = cls._parse_remote_args(user_args)
        if remote_args is None:
            return cls(
                elf=elf,
                libc=inferred_libc,
                ld=ld,
                local_argv=tuple(user_args),
            )

        host, port = remote_args
        return cls(
            elf=elf,
            libc=inferred_libc,
            ld=ld,
            remote_host=host,
            remote_port=port,
        )

    @staticmethod
    def _parse_remote_args(
        args: Sequence[str],
    ) -> Optional[Tuple[str, int]]:
        # style: host:port [extra...]
        if args and ":" in args[0]:
            host, port_str = args[0].rsplit(":", 1)
            if not host or not port_str:
                return None
            try:
                port = int(port_str)
            except ValueError as exc:
                raise ValueError(f"invalid remote endpoint: {args[0]}") from exc
            return host, port

        # style: host port [extra...]
        if len(args) >= 2:
            try:
                port = int(args[1])
            except ValueError:
                return None
            return args[0], port

        return None
