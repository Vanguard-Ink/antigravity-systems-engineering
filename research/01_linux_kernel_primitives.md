# Dossier 01: Linux Kernel Primitives for Agent Isolation

## 1. Linux Namespaces Architecture (`clone(2)` & `unshare(2)`)

Linux namespaces partition kernel resources such that one set of processes sees one set of resources while another set sees a completely isolated set. Autonomous agent processes must execute in partitioned namespaces to restrict ambient discovery and lateral traversal.

### 1.1 Canonical Namespace Flags & Definitions (`<linux/sched.h>`)

| Namespace | Clone Flag | Kernel Introduced | Isolated Resource Sphere | Risk if Leaked to Agent |
| :--- | :--- | :--- | :--- | :--- |
| **PID** | `CLONE_NEWPID` | Linux 2.6.24 | Process IDs, `/proc` process visibility | Agent can view, signal (`kill -9`), or `ptrace` host system processes. |
| **Network** | `CLONE_NEWNET` | Linux 2.6.29 | Network devices, routing tables, firewall rules, ports | Agent can access local cloud metadata services (`169.254.169.254`), host loopback listeners, or exfiltrate tokens over WAN. |
| **Mount** | `CLONE_NEWNS` | Linux 2.4.19 | Filesystem mount points and root directory (`chroot`/`pivot_root`) | Agent can overwrite host binaries (`/bin`, `/lib`), read `/etc/shadow`, or poison host configuration. |
| **User** | `CLONE_NEWUSER` | Linux 3.8 | UID/GID mappings, capabilities (`CAP_*`) | Allows running as root inside sandbox while mapped to unprivileged user (e.g. UID 1000) on host; prevents root escalation. |
| **IPC** | `CLONE_NEWIPC` | Linux 2.6.19 | System V IPC, POSIX message queues, shared memory | Agent can snoop on host shared memory segments (`shmget`, `/dev/shm`) or poison inter-process queues. |
| **UTS** | `CLONE_NEWUTS` | Linux 2.6.19 | Hostname and NIS domain name | Minor direct risk, but leaks infrastructure topology naming conventions. |
| **Cgroup** | `CLONE_NEWCGROUP`| Linux 4.6 | Root directory of `/proc/self/cgroup` | Exposes host cgroup hierarchy, enabling noisy-neighbor attacks or resource escaping. |
| **Time** | `CLONE_NEWTIME` | Linux 5.6 | Monotonic and boot clocks | Clock tampering affecting time-based cryptographic tokens. |

### 1.2 User Namespace UID/GID Mapping Mechanics
Rootless isolation maps container root (UID 0) to an unprivileged host UID:
```text
Host UID 1000  <==== mapping ====>  Sandbox UID 0 (root inside sandbox)
Host UID 1001+ <==== unmapped ===>  Inaccessible / Overflow UID (65534 / nobody)
```
Kernel file: `/proc/[pid]/uid_map` format:
```text
ID-inside-ns   ID-outside-ns   length
0              1000            1
```

---

## 2. Control Groups v2 (cgroups v2) Unified Hierarchy

cgroups v2 organizes processes hierarchically and distributes system resources along that hierarchy under a single unified tree (`/sys/fs/cgroup`).

### 2.1 Unified Hierarchy Layout
```text
/sys/fs/cgroup/
├── cgroup.controllers          # Available root controllers (cpu memory pids io)
├── cgroup.subtree_control      # Enabled controllers for immediate child groups
└── agent-workers.slice/        # Dedicated slice for autonomous agent execution
    ├── cgroup.procs            # PIDs assigned to this slice
    ├── memory.max              # Hard OOM threshold (e.g. 512M)
    ├── memory.high             # Throttling threshold (e.g. 400M)
    ├── memory.current          # Current memory consumption in bytes
    ├── memory.events           # Count of oom, oom_kill, high events
    ├── pids.max                # Max process/thread count (prevents fork-bombs)
    ├── pids.current            # Current process count
    ├── cpu.max                 # Bandwidth quota (e.g. 50000 100000 = 50% of 1 CPU)
    ├── cpu.stat                # usage_usec, user_usec, system_usec
    └── io.weight               # Proportional IO bandwidth (1 - 1000)
```

### 2.2 Critical Invariant Settings for Agent Sandboxing
- **Fork-Bomb Neutralization**: Set `pids.max = 64`. A runaway recursive shell script or malicious build step (`:(){ :|:& };:`) hits the limit and fails with `EAGAIN` (`Resource temporarily unavailable`) without starving host PIDs.
- **Out-of-Memory Containment**: Set `memory.max = 536870912` (512MB). Triggers the kernel cgroup OOM killer specifically within the cgroup boundary without terminating host daemons.
- **CPU Quota Throttling**: Set `cpu.max = "50000 100000"` (50ms per 100ms period). Prevents crypto-mining or infinite compiler loops from pegging 100% of host cores.

---

## 3. Seccomp-BPF (Secure Computing with Berkeley Packet Filters)

Seccomp filters syscalls before they reach the kernel dispatch table.

### 3.1 BPF Filter Structure (`<linux/seccomp.h>`, `<linux/filter.h>`)
```c
struct sock_filter {    /* Filter block */
    __u16   code;       /* Actual filter code */
    __u8    jt;         /* Jump true offset */
    __u8    jf;         /* Jump false offset */
    __u32   k;          /* Generic multiuse field (syscall nr / arg value) */
};

struct sock_fprog {     /* Required for PR_SET_SECCOMP */
    unsigned short      len;    /* Number of filter blocks */
    struct sock_filter  *filter;
};
```

### 3.2 Key Action Return Codes
- `SECCOMP_RET_KILL_PROCESS` (0x80000000U): Terminates the entire process immediately without executing the syscall.
- `SECCOMP_RET_TRAP` (0x00030000U): Sends `SIGSYS` to the thread, allowing user-space handler inspection.
- `SECCOMP_RET_ERRNO` (0x00050000U | errno): Returns a specific errno (e.g. `EPERM` 1) directly to caller without executing syscall.
- `SECCOMP_RET_ALLOW` (0x7fff0000U): Allows the system call to proceed.

### 3.3 Default Blocked Syscalls for Autonomous Coding Agents
```text
- ptrace(2)           : Prevents inspecting/modifying memory of sibling processes.
- bpf(2)              : Blocks loading unauthorized eBPF programs into the host kernel.
- mount(2), umount2(2): Blocks modifying filesystem mount trees.
- kexec_load(2)       : Prevents booting replacement kernels.
- reboot(2)           : Prevents system shutdown.
- init_module(2)      : Blocks loading rogue kernel modules (.ko).
- keyctl(2)           : Prevents accessing kernel keyring storage.
```

---

## 4. Landlock LSM (Linux 5.13+)

Landlock allows unprivileged processes to restrict their own file and socket access without root privileges:
```c
#include <linux/landlock.h>
#include <sys/prctl.h>
#include <sys/syscall.h>

struct landlock_ruleset_attr ruleset_attr = {
    .handled_access_fs = LANDLOCK_ACCESS_FS_EXECUTE |
                         LANDLOCK_ACCESS_FS_WRITE_FILE |
                         LANDLOCK_ACCESS_FS_READ_FILE |
                         LANDLOCK_ACCESS_FS_READ_DIR |
                         LANDLOCK_ACCESS_FS_REMOVE_DIR |
                         LANDLOCK_ACCESS_FS_REMOVE_FILE |
                         LANDLOCK_ACCESS_FS_MAKE_REG,
};
```
Enforcement requires:
1. `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)`: Prohibits gaining privileges via `setuid` binaries.
2. `syscall(SYS_landlock_restrict_self, ruleset_fd, 0)`: Locks the process and all future descendants into the rule sandbox permanently.
