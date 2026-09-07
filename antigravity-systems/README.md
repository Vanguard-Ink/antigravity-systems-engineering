# Antigravity Systems: Companion Codebase

> Companion repository for the canonical monograph:  
> **"ANTIGRAVITY SYSTEMS ENGINEERING: Runtime Isolation, Adversarial Containment, and Headless Agent Daemons"**

---

## Architectural Tree Overview

```text
antigravity-systems/
├── harnesses/        # Daemon lifecycle engines, supervisors, and IPC brokers
├── sandboxes/        # Antigravity & Linux kernel isolation templates (bwrap, systemd, cgroups)
├── shims/            # Deterministic interception proxies (git, curl, npm wrappers)
├── labs/             # 13 failure reproduction labs (Labs 01 – 13)
└── case-studies/     # Production Capstone: Autonomous SRE Daemon full codebase
```

---

## Component Catalog

### 1. [`harnesses/`](./harnesses)
Houses the core host runtime processes:
- `supervisor.py`: Process supervisor enforcing timeouts, process group teardown, and signal propagation.
- `ipc_broker.py`: High-throughput UNIX Domain Socket server with length-prefixed JSON-RPC 2.0 and `SO_PEERCRED` authentication.

### 2. [`sandboxes/`](./sandboxes)
Production templates for unescapable rootless isolation:
- `bubblewrap_strict.sh`: Complete Bubblewrap launcher disassociating all namespaces with zero-overhead mounts.
- `antigravity-agent@.service`: Production Systemd unit with cgroups v2 resource ceilings and capability drops.
- `antigravity_policy.json`: Declarative JSON policy for runtime isolation.

### 3. [`shims/`](./shims)
Deterministic binary wrappers mounted in the agent's restricted `PATH`:
- `curl`: Drops unauthorized WAN egress and blocks local secret file leakage (`.env`, `id_rsa`).
- `git`: Intercepts and blocks dangerous flags (`--upload-pack`, `-c core.editor`) and force-pushes.
- `npm`: Restricts unpinned package executions and arbitrary install hooks.
- `env-clean`: Flushes ambient authority and launches commands under a pristine environment.

### 4. [`labs/`](./labs)
The 13 Failure Labs corresponding directly to Chapters 1 through 13 of the monograph:
- `lab01-shell`: Ambient `.env` leak via indirect prompt injection in third-party markdown.
- `lab02-process`: Linux pipe buffer deadlock (64KB overflow) and zombie PID table exhaustion.
- `lab03-sandbox`: Fork-bomb & disk-fill containment via cgroups v2.
- `lab04-permissions`: Bypassing regex command filters vs. AST-based allowlisting.
- `lab05-ephemeral`: Workspace corruption recovery via zero-latency OverlayFS Copy-on-Write rollback.
- `lab06-threat-modeling`: Intercepting hallucinated packages / slopsquatting egress callbacks.
- `lab07-injection`: Defending against destructive DB commands via structural context fencing.
- `lab08-shims`: Intercepting obfuscated `base64 | sh` payloads with binary shims.
- `lab09-network`: Blocking unauthorized reverse TCP backdoors and DNS tunneling.
- `lab10-daemon`: Unattended background webhook consumer daemon with systemd watchdog.
- `lab11-checkpoints`: Mid-flight `kill -9` crash recovery from durable WAL checkpoint logs.
- `lab12-ipc`: Host dispatcher coordinating 3 parallel worker sandboxes via UNIX domain sockets.
- `lab13-sre`: End-to-end Autonomous SRE Daemon handling 02:00 AM production memory leak.

### 5. [`case-studies/`](./case-studies)
- `autonomous-sre/`: Complete end-to-end codebase of the Autonomous SRE Daemon demonstrating the union of Runtime Isolation, Adversarial Containment, and Headless Daemons.
