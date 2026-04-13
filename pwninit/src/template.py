#!/usr/bin/env python3
import sys
from pwn import *

context(arch="amd64", os="linux", endian="little")
context.terminal = "tmux split-window -h -p 65 -b".split()

# ---------------- helpers ----------------
lg = lambda k, v: log.info(f"{{k}} @ {{v}}")
_b = lambda x: x if isinstance(x, bytes) else str(x).encode()

s = lambda x: p.send(_b(x))
sl = lambda x: p.sendline(_b(x))
sa = lambda d, x: p.sendafter(_b(d), _b(x))
sla = lambda d, x: p.sendlineafter(_b(d), _b(x))
r = lambda: p.recv()
rl = lambda: p.recvline()
ru = lambda d: p.recvuntil(_b(d))
rvn = lambda n: p.recvn(n)

uu64 = lambda d: u64(d.ljust(8, b"\x00"))


def start(e):
    # ./ex.py <host> <port>
    if len(sys.argv) >= 3:
        host, port = sys.argv[1], sys.argv[2]
        log.info(f"Running remote @ {{host}}:{{port}}...")
        return remote(host, int(port))

    if args.REMOTE:
        host = args.HOST or "127.0.0.1"
        port = int(args.PORT or 1337)
        log.info(f"Running remote @ {{host}}:{{port}}...")
        return remote(host, port)

    if args.GDB:
        log.info("Running local with GDB...")
        return gdb.debug({proc_args}, gdbscript=gs)

    log.info(f"Running local...")
    return process({proc_args})


# -------------- Heap exploit --------------
def menu(n):
    pass


def alloc():
    pass


def free():
    pass


def edit():
    pass


def show():
    pass


# ---------------- exploit ----------------
def exploit():
    pass


if __name__ == "__main__":
    {bindings}
    libc = e.libc
    p = start(e)

    exploit()
