# Runtime environment parser preflight

Use when deploying a compiled service whose startup strictly rejects unknown `.env` keys.

## Failure pattern

The current process can remain healthy while the checked-out source no longer accepts keys added to the live environment by a newer or adjacent integration. Replacing and restarting the binary then causes an avoidable restart loop such as `unknown setting KEY`, even though build and tests passed.

## Preflight

Before installing the candidate binary:

1. Read only the live environment's key names; never print values.
2. Compare those names with the candidate parser's accepted-key registry.
3. Start the candidate binary against the effective runtime env on an ephemeral listener or invoke a config-validation mode if available.
4. Require successful config parsing before replacing the exact systemd `ExecStart` artifact.
5. If extra keys are intentional but not yet wired, accept them explicitly as ignored compatibility keys and add a regression proving the real key set loads. Do not delete or rename live secrets merely to satisfy an older parser.
6. Install, restart, poll local health, and then probe public proxy health as separate gates.

## Recovery after a failed restart

Inspect the fresh journal first. If strict parsing rejected a legitimate runtime key, make the narrow compatibility change, test it, rebuild, reinstall, restart, and poll readiness. Avoid changing unrelated integration behavior during recovery.
