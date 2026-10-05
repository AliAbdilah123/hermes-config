---
name: feature-bounded-resource-capture
description: Use when implementing an on-demand timed host-process resource capture with one active run, progress polling, tolerant sampling, top-N aggregation, and atomic latest-result persistence.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, monitoring, processes, sampling]
    related_skills: []
---
# Feature: Bounded Resource Capture

A capture manager permits one active bounded run. Sample process CPU/memory at a fixed interval, parse defensively, tolerate individual sample failures, aggregate by stable process identity, and fail only when all samples fail. Persist the latest completed result by temp file plus atomic rename. Status exposes phase/progress without blocking.

## Configuration
Port/address, capture duration/interval/max processes, result path, and platform sampler selection. The Unix `ps` implementation must be labeled platform-specific.

## Templates
- `templates/capture-manager.go`
- `references/sampling-and-verification.md`

## Pitfalls
Assuming portable `ps`; unbounded captures; overlapping runs; partial JSON writes; treating one failed sample as total failure; PID reuse over long windows; claiming restart resume when only latest completed output persists.

## Verification
Concurrent start rejection, deterministic injected samples, parser fixtures, partial/all failure behavior, progress, top-N ordering, atomic output, and restart behavior.

## Provenance
`server-monitor` capture manager, parser, aggregation, atomic JSON persistence, API and tests.
