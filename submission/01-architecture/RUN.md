# Architecture test

**Rule.** `InvoiceApp.Domain` must not reference web, host, data-access, Azure SDK or outbound-HTTP assemblies. This is the AGENTS.md rule "Domain: business rules, no web or storage code".

**Why this rule.** It is the rule the production changes are most likely to break: Azure SQL, the outbox and the PayEx client all arrive at once.

**Test.** `backend/tests/InvoiceApp.Tests/Architecture/DomainLayerArchitectureTests.cs`

**Command**

```
dotnet test backend/InvoiceApp.sln --filter Category=Architecture
```

**Proof that it bites** (`python3 scripts/demo_arch_test.py`)

| Step | Expected | Actual | Evidence |
|---|---|---|---|
| Before the violation | pass | TODO | `evidence/arch-test-1-green-before.txt` |
| With the violation (FrameworkReference plus an `IResult` in Domain) | fail | TODO | `evidence/arch-test-2-red-violation.txt`, `evidence/arch-violation.diff` |
| After reverting | pass | TODO | `evidence/arch-test-3-green-after.txt` |

**CI run:** TODO link to the green GitHub Actions run on your fork.

**Known limits.** The test checks compiled assembly references. It will not catch a dependency that is declared but unused, or a violation smuggled in through reflection.
