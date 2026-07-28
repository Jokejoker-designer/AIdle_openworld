# AIdle Grok Character Subagents v1.0

Bộ này tổ chức việc phát triển nhân vật AIdle thành một dây chuyền nhiều vai trò,
dùng được với Grok theo hai cách:

1. **Có cơ chế agent/task:** dùng từng file trong `agents/` làm system prompt cho
   một agent riêng.
2. **Không có subagent native:** mở nhiều cuộc hội thoại Grok riêng, gán mỗi cuộc
   hội thoại một prompt vai trò, sau đó dùng `01_GROK_ORCHESTRATOR.md` để điều phối.

## Cấu trúc

- `01_GROK_ORCHESTRATOR.md`: điều phối toàn bộ quy trình.
- `agents/01...08`: tám vai trò chuyên môn.
- `contracts/`: hợp đồng đầu vào, bàn giao và hồ sơ nhân vật cuối.
- `workflow/`: trạng thái công việc và quy tắc chạy.
- `examples/`: work order và ví dụ bàn giao.
- `reference/`: Character Foundry 28 nhân vật do người dùng cung cấp.

## Dây chuyền

`REQUEST -> ARCHITECT -> STYLE -> VISUAL -> GAMEPLAY -> TECHNICAL -> PROMPT_FACTORY
-> RED_REVIEW -> REWORK_IF_NEEDED -> PURPLE_VERIFY -> HUMAN_ACCEPT`

## Nguyên tắc bất biến

- Mỗi nhân vật phải có gameplay role thực và limitation rõ.
- AI/NPC không có quyền trực tiếp mutation canonical world state.
- Không tạo nhân vật mới bằng cách chỉ đổi màu.
- Không sao chép mascot, silhouette, costume hoặc prop đặc trưng của IP khác.
- Nhân vật phải đọc được dưới camera 2.5D/isometric.
- Worker không được tự chấp nhận đầu ra của mình.
- Red Team chỉ tìm lỗi; không sửa.
- Purple Reviewer chỉ xác minh; không sửa.
- Human Owner chấp nhận cuối cùng.
