#!/usr/bin/env bash
# ==============================================================================
# Antigravity Systems Engineering - Chapter 3 Sandbox Template
# Artifact: bubblewrap_strict.sh
# Purpose: Launches an untrusted autonomous agent command inside an unescapable,
#          rootless Bubblewrap sandbox.
# ==============================================================================

set -euo pipefail

if ! command -v bwrap >/dev/null 2>&1; then
    echo "[!] Error: 'bwrap' (Bubblewrap) is not installed on this host." >&2
    echo "    Install via: apt-get install -y bubblewrap" >&2
    exit 1
fi

WORKSPACE_DIR="${1:-$(pwd)}"
shift || true
CMD_TO_RUN="${*:-/bin/bash}"

# Ephemeral scratch directory for this invocation
SCRATCH_DIR=$(mktemp -d /tmp/antigravity-scratch-XXXXXX)
trap 'rm -rf "$SCRATCH_DIR"' EXIT

echo "[*] Spawning Bubblewrap sandbox..." >&2
echo "    Workspace: $WORKSPACE_DIR" >&2
echo "    Scratch:   $SCRATCH_DIR" >&2

# Bubblewrap arguments for strict zero-ambient isolation:
# 1. --unshare-all: Unshares user, ipc, pid, net, uts, and cgroup namespaces.
# 2. --die-with-parent: Kills sandbox instantly if host supervisor dies.
# 3. Read-only system binds (/usr, /lib, /lib64, /bin, /etc/ssl).
# 4. Ephemeral isolated tmpfs on /tmp.
# 5. Read-write bind of workspace only.
# 6. Cleans environment variables (PATH, LANG, TERM).

exec bwrap \
    --unshare-all \
    --die-with-parent \
    --ro-bind /usr /usr \
    --ro-bind /lib /lib \
    --ro-bind-try /lib64 /lib64 \
    --ro-bind /bin /bin \
    --ro-bind-try /etc/ssl /etc/ssl \
    --ro-bind-try /etc/resolv.conf /etc/resolv.conf \
    --proc /proc \
    --dev /dev \
    --tmpfs /tmp \
    --bind "$WORKSPACE_DIR" "$WORKSPACE_DIR" \
    --chdir "$WORKSPACE_DIR" \
    --clearenv \
    --setenv PATH "/usr/local/bin:/usr/bin:/bin" \
    --setenv LANG "C.UTF-8" \
    --setenv LC_ALL "C.UTF-8" \
    --setenv TERM "xterm-256color" \
    --setenv ANTIGRAVITY_SANDBOX "1" \
    $CMD_TO_RUN
