# Where the agent was wrong, sycophantic or useless

Appended with `/agent-wrong <what happened>`. One entry per incident. Each entry is used as evidence in the ADR and in the video.

## 2026-10-30T11:36:22Z · task-1-architecture
- What the agent said or did: First citation pass had five wrong line numbers; only caught after I had the verifier tightened to check ±3 lines. Fixed by re-reading the source.
- How it was caught: Only caught after I had the verifier tightened to check ±3 lines.
- Correction applied: Fixed by re-reading the source.
- Related log ids: 20261030T112559Z-56449d0c-p11, 20261030T113429Z-56449d0c-p12, 20261030T113618Z-56449d0c-p13

## 2026-10-30T11:42:56Z · task-1-architecture
- What the agent said or did: Unscoped run drew ApprovalService -> DiscountCalculator from AGENTS.md wording; no such call exists in the code. Caught by comparing against citations.md.
- How it was caught: Caught by comparing against citations.md.
- Correction applied: pending
- Related log ids: 20261030T113741Z-56449d0c-p15, 20261030T114012Z-56449d0c-p16, 20261030T114252Z-56449d0c-p17
