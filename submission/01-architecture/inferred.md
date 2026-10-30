# Inferred items and corrections

## 1. Inferred during the scoped as-built run (no citation found)

| # | What the agent suspected | Why | Verdict (human) | Correction |
|---|---|---|---|---|
| 1 | Tests, e2e and CI exist (xUnit with FakeInvoiceRepository, Playwright page objects) | Subagent did not open backend/tests, e2e/ or .github/workflows; matches naming conventions only | Confirmed | Exist: `backend/tests/InvoiceApp.Tests/ApprovalServiceTests.cs`, `FakeInvoiceRepository.cs`; `e2e/` (Playwright config, pages, tests); `.github/workflows/ci.yml`. Out of scope for the runtime diagrams, so not drawn. |
| 2 | Demo user roles and passwords | Seen only in grep output (appsettings.json:9, UserSession.cs:12), full content not read | Confirmed | `appsettings.json:9-12` defines two users: `demo.approver` (Approver) and `demo.admin` (Admin), bound to `DemoUsersOptions` (`UserSession.cs`). Only two roles exist. |
| 3 | Invoice defaults, InvoiceStatus values and DiscountCalculator use | Files not read; DiscountCalculator not referenced in the traced approval path | Confirmed | `Invoice.cs`: `Status = Draft`, `CreatedAt = UtcNow`. `InvoiceStatus`: Draft, PendingApproval, Approved, Rejected. `DiscountCalculator` is referenced nowhere in the app or tests: unused code, correctly not drawn. |
| 4 | Sessions never expire | SessionStore has no TTL code in the files read; absence not confirmed across the project | Confirmed | `SessionStore.cs` is an in-memory `ConcurrentDictionary` with no expiry; sessions are removed only on logout (`AuthController.cs:44`) and lost on restart. |
| 5 | Further access rules on GET, create and submit beyond sign-in | Only Delete carries [RequireRole] in InvoicesController.cs:73; other rules not confirmed | Confirmed | GET, create and submit need only a session (`SessionAuthMiddleware`). Role checks: Delete is Admin-only (`InvoicesController.cs:73`); approve and reject are Approver or Admin (`ApprovalsController.cs:9`). Any signed-in user can create and submit. |
| 6 | No database, message topic or payment provider in code | None found in the files read; InvoiceApp.Api.csproj not read, so an unused package reference is not ruled out | Confirmed | `InvoiceApp.Api.csproj` has only a `ProjectReference` to Domain: no packages, so no database, messaging or HTTP client. |

## 2. Present in the unscoped run, absent from the code

These items come from the agent reading planning documents (`ops/`, `docs/`, READMEs) as if they described the running system.

| # | Element or claim | Came from | Correction (human) |
|---|---|---|---|
| 1 | Load balancer in front of three instances (web-01, web-02, web-03), and the user-to-load-balancer connection | `ops/incidents/INC-2041/README.md` line 32; `ops/incidents/INC-2041/app-logs.txt` (`instance=web-0N`) | DEPLOYMENT: Operational or deployment detail from ops/, not in the code. Out of scope for the as-built view. |
| 2 | Relational database, and the repository-to-database connection | `ops/README.md` lines 15-19 ("a database") | PLANNED: Not built. Planned in `ops/README.md`. Appears in the target diagram only if ADR-001 requires it. |
| 3 | PayEx payment provider (external, HTTPS), `PayExClient`, and the approval-to-PayEx submission | `ops/incidents/INC-2041/README.md` lines 30-31; `ops/incidents/INC-2041/deploy-diff.patch` (`src/InvoiceApp.Api/Clients/PayExClient.cs`, `SubmitAsync`); `ops/incidents/INC-2047/recent-changes.md` (PayEx API key rotation) | PLANNED: Not built. Planned in `ops/incidents/INC-2041/deploy-diff.patch`. Appears in the target diagram only if ADR-001 requires it. |
| 4 | `EventPublisher` component and the approval-to-publisher connection (`InvoiceApproved` events) | `ops/incidents/INC-2047/publisher-logs.txt` | PLANNED: Not built. Planned in `ops/incidents/INC-2047/publisher-logs.txt`. Appears in the target diagram only if ADR-001 requires it. |
| 5 | Service Bus topic `invoice-events` (namespace `sb-invoice-prod`) and the publisher-to-topic connection | `ops/incidents/INC-2047/servicebus-status.txt`; `ops/incidents/INC-2047/worker-logs.txt` line 6 | PLANNED: Not built. Planned in `ops/incidents/INC-2047/servicebus-status.txt`. Appears in the target diagram only if ADR-001 requires it. |
| 6 | Topic subscriptions `notification-worker`, `analytics-export` and `audit-archive` | `ops/incidents/INC-2047/servicebus-status.txt` | PLANNED: Not built. Planned in `ops/incidents/INC-2047/servicebus-status.txt`. Appears in the target diagram only if ADR-001 requires it. |
| 7 | `notification-worker` process and its topic-to-worker connection | `ops/incidents/INC-2047/worker-logs.txt`; `ops/incidents/INC-2047/alert.md` | PLANNED: Not built. Planned in `ops/incidents/INC-2047/worker-logs.txt`. Appears in the target diagram only if ADR-001 requires it. |
| 8 | Email notifications to suppliers | `ops/incidents/INC-2047/worker-logs.txt` (`channel=email`); `ops/incidents/INC-2047/alert.md` lines 16-18 | PLANNED: Not built. Planned in `ops/incidents/INC-2047/worker-logs.txt`. Appears in the target diagram only if ADR-001 requires it. |
| 9 | Central audit archive and the nightly audit export, with connections from the audit-archive subscription and the export | `ops/incidents/INC-2047/recent-changes.md` lines 15-19 | PLANNED: Not built. Planned in `ops/incidents/INC-2047/recent-changes.md`. Appears in the target diagram only if ADR-001 requires it. |
| 10 | Persisted approval audit trail | `ops/incidents/INC-2047/alert.md` line 23 ("the approval audit trail is complete"). The code only has `DecidedBy` and `DecidedAt` on the invoice, which are cited. | PLANNED: Not built. The code keeps only the last decision on the invoice (DecidedBy, DecidedAt, DecisionNote) and overwrites it; there is no history. The 'complete' audit trail in ops/incidents/INC-2047/alert.md describes the planned deployment. Needed for the 7-year SOC 2 requirement (source: submission/SCENARIO.md, Compliance row), so ADR-001 and the target diagram must cover it. |
| 11 | Alerting rules and 24x7 on-call rotation watching the service | `ops/incidents/INC-2041/alert.md`; `ops/incidents/INC-2047/alert.md`; `ops/README.md` lines 17-18 | DEPLOYMENT: Operational or deployment detail from ops/, not in the code. Out of scope for the as-built view. |
| 12 | `/health` endpoint on the application | `ops/pipeline/ci-pipeline.yml` (`npx wait-on http://localhost:5000/health`). No match for "health" under `backend/src`. | PLANNED: Not built. Planned in `ops/pipeline/ci-pipeline.yml`. Appears in the target diagram only if ADR-001 requires it. |
| 13 | Container image built by CI and deployed as the service (a Dockerfile) | `ops/pipeline/ci-pipeline.yml` (`docker build`, `trivy image`). There is no Dockerfile in the repository. | PLANNED: Not built. Planned in `ops/pipeline/ci-pipeline.yml`. Appears in the target diagram only if ADR-001 requires it. |
| 14 | CI pipeline with security scans, CodeQL, licence check and end-to-end stage | `ops/pipeline/ci-pipeline.yml`. The repository's own `.github/workflows/ci.yml` only builds and tests. | CI: The repo has build-and-test CI only (.github/workflows/ci.yml). The deploy pipeline in ops/pipeline/ci-pipeline.yml is not in this repo. |
| 15 | Bulk approval, with batch summary and audit trail | `docs/use-cases/UC-1-bulk-approval.md` | NOT IMPLEMENTED: Use case in docs/use-cases; no implementation in backend/src. |
| 16 | Second approver for invoices over $1,000 | `docs/use-cases/UC-1-bulk-approval.md` line 19 | NOT IMPLEMENTED: Use case in docs/use-cases; no implementation in backend/src. |
| 17 | Partial approval, with invoiced and approved amounts | `docs/use-cases/UC-2-partial-approval.md` | NOT IMPLEMENTED: Use case in docs/use-cases; no implementation in backend/src. |
| 18 | In-app notifications | `docs/use-cases/UC-1-bulk-approval.md` lines 21-23 | NOT IMPLEMENTED: No notification code in backend/src; UC-1 lists notifications as out of scope. The topic and notification-worker in ops/ are planned (see the PLANNED rows). |
| 19 | `DiscountCalculator` and its connection to `ApprovalService`. The class exists but is not on the approval path and nothing calls it from `ApprovalService`. | `backend/src/InvoiceApp.Domain/DiscountCalculator.cs`; the "Domain" description in `AGENTS.md` | EXISTS, UNUSED: DiscountCalculator exists but nothing calls it. The ApprovalService -> DiscountCalculator edge was invented from AGENTS.md wording. |
| 20 | xUnit tests (`FakeInvoiceRepository`, `DomainLayerArchitectureTests`) and Playwright end-to-end tests, as a node feeding CI. They exist in the repository but have no citation row. | `backend/tests/InvoiceApp.Tests/`; `e2e/`; `AGENTS.md`; `.github/workflows/ci.yml` | EXISTS, OUT OF SCOPE: Exists; tests are not runtime elements. |

## 3. Other corrections made to agent output

| # | What was wrong | How it was caught | Log id |
|---|---|---|---|
| 1 | The first citation pass had five wrong line numbers (rows C3, C5, S12, S16 and S18 in the current numbering; S10, S14 and S15 when found). The whole-file symbol check let them through. | The verifier was tightened to check the symbol within ±3 lines of the cited line, then the source was re-read. | agent-wrong 2026-10-30T11:36:22Z |
| 2 | The unscoped run drew an `ApprovalService -> DiscountCalculator` edge from AGENTS.md wording. No such call exists in the code. | Compared against `citations.md`. | agent-wrong 2026-10-30T11:42:56Z |

## 4. Observations about the as-built code (not drawn)

These are read from the code by the cartographer subagent, and I re-read the cited lines. They are behaviours, not elements or edges, so they are not in the diagrams or `citations.md`.

| # | Observation | File and line |
|---|---|---|
| 1 | Nothing stops the approver being the submitter. `ApprovalService.Approve(invoiceId, approver)` only checks that the invoice is pending, then records the approver's name. `Submit` takes no user at all, and `Invoice` has no field for who submitted it, so there is nothing to compare against. | `backend/src/InvoiceApp.Domain/ApprovalService.cs:16` (`Submit`), `:31-41` (`Approve`); `backend/src/InvoiceApp.Domain/Invoice.cs:5-12` (no submitter field) |
| 2 | The repository mutates the object it hands out. `GetById` returns the stored `Invoice` instance, `ApprovalService` changes its fields in place, and `Update` then writes the same instance back. The status change is visible to anyone holding the reference before `Update` runs, and `Update` does not make the change atomic. The `lock` covers only the list operations. `GetAll` copies the list but returns the same `Invoice` objects. | `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs:27` (`GetById`), `:22` (`GetAll`), `:50-56` (`Update`); `backend/src/InvoiceApp.Domain/ApprovalService.cs:36-39` (fields set, then `Update`) |

Checked: `ApprovalsController.cs:22-23` passes only the signed-in `Username` as the approver, with no submitter comparison, and any signed-in user, including an Approver, can submit (section 1, item 5). Observation 1 is confirmed. Observation 2 depends on `InMemoryInvoiceRepository` being registered as a singleton (`Program.cs:14`) and `ApprovalService` as scoped (`Program.cs:15`), as recorded in citations E13 and E14.
