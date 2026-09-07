#!/usr/bin/env bash
# ==============================================================================
# Antigravity Systems Engineering - Chapter 1 Companion
# Artifact: hardened_subshell_wrapper.sh
# Purpose: Deterministic POSIX wrapper providing basic environment stripping,
#          file descriptor hygiene, and execution containment for agent commands.
# ==============================================================================

set -euo pipefail

# 1. Close all non-standard inherited file descriptors (FD 3 through 1024)
# Prevents child processes from reading parent sockets, pipes, or DB handles.
close_inherited_fds() {
    local fd
    for fd in $(seq 3 1024); do
        eval "exec $fd>&-" 2>/dev/null || true
    done
}

# 2. Enforce clean minimal environment (Deny-by-default environment scrub)
# Strips AWS keys, GITHUB_TOKEN, and arbitrary secret variables.
CLEAN_PATH="/usr/local/bin:/usr/bin:/bin"
SAFE_VARS=(
    "TERM=${TERM:-xterm-256color}"
    "LANG=C.UTF-8"
    "LC_ALL=C.UTF-8"
    "PATH=${CLEAN_PATH}"
    "TMPDIR=/tmp/agent_sandboxed_$$"
)

# 3. Create ephemeral sandboxed temporary directory
mkdir -p "/tmp/agent_sandboxed_$$"
trap 'rm -rf "/tmp/agent_sandboxed_$$"' EXIT

# Execute file descriptor closure
close_inherited_fds

# 4. Command Execution via env -i (Zero Ambient Authority)
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <command string to execute>" >&2
    exit 1
fi

COMMAND_PAYLOAD="$1"

echo "[HARDENED WRAPPER] Stripping ambient authority and launching sanitized subshell..." >&2

# Use env -i to completely purge parent environment block
exec /usr/bin/env -i \
    "${SAFE_VARS[@]}" \
    /bin/bash --noprofile --norc -c "$COMMAND_PAYLOAD"
