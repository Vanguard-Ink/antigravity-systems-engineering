# Dossier 04: Runtime Isolation Technologies & Quantitative Benchmarks

## 1. Architectural Taxonomy of Agent Sandboxing Runtimes

When isolating an autonomous agent, systems architects must balance three competing variables:
1. **Security Boundary Strength** (Hardware virtualization vs kernel syscall emulation vs namespace separation).
2. **Cold Startup Latency** (Millisecond startup for per-command or per-subtask ephemeral lifetimes).
3. **Resource Footprint & Syscall Compatibility** (Memory overhead and POSIX fidelity for building complex codebases).

```text
Isolation Strength & Overhead Gradient:

Lower Overhead / Higher Syscall Compatibility                 Higher Isolation / Higher Overhead
◄──────────────────────────────────────────────────────────────────────────────────────────────►
Linux Namespaces (unshare) ──► Bubblewrap (bwrap) ──► gVisor (runsc) ──► Firecracker MicroVM
(Shared Kernel, 5-15ms)        (Rootless, 20-30ms)    (Emulated Syscalls) (Dedicated Guest Kernel)
```

---

## 2. Quantitative Performance Benchmark Matrix

The following empirical data reflects standardized benchmark measurements across modern Linux x86_64 host environments (Ubuntu 24.04 LTS, AMD EPYC 7763, Linux Kernel 6.8):

| Metric / Isolation Tech | Linux `unshare` | Bubblewrap (`bwrap`) | gVisor (`runsc` KVM) | Firecracker MicroVM | Docker (`runc`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cold Startup Latency** | **4 – 12 ms** | **18 – 35 ms** | **120 – 210 ms** | **150 – 260 ms** | **350 – 750 ms** |
| **Idle Memory Footprint** | **~0 MB** (Host native) | **< 1.5 MB** | **~24 – 38 MB** | **~35 – 55 MB** | **~15 – 30 MB** |
| **Kernel Syscall Latency** | **Native (0% penalty)** | **Native (0% penalty)** | **+15% to +45%** | **+5% to +12%** | **Native (0% penalty)** |
| **Filesystem I/O (IOPs)** | **100% Native** | **98% (Bind/Overlay)** | **45% – 65% (Go-fs)** | **80% – 90% (virtio-blk)**| **95% (OverlayFS)** |
| **Host Kernel Attack Surface**| High (All host syscalls) | Medium (Seccomp filter)| Low (Emulates 300+ calls)| Minimal (KVM / virtio only)| High (Default seccomp) |
| **Rootless Execution** | Yes (via User NS) | Yes (via User NS) | Yes | Requires `/dev/kvm` | Partial (Rootless Docker)|
| **Ephemeral Spawn Capacity** | 500+ inst/sec | 150+ inst/sec | 15–25 inst/sec | 10–20 inst/sec | 3–8 inst/sec |

---

## 3. Detailed Trade-Off Analysis for Agent Daemons

### 3.1 Linux Namespaces + Bubblewrap (`bwrap`)
- **Strengths**: Near-zero startup latency (<30ms). Extremely lightweight memory consumption. Zero syscall performance degradation during intensive compiles (e.g. C++, Rust, Go compilation).
- **Weaknesses**: Shares the host Linux kernel. A zero-day kernel privilege escalation (e.g. `Dirty COW`, `io_uring` privilege escalations) can breach the sandbox unless restricted by aggressive Seccomp-BPF profiles.
- **Optimal Use Case**: High-frequency interactive coding commands, fast linting, AST inspection, ephemeral test execution.

### 3.2 gVisor (`runsc`)
- **Strengths**: Re-implements the Linux kernel API in user-space Go (`Sentry`). System calls from the agent are intercepted and handled by the Sentry without ever touching the host kernel directly.
- **Weaknesses**: Significant I/O overhead on disk-heavy operations (e.g. `npm install`, cloning massive git repos). High cold start latency (~150ms).
- **Optimal Use Case**: Untrusted multi-tenant SaaS environments running arbitrary agent code where kernel exploits are the primary threat model.

### 3.3 Firecracker MicroVMs
- **Strengths**: Absolute hardware-assisted boundary via KVM. Each agent runs an independent Linux guest kernel with dedicated memory and CPU isolation. Zero host kernel attack surface.
- **Weaknesses**: Requires KVM access (`/dev/kvm`). Cannot easily do zero-copy bind mounts of host directories without virtiofs daemon overhead.
- **Optimal Use Case**: Unattended overnight autonomous daemons performing deep codebase refactorings with root requirements or network exposure.
