---
name: slack-reminders
description: Schedule Slack reminders. Use when the user asks to schedule, remind, or send a Slack message at a specific time.
allowed-tools: Bash(bash *)
---

[!EXECUTE]: Run the script with MESSAGE and DATETIME. The script lives at `scripts/schedule-reminder.sh` relative to this skill's directory.

```bash
./scripts/schedule-reminder.sh "<message>" "<datetime>"
```

[!DATETIME-FORMATS]: The script accepts these formats: ISO `2026-01-17 10:00`, relative `+1h` `+30m` `+2d`, natural `tomorrow 09:00` `friday 14:30`. Always prefer ISO for precision.

[!OUTPUT]: On success the script prints the scheduled message ID and post_at timestamp. On failure it prints the error from Slack API. Report success or failure to the user accordingly.
