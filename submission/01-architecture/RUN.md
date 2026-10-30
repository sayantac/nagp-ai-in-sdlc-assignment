# Architecture test

**Rule.** `InvoiceApp.Domain` must not reference web, host, data-access, Azure SDK or outbound-HTTP assemblies. This is the AGENTS.md rule "Domain: business rules, no web or storage code".

**Why this rule.** It is the rule the production changes are most likely to break: Azure SQL, the outbox and the PayEx client all arrive at once.

**Test.** `backend/tests/InvoiceApp.Tests/Architecture/DomainLayerArchitectureTests.cs`

**Command**

```
dotnet test backend/InvoiceApp.sln --filter Category=Architecture
```

**Proof that it bites** (`python3 scripts/demo_arch_test.py`, run on git HEAD `45d3790`, 2026-10-30; the script's own result line was "RESULT: PASS - the test bites")

| Step | Expected | Actual | Evidence |
|---|---|---|---|
| Before the violation | pass | Passed: exit 0, 9 of 9 tests passed | `evidence/arch-test-1-green-before.txt` |
| With the violation (FrameworkReference plus an `IResult` in Domain) | fail | Failed: exit 1, 8 passed and 1 failed. The failure was the `Microsoft.AspNetCore` case: "Found: Microsoft.AspNetCore.Http.Abstractions, Microsoft.AspNetCore.Http.Results" | `evidence/arch-test-2-red-violation.txt`, `evidence/arch-violation.diff` |
| After reverting | pass | Passed: exit 0, 9 of 9 tests passed | `evidence/arch-test-3-green-after.txt` |

**CI:** the build and test steps from `.github/workflows/ci.yml` were run locally; output in `evidence/ci-local.txt`. No GitHub Actions run (local repository).

**Known limits.** The test checks compiled assembly references. It will not catch a dependency that is declared but unused, or a violation smuggled in through reflection.
