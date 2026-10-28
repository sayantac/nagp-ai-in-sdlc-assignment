---
description: Record a moment where the agent was wrong, sycophantic or useless (argument = what happened)
argument-hint: <what the agent got wrong and how you caught it>
---
Append one entry to `ai-logs/agent-wrong.md` in exactly this format, and change nothing else:

```
## <UTC timestamp> · <current git branch>
- What the agent said or did: <from the human's description: $ARGUMENTS>
- How it was caught: <from the human's description>
- Correction applied: <from the human's description, or "pending">
- Related log ids: <output of `python3 scripts/normalize_logs.py --latest 3`>
```

Use the human's words. Do not soften them or add your own interpretation.
