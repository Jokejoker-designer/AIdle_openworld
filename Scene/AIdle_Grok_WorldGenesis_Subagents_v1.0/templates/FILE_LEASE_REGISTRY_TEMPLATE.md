# File Lease Registry

| Lease ID | Work order | Agent | File/glob | Start | End/Release | State |
|---|---|---|---|---|---|---|
| EXAMPLE | WO-... | agent_id | path/** | ISO-8601 | pending | CLAIMED |

Rules:

- Một file chỉ có một writer lease.
- Reviewer không lấy writer lease product file.
- Parent coordinator không lấy product writer lease.
- Lease phải được release hoặc chuyển rõ ràng trước rework.
