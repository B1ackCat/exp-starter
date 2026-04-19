#!/bin/sh
# ------------------------------------------------------------------------------
# krun.sh - Flexible QEMU launcher for kernel pwn practice
#
# Author: BlackCat
# Website: https://b1ackcat.com
#
# Description:
#   - Runs a kernel/initramfs under qemu-system-x86_64 with sensible defaults.
#   - Avoids editing run.sh every time by exposing common kernel-pwn toggles.
#   - Supports mitigation toggles such as KASLR/PTI/SMEP/SMAP via CLI options.
#
# Usage:
#   ./krun.sh [options]
#
# Options:
#   --kernel PATH       Kernel image path (default: ./bzImage)
#   --initrd PATH       Initramfs path (default: ./rootfs.cpio.gz)
#   --rootfs PATH       Alias of --initrd
#   --mem SIZE          VM memory size (default: 256M)
#   --nokaslr           Disable KASLR
#   --nopti             Disable PTI
#   --nosmep            Disable SMEP
#   --nosmap            Disable SMAP
#   --append "ARGS"     Extra kernel cmdline args to append
#   --no-gdb            Disable qemu gdb stub (-s)
#   -h, --help          Show help
# ------------------------------------------------------------------------------

set -eu

KERNEL="./bzImage"
INITRD="./rootfs.cpio.gz"
MEM="256M"
KASLR="on"
PTI="on"
SMEP="on"
SMAP="on"
SMP="1"
KVM="0"
GDB_WAIT="0"
EXTRA_APPEND=""
ENABLE_GDB="1"
QEMU_BIN="qemu-system-x86_64"

usage() {
    cat <<'EOF'
krun.sh - Flexible QEMU launcher for kernel pwn practice

Usage:
  ./krun.sh [options]

Options:
  --kernel PATH       Kernel image path (default: ./bzImage)
  --initrd PATH       Initramfs path (default: ./rootfs.cpio.gz)
  --rootfs PATH       Alias of --initrd
  --mem SIZE          VM memory size (default: 256M)
  --smp N             Number of CPUs (default: 1)
  --kvm               Enable KVM acceleration
  --nokaslr           Disable KASLR
  --nopti             Disable PTI
  --nosmep            Disable SMEP
  --nosmap            Disable SMAP
  --append "ARGS"     Extra kernel cmdline args to append
  --no-gdb            Disable qemu gdb stub (-s)
  --gdb-wait          Freeze CPU at startup until GDB connects (-S)
  -h, --help          Show help
EOF
}

die() {
    echo "[krun] $*" >&2
    exit 1
}

need_arg() {
    [ $# -ge 2 ] || die "Missing value for option: $1"
}

while [ $# -gt 0 ]; do
    case "$1" in
    --kernel)
        need_arg "$@"
        KERNEL="$2"
        shift 2
        ;;
    --initrd | --rootfs)
        need_arg "$@"
        INITRD="$2"
        shift 2
        ;;
    --mem)
        need_arg "$@"
        MEM="$2"
        shift 2
        ;;
    --smp)
        need_arg "$@"
        SMP="$2"
        shift 2
        ;;
    --kvm)
        KVM="1"
        shift
        ;;
    --nokaslr)
        KASLR="off"
        shift
        ;;
    --nopti)
        PTI="off"
        shift
        ;;
    --nosmep)
        SMEP="off"
        shift
        ;;
    --nosmap)
        SMAP="off"
        shift
        ;;
    --append)
        need_arg "$@"
        EXTRA_APPEND="$2"
        shift 2
        ;;
    --no-gdb)
        ENABLE_GDB="0"
        shift
        ;;
    --gdb-wait)
        GDB_WAIT="1"
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        die "Unknown option: $1 (use --help)"
        ;;
    esac
done

APPEND="console=ttyS0 oops=panic loglevel=3 panic=-1 pti=$PTI"
if [ "$KASLR" = "on" ]; then
    APPEND="$APPEND kaslr"
else
    APPEND="$APPEND nokaslr"
fi
if [ -n "$EXTRA_APPEND" ]; then
    APPEND="$APPEND $EXTRA_APPEND"
fi

CPU="kvm64,smep=$SMEP,smap=$SMAP"
KVM_ARG=""
if [ "$KVM" = "1" ]; then
    KVM_ARG="-enable-kvm"
fi
GDB_ARGS=""
if [ "$ENABLE_GDB" = "1" ]; then
    GDB_ARGS="-s"
fi
if [ "$GDB_WAIT" = "1" ]; then
    GDB_ARGS="$GDB_ARGS -S"
fi

command -v "$QEMU_BIN" >/dev/null 2>&1 || die "qemu-system-x86_64 not found"
[ -f "$KERNEL" ] || die "Kernel not found: $KERNEL"
[ -f "$INITRD" ] || die "Initrd not found: $INITRD"

"$QEMU_BIN" \
    -m "$MEM" \
    -smp "$SMP" \
    -nographic \
    -kernel "$KERNEL" \
    -initrd "$INITRD" \
    -append "$APPEND" \
    -no-reboot \
    -cpu "$CPU" \
    -monitor none \
    -netdev user,id=net0 \
    -device virtio-net-pci,netdev=net0 \
    $KVM_ARG \
    $GDB_ARGS
