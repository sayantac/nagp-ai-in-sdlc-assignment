---
description: Task 5a - draft the lethal-trifecta audit from the actual agent configuration
---
Audit the agent setup used for this assignment against the lethal trifecta: access to private data, exposure to untrusted content, and the ability to communicate externally.

Evidence to read: `.claude/settings.json`, `.mcp.json`, every file in `.claude/agents/`, `.claude/hooks/`, `AGENTS.md`, and the MCP servers you have available in this session.

1. Fill sections 1 and 2 of `submission/05-risk/trifecta-audit.md`. For each leg, say whether it is present, through which tool, file or MCP server (cite file and line), and which subagent can reach it.
2. Demonstrate the deny rule: attempt a WebFetch of https://example.com and record the exact result in section 3.
3. Leave the Decision section for the human.
