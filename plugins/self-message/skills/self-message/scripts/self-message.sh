#!/bin/bash
# Self-Message: write a continuation message for the Stop hook to pick up.
# Usage: self-message.sh "Your continuation message here"
#
# Writes to a unique temp file to avoid collisions between concurrent sessions.

MSG_DIR="/tmp/claude-self-msg"

if [ -z "$1" ]; then
  echo "Error: no message provided."
  echo "Usage: self-message.sh \"Your continuation message\""
  exit 1
fi

mkdir -p "$MSG_DIR"
TMPFILE=$(mktemp "${MSG_DIR}/msg.XXXXXX")
echo "$1" > "$TMPFILE"
echo "Self-message queued."
