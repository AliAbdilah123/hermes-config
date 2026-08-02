# Move-operation verification

Use for board/job/task moves that can target an existing destination or create one.

Focused regression pattern:

1. Create an authenticated owner, board, project, and source column.
2. Create a job in the source column, including at least one non-todo lifecycle state if the operation permits it.
3. POST the move with an existing destination and assert HTTP success plus the persisted lane/column change.
4. POST the move with a new destination name and assert HTTP success, a non-zero returned destination ID, the created destination row, and the job’s persisted lane/column change.
5. Exercise the destination-not-found probe carefully: if the SQL query is expected to return no rows, normalize that expected result to nil before continuing the transaction. Otherwise a stale `sql.ErrNoRows` can make a later valid operation fail with a misleading target-validation response.
6. In the frontend, refresh destination options when opening the move dialog so stale board state cannot submit an invalid target.
7. Run the focused backend test through a directly executed `/tmp/hermes-verify-*` temporary script when workspace verification is not automatically registered, then run the proportionate frontend test/build in the same script. Use `mktemp`, a cleanup trap, and report the result as ad-hoc targeted verification.

Do not claim browser E2E from API tests or a build. If authenticated browser execution is unavailable, report that boundary separately while retaining the passing API/build evidence.
