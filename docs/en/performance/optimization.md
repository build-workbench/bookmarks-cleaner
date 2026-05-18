# Performance Methodology

This page describes how to read performance claims across the site. It intentionally avoids unsupported tuning folklore and focuses on the maintained runtime shape.

## Measurement Envelope

Published numbers should be interpreted along four axes:

| Axis | Question |
|------|----------|
| Cold start | How expensive is entering the runtime before heavy intelligence layers load? |
| Steady-state throughput | How fast does the pipeline move once the processing stages are active? |
| Mode width | Is the run rules-only, hybrid, or LLM-assisted? |
| Resource pressure | What memory and concurrency constraints define the practical upper bound? |

## What the Reported Numbers Mean

- **Rules-first numbers** describe the cheapest reliable path through the system.
- **Hybrid numbers** include additional model and semantic work, so they should be read as richer but costlier runs.
- **Optional LLM participation** should be treated as escalation for ambiguous cases, not a baseline requirement.

## Supported Optimization Levers

The maintained performance story relies on levers already consistent with the repository architecture:

1. **Keep the common path deterministic.** The more bookmarks that resolve in the rules layer, the lower the marginal cost of a run.
2. **Avoid unnecessary intelligence width.** ML, semantic, and LLM paths are useful, but they are not free.
3. **Preserve local execution.** Avoid turning performance work into network-roundtrip work unless the user explicitly opts into it.
4. **Read concurrency as workload-dependent.** Thread-level gains depend on how much of the run is parallelizable and how much time is spent in heavy libraries.

## Relationship to the Other Performance Pages

- [Concurrency](/en/performance/concurrency) discusses why the runtime uses its current concurrency model.
- [Caching](/en/performance/caching) discusses what reuse can and cannot buy you.
- [Whitepaper](/en/whitepaper) situates performance inside the broader system boundary and failure model.
