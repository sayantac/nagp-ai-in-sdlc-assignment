# Lethal trifecta audit: the agent setup used for this submission

Scope: see ASSUMPTIONS.md, A1.

## 1. Legs present

| Leg | Present? | Through (tool / MCP / file, with line) | Notes |
|---|---|---|---|
| Access to private data | | | |
| Exposure to untrusted content | | | |
| Ability to communicate externally | | | |

## 2. Which agent can reach which leg

| Agent | Private data | Untrusted content | External communication | All three? |
|---|---|---|---|---|
| main session | | | | |
| codebase-cartographer | | | | |
| evidence-analyst | | | | |
| incident-first-responder | | | | |
| devils-advocate | | | | |
| eval harness (`claude -p`) | | | | |

## 3. Control demonstrated
<!-- The attempted WebFetch and its exact denial, plus any GuardBlock events from ai-logs/raw.jsonl. -->

## 4. Decision
- [ ] **Redesign**: the leg removed, and how (config file and line)
- [ ] **Accept**: the risk accepted, in writing

Owner: TODO · Date: TODO · Revisit when: TODO (a concrete trigger, e.g. "any MCP server with network egress is added", "the agent is given write access to the incident channel")

## 5. Residual risk
<!-- e.g. Bash is gated by a permission prompt, not denied; `git push` asks rather than denies. -->
