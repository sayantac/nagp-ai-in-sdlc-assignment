# Assignment runbook (Claude Code)

The shortest path to a clean submission. Each step lists what you run, what you must do yourself (**YOU**), and what to commit. The agent does the mechanical work; you own the decisions and the verification. The logs prove which was which.

Estimated total: about 9–11 hours, most of it in Task 2 writing and Task 4 scoring.

## Every session

- **Start:** start `claude` in the repo root, on the branch for the task.
- **During:**
  - After each meaningful step, run `/ai-log-entry`. Answer its three questions in your own words.
  - When the agent is wrong, sycophantic or useless, run `/agent-wrong <what happened>` immediately. These entries become an ADR section and video material.
- **End:** run `/wrap`, then `/export` to `ai-logs/transcripts/<date>-<topic>.txt`, then commit. The `AI-Log-Id` trailer is added automatically.
- **Modes:** start each task in plan mode (Shift+Tab). Switch to default mode to let it write files.

---

## Phase 0: Setup (30 min)

1. Fork `NITIN1670/ai-in-sdlc-assignment`, clone your fork, and unzip this scaffold at the repo root.
2. Run `python3 scripts/setup_scaffold.py`. It installs the commit hook and lists anything missing.
3. Install the Mermaid MCP:
   ```
   npm install -g claude-mermaid
   claude mcp add --scope project mermaid claude-mermaid
   ```
   This uses local rendering, so no diagram content leaves your machine (see ASSUMPTIONS.md, A7). If your workshop used a different Mermaid MCP, use that instead and update A7.
4. **YOU, verify the plumbing (10 min).** The scaffold was built outside your environment, so check these before trusting it:
   - Start `claude`, approve the project hooks, send a prompt, then check that `ai-logs/raw.jsonl` gained lines. If `python3` is not on your PATH (some Windows setups), replace `python3` in `.claude/settings.json`.
   - Run `/mcp`. `mermaid` should be connected and `playwright` shown, but its tools are denied by `permissions.deny`.
   - Run `dotnet test backend/InvoiceApp.sln --filter Category=Architecture`. It should pass.
   - Run `python3 scripts/normalize_logs.py` and check that a `model` id appears for your prompt.
5. Edit the two seed entries in `ai-logs/ai-log.jsonl` and replace their `TODO(Sayantan)` fields.
6. Commit: `chore: add AI-in-SDLC scaffold`. Then create the branches `task-1-architecture`, `task-2-adr`, `task-3-autonomy`, `task-4-evals` and `task-5-risk`. Log stages are derived from the branch name.

## Task 5b first: baseline numbers (20 min; independent and quick)

1. On branch `task-5-risk`, run `/t5-baseline`.
2. **YOU:** pick the two numbers you will report. Pipeline duration and CI failure rate are measured; the lead time is a proxy, and the script warns that two branches map to the same push. Fill `measurement-plan.md`.
3. Commit.

## Task 1: Diagrams and architecture test (1.5 h)

1. Run `/t1-asbuilt`. It uses the cartographer subagent and the Mermaid MCP, then the citation check.
2. **YOU:** open about five citations at random and confirm they are right. Fix anything wrong and log it.
3. Run `/t1-unscoped`.
   - **YOU:** fill the `Correction` column in `inferred.md` section 2. This is your strongest evidence of correcting the agent, so keep it in the video.
4. Run `/t1-archtest`. It runs the test, then the red/green demo.
   - **YOU:** read the red output. Confirm the architecture test failed, not the build.
   - Push and paste the green CI link into `RUN.md`.
5. Commit. The target diagrams come after Task 2.

## Task 2: Exactly-once ADR (2–2.5 h)

1. Run `/t2-evidence`. **YOU:** spot-check three citations in `payex-evidence.md`.
2. In plan mode, run `/t2-options`.
3. Run the three stress tests as separate turns, logging each one straight after:
   - `/t2-stress-prefer <the option the agent did not recommend>`, then `/ai-log-entry`. Record whether the recommendation moved, and whether it moved for a new reason or for none.
   - `/t2-stress-3am`, then `/ai-log-entry`. Record whether the answer was specific (concurrency, multiple instances, unknown-state handling) or generic.
   - `/t2-stress-cost`, then `/ai-log-entry`. Record whether the numbers are grounded or invented.
4. **YOU:** write `ADR-001-exactly-once-payex.md` yourself. Fill "Where the agent was wrong or useless" from `ai-logs/agent-wrong.md` and the stress-test entries.
5. Run `/t2-critique`. **YOU:** add a short "Critique accepted / rejected" note to the ADR.
6. Back on the Task 1 branch (or merge first), run `/t1-target`, then `python3 scripts/verify_citations.py --target`.
7. Commit.

## Task 3: Autonomy policy (1.5 h)

Write autonomy-policy.md (one page); state the day-one level. No incident trial was run.

## Task 4: Review eval (2.5–3 h, mostly unattended runs plus scoring)

1. **YOU:** read all ten cases and fill `answer-key.csv`: expected, defect description, location, and whether the case was shown in the session. **Commit before any run.**
2. Run `/t4-newcase 11 <real defect you've seen>` and `/t4-newcase 12 clean: <correct change>`.
   - **YOU:** verify case-12 really is clean and case-11 really contains the defect. Add their key rows and commit.
3. Fill `eval-protocol.md`, including the model id. Move `~/.claude/CLAUDE.md` aside if it isn't empty.
4. From a normal terminal (not inside Claude Code), run the baseline:
   ```
   python3 scripts/run_evals.py --label baseline --context none --model <model-id>
   ```
   That is 36 calls, and it resumes if interrupted.
5. Run `python3 scripts/score_evals.py baseline`. **YOU** score each row strictly; about 20–30 seconds a row.
6. Run the changed variable with the same model:
   ```
   python3 scripts/run_evals.py --label with-agents-md --context repo --model <model-id>
   ```
   Then run `python3 scripts/score_evals.py with-agents-md`.
7. Run `python3 scripts/eval_report.py baseline with-agents-md`.
   - **YOU:** write the verdict line in `results.md`: improvement, no detectable change or regression, and your confidence.
8. Log the eval work with `/ai-log-entry`. The `EvalRun` events are already in `raw.jsonl`. Commit.

## Task 5a: Trifecta audit (45 min)

1. Run `/t5-trifecta`. It also attempts a WebFetch that should be denied.
2. **YOU:** tick Redesign or Accept, and fill the owner, date and revisit trigger. The recommended framing is "Redesign": external communication is removed for every agent that reads untrusted content, via `permissions.deny`.
3. **YOU:** state the residual risks plainly. Bash is permission-gated, not denied, and the guard hook does not cover Bash writes.
4. Send the trainer the A1 question if you haven't yet, and record the date in ASSUMPTIONS.md.
5. Commit.

## Video (1–1.5 h)

Follow `submission/video/video-script.md`. Record at 1080p, trim to 8–10 minutes, upload, and paste the link in `submission/README.md`.

## Package (20 min)

1. Run `/wrap`, export the last transcript, and commit.
2. Run `python3 scripts/precheck.py` and clear every FAIL. Each WARN should be either fixed or explained in ASSUMPTIONS.md.
3. Merge the task branches to `main`, push, and confirm CI is green.
4. Submit the fork URL and the video link.

---

## What I could not verify for you

These are the first things to check in Phase 0, step 4.

- **The .NET pieces.** The architecture test and `demo_arch_test.py` were not compiled in the environment that produced this scaffold, which had no .NET SDK.
- **Claude Code payload fields and flags.**
  - The hook payload field `permission_mode`: if your version doesn't send it, `mode` falls back to an ask/agent heuristic.
  - The `claude -p` flags used by `run_evals.py` (`--disallowedTools`, `--strict-mcp-config`, `--output-format json`): check them against `claude --help` for your version.
