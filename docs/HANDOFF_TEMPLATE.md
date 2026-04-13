# Handoff Template

Use this template for every specialist -> QA and QA -> supervisor handoff.

## Standard Output Block

```text
HANDOFF
Task: <ID - title>
From: <agent>
To: <agent>
Status: <ready-for-qa | qa-pass | qa-fail | blocked>
Recommendation: <accept | needs-changes | blocked>
Summary: <1-3 lines>
Scope:
- <files/areas changed>
Checks Run:
- <command>: <result>
Evidence:
- <key observations, outputs, screenshots if relevant>
Risks:
- <known risk or "none">
Findings:
- <severity: Critical|Major|Minor - short finding or "none">
Requested Action:
- <what receiver should do next>
```

## Required Rules

- Keep handoff concise and factual.
- Include only checks that were actually run.
- If blocked, include attempted resolutions.
- If QA fails, include reproducible steps and severity.
- Link task ID exactly as shown in `tasks/TASKS.md`.
- QA handoffs must include `Recommendation` and at least one `Findings` line.

## QA Severity Labels

- `Critical`: blocks merge or release
- `Major`: significant defect, fix before acceptance
- `Minor`: non-blocking defect or polish item

## Supervisor Decision Mapping

- `Critical` finding present: do not accept; return for fix.
- `Major` finding present: do not accept by default.
- `Minor` findings only: may accept with follow-up task(s).
