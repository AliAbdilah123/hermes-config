# Frontend verification after final edits

- Any production or test edit invalidates prior evidence. After the true final edit, rerun focused tests and canonical typecheck/build commands.
- Run commands from the package directory containing `package.json` and `tsconfig.json`. Prefer package scripts such as `pnpm run typecheck`; a workspace-resolved `tsc` from the repository root may only print help and check nothing.
- A production-build timeout after `modules transformed` is neither a code failure nor passing evidence. Chunk rendering can take substantially longer than transformation.
- After such a timeout, rerun the same canonical build once with the tool's maximum foreground timeout rather than repeatedly increasing short timeouts.
- Claim a blocker only if the maximum-duration canonical run still cannot complete. Report only fresh results produced after the last edit.
