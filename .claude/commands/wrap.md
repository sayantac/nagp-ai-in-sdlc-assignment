---
description: End-of-session housekeeping - regenerate logs and summary, check status
---
1. Run `python3 scripts/normalize_logs.py` and show its one-line report.
2. Run `git status --short`.
3. Remind the human to run `/export` and save the transcript as `ai-logs/transcripts/<date>-<topic>.txt`, and to run `/ai-log-entry` for any step that does not have a curated entry yet. The normaliser output lists the uncovered prompts.
