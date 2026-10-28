# Scenario facts

Transcribed from the assignment brief (AI-in-SDLC-Home_Assignment-2.pdf), because `ops/README.md` in the repository does not contain them (see ASSUMPTIONS.md, A2). Agents are pointed at this file as the single source of scenario facts.

| Fact | Detail |
|---|---|
| Service | Invoice Approval. 18 months as an internal tool, maintained part-time by one person. Becomes tier-2 in January. |
| Tier-2 means | 24x7 on-call rotation, a published SLO, and a new integration that submits approved invoices to the external payment provider PayEx |
| Team | Six engineers, two of them new to this codebase; one-week on-call rotation |
| Platform | ASP.NET Core 8 on Azure App Service, Azure SQL, GitHub Actions |
| Available but unused | Azure Service Bus is provisioned; nothing uses it yet |
| Volume | About 40,000 invoices a month, 60% of them in the last three working days, peaking near 80 approvals a minute |
| Persistence today | None. The repository uses an in-memory store, so the database is part of going to production |
| PayEx behaviour | Returns a reference on success. Times out at 30 seconds, and a timeout does not reliably mean the submission failed |
| Compliance | SOC 2 Type II audit in six months; approval actions auditable for seven years |

The planned production deployment is described in `ops/`. The code as it stands is described only by `backend/` (see AGENTS.md).
