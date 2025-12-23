---
name: langfuse-traces
description: Query Langfuse traces for debugging LLM calls, analyzing token usage, and investigating workflow executions. Use when debugging AI/LLM behavior, checking trace data, or analyzing observability metrics.
allowed-tools: Bash, Read
---

# Langfuse Traces Skill

Query and analyze Langfuse trace data directly from Claude Code.

## Usage

Invoke the query script using the **base directory shown above**:

```bash
bash <base_directory>/scripts/query.sh <command> [options]
```

## Commands

| Command | Args | Description |
|---------|------|-------------|
| `traces` | [limit] [session_id] [name] | List recent traces |
| `trace` | trace_id | Get full trace with observations |
| `observations` | [limit] [trace_id] | List spans/generations |
| `sessions` | [limit] | List sessions |
| `summary` | [limit] | Compact one-line-per-trace view |

## Examples

```bash
# List last 20 traces
bash <base_directory>/scripts/query.sh traces 20

# Get specific trace detail
bash <base_directory>/scripts/query.sh trace tr-abc123

# List observations for a trace
bash <base_directory>/scripts/query.sh observations 50 tr-abc123

# Quick summary of recent activity
bash <base_directory>/scripts/query.sh summary 10
```

## Credentials

The script reads credentials from `.env.local`, `.env`, or environment variables:

```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com  # optional, default
```

## Requirements

- `curl` (standard on macOS/Linux)
- `jq` for JSON parsing

## Output

All commands return JSON (piped through jq). Use jq filters for specific fields:

```bash
bash <base_directory>/scripts/query.sh traces 5 | jq '.data[].name'
```
