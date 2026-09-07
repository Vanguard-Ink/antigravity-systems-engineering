# Antigravity Sandboxes: Runtime Isolation Templates

This directory provides production-hardened templates for Linux kernel sandbox isolation and headless daemon service management.

---

## Files

- **`bubblewrap_strict.sh`**: Rootless unshare launcher using Bubblewrap (`bwrap`). Enforces read-only root filesystems, ephemeral tmpfs scratch spaces, network namespace isolation, and dropped Linux capabilities.
- **`antigravity-agent@.service`**: Production Systemd service unit template with cgroups v2 resource ceilings (`MemoryMax=2G`, `TasksMax=64`), watchdog health checks (`WatchdogSec=30s`), and strict filesystem protection.
- **`antigravity_policy.json`**: Declarative isolation policy defining allowed mounts, network egress restrictions, and resource limits.
