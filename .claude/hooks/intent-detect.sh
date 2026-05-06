#!/bin/bash
# Intent Detection Hook - Injects intent routing rules
# This hook runs on every user input and injects .info/info.md into context

set -e

# Path to intent routing rules
INFO_MD="$CLAUDE_PROJECT_DIR/.info/info.md"

# Read JSON input (for potential future use)
INPUT=$(cat)

# Extract prompt for logging/debugging (optional)
if command -v jq >/dev/null 2>&1; then
    PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty' 2>/dev/null || echo "")
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)
else
    PROMPT=$(echo "$INPUT" | grep -o '"prompt":"[^"]*"' | cut -d'"' -f4 || echo "")
    SESSION_ID="unknown"
fi

# Output intent routing rules file
if [ -f "$INFO_MD" ]; then
    cat "$INFO_MD"
fi
# info.md 不存在时不输出警告，避免每次输入都产生噪音

# Optional: Add a simple intent detection summary below the rules
# This provides quick context without repeating the full rules
if [ -n "$PROMPT" ]; then
    echo ""
    echo "────────────────────────────────────────────────────────────"
    echo "📍 当前输入: $PROMPT"
    echo "   请参考上述规则进行意图识别和分发"
    echo "────────────────────────────────────────────────────────────"
fi

exit 0
