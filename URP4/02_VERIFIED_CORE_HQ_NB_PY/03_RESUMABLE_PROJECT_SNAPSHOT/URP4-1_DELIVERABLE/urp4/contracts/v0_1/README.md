# URP4 common contract v0.1

`CINT-01` fixes the cross-module envelope and semantic identity rules before
LEGACY adapters, generator plugins, the descriptor service, Training plugins, or
the thin orchestrator are implemented.

The five object types are:

1. `GenerationRequest`
2. `GeometryArtifact`
3. `DescriptorResult`
4. `DatasetManifest`
5. `TrainingRunManifest`

Key rules:

- Existing aliases and IDs are preserved in `legacy_ids`; they are not renamed.
- Formula, population, backend, statistic, and unit jointly define a descriptor
  scalar player.
- A `DescriptorResult` adds geometry, run, code, and config identity to that
  scalar player.
- Local absolute paths, timestamps, notes, values, metrics, and review state do
  not enter semantic identity hashes.
- Every artifact path stored in a contract is project-relative and portable.
- Scientific status, modeling eligibility, and execution state are separate axes.
- Dataset and Training split contracts must include `base_geometry_id`; random-row
  splitting is not an allowed strategy.
- Bare Excel columns such as `Z`, `AI`, `AY`, `AQ`, or `GM` are rejected as
  feature/target identities. Keep them only under `legacy_ids` and use a
  source-scoped semantic ID in active fields.

The JSON Schema is `schemas/urp4_contracts_v0_1.schema.json`. Runtime validation
uses `jsonschema` under `KMK312`; the Python wrappers do not read notebook globals
or environment-specific scientific configuration.

