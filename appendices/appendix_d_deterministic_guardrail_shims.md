# Appendix D: Deterministic Guardrail Interception Shims

This appendix provides production-grade interception wrappers (shims) designed to replace standard system binaries in the agent's restricted `PATH`. These shims enforce deterministic guardrails, strip ambient tokens, and reject unauthorized operations at sub-millisecond speeds without probabilistic LLM-as-a-judge overhead.

---

## D.1 Universal Curl Interception Shim (`/usr/local/shim/curl`)

This executable script intercepts all `curl` executions within the agent's environment:
- Disallows arbitrary internet egress.
- Enforces loopback proxy routing (`ANTIGRAVITY_EGRESS_PROXY`).
- Blocks sending raw environment files (`.env`, `id_rsa`, AWS credentials).

```bash
#!/usr/bin/env bash
# Antigravity Egress Interception Shim: curl
set -euo pipefail

REAL_CURL="/usr/bin/curl"
AUDIT_LOG="/var/log/antigravity/egress_audit.log"

# Inspect arguments for sensitive local file disclosures
for arg in "$@"; do
    if [[ "$arg" =~ \.env|\.aws|\.ssh|id_rsa|credentials|shadow ]]; then
        echo "[SECURITY SHIM BLOCKED] curl attempt referencing sensitive file: $arg" >&2
        echo "$(date -u --iso-8601=seconds) BLOCKED_FILE_DISCLOSURE PID=$$ ARGS=$*" >> "$AUDIT_LOG"
        exit 126
    fi
done

# If offline mode is mandated, block all network egress
if [[ "${ANTIGRAVITY_OFFLINE:-1}" == "1" ]]; then
    echo "[SECURITY SHIM BLOCKED] Outbound network egress disabled by Antigravity sandbox policy." >&2
    echo "$(date -u --iso-8601=seconds) BLOCKED_OFFLINE_EGRESS PID=$$ ARGS=$*" >> "$AUDIT_LOG"
    exit 126
fi

# Route through inspecting proxy if defined
if [[ -n "${ANTIGRAVITY_EGRESS_PROXY:-}" ]]; then
    exec "$REAL_CURL" --proxy "$ANTIGRAVITY_EGRESS_PROXY" "$@"
else
    exec "$REAL_CURL" "$@"
fi
```

---

## D.2 Git Security Shim (`/usr/local/shim/git`)

Blocks destructive git operations, forced pushes to protected branches, and arbitrary command execution via git configs:

```bash
#!/usr/bin/env bash
# Antigravity Git Guardrail Shim
set -euo pipefail

REAL_GIT="/usr/bin/git"

# Disallow dangerous git execution flags
for arg in "$@"; do
    case "$arg" in
        --upload-pack*|--exec*|-c\ core.editor=*|-c\ sequence.editor=*)
            echo "[SECURITY SHIM BLOCKED] Prohibited git argument: $arg" >&2
            exit 126
            ;;
    esac
done

# Inspect first subcommand
SUBCMD="${1:-}"

case "$SUBCMD" in
    push)
        # Verify agent is not force-pushing to main/master
        for arg in "$@"; do
            if [[ "$arg" == "--force" || "$arg" == "-f" ]]; then
                echo "[SECURITY SHIM BLOCKED] Autonomous agents are strictly forbidden from force-pushing." >&2
                exit 126
            fi
        done
        exec "$REAL_GIT" "$@"
        ;;
    clean)
        # Block recursive force-clean without dry-run
        for arg in "$@"; do
            if [[ "$arg" == "-f" || "$arg" == "-force" ]]; then
                echo "[SECURITY SHIM BLOCKED] Unsupervised git clean -f prohibited. Use dry-run first." >&2
                exit 126
            fi
        done
        exec "$REAL_GIT" "$@"
        ;;
    *)
        exec "$REAL_GIT" "$@"
        ;;
esac
```

---

## D.3 Environment Sanitizer Shim (`/usr/local/shim/env-clean`)

Completely flushes the process environment block before executing any user command:

```bash
#!/usr/bin/env bash
# Flushes ambient authority and launches command with strictly whitelisted variables
exec /usr/bin/env -i \
    HOME="${HOME:-/home/agent}" \
    USER="${USER:-agent}" \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    TERM="xterm-256color" \
    PATH="/usr/local/shim:/usr/local/bin:/usr/bin:/bin" \
    "$@"
```
