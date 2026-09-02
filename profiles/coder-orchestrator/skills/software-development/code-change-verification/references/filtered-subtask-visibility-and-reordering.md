# Filtered subtask visibility and persistent reordering

When expanded nested task rows hide terminal children such as `completed` and `not done`, filtering changes the rendered drag indices. Reusing those indices against the full cached sibling array can move the wrong child whenever a hidden sibling precedes a visible one.

## Safe contract

1. Derive `resolvedSubtasks` after any surface-specific filter.
2. Count terminal children from that resolved set.
3. Render active children by default; expose one accessible toggle such as `Show N finished subtasks` / `Hide finished subtasks`.
4. Keep the toggle visible when every child is terminal, even though no child row initially renders.
5. Encode the visibility mode in the nested droppable identity, for example:
   - `subtasks:<parentId>:unfinished`
   - `subtasks:<parentId>:all`
6. In every drag-end handler that owns that droppable, parse the mode and construct the source ID list with the exact same visibility predicate as the renderer.
7. Submit only the reordered visible IDs to a merge routine that replaces those children in their existing slots, preserving hidden siblings and their relative order.

## Verification matrix

- Mixed children: active visible; `completed` and `not done` hidden.
- Toggle count equals hidden terminal children.
- Show reveals both terminal statuses; Hide removes them again.
- All-terminal parent still displays the Show action.
- No-terminal parent displays no finished-subtask action.
- Hidden terminal child before active children: dragging active children moves the intended IDs and preserves the hidden child’s slot.
- All children shown: dragging uses full displayed order.
- Exercise every surface with its own drag-end handler; a shared renderer does not prove handler parity.

A build proves compilation only. Leave one focused browser regression for visibility/toggle behavior and a focused reorder assertion for filtered indices.
