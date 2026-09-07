# Dossier 06: IPC Mechanics & Systemd Supervision Specifications

## 1. Inter-Process Communication (IPC): UNIX Domain Sockets vs TCP

When supervising autonomous worker agents on a single host machine, the communication channel between the Host Dispatcher and Worker Sandboxes must satisfy:
1. **Low Latency & High Bandwidth** (Streaming large token buffers, ASTs, and file diffs).
2. **Access Control & Authenticated Peer Credentials** (Preventing rogue processes from injecting commands).
3. **Capability Passing** (Passing open file descriptors across process boundaries).

### 1.1 IPC Performance Benchmark (Single Host Linux 6.8)
| IPC Mechanism | Round-Trip Latency (64B payload) | Throughput (1GB stream) | Zero-Copy Support | Peer Auth Verification |
| :--- | :--- | :--- | :--- | :--- |
| **UNIX Domain Socket (`AF_UNIX`)** | **1.2 µs** | **4.2 GB/sec** | Yes (`vmsplice`/pipe) | Native (`SO_PEERCRED`) |
| **Loopback TCP (`127.0.0.1`)** | **9.8 µs** | **1.6 GB/sec** | No (TCP/IP stack) | Weak (Port hijack risk) |
| **gRPC over HTTP/2 (Loopback)** | **45.0 µs** | **780 MB/sec** | No (Protobuf overhead)| TLS / Auth tokens |
| **Named Pipes (`mkfifo`)** | **2.4 µs** | **2.8 GB/sec** | Partial | Filesystem permissions |

### 1.2 Peer Credential Authentication (`SO_PEERCRED`)
Unlike TCP sockets which any local user can connect to, UNIX domain sockets allow the server to ask the kernel for the client's verified PID, UID, and GID:
```c
struct ucred credentials;
socklen_t ucred_len = sizeof(struct ucred);
if (getsockopt(client_fd, SOL_SOCKET, SO_PEERCRED, &credentials, &ucred_len) == 0) {
    // Verified by Linux kernel:
    printf("Client PID: %d, UID: %d, GID: %d\n", 
           credentials.pid, credentials.uid, credentials.gid);
}
```

### 1.3 Capability Passing via `SCM_RIGHTS`
The supervisor can open a specific file or network socket on the host with elevated privileges, and then safely pass the file descriptor into the restricted sandbox via ancillary socket messages (`sendmsg(2)` with `cmsg_type = SCM_RIGHTS`). The sandboxed child receives the ready-to-use descriptor without having permission to open the file or network device itself.

---

## 2. Systemd Headless Daemon Supervision Specification

To run autonomous agents continuously without human interactive oversight, they must be supervised by `systemd` to handle OOM events, signal propagation, and watchdog deadlocks.

### 2.1 Production Systemd Service Unit (`/etc/systemd/system/antigravity-worker@.service`)
```ini
[Unit]
Description=Antigravity Autonomous Headless Agent Worker (%i)
After=network.target local-fs.target
Documentation=https://antigravity.google/docs/daemon

[Service]
Type=notify
ExecStart=/usr/local/bin/antigravity-daemon --worker-id=%i --config=/etc/antigravity/worker.json
Restart=on-failure
RestartSec=5s

# Watchdog & Liveness (Dead Man's Switch)
# Agent must ping systemd via sd_notify(0, "WATCHDOG=1") every 30s.
# If agent enters an infinite reasoning loop or freezes, systemd kills it.
WatchdogSec=30s

# Process & Resource Quotas (cgroups v2 mapping)
Slice=antigravity-agents.slice
TasksMax=128
MemoryMax=2G
MemoryHigh=1.6G
CPUWeight=100
IOWeight=100

# Kernel & Filesystem Sandboxing
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
NoNewPrivileges=yes

# Linux Capability Dropping
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=

# Logging & Telemetry
StandardOutput=journal
StandardError=journal
SyslogIdentifier=antigravity-%i

[Install]
WantedBy=multi-user.target
```

### 2.2 Systemd Transient Dynamic Units (`systemd-run`)
For ad-hoc agent jobs, supervisors spawn transient cgroups without static service files:
```bash
systemd-run --unit="agent-task-$(uuidgen)" \
            --slice="antigravity-tasks.slice" \
            --property="MemoryMax=512M" \
            --property="TasksMax=32" \
            --property="PrivateTmp=yes" \
            --property="NoNewPrivileges=yes" \
            /usr/local/bin/agent-task-runner --job-id=9942
```
