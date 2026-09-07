# Failure Lab 03: Sandbox Internals & Process Virtualization

## Vulnerability Focus
- **Failure Mode**: Classical shell fork-bomb (`:(){ :|:& };:`) spawned by a compromised or hallucinating agent exhausting the host's PID table, freezing the entire server.
- **Systems Root Cause**: Unconstrained PID allocation in the default host process namespace.

## Files
- `forkbomb_exploit.sh`: Shell script attempting recursive subshell spawning.
- `cgroup_enforcer.sh`: Enforces cgroups v2 `pids.max=64` and `memory.max=512M` to contain the explosion locally.
