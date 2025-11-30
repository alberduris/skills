---
name: second-opinion
description: Consult peer LLM for alternative perspectives when you need second opinion, peer review, or fresh take on technical decisions; useful for validating approaches or exploring alternative solutions
allowed-tools: Read, Bash
---

# Second Opinion Skill

Use this skill when you need an alternative perspective on technical decisions, architecture choices, or implementation approaches.

## Usage

Invoke the consultation script using the **base directory shown above** when this skill loads:

```bash
npx tsx <base_directory>/scripts/consult.ts --message "your question" --files path1,path2,path3
```

**Important**:
- Replace `<base_directory>` with the actual "Base directory for this skill" path shown above
- The script will look for `OPENAI_API_KEY` in this order: `.env.local`, `.env`, system environment variable
- Default timeout is 30 minutes; match this in your Bash tool timeout parameter (1800000ms)
- Do NOT run in background—synchronous execution avoids polling overhead

**Note on GPT-5 models**: GPT-5 was released on August 7, 2025. Available variants: `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro` (thinking model). Default is `gpt-5-pro-2025-10-06`. Override via `SECOND_OPINION_MODEL` env var.

## Context Responsibility

**Critical**: You must pass ALL relevant context. The peer consultant has no access to this codebase, conversation history, or project context beyond what you provide.

Include:
- Complete problem description
- Relevant code files (via --files)
- Constraints, requirements, decisions made
- Specific questions or areas for review

## Interpretation Authority

**You retain final judgment**. The peer consultant provides alternative viewpoints, but you must:
- Evaluate responses against conversation context
- Reject/question suggestions that conflict with established requirements
- Apply your understanding of the full project context
- Make final decisions based on complete information

The peer opinion is input, not directive.
