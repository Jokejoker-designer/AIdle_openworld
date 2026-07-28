# Character Development Workflow

## Trạng thái

`READY -> CLAIMED -> IN_PROGRESS -> REVIEW_REQUESTED -> VERIFIED -> HUMAN_ACCEPT`

Nhánh lỗi:

`REVIEW_REQUESTED -> CHANGES_REQUESTED -> IN_PROGRESS`

Ba failure signature giống nhau:

`NEED_HUMAN`

## Phân quyền file

- Architect sở hữu Character Brief.
- Style Guardian sở hữu Style Lock.
- Visual Designer sở hữu Visual Spec.
- Gameplay Designer sở hữu Gameplay Spec.
- Technical Designer sở hữu Technical Spec.
- Prompt Factory sở hữu Prompt Package.
- Red và Purple chỉ ghi review riêng, không sửa file worker.
- Orchestrator hợp nhất final package sau khi rework xong.

## Work order mẫu

1. Tạo một hoặc nhiều nhân vật.
2. Xác định world và gameplay gap.
3. Chỉ rõ nhân vật gần nhất cần tránh.
4. Chỉ rõ cần reuse rig nào nếu có.
5. Chỉ rõ output: concept-only, production spec hoặc full package.

## Parallelism

Có thể chạy song song:

- Style Guardian và Architect collision scan sau khi Brief sơ bộ có.
- Gameplay và Visual sau khi Brief + Style Lock xong.
- Technical chỉ bắt đầu khi Visual + Gameplay đủ.
- Prompt Factory chỉ bắt đầu khi Visual + Technical đủ.
- Red sau khi package hợp nhất.
- Purple sau rework.

## Definition of Done

Một Character Package hoàn chỉnh gồm:

- work_order.yaml
- character_brief.yaml
- style_lock.yaml
- visual_spec.yaml
- gameplay_spec.yaml
- technical_spec.yaml
- prompt_package.yaml
- red_review.yaml
- rework_log.md
- purple_verification.yaml
- final_character.md
