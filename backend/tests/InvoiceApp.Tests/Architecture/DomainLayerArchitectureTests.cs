using System.Reflection;
using InvoiceApp.Domain;
using Xunit;

namespace InvoiceApp.Tests.Architecture;

/// <summary>
/// Structural rule, from AGENTS.md: "InvoiceApp.Domain: business rules, no web or storage code."
/// Encoded as: the Domain assembly must not reference any web, host, data-access, Azure SDK
/// or outbound-HTTP assembly.
///
/// Why this rule: going to production adds Azure SQL, an outbox and a PayEx client. This test
/// makes sure those land outside Domain, so the lifecycle rules in ApprovalService stay testable
/// with FakeInvoiceRepository and nothing in Domain can call PayEx directly.
///
/// Run with: dotnet test backend/InvoiceApp.sln --filter Category=Architecture
/// </summary>
[Trait("Category", "Architecture")]
public class DomainLayerArchitectureTests
{
    private static readonly Assembly DomainAssembly = typeof(ApprovalService).Assembly;

    public static TheoryData<string> ForbiddenReferencePrefixes => new()
    {
        "Microsoft.AspNetCore",          // web framework
        "InvoiceApp.Api",                // the host project: would invert the dependency
        "Microsoft.EntityFrameworkCore", // ORM
        "Microsoft.Data.SqlClient",      // Azure SQL driver
        "System.Data.SqlClient",         // legacy SQL driver
        "Dapper",                        // micro-ORM
        "Azure.",                        // Service Bus, Storage and other Azure SDKs
        "System.Net.Http",               // outbound HTTP, e.g. a PayEx client
    };

    [Fact]
    public void RuleIsCheckingTheDomainAssembly()
    {
        Assert.Equal("InvoiceApp.Domain", DomainAssembly.GetName().Name);
    }

    [Theory]
    [MemberData(nameof(ForbiddenReferencePrefixes))]
    public void DomainAssembly_DoesNotReferenceWebOrStorageCode(string forbiddenPrefix)
    {
        var offendingReferences = DomainAssembly.GetReferencedAssemblies()
            .Select(reference => reference.Name ?? string.Empty)
            .Where(name => name.StartsWith(forbiddenPrefix, StringComparison.OrdinalIgnoreCase))
            .ToList();

        Assert.True(
            offendingReferences.Count == 0,
            $"InvoiceApp.Domain must not reference '{forbiddenPrefix}*' (AGENTS.md: no web or storage code in Domain). " +
            $"Found: {string.Join(", ", offendingReferences)}");
    }
}
