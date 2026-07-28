# Ví dụ chạy nhiều Grok session

## Session 1 — Orchestrator

Nạp:

- `01_GROK_ORCHESTRATOR.md`
- `contracts/character_work_order.schema.json`
- Character Foundry reference
- `examples/example_work_order.yaml`

Yêu cầu Orchestrator tạo assignment.

## Session 2 — Character Architect

Nạp:

- `agents/01_CHARACTER_ARCHITECT.md`
- Work order
- Character Schema
- Character Index
- 3 nhân vật gần nhất

Lấy `character_brief.yaml`.

## Session 3 — Style Guardian

Nạp prompt agent, Character Brief và World Index.

## Session 4–6

Lần lượt Visual, Gameplay, Technical.

## Session 7

Prompt Factory tạo bộ prompt sản xuất và nhân rộng.

## Session 8 — Red Team

Nạp toàn package. Chỉ nhận findings, không cho Red sửa.

## Rework

Orchestrator phân findings về đúng worker.

## Session 9 — Purple

Nạp final package, findings và rework log. Chỉ chấp nhận khi trả
`purple_verification.verdict: VERIFIED`.

## Quy tắc sao chép giữa session

Mỗi lần bàn giao phải kèm:

```yaml
step_id:
agent_id:
status: REVIEW_REQUESTED
inputs:
outputs:
evidence:
open_risks:
next_owner:
```
