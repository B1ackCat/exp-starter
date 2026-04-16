#!/usr/bin/env python3
from pwn import ELF
from explib import Exploit as BaseExploit
from explib import configure_context
from explib import gdb

configure_context()


# -------------- menu helpers -----------------
def menu():
    pass


def alloc():
    pass


def free():
    pass


def edit():
    pass


def show():
    pass


class Exploit(BaseExploit):
    # ---------------- exploit ----------------
    def exploit(self):
        # gdb("b *main\\nc")
        pass


if __name__ == "__main__":
    {bindings}
    Exploit({bin_name}).run()
