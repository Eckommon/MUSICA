# M7-R0 Traceability / M7-R0 추적성

| Decision | Contract / Evidence |
|---|---|
| Canonical automation distinct from derived execution state | `docs/M7_AUTOMATION_AUTHORITY.md` |
| Stable lane/point/parameter identity | `automation-material-v0.schema.json` |
| project/part scope only | `automation-material-v0.schema.json`, contract tests |
| Source-bound non-canonical proposals | `automation-edit-candidate-v0.schema.json` |
| READY/BLOCKED fail-closed result | `automation-authority-result-v0.schema.json` |
| Stable lock targeting | `automation-lock-v0.schema.json`, `automation_contracts.py` |
| Cross-field deterministic invariants | `src/musica/automation_contracts.py` |
| Positive/negative contract examples | `examples/automation/**` |
| Executable proof | `tests/test_m7_r0_automation_contracts.py` |
| Reproducible evidence | `.github/workflows/m7-r0-automation-contract-evidence.yml`, `m7_r0_evidence.py` |

R0 does not provide runtime automation authority; traceability is limited to contract/design evidence.
