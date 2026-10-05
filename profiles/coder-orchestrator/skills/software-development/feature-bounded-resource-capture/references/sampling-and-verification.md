# Sampling and verification

Inject sampler and clock for tests. Unix adapter invokes `ps` without shell and parses fixture output defensively. Aggregate samples explicitly (mean/max as chosen), sort deterministic top-N, and use PID+start-time where available. Atomic persistence writes/syncs/closes temp file then renames. Status documents that active captures do not resume after restart; latest completed result does.
