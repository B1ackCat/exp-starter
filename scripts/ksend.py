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
#   - Rebuilds the binary at the destination path (`base64 -d`) and sets
#     executable permission with `chmod +x`.
#   - Drops into interactive mode after upload so you can run exploit commands
#     manually.
#
# Usage:
#   ./ksend.py <host> <port> <file> [options]
#
# Arguments:
#   host              Target host/IP.
#   port              Target TCP port.
#   file              Local binary path to upload.
#
# Options:
#   --dest PATH       Remote destination path (default: /tmp/exploit)
#   --prompt STR      Remote shell prompt string (default: "$ ")
#   --chunk N         Base64 chunk size in bytes (default: 512)
#   --exec            Execute the binary after upload
# ------------------------------------------------------------------------------

from pwn import *
import argparse
import base64
import os

context.log_level = "info"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ksend.py",
        description="Upload a local exploit binary to a remote shell target",
    )
    parser.add_argument("host", help="Target host/IP")
    parser.add_argument("port", type=int, help="Target TCP port")
    parser.add_argument("file", help="Local binary path to upload")
    parser.add_argument("--dest", default="/tmp/exploit", help="Remote destination path (default: /tmp/exploit)")
    parser.add_argument("--prompt", default="$ ", help='Remote shell prompt (default: "$ ")')
    parser.add_argument("--chunk", type=int, default=512, help="Base64 chunk size in bytes (default: 512)")
    parser.add_argument("--exec", dest="execute", action="store_true", help="Execute the binary after upload")
    return parser.parse_args()


args = parse_args()

if not os.path.exists(args.file):
    log.error(f"File not found: {args.file}")

dest = args.dest
dest_dir = os.path.dirname(dest) or "/tmp"
dest_name = os.path.basename(dest)
prompt = args.prompt.encode()


def run(cmd):
    p.sendlineafter(prompt, cmd)
    p.recvline()


with open(args.file, "rb") as f:
    raw = f.read()

payload = base64.b64encode(raw).decode()
total = len(payload)

p = remote(args.host, args.port)

run(f"cd {dest_dir}")

b64_tmp = f"b64_{dest_name}"
log.info(f"Uploading {args.file} -> {dest} ({len(raw)} bytes)")
for i in range(0, total, args.chunk):
    log.info(f"Uploading... {i:x} / {total:x}")
    run(f'echo "{payload[i:i+args.chunk]}" >> {b64_tmp}')

run(f"base64 -d {b64_tmp} > {dest_name}")
run(f"rm {b64_tmp}")
run(f"chmod +x {dest_name}")
log.success(f"Upload complete: {dest}")

if args.execute:
    log.info(f"Executing {dest}")
    run(dest)

p.interactive()
