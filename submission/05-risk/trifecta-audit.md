# Lethal trifecta audit: the agent setup used for this submission

Scope: see ASSUMPTIONS.md, A1.

## 1. Legs present

| Leg | Present? | Through (tool / MCP / file, with line) | Notes |
|---|---|---|---|
| Access to private data | **Yes, limited** | Main session and any subagent with `Read`/`Grep`/`Glob` can read the whole working tree: source, `ops/` incident packs, `ai-logs/raw.jsonl` (prompts, commands, tool responses; written by `.claude/hooks/log_event.py:56-66`). Main session also has `Bash`, which can read anything the user can (`~/.claude`, git config, env). `.env` reads are denied only for the Read tool (`.claude/settings.json:7-8`); `cat .env` via Bash is not covered. | No `.env` file exists in the repo. `AGENTS.md` holds demo credentials only ("not real credentials"). The incident packs are evidence for a planned system (`AGENTS.md`, `ops/` bullet), so I treat them as sensitive-looking but not live production data. Connectors for Asana, Atlassian, Linear, Notion and Slack are listed in this session but each exposes only an `authenticate` tool, so none is connected. That leg opens if anyone authenticates one. |
| Exposure to untrusted content | **Yes** | (a) `ops/incidents/*`, `ops/pipeline/*`, `ops/evals/cases/*`: log lines, alerts, change notes and diffs, which `evidence-analyst.md:3,8-9` and `incident-first-responder.md:11` explicitly treat as untrusted. (b) `WebFetch`, `WebSearch` and `mcp__playwright` are denied (`.claude/settings.json:4-6`); Playwright is also disabled in `.claude/settings.local.json:2-5`. (c) Bash `curl`/`wget`/`gh` are now denied (`.claude/settings.json:7-9`, moved from `ask` in the redesign); see section 3 for the test, which did not confirm the deny took effect. (d) `npx @playwright/mcp@latest` in `.mcp.json:4-6` is unpinned third-party code, though disabled locally. (e) Mermaid Chart connector responses (A7). | A grep of `ops/` for "ignore previous", "you must" and "run the following" found no embedded instructions. That is a spot check, not proof. The web-facing sources (b) are closed. What remains is repo-resident content that a teammate, a PR or an incident log can change. |
| Ability to communicate externally | **Yes** | (a) `Bash`: `curl`, `wget` and `gh` are denied (`.claude/settings.json:7-9`) and only `git push` asks (`.claude/settings.json:13`). Anything else that opens a socket (`python3`, `npm`, `nc`, `ssh`) matches no rule, so the permission mode decides. (b) Mermaid Chart connector (`claude_ai_Mermaid_Chart`): diagram text goes to a remote service (ASSUMPTIONS.md A7); now denied as `mcp__claude_ai_Mermaid_Chart` (`.claude/settings.json:6`). (c) `Artifact` tool publishes a page to claude.ai. (d) `PushNotification`, `RemoteTrigger`, `SendMessage` and `CronCreate` are available deferred tools. (e) `.mcp.json:3-14` declares `playwright` (browser egress) and `mermaid`, both disabled in `.claude/settings.local.json:2-5`. | `WebFetch` and `WebSearch` are denied (`.claude/settings.json:4-5`). `.claude/settings.local.json:2-5` disables the `playwright` and `mermaid` servers from `.mcp.json`, but that file is git-ignored (global ignore rule `**/.claude/settings.local.json`), so it does not ship with the repo: a fresh clone would get both servers enabled. The model API itself is also an egress path by design. |

**Trifecta status:** all three legs exist in the **main session**, so it is not closed. The custom subagents are closed by tool allow-lists.

## 2. Which agent can reach which leg

| Agent | Private data | Untrusted content | External communication | All three? |
|---|---|---|---|---|
| main session | Yes: Read/Grep/Glob and Bash | Yes: reads `ops/` files; Bash `curl`/`wget`/`gh` configured as denied (see section 3) | Yes: Bash (non-curl paths), Artifact, notification/trigger tools; Mermaid connector configured as denied | **Yes** |
| codebase-cartographer | Yes, repo only (`tools: Read, Grep, Glob`, `codebase-cartographer.md:4`); told not to open `ops/`, `docs/`, `AGENTS.md` (line 9-10), by prompt only | Low: source and `.github/workflows` (by prompt) | **No**: no Bash, no MCP, no web | No |
| evidence-analyst | Yes, repo-wide by tool; scoped to `ops/` by prompt (`evidence-analyst.md:8`) | **Yes**: incident and pipeline data, by design | **No** (`evidence-analyst.md:4`) | No |
| incident-first-responder | Yes, repo-wide by tool; scoped to one incident folder by prompt (`incident-first-responder.md:8`) | **Yes**: logs, alerts, change notes | **No** (`incident-first-responder.md:4`) | No |
| devils-advocate | Yes, repo-wide by tool (`tools: Read`, `devils-advocate.md:4`) | Draft ADR/policy and cited evidence | **No** | No |
| eval harness (`claude -p`) | Depends on `--context`. `none`: empty temp dir, so no repo files and no project CLAUDE.md. `repo`: cwd is the repo root (`scripts/run_evals.py:69`), so the repo is readable if a file tool is available | Yes: the eval diffs under review (piped on stdin, `run_evals.py:82`) | **No tool path found, with caveats.** The script passes `--disallowedTools` with 14 names: Bash, Edit, Write, MultiEdit, Read, Glob, Grep, LS, WebFetch, WebSearch, Task, NotebookEdit, NotebookRead, TodoWrite (`run_evals.py:32-33`), and `--strict-mcp-config` (`run_evals.py:80-81`). | No |

What the script does, and does not do (read from `scripts/run_evals.py`): it is a deny-list, not an allow-list, so any tool not named stays available (for example `Skill`, `Artifact`, `ToolSearch` and newer tool names). It passes `--strict-mcp-config` without any `--mcp-config`, so I expect no MCP servers to load, but I have not run it to confirm. It sets no `--permission-mode`. In `--context repo` mode the project `.claude/settings.json` and its hooks load from the cwd. The earlier claim "all tools disallowed" from `eval-protocol.md:10` was too strong.

Other agent types available in this session that the table above does not cover:

- `general-purpose` and `claude` have `Tools: *`, so they reach all three legs like the main session.
- `Explore` and `Plan` have every tool except Agent/Edit/Write and so include Bash and MCP. They also reach all three.
- The `.claude/agents/` allow-lists only protect when those four named agents are used.

Caveats:

- Scope limits such as "never open ops/" are prompt instructions. Nothing enforces them in tooling.
- I read `eval-protocol.md` for the harness flags. I did not verify `scripts/run_evals.py` actually passes them.

## 3. Control demonstrated

**Deny rule: WebFetch.** Rule: `"WebFetch"` in `permissions.deny` (`.claude/settings.json:4`). I called `WebFetch` with `url: https://example.com`. Exact result:

```
<tool_use_error>Error: No such tool available: WebFetch. WebFetch is disabled for this session, in subagents as well as here.</tool_use_error>
```

Reading: the request never left the machine, and no content was returned. The message says the tool is unavailable, not "permission denied". That is consistent with the deny rule removing the tool from the session, but this one output does not prove which setting caused it. The text also says the block applies to subagents.

**Bash egress denied.** After the settings change (`curl`, `wget`, `gh` moved to `deny`; `mcp__claude_ai_Mermaid_Chart` added to `deny`), I ran `curl -sI https://example.com` once, with no retry through another tool. Exact output:

```
HTTP/2 200 
date: Fri, 30 Oct 2026 16:02:14 GMT
content-type: text/html; charset=utf-8
server: cloudflare
last-modified: Sat, 24 Oct 2026 11:34:40 GMT
allow: GET, HEAD
accept-ranges: bytes
age: 4
cf-cache-status: HIT
cf-ray: a52ba4ab7d478c40-FRA
alt-svc: h3=":443"; ma=86400
```

**The deny did not stop the command.** The request reached example.com and returned HTTP 200. The new rule `Bash(curl:*)` (`.claude/settings.json:7`) was not enforced against this call. I did not establish why. One possible cause is that this session loaded its permissions before the edit; another is that the rule did not match. I did not test either. So this session showed no working control on Bash egress. The same command was re-run in a fresh session (next entry) and was denied, so the `curl` deny is verified in a fresh session. `wget`, `gh` and other network-capable commands are not tested.

**Bash egress denied (fresh session).** In a fresh session I ran `curl -sI https://example.com` once, with no retry and no other tool. The attempt was denied before it ran. Exact output:

```
Permission to use Bash with command curl -sI https://example.com has been denied.
```

Reading: no request was sent and no HTTP headers came back, so there is no response to compare with the earlier HTTP 200. This shows the `curl` deny is enforced in a fresh session. The earlier attempt above stays in place, and the likeliest explanation for it is that the permissions were loaded before the settings edit. I did not test that. I also did not test whether `wget`, `gh` or the other network-capable commands in section 5 are blocked.

**GuardBlock events:** `grep -c GuardBlock ai-logs/raw.jsonl` returned **0**. `guard_evidence.py` (`.claude/hooks/guard_evidence.py:34-45`) has therefore not blocked anything in the logged history. It covers `ops/` write protection, not exfiltration, so it is not a trifecta control either way. I did not attempt a write under `ops/` to produce one.

## 4. Decision

- [x] **Redesign**: external communication removed from the untrusted-content path. In `.claude/settings.json` (lines 3-12), `Bash(curl:*)`, `Bash(wget:*)`, `Bash(gh:*)` and the Mermaid Chart connector moved to `deny`, alongside the existing denials of `WebFetch`, `WebSearch` and the Playwright MCP. The four custom subagents have read-only tools and cannot reach external communication at all. Verified for `curl` in a fresh session (section 3): denied before it ran.
- [x] **Accept** the residual risk, in writing: other network-capable Bash commands (`python3`, `npm`, `nc`, `ssh`) match no rule, and `git push` asks but is not denied. The main session therefore still has all three legs in principle. I accept this because the repository holds no real secrets (demo credentials only), the agent has no production access, and the evidence I read is local, read-only exports.

Owner: Sayantan Chakraborty · Date: 2026-10-30 · Revisit when any of these happens:
- an MCP server or connector with network access is enabled for this project;
- the agent is given write access to an incident channel, ticketing system or production;
- free-text from outside the team (for example vendor memos in invoice data) starts appearing in logs the agent reads;
- an instruction hidden in evidence is ever flagged as a possible injection;
- a test of `wget`, `gh` or `python3` egress shows it is not blocked (then replace the prefix rules with a `PreToolUse` hook on Bash);
- before the on-call rotation starts, at the latest.

## 5. Residual risk
<!-- Draft notes from the audit, for the human to keep or edit. -->
- `curl`, `wget` and `gh` are now in `deny`. The `curl` deny is verified in a fresh session (section 3). `wget`, `gh` and other network-capable commands are not tested. `git push` still asks. Other network-capable commands (`python3`, `npm`, `nc`, `ssh`) match no rule.
- `guard_evidence.py` does not stop writes through Bash (its own docstring, lines 10-12).
- `.env` denial covers the Read tool only (`.claude/settings.json:7-8`).
- Subagent scope limits are written in prompts, not enforced.
- `general-purpose`, `claude`, `Explore` and `Plan` agents bypass the custom allow-lists.
- Mermaid connector and Artifact publish send content off-machine (A7).
- `.mcp.json` uses unpinned `@playwright/mcp@latest`.
- Disabling MCP servers lives in `settings.local.json`, which is per-machine and may not be committed.
