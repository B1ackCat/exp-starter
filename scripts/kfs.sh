#!/bin/sh
# ------------------------------------------------------------------------------
# kfs.sh - initramfs/rootfs unpack, inject, repack helper
#
# Author: BlackCat
# Website: https://b1ackcat.com
#
# Description:
#   - Unpacks rootfs/initramfs cpio(.gz) into a working directory.
#   - Injects a local exploit binary into the ramfs and sets +x.
#   - Rebuilds the archive back to cpio.gz (or cpio) after changes.
# ------------------------------------------------------------------------------

set -eu

SCRIPT_NAME="$(basename "$0")"
WORKDIR=".ramfs-work"
ROOTFS_DIR=""
ARCHIVE_PATH=""
DEST_PATH="/tmp/exploit"
EXPLOIT_PATH=""
FORCE="0"
NO_REPACK="0"

log() {
    printf '[kfs] %s\n' "$*"
}

warn() {
    printf '[kfs] warning: %s\n' "$*" >&2
}

die() {
    printf '[kfs] error: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<EOF
Usage:
  ./${SCRIPT_NAME} unpack [--archive FILE] [--workdir DIR] [--force]
  ./${SCRIPT_NAME} inject --exploit FILE [--dest /tmp/exploit] [--archive FILE] [--workdir DIR] [--no-repack]
  ./${SCRIPT_NAME} repack [--archive FILE] [--workdir DIR]
  ./${SCRIPT_NAME} help

Defaults:
  archive auto-detect order:
    ./rootfs.cpio.gz -> ./initramfs.cpio.gz
  workdir: ./.ramfs-work
  extracted root: <workdir>/rootfs
  inject dest: /tmp/exploit

Examples:
  ./${SCRIPT_NAME} unpack --archive ./rootfs.cpio.gz
  ./${SCRIPT_NAME} inject --exploit ./exp --dest /tmp/exploit
  ./${SCRIPT_NAME} repack
EOF
}

need_arg() {
    [ $# -ge 2 ] || die "missing value for option: $1"
}

require_tools() {
    command -v cpio >/dev/null 2>&1 || die "cpio not found"
    command -v find >/dev/null 2>&1 || die "find not found"
}

is_gz() {
    case "$1" in
        *.gz) return 0 ;;
        *) return 1 ;;
    esac
}

default_archive() {
    for f in rootfs.cpio.gz initramfs.cpio.gz; do
        if [ -f "$f" ]; then
            printf '%s\n' "$f"
            return 0
        fi
    done
    return 1
}

resolve_archive_for_unpack_or_inject() {
    if [ -n "$ARCHIVE_PATH" ]; then
        printf '%s\n' "$ARCHIVE_PATH"
        return 0
    fi
    default_archive || die "archive not found (use --archive)"
}

resolve_archive_for_repack() {
    if [ -n "$ARCHIVE_PATH" ]; then
        printf '%s\n' "$ARCHIVE_PATH"
        return 0
    fi
    if [ -f "${WORKDIR}/.archive_path" ]; then
        cat "${WORKDIR}/.archive_path"
        return 0
    fi
    default_archive || die "archive not found (use --archive)"
}

load_paths() {
    ROOTFS_DIR="${WORKDIR}/rootfs"
}

safe_rel_dest() {
    # Convert "/tmp/exploit" -> "tmp/exploit"
    # Keep relative paths as-is.
    case "$DEST_PATH" in
        /*) printf '%s\n' "${DEST_PATH#/}" ;;
        *) printf '%s\n' "$DEST_PATH" ;;
    esac
}

unpack_archive() {
    archive="$1"
    load_paths

    if [ -d "$ROOTFS_DIR" ] && [ "$(ls -A "$ROOTFS_DIR" 2>/dev/null || true)" ] && [ "$FORCE" != "1" ]; then
        die "${ROOTFS_DIR} already exists and is not empty (use --force)"
    fi

    rm -rf "$ROOTFS_DIR"
    mkdir -p "$ROOTFS_DIR"

    log "Unpacking ${archive} -> ${ROOTFS_DIR}"

    if is_gz "$archive"; then
        command -v gzip >/dev/null 2>&1 || die "gzip not found for .gz archive"
        gzip -dc "$archive" | (cd "$ROOTFS_DIR" && cpio -idmu --no-absolute-filenames >/dev/null 2>&1)
    else
        cat "$archive" | (cd "$ROOTFS_DIR" && cpio -idmu --no-absolute-filenames >/dev/null 2>&1)
    fi

    printf '%s\n' "$archive" > "${WORKDIR}/.archive_path"
    log "Done. Edit files under: ${ROOTFS_DIR}"
}

repack_archive() {
    archive="$1"
    load_paths

    [ -d "$ROOTFS_DIR" ] || die "extracted rootfs not found: ${ROOTFS_DIR} (run unpack first)"

    tmp_out="${archive}.tmp.$$"
    log "Repacking ${ROOTFS_DIR} -> ${archive}"

    if is_gz "$archive"; then
        command -v gzip >/dev/null 2>&1 || die "gzip not found for .gz archive"
        (cd "$ROOTFS_DIR" && find . -print | cpio -o -H newc 2>/dev/null) | gzip -c > "$tmp_out"
    else
        (cd "$ROOTFS_DIR" && find . -print | cpio -o -H newc 2>/dev/null) > "$tmp_out"
    fi

    mv "$tmp_out" "$archive"
    log "Repack complete: ${archive}"
}

inject_exploit() {
    archive="$1"
    load_paths

    [ -f "$EXPLOIT_PATH" ] || die "exploit not found: ${EXPLOIT_PATH}"

    # Always refresh from archive for deterministic inject.
    FORCE="1"
    unpack_archive "$archive"

    rel_dest="$(safe_rel_dest)"
    dest_full="${ROOTFS_DIR}/${rel_dest}"
    dest_dir="$(dirname "$dest_full")"
    mkdir -p "$dest_dir"
    cp "$EXPLOIT_PATH" "$dest_full"
    chmod +x "$dest_full"
    log "Injected: ${EXPLOIT_PATH} -> /${rel_dest}"

    if [ "$NO_REPACK" = "1" ]; then
        log "Skip repack (--no-repack). You can edit and run: ./${SCRIPT_NAME} repack"
        return 0
    fi

    repack_archive "$archive"
}

[ $# -ge 1 ] || {
    usage
    exit 1
}

case "$1" in
    -h|--help|help)
        usage
        exit 0
        ;;
esac

COMMAND="$1"
shift

while [ $# -gt 0 ]; do
    case "$1" in
        --archive)
            need_arg "$@"
            ARCHIVE_PATH="$2"
            shift 2
            ;;
        --workdir)
            need_arg "$@"
            WORKDIR="$2"
            shift 2
            ;;
        --exploit)
            need_arg "$@"
            EXPLOIT_PATH="$2"
            shift 2
            ;;
        --dest)
            need_arg "$@"
            DEST_PATH="$2"
            shift 2
            ;;
        --force)
            FORCE="1"
            shift
            ;;
        --no-repack)
            NO_REPACK="1"
            shift
            ;;
        -h|--help|help)
            usage
            exit 0
            ;;
        *)
            die "unknown option: $1"
            ;;
    esac
done

require_tools
mkdir -p "$WORKDIR"

case "$COMMAND" in
    unpack)
        archive="$(resolve_archive_for_unpack_or_inject)"
        [ -f "$archive" ] || die "archive not found: $archive"
        unpack_archive "$archive"
        ;;
    repack)
        archive="$(resolve_archive_for_repack)"
        repack_archive "$archive"
        ;;
    inject)
        [ -n "$EXPLOIT_PATH" ] || die "inject requires --exploit FILE"
        archive="$(resolve_archive_for_unpack_or_inject)"
        [ -f "$archive" ] || die "archive not found: $archive"
        inject_exploit "$archive"
        ;;
    help)
        usage
        ;;
    *)
        die "unknown command: ${COMMAND} (use help)"
        ;;
esac
