# Worked conversation-branching pattern

## Surface map

| Surface | Purpose | Maximum branch detail |
|---|---|---|
| Job card | Scan work across a board | Aggregate count/progress only |
| Job detail modal | Understand job and immediate attention | Aggregate plus up to three actionable branches |
| Conversation detail | Navigate and operate the hierarchy | Full tree and focused transcript |

## Example state

A running job has five forks:

- three merged with no later activity;
- one active;
- one waiting for user input.

Recommended rendering:

- Parent badge remains **IN PROGRESS**.
- Card says **3/5 resolved** with three merged, one active, and one waiting segment.
- Modal lists only the active and waiting forks, with breadcrumbs when nested.
- Dedicated view shows all five forks in the tree.

## Multi-fork creation

Both a message menu and footer action open the same dialog. The message action captures that event; the footer action captures the latest event. The dialog begins with one multiline opening reply and a plus control. Every non-empty field creates one sibling child. Submit as one transaction and open the first child after success.

## Merge semantics

A child’s **Merge back to parent** action generates important points since the previous merge watermark. The user edits the list before confirming. Confirmation creates one immutable parent event and updates the child’s watermark. Later child activity makes it unmerged again.

## Useful acceptance checks

- Main never displays **Merge back to parent**.
- N valid opening replies create exactly N siblings or none.
- Message-menu and footer forks record different fork points correctly.
- A nested fork merges only to its direct parent.
- Job status does not change when fork state changes.
- Zero-fork jobs show no branch-progress decoration.
- Card aggregates equal modal and tree totals.
- Waiting state has accessible text and does not rely only on color.
