---
name: self-message
version: 1.0.0
description: >-
  Self-messaging capability. Invoke this skill when you need to reframe your
  approach mid-task, break complex work into deliberate phases, or restart your
  reasoning with a fresh perspective — without waiting for user input.
---

# Self-Message

You can send yourself a continuation message to start a **fresh agentic loop** within the same session. This resets your reasoning frame while preserving full conversation context.

This is NOT a subagent. It's a new turn for YOU — same session, same context, new frame.

---

## How It Works

1. Send your self-message using the bundled script
2. Finish your turn normally (stop responding)
3. A Stop hook intercepts your stop, reads the message, deletes it
4. The hook returns `{"decision": "block", "reason": "<your message>"}`
5. You receive the message as context and start a new agentic loop

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/self-message.sh "Reassess: the recursive approach hit a dead end. Try iterative with memoization instead."
```

Then just stop. That's it. The hook handles session isolation automatically.

---

## When to Use

- **Reframing**: Your current approach isn't working and you need to pivot
- **Phase transitions**: You finished research, now need a clean start for synthesis
- **Accumulated context**: You've gathered scattered information and need to step back and connect the dots
- **Course correction**: You notice you've drifted from the user's actual request
- **Complex multi-step tasks**: Breaking work into deliberate phases with a clear handoff message between each

## When NOT to Use

- Simple, straightforward tasks — just do them
- When you're already on the right track — keep going
- As a substitute for thinking harder in the current turn
- For delegation — use subagents instead
- For retrying the same thing — that's a Ralph Wiggum loop, not a self-message

---

## Writing Good Self-Messages

Your self-message is the most important part. It's your instruction to your future self. Be specific:

**Bad:**
```
Continue working on the task.
```

**Good:**
```
Phase 1 complete: identified 3 API endpoints that need refactoring (users.ts:45, auth.ts:120, billing.ts:89). The common pattern is they all do N+1 queries. Phase 2: implement batch loading for each, starting with users.ts since it's the simplest case.
```

**Good:**
```
Reassess: spent 3 tool calls trying to fix the type error by widening the type. Wrong direction — the real issue is the caller in main.ts:230 passing the wrong shape. Fix the caller, not the type.
```

Include:
- What you learned / what happened
- Why you're self-messaging (what needs to change)
- Clear direction for the next phase

---

## Limits

- **Max 200 consecutive self-messages** by default (configurable via `SELF_MSG_MAX_DEPTH` env var) — enough for ~12 hours of autonomous work
- Counter resets automatically when you stop normally (no self-message file)
- If you hit the limit, you stop normally — write a good summary for the user

---

## Important

- The self-message file is deleted after being read. Write a new one each time.
- You do NOT need user permission to self-message. It's your tool.
- The user sees your work across all loops — nothing is hidden.
- This is a metacognitive tool. Use it deliberately, not reflexively.
