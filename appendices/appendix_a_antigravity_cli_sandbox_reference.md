# Appendix A: Antigravity CLI & Sandbox Configuration Specification

This appendix provides the canonical, production-hardened configuration reference for Google Antigravity CLI (`agy`) and the underlying Antigravity runtime sandbox.

---

## A.1 Global Configuration Schema (`~/.gemini/antigravity-cli/settings.json`)

```json
{
  "$schema": "https://antigravity.google/schemas/v1/runtime-config.json",
  "version": "1.0.0",
  "runtime": {
    "engine": "bubblewrap",
    "log_level": "info",
    "audit_log_path": "/var/log/antigravity/audit.jsonl"
  },
  "sandbox": {
    "enabled": true,
    "mode": "strict",
    "unshare_flags": [
      "ipc",
      "net",
      "pid",
      "uts",
      "cgroup"
    ],
    "limits": {
      "max_pids": 64,
      "max_memory_mb": 1024,
      "max_cpu_percent": 80,
      "max_open_files": 512,
      "timeout_seconds": 300,
      "max_output_bytes": 65536
    },
    "filesystem": {
      "rootfs_readonly": true,
      "mounts": [
        {
          "type": "ro-bind",
          "source": "/usr",
          "destination": "/usr"
        },
        {
          "type": "ro-bind",
          "source": "/lib",
          "destination": "/lib"
        },
        {
          "type": "ro-bind",
          "source": "/bin",
          "destination": "/bin"
        },
        {
          "type": "ro-bind",
          "source": "/etc/ssl",
          "destination": "/etc/ssl"
        },
        {
          "type": "overlay",
          "lower": "/workspace",
          "upper": "/tmp/antigravity-cow/upper",
          "work": "/tmp/antigravity-cow/work",
          "destination": "/workspace"
        },
        {
          "type": "tmpfs",
          "destination": "/tmp",
          "size_mb": 256
        }
      ]
    },
    "network": {
      "policy": "deny_all",
      "allowed_domains": [],
      "dns_proxy_port": 0
    }
  },
  "guardrails": {
    "ast_parser": {
      "enabled": true,
      "engine": "tree-sitter-bash"
    },
    "ambient_environment": {
      "strip_all": true,
      "whitelist": [
        "LANG",
        "LC_ALL",
        "TERM",
        "PATH"
      ],
      "injected_env": {
        "CI": "true",
        "ANTIGRAVITY_SANDBOX": "1"
      }
    },
    "blocked_binaries": [
      "sudo",
      "su",
      "curl",
      "wget",
      "nc",
      "netcat",
      "ncat",
      "socat",
      "ssh",
      "scp",
      "base64",
      "xxd",
      "dd"
    ]
  }
}
```

---

## A.2 Antigravity CLI Flag Reference (`agy`)

| Flag Name | Type | Default | Systems Effect & Kernel Boundary |
| :--- | :--- | :--- | :--- |
| `--sandbox` | string | `strict` | Sets sandbox isolation tier: `off`, `light` (mount only), `strict` (all namespaces + cgroups + seccomp). |
| `--no-net` | boolean | `false` | Unshares network namespace (`CLONE_NEWNET`); drops `lo` interface. |
| `--memory-limit` | string | `1G` | Configures `memory.max` in the cgroups v2 task slice. |
| `--pids-limit` | integer| `64` | Configures `pids.max` in cgroups v2; prevents fork-bomb attacks. |
| `--read-only` | boolean | `false` | Mounts workspace as read-only; blocks all file modification tools. |
| `--caps` | string | `none` | Controls Linux capability bounding set (e.g. `CAP_NET_BIND_SERVICE`). |
| `--audit-log` | path | `none` | Emits structured JSONL audit logs of all tool calls and subshell execs. |
| `--timeout` | integer| `300` | Hard supervisor timeout in seconds; sends `SIGKILL` on expiration. |

---

## A.3 Environment Variable Overrides

- `ANTIGRAVITY_SANDBOX_STRICT=1`: Forces strict rootless bubblewrap sandboxing across all subagents.
- `ANTIGRAVITY_EGRESS_PROXY=http://127.0.0.1:8080`: Routes all authorized agent HTTP requests through an inspecting proxy with TLS termination and token brokering.
- `ANTIGRAVITY_AUDIT_FD=3`: Passes open file descriptor 3 to agent supervisor for zero-latency audit streaming over Unix domain sockets.
