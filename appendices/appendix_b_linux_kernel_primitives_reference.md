# Appendix B: Linux Kernel Primitives Quick Reference

This appendix serves as an authoritative systems reference for low-level Linux kernel primitives used to construct adversarial containment sandboxes for autonomous coding agents.

---

## B.1 Namespace System Calls & Bitmasks

### B.1.1 Syscall Signatures (`<sched.h>`, `<unistd.h>`)
```c
#define _GNU_SOURCE
#include <sched.h>

// Spawns a child process inside newly unshared namespaces
int clone(int (*fn)(void *), void *stack, int flags, void *arg, ... 
          /* pid_t *parent_tid, void *tls, pid_t *child_tid */);

// Disassociates the calling process from host namespaces
int unshare(int flags);

// Attaches the calling thread to an existing namespace via file descriptor
int setns(int fd, int nstype);
```

### B.1.2 Namespace Flags Reference
```c
#define CLONE_NEWNS      0x00020000 /* Mount namespace */
#define CLONE_NEWCGROUP  0x02000000 /* Cgroup namespace */
#define CLONE_NEWUTS     0x04000000 /* UTS (hostname) namespace */
#define CLONE_NEWIPC     0x08000000 /* IPC namespace */
#define CLONE_NEWUSER    0x10000000 /* User namespace */
#define CLONE_NEWPID     0x20000000 /* PID namespace */
#define CLONE_NEWNET     0x40000000 /* Network namespace */
#define CLONE_NEWTIME    0x00000080 /* Time namespace */
```

---

## B.2 Control Groups v2 (cgroups v2) Reference Architecture

### B.2.1 Core Controller Knobs (`/sys/fs/cgroup/<slice>/`)
- **`pids.max`**: Hard upper bound on active tasks/threads.
  ```bash
  echo 64 > /sys/fs/cgroup/antigravity.slice/pids.max
  ```
- **`memory.max`**: Memory usage hard limit. Reaching this triggers the kernel cgroup OOM killer.
  ```bash
  echo 1073741824 > /sys/fs/cgroup/antigravity.slice/memory.max # 1 GiB
  ```
- **`memory.high`**: Memory throttling threshold. Slows down process allocation without terminating.
  ```bash
  echo 805306368 > /sys/fs/cgroup/antigravity.slice/memory.high # 768 MiB
  ```
- **`cpu.max`**: CPU quota in microseconds per period: `quota period`.
  ```bash
  echo "80000 100000" > /sys/fs/cgroup/antigravity.slice/cpu.max # 80% of 1 core
  ```
- **`cgroup.kill`**: Writing `1` atomically sends `SIGKILL` to all processes in the slice.
  ```bash
  echo 1 > /sys/fs/cgroup/antigravity.slice/cgroup.kill
  ```

---

## B.3 Seccomp-BPF Assembly Reference

### B.3.1 BPF Filter Assembly Example (Blocking Dangerous Syscalls)
The following BPF filter allows standard execution but returns `EPERM` immediately if the agent attempts `ptrace(2)`, `mount(2)`, or `bpf(2)`:

```c
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <stddef.h>
#include <errno.h>

struct sock_filter filter[] = {
    /* [0] Load architecture from seccomp_data */
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
    /* [1] Verify architecture is x86_64; if false jump to kill */
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

    /* [2] Load system call number */
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

    /* [3] Check if syscall == ptrace */
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_ptrace, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

    /* [4] Check if syscall == mount */
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mount, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

    /* [5] Check if syscall == bpf */
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_bpf, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

    /* [6] Default: Allow all other syscalls */
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
};

struct sock_fprog prog = {
    .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
    .filter = filter,
};
```

Enforcement invocation:
```c
prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
```
