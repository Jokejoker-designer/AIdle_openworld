# AIdle Grok World Genesis Subagents v1.0

Bộ subagent này dùng để Grok cùng đảm nhận việc phát triển **AIdle World Genesis**
từ thiết kế concept đến UX, controls, character integration, Godot implementation,
AI prompt-to-world runtime, asset pipeline và bằng chứng nghiệm thu.

## Thành phần

- 1 Master Orchestrator.
- 13 subagent chuyên trách.
- Schema cho work order, handoff, scene package và evidence bundle.
- Hồ sơ 7 World Profiles theo thứ tự triển khai đã khóa.
- Template tracker, file lease, review và worklog.
- Ví dụ work order cho Cozy Control 1B, Cozy Character 1C và Tiny Diorama bước 2.
- Toàn bộ tài liệu nguồn người dùng được đặt trong `reference/`.

## Thứ tự triển khai bắt buộc

1. Cozy Cyber-Pixel / Dreamy Low-Poly
2. Tiny Diorama World
3. Solarpunk Haven
4. Arcane Clockwork
5. Spirit Valley
6. Surrealism Canvas
7. Oceanpunk / Bioluminescent Abyss

World N+1 luôn `BLOCKED` cho đến khi World N `ACCEPTED`.

## Quyền nghiệm thu

- Grok: thực thi work order, tạo patch draft và evidence.
- Red Team: chỉ tìm lỗi.
- Purple Reviewer: chỉ xác minh.
- Codex: machine acceptor.
- Human Product Lead: cổng HITL/alpha và quyết định cuối khi được yêu cầu.

Grok không được tự chuyển trạng thái sang `ACCEPTED`.

## Cách dùng với Grok

### Có hệ thống agent

Nạp `01_MASTER_ORCHESTRATOR.md` cho parent agent. Parent chỉ điều phối, sau đó
spawn đúng agent trong `agents/` theo assignment.

### Không có subagent native

Mở nhiều phiên Grok riêng. Mỗi phiên nạp một file agent, work order, các file
nguồn liên quan và handoff từ bước trước. Parent/Orchestrator hợp nhất kết quả.

## Workflow

`READY -> CLAIMED -> IN_PROGRESS -> REVIEW_REQUESTED -> VERIFIED -> ACCEPTED`

Nhánh lỗi:

`REVIEW_REQUESTED -> CHANGES_REQUESTED -> IN_PROGRESS`

Ba failure signature giống nhau:

`NEED_HUMAN`

## Nguyên tắc bất biến

- Evidence không phải workflow state.
- Một writer sở hữu một file tại một thời điểm.
- Parent coordinator không vá product file.
- Child không spawn grandchild.
- AI chỉ đề xuất; World Commit mới được mutation canonical state.
- Preview không có ownership hoặc collision chính thức.
- Worklog là append-only.
- Không tuyên bố hoàn thành nếu không có executable acceptance evidence.
