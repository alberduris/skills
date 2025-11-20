---
name: second-opinion
description: Consult peer LLM for alternative perspectives when you need second opinion, peer review, or fresh take on technical decisions; useful for validating approaches or exploring alternative solutions
allowed-tools: Read, Bash
---

# Second Opinion Skill

Use this skill when you need an alternative perspective on technical decisions, architecture choices, or implementation approaches.

## Usage

Invoke the consultation script with your question and relevant context files:

```bash
source .env.local && pnpm exec tsx .claude/skills/second-opinion/scripts/consult.ts --message "your question" --files path1,path2,path3
```

**Important**:
- Must source `.env.local` to load `OPENAI_API_KEY`; use `pnpm exec tsx` to execute TypeScript
- Default timeout is 30 minutes; match this in your Bash tool timeout parameter (1800000ms)
- Do NOT run in background—synchronous execution avoids polling overhead

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
