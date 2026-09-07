# Dossier 05: Google Antigravity Architecture & SDK Specifications

## 1. Antigravity System Architecture

Google Antigravity operates on an agentic architecture designed for safe software engineering:
1. **The Reasoning & Generation Plane**: Hosted foundation models (Gemini family) generating intent, chain-of-thought, and strongly typed `ToolCall` events.
2. **The Supervision & Dispatch Plane**: The Antigravity Host Process (`agy` CLI or `Agent` SDK daemon) receiving events, validating policies, acquiring lock tokens, and routing commands.
3. **The Execution & Isolation Plane (The Sandbox)**: An isolated process boundary where file mutations, terminal commands, and build scripts execute.

```text
┌────────────────────────────────────────────────────────┐
│     Reasoning Plane (Gemini Foundation Models)         │
└───────────────────────────┬────────────────────────────┘
                            │ ToolCall (Structured Event)
                            ▼
┌────────────────────────────────────────────────────────┐
│   Supervision Plane (Antigravity Daemon / Host CLI)    │
│  - CapabilitiesConfig Policy Engine                    │
│  - Hook Pipeline (Pre-Execution / Post-Execution)      │
│  - Token / Secret Brokering Layer                      │
└───────────────────────────┬────────────────────────────┘
                            │ Filtered & Sanitized Payload
                            ▼
┌────────────────────────────────────────────────────────┐
│   Execution Plane (Antigravity Sandboxed Subshell)     │
│  - Ephemeral OverlayFS Mount                           │
│  - Stripped Environment (No Ambient Cloud Secrets)     │
│  - Restricted PID & Net Namespaces                     │
└────────────────────────────────────────────────────────┘
```

---

## 2. Python SDK Deep Architecture (`google-antigravity`)

### 2.1 Configuration Primitives (`LocalAgentConfig` & `CapabilitiesConfig`)
The Antigravity SDK enforces security defaults through strongly-typed configuration classes:

```python
from google.antigravity import LocalAgentConfig, CapabilitiesConfig

# Production-Hardened Read-Only Configuration
read_only_config = LocalAgentConfig(
    system_instructions="You are an automated code security auditor.",
    capabilities=CapabilitiesConfig(
        can_run_commands=False,
        can_edit_files=False,
        can_access_network=False,
        allowed_paths=["/workspace/src", "/workspace/docs"]
    )
)

# Constrained Mutation Configuration for Supervised SRE Workflows
supervised_worker_config = LocalAgentConfig(
    system_instructions="You are an autonomous SRE triage worker.",
    capabilities=CapabilitiesConfig(
        can_run_commands=True,
        can_edit_files=True,
        can_access_network=False, # Egress denied by default
        command_allowlist=["pytest", "cargo test", "npm test", "git diff"],
        command_timeout_seconds=60,
        max_output_bytes=65536 # Prevents buffer overflow deadlocks
    )
)
```

### 2.2 Event Streaming & Execution Hooks
The SDK exposes streaming generators for real-time observation and intervention:
- `response.thoughts`: Real-time streaming of model deliberation. Allows supervisor daemons to detect malicious intent or reasoning divergence before tool dispatch.
- `response.tool_calls`: Strongly-typed tool invocation structures (`name`, `args`).
- **Pre-execution interceptor hooks**: Custom Python callables that inspect every `ToolCall` and can abort, modify, or escalate for human approval.

---

## 3. Antigravity CLI (`agy`) Runtime Configuration

### 3.1 Settings Architecture (`~/.gemini/antigravity-cli/settings.json`)
```json
{
  "sandbox": {
    "enabled": true,
    "runtime": "bubblewrap",
    "network_isolation": "deny_all",
    "timeout_seconds": 300,
    "max_memory_mb": 1024,
    "max_pids": 64,
    "readonly_mounts": [
      "/usr",
      "/lib",
      "/bin",
      "/etc"
    ],
    "ephemeral_mounts": [
      "/tmp",
      "/workspace"
    ]
  },
  "guardrails": {
    "ast_shell_parser": true,
    "strip_ambient_env": true,
    "drop_dangerous_caps": true,
    "blocked_binaries": [
      "curl",
      "wget",
      "nc",
      "socat",
      "ncat",
      "base64",
      "sudo",
      "su"
    ]
  }
}
```

### 3.2 CLI Flags for Process Sandboxing
- `agy --sandbox=strict`: Spawns all agent tools inside a rootless Bubblewrap sandbox.
- `agy --no-net`: Unshares network namespace (`CLONE_NEWNET`) for all command executions.
- `agy --read-only`: Disables file mutation tools completely.
- `agy --audit-log=/var/log/antigravity-audit.jsonl`: Emits structured JSON audit events for every syscall, subshell execution, and file diff.
