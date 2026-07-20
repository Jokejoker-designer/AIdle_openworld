You are the direct Grok worker `aidle-core`, not the conductor and not the final
acceptor. Work only on directive 8 task G2-005 under PATCH_DRAFT authority.

Before editing, read AGENTS.md, E:\standards\maf\COMPLIANCE.md,
E:\agents\characters\registry.yaml, ARCHITECTURE_LOCK.md,
orchestration/control/codex_directive.json,
orchestration/work_orders/WO-G2-BRIDGE-CORRECTION-002.md, and the existing
bridge implementation/tests. Do not spawn subagents.

Repair the existing implementation in place. Do not roll back or replace
accepted code. Fix standalone Godot class loading, dialog/window type errors,
inferred-null parse errors, and the false-positive smoke that prints PASS while
scripts fail. Preserve manual visible consent, file/clipboard-only transport,
no networking, stale/replay rejection, and explicit credential deny-lists.

Write only within the work-order scope. Never edit tasks.json,
codex_directive.json, grok_status.json, architecture/contracts, or another
module. Never create an ACCEPT file or mark the task ACCEPTED.

Run the Python bridge smoke, Godot bridge smoke, project validator, and inspect
the complete Godot log for parse/compile/script/runtime errors. Finish by
writing a valid MAF PATCH_DRAFT receipt to orchestration/receipts/G2-005.json
with state REVIEW_REQUESTED, changed files, exact commands/results, and risks.

