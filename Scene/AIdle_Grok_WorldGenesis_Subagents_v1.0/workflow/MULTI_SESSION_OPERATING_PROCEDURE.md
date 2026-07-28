# Grok Multi-Session Operating Procedure

1. Parent nạp `01_MASTER_ORCHESTRATOR.md`, governance, tracker và work order.
2. Parent gọi SSOT Guardian trước.
3. Khi preflight `READY`, parent giao tối đa 5 child không chồng writer set.
4. Mỗi child trả `agent_step_contract.json`.
5. Parent chỉ collate, không patch.
6. QA tạo evidence bundle.
7. Red review chỉ findings.
8. Rework do đúng Blue writer thực hiện.
9. Purple verify độc lập.
10. Chuyển Codex machine review.
11. Human Product Lead xử lý HITL.
12. Tracker Steward chỉ cập nhật sau quyết định có authority.

## Handoff tối thiểu

```yaml
step_id:
work_order_id:
agent_id:
authority:
status: REVIEW_REQUESTED
inputs:
outputs:
evidence_refs:
writer_lease:
self_accept: false
open_risks:
failure_signature:
next_owner:
```
