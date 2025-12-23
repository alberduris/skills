#!/usr/bin/env bash
set -euo pipefail

# Langfuse Traces Query Script
# Usage: ./query.sh <command> [options]

load_credentials() {
  local env_file

  # Try .env.local first, then .env
  for env_file in ".env.local" ".env"; do
    if [[ -f "$env_file" ]]; then
      LANGFUSE_PUBLIC_KEY="${LANGFUSE_PUBLIC_KEY:-$(grep -E '^LANGFUSE_PUBLIC_KEY=' "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '"' || true)}"
      LANGFUSE_SECRET_KEY="${LANGFUSE_SECRET_KEY:-$(grep -E '^LANGFUSE_SECRET_KEY=' "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '"' || true)}"
      LANGFUSE_BASE_URL="${LANGFUSE_BASE_URL:-$(grep -E '^LANGFUSE_BASE_URL=' "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '"' || true)}"
    fi
  done

  LANGFUSE_BASE_URL="${LANGFUSE_BASE_URL:-https://cloud.langfuse.com}"

  if [[ -z "${LANGFUSE_PUBLIC_KEY:-}" || -z "${LANGFUSE_SECRET_KEY:-}" ]]; then
    echo "Error: LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY required" >&2
    echo "Set in .env.local, .env, or environment variables" >&2
    exit 1
  fi
}

api_call() {
  local endpoint="$1"
  shift
  curl -s -u "${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}" \
    "${LANGFUSE_BASE_URL}/api/public${endpoint}" "$@"
}

cmd_traces() {
  local limit="${1:-10}"
  local session_id="${2:-}"
  local name="${3:-}"

  local params="limit=${limit}"
  [[ -n "$session_id" ]] && params="${params}&sessionId=${session_id}"
  [[ -n "$name" ]] && params="${params}&name=${name}"

  api_call "/traces?${params}" | jq '.'
}

cmd_trace() {
  local trace_id="$1"
  if [[ -z "$trace_id" ]]; then
    echo "Error: trace_id required" >&2
    exit 1
  fi
  api_call "/traces/${trace_id}" | jq '.'
}

cmd_observations() {
  local limit="${1:-20}"
  local trace_id="${2:-}"
  local type="${3:-}"

  local params="limit=${limit}"
  [[ -n "$trace_id" ]] && params="${params}&traceId=${trace_id}"
  [[ -n "$type" ]] && params="${params}&type=${type}"

  api_call "/observations?${params}" | jq '.'
}

cmd_sessions() {
  local limit="${1:-10}"
  api_call "/sessions?limit=${limit}" | jq '.'
}

cmd_summary() {
  local limit="${1:-5}"
  api_call "/traces?limit=${limit}" | jq -r '
    .data[] |
    "[\(.id[:8])] \(.name // "unnamed") | \(.createdAt[:19]) | tokens: \(.usage.totalTokens // 0) | \(.metadata // {} | keys | join(","))"
  '
}

show_help() {
  cat <<EOF
Langfuse Traces Query Tool

Commands:
  traces [limit] [session_id] [name]   List traces (default: 10)
  trace <trace_id>                     Get trace detail with observations
  observations [limit] [trace_id]      List observations/spans
  sessions [limit]                     List sessions
  summary [limit]                      Compact trace summary

Examples:
  ./query.sh traces 20
  ./query.sh trace abc123
  ./query.sh observations 50 abc123
  ./query.sh summary 10

Environment:
  LANGFUSE_PUBLIC_KEY   Your Langfuse public key
  LANGFUSE_SECRET_KEY   Your Langfuse secret key
  LANGFUSE_BASE_URL     API base URL (default: https://cloud.langfuse.com)
EOF
}

main() {
  load_credentials

  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    traces)       cmd_traces "$@" ;;
    trace)        cmd_trace "$@" ;;
    observations) cmd_observations "$@" ;;
    sessions)     cmd_sessions "$@" ;;
    summary)      cmd_summary "$@" ;;
    help|--help)  show_help ;;
    *)            echo "Unknown command: $cmd" >&2; show_help; exit 1 ;;
  esac
}

main "$@"
