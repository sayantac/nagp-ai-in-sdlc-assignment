---
description: Task 1 - review, run and prove the architecture test (red/green)
---
1. Read `AGENTS.md` and `backend/tests/InvoiceApp.Tests/Architecture/DomainLayerArchitectureTests.cs`. Check that the test encodes the rule "Domain: business rules, no web or storage code". Point out any gap, but do not widen the rule without asking.
2. Run `dotnet test backend/InvoiceApp.sln --filter Category=Architecture` and show the result.
3. Run `python3 scripts/demo_arch_test.py`. It injects a deliberate violation, expects the test to fail, reverts, and expects it to pass. Confirm all three outcomes from the files it writes in `submission/01-architecture/evidence/`.
4. Fill `submission/01-architecture/RUN.md` with the command, the three outcomes, and paths to the evidence files.
