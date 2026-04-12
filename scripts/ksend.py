#!/usr/bin/python3
# ------------------------------------------------------------------------------
# ksend.py - Upload a local exploit binary to a remote shell target
#
# Author: BlackCat
# Website: https://b1ackcat.com
#
# Description:
#   - Designed for CTF/pwn workflows where direct file transfer is unavailable.
#   - Connects to <host>:<port> using pwntools and uploads a local binary by
#     base64-encoding it and appending chunked data on the remote shell.
#   - Rebuilds the binary at /tmp/exploit (`base64 -d`) and sets executable
#     permission with `chmod +x`.
#   - Drops into interactive mode after upload so you can run exploit commands
#     manually.
#
# Usage:
#   ./ksend.py <host> <port> <file>
#
# Arguments:
#   host              Target host/IP.
#   port              Target TCP port.
#   file              Local binary path to upload.
#
# Notes:
#   - Assumes remote shell prompt is `$ ` (used by `sendlineafter`).
#   - Upload chunk size is 512 bytes (base64 text).
#   - Script prepares `/tmp/exploit` but does not execute it automatically.
# ------------------------------------------------------------------------------

from pwn import *
import base64
import sys
import os

context.log_level = "info"


def usage():
    """
    Print CLI usage and exit.

    Args:
        host: Target host or IP address.
        port: Target TCP port (integer).
        file: Local exploit binary path to upload.

    Example:
        ./ksend.py 127.0.0.1 1337 ./exploit
    """
    print("Usage: ksend.py <host> <port> <file>")
    sys.exit(1)


if len(sys.argv) != 4:
    usage()

host = sys.argv[1]
port = int(sys.argv[2])
file_path = sys.argv[3]

if not os.path.exists(file_path):
    log.error(f"File not found: {file_path}")
    sys.exit(1)


def run(cmd):
    p.sendlineafter("$ ", cmd)
    p.recvline()


with open(file_path, "rb") as f:
    raw = f.read()

payload = base64.b64encode(raw).decode()

p = remote(host, port)

run("cd /tmp")

log.info("Uploading...")
for i in range(0, len(payload), 512):
    log.info(f"Uploading... {i:x} / {len(payload):x}")
    run(f'echo "{payload[i:i+512]}" >> b64exp')

run("base64 -d b64exp > exploit")
run("rm b64exp")
run("chmod +x exploit")

p.interactive()
