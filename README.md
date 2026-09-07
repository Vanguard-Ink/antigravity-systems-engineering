# ANTIGRAVITY SYSTEMS ENGINEERING
## Companion Codebase: Runtime Isolation, Adversarial Containment, and Headless Agent Daemons

> **Core Systems Invariant**:  
> *"Agent autonomy is not a prompt-safety problem. It is an operating-system problem."*

This repository is the official open-source companion codebase for the technical monograph **"ANTIGRAVITY SYSTEMS ENGINEERING"**. It contains production-grade isolation templates, deterministic interception shims, supervisor harnesses, and all 13 experimental Failure Labs.

---

### Repository Layout

```text
antigravity-systems/
├── harnesses/        # Daemon lifecycle engines, supervisors, and IPC brokers
├── sandboxes/        # Antigravity & Linux kernel isolation templates (bwrap, systemd, policy)
├── shims/            # Deterministic interception proxies (curl, git, npm, env-clean wrappers)
├── labs/             # 13 failure reproduction labs (Labs 01 – 13)
└── case-studies/     # Production Capstone: Autonomous SRE Daemon full codebase
```

---

### Key Components

1. **`harnesses/`**:
   - `supervisor.py`: Process supervisor enforcing timeouts, process group (`setpgrp`) teardown, and signal forwarding.
   - `ipc_broker.py`: High-throughput UNIX Domain Socket server with length-prefixed JSON-RPC 2.0 and `SO_PEERCRED` authentication.

2. **`sandboxes/`**:
   - `bubblewrap_strict.sh`: Complete Bubblewrap launcher disassociating all namespaces with zero-overhead mounts.
   - `antigravity-agent@.service`: Production Systemd unit with cgroups v2 resource ceilings and capability drops.
   - `antigravity_policy.json`: Declarative JSON policy for runtime isolation.

3. **`shims/`**:
   - `curl`: Drops unauthorized WAN egress and blocks local secret file leakage (`.env`, `id_rsa`).
   - `git`: Intercepts and blocks dangerous flags (`--upload-pack`, `-c core.editor`) and force-pushes.
   - `npm`: Restricts unpinned package executions and arbitrary install hooks.
   - `env-clean`: Flushes ambient authority and launches commands under a pristine environment (`env -i`).

4. **`labs/`**:
   - The 13 Failure Labs corresponding directly to Chapters 1 through 13 of the monograph.

5. **`case-studies/`**:
   - `autonomous-sre/`: Complete end-to-end codebase of the Autonomous SRE Daemon demonstrating the union of Runtime Isolation, Adversarial Containment, and Headless Daemons.
