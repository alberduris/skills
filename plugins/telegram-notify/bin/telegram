#!/usr/bin/env bash
# telegram — send a message via Telegram Bot API
# Usage: telegram <command> [flags]
#
# Commands:
#   send <text>           Send a message
#   me                    Get bot info (verify credentials)
#
# Credentials resolve from (first match wins):
#   1. .env.local in cwd
#   2. .env in cwd
#   3. .env.local in plugin directory
#   4. .env in plugin directory
#   5. Environment variables

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# --- credential resolution (matches x-twitter pattern) ---

load_env_file() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"          # strip comments
    line="${line#"${line%%[![:space:]]*}"}"  # trim leading
    line="${line%"${line##*[![:space:]]}"}"  # trim trailing
    [[ -z "$line" || "$line" != *=* ]] && continue
    local key="${line%%=*}"
    local val="${line#*=}"
    val="${val#\"}" ; val="${val%\"}"   # strip quotes
    val="${val#\'}" ; val="${val%\'}"
    export "$key=$val" 2>/dev/null || true
  done < "$file"
}

# Priority order: cwd first, then plugin dir
load_env_file "$PWD/.env.local"
load_env_file "$PWD/.env"
load_env_file "$PLUGIN_DIR/.env.local"
load_env_file "$PLUGIN_DIR/.env"

# --- validate ---

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "Error: TELEGRAM_BOT_TOKEN not set." >&2
  echo "Set it in .env.local, .env, or as an environment variable." >&2
  exit 1
fi

if [[ -z "${TELEGRAM_CHAT_ID:-}" ]]; then
  echo "Error: TELEGRAM_CHAT_ID not set." >&2
  echo "Set it in .env.local, .env, or as an environment variable." >&2
  exit 1
fi

API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}"

# --- commands ---

cmd_send() {
  local text="$*"
  if [[ -z "$text" ]]; then
    echo "Error: no message text provided." >&2
    exit 1
  fi

  local -a data=(
    -d "chat_id=${TELEGRAM_CHAT_ID}"
    -d "text=${text}"
  )

  local response
  response=$(curl -s -X POST "${API}/sendMessage" "${data[@]}")

  local ok
  ok=$(echo "$response" | grep -o '"ok":[a-z]*' | head -1 | cut -d: -f2)

  if [[ "$ok" == "true" ]]; then
    echo "Message sent."
  else
    local desc
    desc=$(echo "$response" | grep -o '"description":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Error: ${desc:-$response}" >&2
    exit 1
  fi
}

cmd_me() {
  curl -s "${API}/getMe" | python3 -m json.tool 2>/dev/null || curl -s "${API}/getMe"
}

# --- dispatch ---

command="${1:-}"
shift 2>/dev/null || true

case "$command" in
  send)
    cmd_send "$@"
    ;;
  me)
    cmd_me
    ;;
  *)
    echo "Usage: telegram <command> [flags]" >&2
    echo "Commands: send, me" >&2
    exit 1
    ;;
esac
