#!/bin/sh
# ------------------------------------------------------------------------------
# setup.sh - Bootstrap local tooling symlinks for exp-starter
#
# Author: BlackCat
# Website: https://b1ackcat.com
#
# Description:
#   - Builds pwninit in release mode when Rust/cargo is available.
#   - Links built pwninit binary to ~/.local/bin/pwninit.
#   - Links all files under ./scripts to ~/.local/bin/<filename>.
#   - If Rust is missing, prints a warning and continues.
# ------------------------------------------------------------------------------

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
SCRIPTS_DIR="${ROOT_DIR}/scripts"
PWNINIT_DIR="${ROOT_DIR}/pwninit"
PWNINIT_BIN="${PWNINIT_DIR}/target/release/pwninit"

log() {
    printf '[setup] %s\n' "$*"
}

warn() {
    printf '[setup] warning: %s\n' "$*" >&2
}

mkdir -p "${BIN_DIR}"
log "Using bin directory: ${BIN_DIR}"

if command -v cargo >/dev/null 2>&1; then
    log "Building pwninit with cargo build --release"
    if (cd "${PWNINIT_DIR}" && cargo build --release); then
        if [ -f "${PWNINIT_BIN}" ]; then
            ln -sf "${PWNINIT_BIN}" "${BIN_DIR}/pwninit"
            log "Linked pwninit -> ${BIN_DIR}/pwninit"
        else
            warn "pwninit build finished but binary not found: ${PWNINIT_BIN}"
        fi
    else
        warn "pwninit build failed; skipping pwninit link"
    fi
else
    warn "Rust toolchain not found (cargo missing); skipping pwninit build/link"
fi

if [ -d "${SCRIPTS_DIR}" ]; then
    linked_count=0
    for script_path in "${SCRIPTS_DIR}"/*; do
        [ -f "${script_path}" ] || continue
        script_name="$(basename "${script_path}")"
        ln -sf "${script_path}" "${BIN_DIR}/${script_name}"
        linked_count=$((linked_count + 1))
        log "Linked script: ${script_name}"
    done
    log "Linked ${linked_count} script(s) from ${SCRIPTS_DIR}"
else
    warn "scripts directory not found: ${SCRIPTS_DIR}"
fi

log "Setup complete"
