---
description: Task 1 - target-state diagrams once persistence and PayEx are in (run after the ADR is written)
---
Read `submission/02-adr/ADR-001-exactly-once-payex.md` (the human's decision), `submission/SCENARIO.md`, and the as-built diagrams.

Write `submission/01-architecture/target-container.mmd` and `submission/01-architecture/target-sequence.mmd`:
- Keep every as-built element with its existing ID.
- Give every element that does not exist yet a new ID and the suffix ` (NEW)` in its label, and attach `classDef planned stroke-dasharray: 5 5` to it. Add a legend node explaining solid versus dashed.
- The sequence must show the success path and the PayEx-timeout path exactly as the ADR decides. Do not substitute a design of your own.
- Add a row to the target section of `citations.md` for each new ID, citing the ADR heading or the `submission/SCENARIO.md` fact that requires it.

Render both with the mermaid MCP to confirm they parse. If the ADR is ambiguous about any element, ask rather than guess.
