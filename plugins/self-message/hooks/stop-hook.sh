#!/bin/bash
# Self-Message Stop Hook for Claude Code
# Enables Claude to send itself continuation messages mid-session.
#
# Checks /tmp/claude-self-msg/ for message files written by the script.
# Claims one atomically via mv, reads it, blocks the stop.
#
# Safety: max consecutive self-messages capped by SELF_MSG_MAX_DEPTH (default 200, ~12h autonomy)

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "default"')

MSG_DIR="/tmp/claude-self-msg"
COUNT_FILE="/tmp/claude-self-msg-count-${SESSION_ID}"
MAX_DEPTH="${SELF_MSG_MAX_DEPTH:-200}"

# Try to claim any available message file
CLAIMED=""
if [ -d "$MSG_DIR" ]; then
  for f in "${MSG_DIR}"/msg.*; do
    [ -f "$f" ] || continue
    TARGET="${MSG_DIR}/claimed-${SESSION_ID}"
    if mv "$f" "$TARGET" 2>/dev/null; then
      CLAIMED="$TARGET"
      break
    fi
  done
fi

if [ -n "$CLAIMED" ]; then
  # Read and increment counter
  COUNT=0
  if [ -f "$COUNT_FILE" ]; then
    COUNT=$(cat "$COUNT_FILE")
  fi
  COUNT=$((COUNT + 1))

  if [ "$COUNT" -gt "$MAX_DEPTH" ]; then
    rm -f "$CLAIMED" "$COUNT_FILE"
    echo "{}"
    exit 0
  fi

  REASON=$(cat "$CLAIMED")
  rm "$CLAIMED"
  echo "$COUNT" > "$COUNT_FILE"
  echo "{\"decision\": \"block\", \"reason\": $(echo "$REASON" | jq -Rs .)}"
  exit 0
fi

# No self-message — normal stop, reset counter
rm -f "$COUNT_FILE"
echo "{}"
exit 0
