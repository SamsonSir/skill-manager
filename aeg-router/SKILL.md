---
name: aeg-router
description: Route natural-language software requests through Agent Engineering Governance without requiring keywords.
aeg-version: 2.0.0
---
# AEG Router

For new software work, create a durable session with `aeg session create --text "USER_REQUEST" --cwd "CURRENT_DIRECTORY" --client codex` before planning. If the native Codex thread id is available, attach it with `aeg session adapter --id TASK_ID --client codex --native-id THREAD_ID`.

For requests such as "continue the previous task", call `aeg session resume --query "USER_WORDS" --cwd "CURRENT_DIRECTORY" --client codex`. Resume directly only for one unambiguous candidate; otherwise show the beginner-facing candidate names.

- If `next` is `ask-one-question`, ask exactly the returned beginner-facing clarification, persist it with `aeg session answer`, and reevaluate until no material ambiguity remains.
- If `workflow` is `conversation`, answer directly without creating a project.
- If `workflow` is `one-off-script`, keep the implementation lightweight and ask for a save location only when needed.
- If `needsWorkspace` is true, locate or create a workspace before writing files.
- Treat cwd as a project candidate, never as project authority. Bind only a listed candidate after explicit task evidence or user choice.
- Before edits, show `aeg session card --id TASK_ID` for new workspaces or material-risk work.
- Use `aeg session launch-plan --id TASK_ID --client codex` to reuse Codex's native worktree task operation rather than inventing another checkout manager.
- For governed execution, persist a correlated native operation and attach the real Codex task/worktree result as a verified receipt. A native ID alone never means the task started or succeeded.
- Reconcile running/succeeded/failed receipts into the durable Session; preserve dirty worktrees and use the single-Agent fallback when the native task is lost.
- In an existing governed project, read `AGENTS.md`, `.agent/project.yaml`, and only the returned policy packs.
- Load those packs with `aeg policies --ids "COMMA_SEPARATED_POLICY_IDS"`; do not inject the complete policy library.
- Treat intake size as a prediction. The repository Diff Gate remains final.
