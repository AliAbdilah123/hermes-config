# Case Study: Self-Flow Subtask Drag Plan (July 2026)

## What happened

A PRD plan to "allow dragging subtasks between homepage statuses" was implemented 3 times and reverted 3 times. Every attempt made the same two mistakes because the plan used generic language instead of naming the specific invariant code.

## The two killer bugs

### Bug 1: Filter removed from `listEntries` useMemo

```tsx
// HomePage.tsx, ~line 620-637
listEntries = flattenedTasks.filter((entry) => {
  const parent = entry.parentChain[entry.parentChain.length - 1];
  if (
    parent &&
    (!entry.task.status ||
      entry.task.status === parent.status ||           // ← THIS CONDITION
      !entry.task.goalIds?.includes(todaysDailyGoal?.id))
  ) {
    return false;  // hides same-status subtasks from flat list
  }
  // ...
});
```

This filter ensures subtasks with the same status as their parent ONLY appear as nested children via expand/collapse — not as separate flat entries. Every implementation removed the entire filter block, causing subtasks to render twice (flat + nested).

**What the plan should have said:** "Modify the `listEntries` filter: remove only the `entry.task.status === parent.status` condition. Keep the other guards and the dedup logic. This allows different-status subtasks into the flat list while same-status subtasks remain nested-only."

### Bug 2: `hideSubtasks` prop changed from conditional to universal

```tsx
// Original (working):
hideSubtasks={!!parent}  // root tasks: false (can expand), subtasks: true (hidden)

// Every implementation changed to:
hideSubtasks             // always true → NO task can expand
```

In `TaskListItem`, `hideSubtasks` controls TWO behaviors:
1. Whether the expand/collapse chevron button appears
2. Whether nested subtasks are rendered

`!!parent` distinguishes root tasks (can expand, show children) from subtasks (cannot expand). Making it always `true` kills expand/collapse for ALL tasks.

**What the plan should have said:** "`hideSubtasks={!!parent}` must not change. This prop is how root tasks get their expand chevron."

## Git history of the failure

```
335b37b Allow dragging subtasks in home list
6845863 Show subtasks as draggable list rows
cd0722b Load subtasks for draggable list rows
433d71f Nest same-status subtasks in list
1e52619 Nest unassociated subtasks in home list
0735755 Fix independent subtask dragging  ← Bug 1+2 introduced
85fec78 REVERT
fed34d2 Keep task expand controls        ← Tried to fix Bug 2, Bug 1 still present
24b3a87 REVERT
4f47fe1 Enable list dragging             ← Same Bug 1+2, fresh attempt
1ddb711 REVERT
6def982 feat: allow dragging subtasks    ← PRD created + same Bug 1+2
377cf45 REVERT
```

Three separate implementation attempts, all making the same two mistakes. The plan was clear about the feature goal but said nothing about which specific props and filter conditions make the current behavior work.

## Pattern

When a plan says "preserve X" or "keep Y working" without naming the exact code that makes X/Y work, implementers will accidentally break X/Y. Plans that extend existing components must enumerate:
- Which props control the current behavior (and whether they change)
- Which filter/guard conditions keep items in the right rendering path
- What "do not touch" looks like in the actual codebase
