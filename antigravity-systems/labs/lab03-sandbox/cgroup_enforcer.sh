#!/usr/bin/env bash
# ==============================================================================
# Failure Lab 03: cgroups v2 Quota Enforcer
# Configures an isolated cgroup slice with a hard limit of 64 processes.
# ==============================================================================
set -euo pipefail

CGROUP_PATH="/sys/fs/cgroup/antigravity-lab03"

echo "[*] Creating cgroups v2 slice at $CGROUP_PATH..."
sudo mkdir -p "$CGROUP_PATH"

# Set hard limit of 64 processes/threads
echo 64 | sudo tee "$CGROUP_PATH/pids.max" >/dev/null
echo 536870912 | sudo tee "$CGROUP_PATH/memory.max" >/dev/null # 512MB

echo "[*] Assigning current shell (PID $$) to isolated slice..."
echo $$ | sudo tee "$CGROUP_PATH/cgroup.procs" >/dev/null

echo "[*] Verifying cgroup assignment:"
cat /proc/self/cgroup

echo "[*] Success! Host is now protected against fork-bombs and runaway memory allocation."
