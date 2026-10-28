---
description: Task 1 - as-built container + approval-path sequence diagrams with citations (source code only)
---
Use the codebase-cartographer subagent to map the system as it is built today.

Then, from its output, write:
1. `submission/01-architecture/as-built-container.mmd`: a Mermaid `flowchart` container/component view. Node IDs are the `C#` / `A#` IDs. Every edge label starts with its `E#` ID, for example `C1 -->|E1: calls| C2`.
2. `submission/01-architecture/as-built-sequence.mmd`: a Mermaid `sequenceDiagram` of the approval path. Participants use their `C#` / `A#` IDs as aliases. Every message starts with its `S#` ID.
3. `submission/01-architecture/citations.md`: fill the table that is already there, one row per ID used in either diagram.
4. Put everything the subagent listed as UNVERIFIED into section 1 of `submission/01-architecture/inferred.md`.

Render both diagrams with the mermaid MCP to confirm they parse, fixing syntax until they do. Then run `python3 scripts/verify_citations.py` and fix every failure it reports. Do not draw anything that is not cited. Do not read anything under `ops/` or `docs/`.

Finish with a list of anything you were unsure about, so the human can check it.
