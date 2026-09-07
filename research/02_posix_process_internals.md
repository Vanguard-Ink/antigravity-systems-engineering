# Dossier 02: POSIX Process Semantics & Shell Execution Mechanics

## 1. Process Lifecycle & Ambient Authority Inheritance

Under the POSIX execution model, every process is created via `fork(2)` (duplicating the caller) followed by `execve(2)` (replacing the process image with a new binary).

### 1.1 The Inheritance Contract
When a parent agent process executes `fork()`, the child inherits:
- **File Descriptor Table**: Every open file descriptor (files, sockets, pipes) remains open in the child unless the `O_CLOEXEC` flag was explicitly specified at creation time.
- **Environment Block (`char **environ`)**: The entire memory array of key-value environment variables is copied bit-for-bit into the child's address space.
- **Current Working Directory (`cwd`)** and root directory (`chroot`).
- **Process Credentials**: Real, effective, and saved UIDs and GIDs; supplementary group IDs.
- **Resource Limits (`getrlimit`/`setrlimit`)** and `umask`.
- **Signal Dispositions**: Handlers reset to default (`SIG_DFL`) on `execve()`, but ignored signals (`SIG_IGN`) remain ignored.

```text
Host / Agent Supervisor (PID 100)
│   Open FDs: 0(in), 1(out), 2(err), 3(DB Socket), 4(Master Token Pipe)
│   Environ : AWS_SECRET_ACCESS_KEY, GITHUB_TOKEN, PATH
│
└── fork() + execve("/bin/bash", ["-c", "npm test"])
    │
    ▼ Child Subshell Process (PID 101)
        Open FDs: 0, 1, 2, 3 (LEAKED DB Socket!), 4 (LEAKED Pipe!)
        Environ : AWS_SECRET_ACCESS_KEY (LEAKED!), GITHUB_TOKEN (LEAKED!)
```

---

## 2. Kernel File Descriptors & Memory Leak Vectors

### 2.1 The `/proc/$PID/environ` Leak Channel
In Linux, the initial environment of every process is exposed via the virtual filesystem:
```bash
cat /proc/101/environ | tr '\0' '\n'
```
Even if an agent script executes `unset AWS_SECRET_ACCESS_KEY`, the `/proc/[pid]/environ` pseudo-file retains the exact byte string passed to `execve(2)` at process spawn. Any compromised child or sibling with matching UID can read these secrets directly.

### 2.2 File Descriptor Leakage (`/proc/$PID/fd`)
If an agent harness opens a database connection or unix domain socket without `FD_CLOEXEC`:
```c
int fd = open("/var/run/docker.sock", O_RDWR); // Missing O_CLOEXEC!
```
The child process can inspect `/proc/self/fd/`:
```bash
ls -l /proc/self/fd/
# lrwx------ 1 agent agent 64 Sep 7 12:00 3 -> /var/run/docker.sock
```
The child process can directly communicate over file descriptor 3 to control the Docker daemon or host database without needing file system path permissions.

---

## 3. Pipes, TTYs, and Deadlock Mechanics

### 3.1 Linux Pipe Buffer Deadlocks (`F_SETPIPE_SZ`)
In Linux, an anonymous pipe created via `pipe(2)` or `pipe2(2)` has a default capacity of **65,536 bytes (64 KB)** (`/proc/sys/fs/pipe-max-size`).

#### The Classic Deadlock Scenario:
1. Agent launches subshell: `subprocess.Popen("mvn test", stdout=PIPE, stderr=PIPE)`.
2. The compiler emits 100 KB of diagnostic data to `stdout`.
3. The child process writes 64 KB, filling the kernel pipe buffer completely.
4. The child's subsequent `write(1, ...)` call blocks in the kernel waiting for reader drain.
5. The agent process is synchronously waiting for `mvn test` to exit (`process.wait()`) before reading `process.stdout.read()`.
6. **Result**: Complete unrecoverable deadlock. The subshell process hangs indefinitely, burning memory and holding open locks.

### 3.2 Stateful PTYs vs. Stateless Subshells

| Metric / Dimension | Stateless Subshell (`sh -c '...'`) | Stateful Pseudo-Terminal (PTY) |
| :--- | :--- | :--- |
| **Persistence** | Discarded on process exit (Zero state drift) | Session persists (directory, shell variables, background jobs) |
| **Buffer Deadlock Risk** | High (blocking pipe buffers without async drain) | Low (PTY line discipline handles flow control) |
| **Interactive Prompts** | Hangs indefinitely on `read` / `sudo` prompts | Can detect and respond to password / confirmation prompts |
| **Process Isolation** | Clean lifecycle per command execution | Lingering background subshells (`&`), leaked child demons |
| **Control Characters** | Transmitted raw (`\r\n`, ANSI escape codes) | Processed via `termios` (echo, canonical mode, raw mode) |

---

## 4. Signal Handling and Zombie Process Reaping

### 4.1 Signal Propagation Matrix
- `SIGINT` (2): Interrupt from keyboard (`Ctrl+C`). Can be trapped and ignored by subshell scripts.
- `SIGTERM` (15): Polite termination request. Gives processes a chance to save state or flush buffers.
- `SIGKILL` (9): Uncatchable kernel-level execution kill. Immediate termination.
- `SIGPIPE` (13): Broken pipe. Triggered when writing to a pipe with no active readers. Default action is silent process termination.

### 4.2 The Zombie Accumulation Problem (`waitpid`)
When a child terminates, its process entry remains in the kernel process table as a `defunct` (zombie) process until the parent calls `wait(2)` or `waitpid(2)` to read its exit status (`wstatus`).
If a long-running agent daemon spawns hundreds of command subshells without a dedicated reaping loop or `SIGCHLD` handler:
1. Kernel process table exhausts available PID numbers.
2. Subsequent `fork()` calls fail system-wide with `EAGAIN`.
3. The agent engine freezes.
