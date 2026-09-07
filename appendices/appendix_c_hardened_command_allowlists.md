# Appendix C: Production-Hardened Command Allowlist Rulesets

This appendix defines the AST-based grammar and categorization rulesets for validating shell commands emitted by autonomous coding agents prior to execution.

---

## C.1 The Three-Tier Command Classification Taxonomy

```text
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Read-Only Commands (Autonomous Safe Execution)                 │
│  - Examples: git status, git diff, ls, cat, grep, find, pwd            │
│  - Execution Policy: Executed automatically without supervisor gating. │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│ TIER 2: Mutating / Build Commands (Monitored Ephemeral Execution)       │
│  - Examples: npm test, cargo build, pytest, go test, make              │
│  - Execution Policy: Executed inside ephemeral CoW sandbox with quotas.│
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│ TIER 3: Blocked / Privileged Commands (Deterministic Rejection)        │
│  - Examples: sudo, su, curl, nc, ssh, dd, mkfs, mount, rm -rf /       │
│  - Execution Policy: Blocked immediately at AST validation layer.      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## C.2 Production AST Allowlist Ruleset Specification

### C.2.1 Git Binary Allowlist Rule
```json
{
  "binary": "git",
  "allowed_subcommands": [
    "status",
    "diff",
    "log",
    "branch",
    "show",
    "add",
    "commit",
    "checkout",
    "stash"
  ],
  "forbidden_flags": [
    "--upload-pack",
    "--exec",
    "-c core.editor=*",
    "-c sequence.editor=*"
  ],
  "require_no_remote_push": true
}
```

### C.2.2 Language Toolchains Allowlist
- **Python / pytest**:
  - `allowed_commands`: `["pytest", "python -m pytest", "flake8", "black --check", "mypy"]`
  - `forbidden_flags`: `["--pdb", "--capture=no"]`
- **Node.js / npm**:
  - `allowed_commands`: `["npm test", "npm run lint", "npx jest", "node --test"]`
  - `forbidden_commands`: `["npm publish", "npm login", "npx *"]` (arbitrary unpinned remote package execution)
- **Rust / Cargo**:
  - `allowed_commands`: `["cargo test", "cargo check", "cargo clippy", "cargo build"]`
  - `forbidden_flags`: `["--target-dir=/"]`

---

## C.3 AST Parsing Validation Architecture (Python Prototype)

```python
import tree_sitter_bash as tsbash
from tree_sitter import Language, Parser

BASH_LANGUAGE = Language(tsbash.language())
parser = Parser(BASH_LANGUAGE)

def validate_command_ast(command_string: str, allowlist_binaries: set, blocked_binaries: set) -> bool:
    tree = parser.parse(bytes(command_string, "utf8"))
    cursor = tree.walk()

    # Traverse all command nodes in the AST
    nodes_to_check = [tree.root_node]
    while nodes_to_check:
        node = nodes_to_check.pop()
        if node.type == "command_name":
            binary_name = node.text.decode("utf8")
            if binary_name in blocked_binaries:
                return False
            if binary_name not in allowlist_binaries:
                return False
        for child in node.children:
            nodes_to_check.append(child)

    return True
```
