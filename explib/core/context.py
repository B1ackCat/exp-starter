from typing import Iterable
from typing import Optional
from typing import Union

from pwn import context


DEFAULT_TERMINAL = ("tmux", "split-window", "-h", "-p", "65", "-b")


def configure_context(
    arch: str = "amd64",
    os: str = "linux",
    endian: str = "little",
    terminal: Optional[Union[str, Iterable[str]]] = DEFAULT_TERMINAL,
) -> None:
    context(arch=arch, os=os, endian=endian)
    if terminal is None:
        return
    if isinstance(terminal, str):
        context.terminal = terminal.split()
    else:
        context.terminal = list(terminal)
