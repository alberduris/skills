# Self-Message

Give Claude Code agents the ability to send themselves continuation messages mid-session.

## What is this?

Claude Code agents have a fixed cycle: `user → agentic loop → stop`. When the agent stops, it can't reframe or redirect itself without user input.

Self-message breaks this. Claude writes a message to itself, stops naturally (`end_turn`), and a Stop hook intercepts the stop and feeds that message back as context for a new agentic loop. Same session, full context preserved, fresh reasoning frame.

This is **not** a Ralph Wiggum loop. Ralph repeats the same prompt. Self-message lets the agent write its own next prompt.

## Install

```bash
/plugin install self-message@alberduris-marketplace
```

## How it works

```
Claude working → writes self-message via script → emits end_turn
    ↓
Stop hook finds the message file → reads it → deletes it
    ↓
Hook returns {"decision": "block", "reason": "<message>"}
    ↓
Claude starts a new agentic loop with the message as context
```

The skill teaches Claude when and how to use it. The hook handles the plumbing.

## When Claude uses it

- **Reframing**: Current approach isn't working, needs to pivot
- **Phase transitions**: Finished research, needs a clean start for synthesis
- **Course correction**: Drifted from the user's actual request
- **Complex multi-step tasks**: Breaking work into deliberate phases

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `SELF_MSG_MAX_DEPTH` | 200 | Max consecutive self-messages per session (~12h autonomy) |

## Architecture

Two components, one plugin:

- **Stop hook** (`hooks/stop-hook.sh`): Intercepts `end_turn`, checks for queued messages, feeds them back via `{"decision": "block"}`
- **Skill** (`skills/self-message/SKILL.md`): Teaches Claude the mechanism, when to use it, how to write good self-messages

Session isolation via atomic `mv` — concurrent sessions can't steal each other's messages.

## License

MIT
