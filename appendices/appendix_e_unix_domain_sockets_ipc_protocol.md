# Appendix E: UNIX Domain Sockets IPC Protocol Specification

This appendix defines the binary framing and structured messaging protocol utilized by Antigravity Host Supervisors and Sandboxed Agent Workers over local UNIX Domain Sockets (`AF_UNIX`).

---

## E.1 Wire Framing Protocol (Length-Prefixed JSON-RPC 2.0)

Every message transmitted across the socket begins with a fixed **4-byte unsigned big-endian integer** indicating the payload size in bytes, followed immediately by UTF-8 encoded JSON-RPC 2.0 payload bytes.

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  PAYLOAD LENGTH (32-bit UINT)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                    JSON-RPC 2.0 PAYLOAD                       +
|                    (Variable Length UTF-8)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

---

## E.2 Core Message Schemas

### E.2.1 Handshake & Peer Attestation (`agent.handshake`)
Sent by the sandboxed worker immediately upon connecting to the supervisor socket:

```json
{
  "jsonrpc": "2.0",
  "id": "init-001",
  "method": "agent.handshake",
  "params": {
    "worker_id": "worker-subagent-9942",
    "protocol_version": "1.0",
    "capabilities": ["fs_read", "fs_write", "exec_allowlisted"],
    "process": {
      "pid": 2048,
      "uid": 1000,
      "gid": 1000
    }
  }
}
```

Supervisor Response:
```json
{
  "jsonrpc": "2.0",
  "id": "init-001",
  "result": {
    "status": "authenticated",
    "session_id": "sess_883a9c72e",
    "heartbeat_interval_seconds": 15
  }
}
```

### E.2.2 Tool Execution Request (`agent.exec_command`)
```json
{
  "jsonrpc": "2.0",
  "id": "task-501",
  "method": "agent.exec_command",
  "params": {
    "command": "cargo test -- --nocapture",
    "timeout_seconds": 60,
    "env_overrides": {
      "RUST_BACKTRACE": "1"
    }
  }
}
```

---

## E.3 Capability Passing via `SCM_RIGHTS` (Python `socket.sendmsg`)

When the host supervisor passes an open file descriptor (e.g. read-only log file or specific socket) into the worker sandbox:

```python
import socket
import array

def send_file_descriptor(sock: socket.socket, fd_to_send: int, message_payload: bytes):
    """Sends a 4-byte length-prefixed payload along with an open FD via SCM_RIGHTS."""
    length_prefix = len(message_payload).to_bytes(4, byteorder="big")
    full_payload = length_prefix + message_payload

    # Pack the FD into ancillary control message data
    ancdata = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [fd_to_send]))]
    
    sock.sendmsg([full_payload], ancdata)

def receive_file_descriptor(sock: socket.socket) -> tuple[bytes, int]:
    """Receives length-prefixed payload and extracts the passed FD."""
    # Read 4-byte length prefix
    raw_len = sock.recv(4)
    length = int.from_bytes(raw_len, byteorder="big")

    # Allocate ancillary data buffer for one integer FD
    anc_buf_size = socket.CMSG_LEN(array.array("i").itemsize)
    msg, ancdata, flags, addr = sock.recvmsg(length, anc_buf_size)

    passed_fd = -1
    for cmsg_level, cmsg_type, cmsg_data in ancdata:
        if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
            fds = array.array("i")
            fds.frombytes(cmsg_data[:len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
            passed_fd = fds[0]

    return msg, passed_fd
```
