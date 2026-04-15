#!/usr/bin/env python3
from pwn import ELF
from explib import Exploit as BaseExploit
from explib import configure_context

configure_context()


class Exploit(BaseExploit):
    """
    Available in exploit() without self:
    sendlineafter/sendafter/sendline/send, recvline/recvuntil/recvn/recv, interactive
    shorthand: sla/sa/sl/s, rl/ru/rvn/r, plus uu64/lg and e/libc
    example: sendlineafter(b"> ", b"1")
    example: sla(b"> ", b"1")
    """

    # ---------------- exploit ----------------
    def exploit(self):
        pass


if __name__ == "__main__":
    {bindings}
    Exploit({bin_name}).run()
