# AIdle Keyboard & Mouse Control — Bản đồ tích hợp 1 → 7

## Nguồn và quyết định thứ tự

- Nguồn: `E:\AIdle_openworld\Control\AIdle Keyboard & Mouse Control Blueprint.docx`.
- SHA-256: `7985470D14B0CACE25AA4EC46981FB8D5096B27369D6122B57591404AB73B8FF`.
- Nguyên tắc nguồn: 80% thao tác dùng chung, 20% thay đổi theo concept.
- Thứ tự triển khai có thẩm quyền vẫn là kế hoạch Scene:
  Cozy → Tiny Diorama → Solarpunk → Arcane Clockwork → Spirit Valley →
  Surrealism Canvas → Oceanpunk.
- Thứ tự trình bày world trong tài liệu Control chỉ là catalog chức năng; không
  được dùng để đổi thứ tự 1 → 7 đã khóa.

## Hiện trạng có bằng chứng

`game/project.godot` hiện đã khai báo: WASD, sprint, `E`, Esc/pause, F3 debug,
mouse-wheel zoom và Q/R camera actions. Chưa có bằng chứng triển khai đầy đủ cho:

- năm Input Context: Exploration, Companion, Build, Inspect và World Tool;
- `C`, `/`, `Tab`, `V`, `B`, `Ctrl+Z`, Delete Proposal;
- cursor/icon theo context;
- context HUD tối đa bốn hành động;
- remap/preset/accessibility và thời gian giữ xác nhận;
- toàn bộ control riêng của Cozy và sáu world còn lại.

Vì vậy trạng thái Control foundation là `PARTIAL`, không phải `ACCEPTED`.

## Ánh xạ vào bảy giai đoạn

| Giai đoạn | Control được triển khai | Trạng thái | Cổng nghiệm thu |
|---:|---|---|---|
| 1 — Cozy | **Control Foundation**: Input Context router; WASD/Shift/E/F/C/`/`/Tab/V/B/Esc; Build placement/rotate/snap/cancel; proposal/receipt/confirm; context HUD; remap/accessibility. **Cozy slice**: V = Helper Pulse, B = Homestead Panel, farming/robot actions. | `PARTIAL / TODO` | Chỉ mở sau khi Directive 25 / G8 remediation được Codex `ACCEPTED`. Giai đoạn 1 chưa `ACCEPTED` nếu Control foundation và Cozy slice chưa qua smoke + headed input checklist. |
| 2 — Tiny Diorama | V = Hand Tool; B = Collection Tray; lift/place/rotate/elevation/scale/snap/group; camera xoay giới hạn. | `TODO` | Common controls không đổi; camera không gây chóng mặt; preview không ghi state. |
| 3 — Solarpunk | V = Eco Scan; B = Ecosystem Dashboard; inspect ô, influence, water/energy flow, Eco Add-on accept/reject. | `TODO` | Eco signals có icon/pattern ngoài màu; proposal vẫn cần preview/confirm. |
| 4 — Arcane Clockwork | V = Layer Shift; B = Mechanism Workbench; physical/arcane inspection, socket/link, validation. | `TODO` | Hai layer phân biệt rõ; kết nối chỉ là preview trước xác nhận. |
| 5 — Spirit Valley | V = Spirit Sense; B = Spirit Journal; companion creature, care, tracking và ritual controls. | `TODO` | Ritual không thành quick-time event; Esc luôn hủy preview an toàn. |
| 6 — Surrealism Canvas | V = Reality Lens; B = Anomaly Registry; inspect/anchor anomaly, portal link, A/B state. | `TODO` | Anomaly/portal có boundary rõ và không kích hoạt bằng một nhấn destructive. |
| 7 — Oceanpunk | V = Sonar Pulse; B = Dive Console; depth up/down, submarine, dock, underwater build controls. | `TODO` | Điều khiển chiều sâu dễ đọc trong 2.5D; cảnh báo không chỉ dùng màu. |

## Giai đoạn 1 gồm hai sub-gate

### 1A — Cozy visual/playable shell

- Directive hiện hành: 24.
- Active work order: `orchestration/work_orders/WO-G8-001-SUBAGENT-WORKFLOW-REMEDIATION-004.md`; bản visual correction 003 được giữ làm technical draft, chưa phải acceptance evidence.
- Mục tiêu: đóng các blocker visual/evidence mà không rebuild code cũ.

### 1B — Control Foundation + Cozy control slice

Chỉ dispatch sau khi 1A được Codex nghiệm thu. Trước Blue implementation, dùng `support-control-a11y` theo work order read-only riêng để khóa flow, Input Context và accessibility. Acceptance tối thiểu:

1. Mọi action có tên ổn định trong Godot InputMap và remap được.
2. Một phím chỉ kích hoạt action của Input Context đang active.
3. `/` mở Prompt Composer; `Ctrl+Enter` gửi; proposal → preview → receipt →
   explicit confirm/cancel vẫn giữ authority boundary.
4. Delete chỉ tạo Delete Proposal; Ctrl+Z tạo rollback/compensating request;
   không xóa lịch sử.
5. Preview không ownership/collision; cancel không orphan; collision chỉ ở
   COMPLETE.
6. Context HUD hiển thị tối đa bốn action, dùng text/icon/pattern thay vì chỉ
   màu.
7. Có remap, left-hand/one-hand preset, hold/toggle option, mouse sensitivity,
   reduced motion, cursor size và configurable confirmation hold.
8. Headless control smoke kiểm tra InputMap/context/conflict/safety; headed
   checklist kiểm tra prompt, Build Mode, Cozy V/B và context HUD.

## Quy tắc xung đột

- `R` chỉ xoay preview trong Build Mode; không làm hành động tương tự ở
  Exploration Mode.
- Q/R không được mở camera tự do trong sáu concept đầu.
- Chuột trái không đồng thời điều khiển di chuyển và dùng công cụ.
- Space, chuột trái và mouse wheel phải được router theo context hiển thị rõ.
- Esc luôn ưu tiên hủy preview/dialogue không quan trọng trước khi mở pause.
- Mọi thay đổi lâu dài vẫn đi qua schema, preview, consent và World Commit.
