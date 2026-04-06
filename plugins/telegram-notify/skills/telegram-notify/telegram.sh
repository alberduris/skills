#!/usr/bin/env bash
# telegram — send and schedule messages via Telegram Bot API
# Usage: telegram <command> [args]
#
# Commands:
#   send <text>                       Send a message now
#   schedule <datetime> <text>        Schedule a message for later
#   scheduled                         List pending scheduled messages
#   cancel <id>                       Cancel a scheduled message
#   me                                Get bot info (verify credentials)
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

# --- validation helpers ---

require_bot_creds() {
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
}

require_worker_creds() {
  if [[ -z "${TELEGRAM_WORKER_URL:-}" ]]; then
    echo "Error: TELEGRAM_WORKER_URL not set." >&2
    echo "" >&2
    echo "Scheduled messages require a Cloudflare Worker (free tier)." >&2
    echo "This is an optional feature — send, me, and other commands work without it." >&2
    echo "" >&2
    echo "To set up: deploy the worker in the worker/ directory, then add to .env.local:" >&2
    echo "  TELEGRAM_WORKER_URL=https://telegram-scheduler.yourname.workers.dev" >&2
    echo "  TELEGRAM_API_TOKEN=your-worker-api-token" >&2
    echo "" >&2
    echo "See README for full setup instructions." >&2
    exit 1
  fi
  if [[ -z "${TELEGRAM_API_TOKEN:-}" ]]; then
    echo "Error: TELEGRAM_API_TOKEN not set." >&2
    echo "" >&2
    echo "Scheduled messages require a Cloudflare Worker (free tier)." >&2
    echo "Set TELEGRAM_API_TOKEN to the API_TOKEN secret you configured in the worker." >&2
    echo "" >&2
    echo "See README for full setup instructions." >&2
    exit 1
  fi
}

# --- datetime parsing ---

parse_datetime() {
  python3 -c '
import sys, re
from datetime import datetime, timedelta, timezone

raw = sys.argv[1]
local_now = datetime.now().astimezone()
local_tz = local_now.tzinfo

# Relative: +30m, +2h, +1d, +2h30m, +1d2h30m
m = re.fullmatch(r"\+(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?", raw)
if m and any(m.groups()):
    d, h, mn = int(m[1] or 0), int(m[2] or 0), int(m[3] or 0)
    result = datetime.now(timezone.utc) + timedelta(days=d, hours=h, minutes=mn)
    print(result.strftime("%Y-%m-%dT%H:%M:%SZ"))
    sys.exit(0)

# today/tomorrow/hoy/mañana HH:MM
m = re.fullmatch(r"(today|tomorrow|hoy|ma[n\xf1]ana)\s+(\d{1,2}):(\d{2})", raw, re.I)
if m:
    word = m[1].lower()
    day = local_now if word in ("today", "hoy") else local_now + timedelta(days=1)
    result = day.replace(hour=int(m[2]), minute=int(m[3]), second=0, microsecond=0)
    print(result.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    sys.exit(0)

# Just HH:MM (today if in the future, otherwise tomorrow)
m = re.fullmatch(r"(\d{1,2}):(\d{2})", raw)
if m:
    result = local_now.replace(hour=int(m[1]), minute=int(m[2]), second=0, microsecond=0)
    if result <= local_now:
        result += timedelta(days=1)
    print(result.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    sys.exit(0)

# ISO and common date+time formats
for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
    try:
        dt = datetime.strptime(raw, fmt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        print(dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        sys.exit(0)
    except ValueError:
        continue

print("Error: could not parse datetime \"%s\"" % raw, file=sys.stderr)
print("", file=sys.stderr)
print("Accepted formats:", file=sys.stderr)
print("  +30m, +2h, +1d, +2h30m    relative from now", file=sys.stderr)
print("  15:00                      today at time (local tz)", file=sys.stderr)
print("  tomorrow 09:00             natural (local tz)", file=sys.stderr)
print("  2026-04-07 09:00           date + time (local tz)", file=sys.stderr)
print("  2026-04-07T09:00:00Z       ISO 8601 (UTC)", file=sys.stderr)
print("", file=sys.stderr)
print("Examples:", file=sys.stderr)
print("  telegram schedule +30m Check the deploy", file=sys.stderr)
print("  telegram schedule \"tomorrow 09:00\" Morning standup", file=sys.stderr)
print("  telegram schedule \"2026-04-07 15:00\" Call with the team", file=sys.stderr)
sys.exit(1)
' "$1"
}

# --- commands ---

cmd_send() {
  require_bot_creds
  local text="$*"
  if [[ -z "$text" ]]; then
    echo "Error: no message text provided." >&2
    exit 1
  fi

  local response
  response=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${text}")

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

cmd_schedule() {
  require_worker_creds
  local datetime="${1:-}"
  shift 2>/dev/null || true
  local text="$*"

  if [[ -z "$datetime" || -z "$text" ]]; then
    echo "Error: usage: telegram schedule <datetime> <text>" >&2
    echo "" >&2
    echo "Datetime formats:" >&2
    echo "  +30m, +2h, +1d, +2h30m    relative from now" >&2
    echo "  15:00                      today at time (local tz)" >&2
    echo "  tomorrow 09:00             natural (local tz)" >&2
    echo "  2026-04-07 09:00           date + time (local tz)" >&2
    echo "  2026-04-07T09:00:00Z       ISO 8601 (UTC)" >&2
    exit 1
  fi

  local send_at
  send_at=$(parse_datetime "$datetime") || exit 1

  local payload
  payload=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1], 'send_at': sys.argv[2]}))" "$text" "$send_at")

  local response
  response=$(curl -s -X POST "${TELEGRAM_WORKER_URL%/}/schedule" \
    -H "Authorization: Bearer ${TELEGRAM_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$payload")

  python3 -c '
import json, sys
from datetime import datetime, timezone

try:
    r = json.loads(sys.argv[1])
except:
    print("Error: unexpected response from worker: %s" % sys.argv[1], file=sys.stderr)
    sys.exit(1)

if r.get("ok"):
    try:
        utc = datetime.strptime(r["send_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        local_str = utc.astimezone().strftime("%Y-%m-%d %H:%M %Z")
    except:
        local_str = r.get("send_at", "unknown")
    print("Scheduled (id: %s)" % r["id"])
    print("  Text: %s" % r["text"])
    print("  Send at: %s (%s)" % (local_str, r["send_at"]))
else:
    print("Error: %s" % json.dumps(r), file=sys.stderr)
    sys.exit(1)
' "$response"
}

cmd_scheduled() {
  require_worker_creds
  local response
  response=$(curl -s -X GET "${TELEGRAM_WORKER_URL%/}/list" \
    -H "Authorization: Bearer ${TELEGRAM_API_TOKEN}")

  python3 -c '
import json, sys
from datetime import datetime, timezone

try:
    data = json.loads(sys.argv[1])
except:
    print("Error: unexpected response from worker: %s" % sys.argv[1], file=sys.stderr)
    sys.exit(1)

pending = data.get("pending", [])

if not pending:
    print("No scheduled messages.")
    sys.exit(0)

print("%d scheduled message(s):\n" % len(pending))
for item in pending:
    try:
        utc = datetime.strptime(item["send_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        local_str = utc.astimezone().strftime("%Y-%m-%d %H:%M %Z")
    except:
        local_str = item.get("send_at", "unknown")
    print("  [%s] %s — %s" % (item.get("id", "?")[:8], local_str, item.get("text", "")))
' "$response"
}

cmd_cancel() {
  require_worker_creds
  local id="${1:-}"
  if [[ -z "$id" ]]; then
    echo "Error: usage: telegram cancel <id>" >&2
    echo "Run 'telegram scheduled' to see pending message IDs." >&2
    exit 1
  fi

  local response
  response=$(curl -s -X DELETE "${TELEGRAM_WORKER_URL%/}/cancel/${id}" \
    -H "Authorization: Bearer ${TELEGRAM_API_TOKEN}")

  python3 -c '
import json, sys
try:
    r = json.loads(sys.argv[1])
except:
    print("Error: unexpected response from worker: %s" % sys.argv[1], file=sys.stderr)
    sys.exit(1)

if r.get("ok"):
    print("Cancelled: %s" % r.get("deleted", sys.argv[2]))
else:
    print("Error: %s" % json.dumps(r), file=sys.stderr)
    sys.exit(1)
' "$response" "$id"
}

cmd_me() {
  require_bot_creds
  curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | python3 -m json.tool 2>/dev/null || curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
}

# --- dispatch ---

command="${1:-}"
shift 2>/dev/null || true

case "$command" in
  send)
    cmd_send "$@"
    ;;
  schedule)
    cmd_schedule "$@"
    ;;
  scheduled|list)
    cmd_scheduled
    ;;
  cancel)
    cmd_cancel "$@"
    ;;
  me)
    cmd_me
    ;;
  *)
    echo "Usage: telegram <command> [args]" >&2
    echo "" >&2
    echo "Commands:" >&2
    echo "  send <text>                Send a message now" >&2
    echo "  schedule <datetime> <text> Schedule a message for later" >&2
    echo "  scheduled                  List pending scheduled messages" >&2
    echo "  cancel <id>                Cancel a scheduled message" >&2
    echo "  me                         Get bot info" >&2
    exit 1
    ;;
esac
