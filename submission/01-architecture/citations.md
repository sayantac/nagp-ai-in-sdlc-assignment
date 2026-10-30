# Citations

Every element in the diagrams has an ID: `C#` container/component, `A#` actor/external system, `E#` connection, `S#` sequence step. Paths are repository-relative. `python3 scripts/verify_citations.py` checks that every ID used in a diagram has a row here, that the path exists, and that the symbol appears in the file. Its latest output is in `evidence/citation-check.txt`.

## As-built

Rows for edges that span several files cite the primary file.

| ID | Element | Path | Symbol | Line |
|---|---|---|---|---|
| C1 | API host | `backend/src/InvoiceApp.Api/Program.cs` | `WebApplication` | 6 |
| C2 | Static web UI | `backend/src/InvoiceApp.Api/Program.cs` | `UseStaticFiles` | 20 |
| C3 | Session auth middleware | `backend/src/InvoiceApp.Api/Auth/SessionAuthMiddleware.cs` | `SessionAuthMiddleware` | 4 |
| C4 | Session store | `backend/src/InvoiceApp.Api/Auth/SessionStore.cs` | `SessionStore` | 7 |
| C5 | Role filter | `backend/src/InvoiceApp.Api/Auth/RequireRoleAttribute.cs` | `RequireRoleAttribute` | 8 |
| C6 | AuthController | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `AuthController` | 8 |
| C7 | InvoicesController | `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs` | `InvoicesController` | 9 |
| C8 | ApprovalsController | `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs` | `ApprovalsController` | 9 |
| C9 | ApiControllerBase | `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs` | `Handle` | 9 |
| C10 | ApprovalService | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `ApprovalService` | 7 |
| C11 | IInvoiceRepository | `backend/src/InvoiceApp.Domain/IInvoiceRepository.cs` | `IInvoiceRepository` | 3 |
| C12 | InMemoryInvoiceRepository | `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs` | `InMemoryInvoiceRepository` | 6 |
| C13 | Demo user config | `backend/src/InvoiceApp.Api/Program.cs` | `DemoUsersOptions` | 12 |
| C14 | UI script | `backend/src/InvoiceApp.Api/wwwroot/app.js` | `fetch` | 19 |
| C15 | Invoice entity | `backend/src/InvoiceApp.Domain/Invoice.cs` | `Invoice` | 3 |
| C16 | InvoiceStatus enum | `backend/src/InvoiceApp.Domain/InvoiceStatus.cs` | `InvoiceStatus` | 3 |
| C17 | appsettings.json demo users (Approver, Admin) | `backend/src/InvoiceApp.Api/appsettings.json` | `Users` | 9 |
| C18 | DemoUser | `backend/src/InvoiceApp.Api/Auth/UserSession.cs` | `DemoUser` | 5 |
| C19 | UserSession | `backend/src/InvoiceApp.Api/Auth/UserSession.cs` | `UserSession` | 3 |
| C20 | index.html | `backend/src/InvoiceApp.Api/wwwroot/index.html` | `script` | 74 |
| A1 | Browser user | `backend/src/InvoiceApp.Api/wwwroot/app.js` | `Authorization` | 18 |
| E1 | A1 to C2 loads page | `backend/src/InvoiceApp.Api/Program.cs` | `UseStaticFiles` | 20 |
| E2 | C14 to C1 fetch | `backend/src/InvoiceApp.Api/wwwroot/app.js` | `fetch` | 19 |
| E3 | C1 to C3 pipeline | `backend/src/InvoiceApp.Api/Program.cs` | `UseMiddleware` | 21 |
| E4 | C3 to C4 lookup | `backend/src/InvoiceApp.Api/Auth/SessionAuthMiddleware.cs` | `Get` | 25 |
| E5 | C3 to C5 session item | `backend/src/InvoiceApp.Api/Auth/RequireRoleAttribute.cs` | `Items` | 19 |
| E6 | C1 to C6, C7, C8 | `backend/src/InvoiceApp.Api/Program.cs` | `MapControllers` | 22 |
| E7 | C6 to C13 credential match | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `DemoUsersOptions` | 14 |
| E8 | C6 to C4 create/remove | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `Create` | 34 |
| E9 | C7, C8 to C10 | `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs` | `ApprovalService` | 14 |
| E10 | C7 to C11 direct use | `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs` | `GetAll` | 25 |
| E11 | C7, C8 to C9 Handle | `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs` | `Handle` | 70 |
| E12 | C10 to C11 | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `Update` | 39 |
| E13 | C11 to C12 DI | `backend/src/InvoiceApp.Api/Program.cs` | `InMemoryInvoiceRepository` | 14 |
| E14 | C1 to C10 DI | `backend/src/InvoiceApp.Api/Program.cs` | `ApprovalService` | 15 |
| E15 | C13 to C17 root config binds Users | `backend/src/InvoiceApp.Api/Program.cs` | `DemoUsersOptions` | 12 |
| E16 | C13 to C18 list of DemoUser | `backend/src/InvoiceApp.Api/Auth/UserSession.cs` | `Users` | 14 |
| E17 | C6 to C19 builds session | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `UserSession` | 34 |
| E18 | C5 to C19 reads role | `backend/src/InvoiceApp.Api/Auth/RequireRoleAttribute.cs` | `UserSession` | 19 |
| E19 | C10 to C15 sets status and decision fields | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `DecidedBy` | 54 |
| E20 | C15 to C16 typed Status | `backend/src/InvoiceApp.Domain/Invoice.cs` | `InvoiceStatus` | 8 |
| E21 | C12 to C15 holds invoices | `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs` | `_invoices` | 11 |
| E22 | C2 to C20 serves page | `backend/src/InvoiceApp.Api/Program.cs` | `UseDefaultFiles` | 19 |
| E23 | C20 to C14 script include | `backend/src/InvoiceApp.Api/wwwroot/index.html` | `script` | 74 |
| S1 | login request | `backend/src/InvoiceApp.Api/wwwroot/app.js` | `login` | 103 |
| S2 | match credentials to config users | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `FirstOrDefault` | 26 |
| S3 | build UserSession, role copied | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `UserSession` | 34 |
| S4 | session created | `backend/src/InvoiceApp.Api/Controllers/AuthController.cs` | `Create` | 34 |
| S5 | submit request | `backend/src/InvoiceApp.Api/wwwroot/app.js` | `submit` | 52 |
| S6 | token lookup | `backend/src/InvoiceApp.Api/Auth/SessionAuthMiddleware.cs` | `Get` | 25 |
| S7 | submit has no role check | `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs` | `Submit` | 69 |
| S8 | Submit via Handle | `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs` | `Handle` | 70 |
| S9 | Submit sets PendingApproval | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `Submit` | 16 |
| S10 | approve/reject request | `backend/src/InvoiceApp.Api/wwwroot/app.js` | `approve` | 72 |
| S11 | token validation | `backend/src/InvoiceApp.Api/Auth/SessionAuthMiddleware.cs` | `Get` | 25 |
| S12 | role check 403 | `backend/src/InvoiceApp.Api/Auth/RequireRoleAttribute.cs` | `Contains` | 21 |
| S13 | class-level role | `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs` | `RequireRole` | 9 |
| S14 | Approve/Reject call | `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs` | `Handle` | 21 |
| S15 | blank reason | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `ArgumentException` | 45 |
| S16 | pending check | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `EnsurePending` | 65 |
| S17 | set status and decision fields | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `DecidedBy` | 54 |
| S18 | state change | `backend/src/InvoiceApp.Domain/ApprovalService.cs` | `Update` | 57 |
| S19 | replace under lock | `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs` | `Update` | 50 |
| S20 | 200 invoice | `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs` | `Ok` | 13 |

## Target (planned, not built)

New elements cite the ADR section or the scenario fact that requires them. Elements that already exist keep their as-built IDs and rows. Check with `python3 scripts/verify_citations.py --target`.

| ID | Element | Path | Symbol | Line |
|---|---|---|---|---|
