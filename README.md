# exp-starter

Practical starter toolkit for binary exploitation (`pwn`) and kernel exploitation (`kernel pwn`) workflows.

## What this repo includes

- `setup.sh`: bootstraps local command symlinks into `~/.local/bin`
- `scripts/krun.sh`: flexible QEMU launcher for kernel challenges
- `scripts/kfs.sh`: unpack/inject/repack helper for `rootfs.cpio(.gz)`
- `scripts/ksend.py`: upload a local exploit binary to a remote shell over TCP
- `scripts/extract-vmlinux`: extract uncompressed `vmlinux` from a kernel image
- `kexp/`: minimal C kernel exploit template + Makefile
- `pwninit/`: vendored `pwninit` source (built by `setup.sh` if Cargo is available)

## Requirements

Minimum tools (depending on what you use):

- `bash`/`sh`, `gcc`, `make`
- `python3` and `pwntools` (for `ksend.py`)
- `qemu-system-x86_64` (for `krun.sh`)
- `cpio`, `gzip`, `find` (for `kfs.sh`)
- `file`, `readelf`, and decompression tools like `gunzip`/`unxz`/`unzstd` (for `extract-vmlinux`)
- `cargo` (optional, to build local `pwninit`)
- `pipx` (optional, for `vmlinux-to-elf` install in setup)

## Quick start

```bash
./setup.sh
```

What `setup.sh` does:

1. Builds `pwninit` in release mode if `cargo` exists.
2. Links built `pwninit` to `~/.local/bin/pwninit`.
3. Links all files in `./scripts` to `~/.local/bin/<script-name>`.
4. Tries to install `vmlinux-to-elf` via `pipx`.

If `~/.local/bin` is not in your `PATH`, add it in your shell config.

To use `explib` in generated `ex.py` templates:

```bash
pip install -e .
```

## Typical workflows

### 1) Userland pwn setup with pwninit

```bash
# in a challenge directory
pwninit
```

This usually patches the binary, fetches compatible loader artifacts, and generates a `ex.py` skeleton.

### 2) Kernel pwn quick loop

1. Launch VM:

```bash
krun.sh --kernel ./bzImage --initrd ./rootfs.cpio.gz --nokaslr
```

2. Build exploit template:

```bash
cd kexp
make release     # builds ./ex
# or: make debug / make static
```

3. Inject exploit into initramfs:

```bash
kfs.sh inject --archive ./rootfs.cpio.gz --exploit ./kexp/ex --dest /tmp/exploit
```

4. Reboot VM and run `/tmp/exploit` inside guest.

## Script usage cheatsheet

### `krun.sh`

```bash
krun.sh [options]
```

Common options:

- `--kernel PATH`
- `--initrd PATH` (`--rootfs` alias)
- `--mem 256M`
- `--nokaslr --nopti --nosmep --nosmap`
- `--append "extra kernel cmdline"`
- `--no-gdb` (disable QEMU gdb stub)

### `kfs.sh`

```bash
kfs.sh unpack [--archive FILE] [--workdir DIR] [--force]
kfs.sh inject --exploit FILE [--dest /tmp/exploit] [--archive FILE] [--workdir DIR] [--no-repack]
kfs.sh repack [--archive FILE] [--workdir DIR]
```

Defaults:

- archive auto-detect: `./rootfs.cpio.gz` then `./initramfs.cpio.gz`
- workdir: `./.ramfs-work`
- extracted root: `<workdir>/rootfs`

### `ksend.py`

```bash
ksend.py <host> <port> <file>
```

It uploads `<file>` to remote `/tmp/exploit` using base64 chunks, then sets executable bit.

Note: current implementation expects remote shell prompt to be `$ `.

### `extract-vmlinux`

```bash
extract-vmlinux <kernel-image> > vmlinux
```

## `kexp/` template targets

Inside `kexp/`:

```bash
make help
make release   # ex
make debug     # ex_dbg (with utils/hexdump)
make static    # static ex
make clean
```

Default device path in template is:

```c
#define DEVICE_PATH "/dev/vuln"
```

Adjust it for your target challenge.

## Notes

- This repository is intentionally minimal and meant to be adapted per challenge.
- You can use scripts directly (`./scripts/...`) or via symlinks after running `./setup.sh`.
