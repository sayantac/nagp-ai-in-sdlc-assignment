---
description: Task 2 - extract every PayEx / submission / retry fact from the incident packs
---
Use the evidence-analyst subagent on `ops/incidents/` and `ops/pipeline/`. The question is: what does the evidence tell us about how the service submits to PayEx, how PayEx behaves on success, failure and timeout, how retries are configured, and whether duplicates or losses have been observed?

Save its output unchanged to `submission/02-adr/work/payex-evidence.md`. Then append a short section, `Open questions for the ADR`, listing the UNKNOWNs that the exactly-once decision depends on.
