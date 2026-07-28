# Shared Governance Contract

## State

`TODO | BLOCKED | READY | CLAIMED | IN_PROGRESS | REVIEW_REQUESTED | VERIFIED |
CHANGES_REQUESTED | HITL_REQUIRED | ACCEPTED`

Coverage là trường riêng:

`NONE | PARTIAL | COMPLETE`

Không kết hợp state và coverage thành một chuỗi mơ hồ.

## Authority rules

- AI proposes.
- Client renders and may predict.
- World Commit validates and commits.
- Preview is non-durable.
- Delete, paid generation, public publish and irreversible action require HITL.
- `request_id` is idempotency key.
- `expected_world_revision` prevents lost updates.
- Undo is a compensating mutation.

## Review roles

### Blue Worker

Chỉ patch file trong approved writer set.

### Red Reviewer

Chỉ tạo findings. Không patch.

### Purple Reviewer

Chỉ verify. Không patch.

### Codex

Machine acceptor và state owner.

### Human Product Lead

HITL, alpha acceptance và thay đổi thứ tự/gate.

## Completion honesty

- Tài liệu không phải implementation.
- Unit test không phải visual proof.
- Screenshot không phải canonical state.
- Agent status không phải acceptance.
- Không có executable evidence thì không được nói “hoàn tất”.
