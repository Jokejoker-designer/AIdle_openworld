# AIdle World Genesis — Bảng triển khai 1 → 7

## Nguồn và phạm vi

- Nguồn thứ tự: `E:\AIdle_openworld\Scene\AIdle World Genesis.docx`, mục **THỨ TỰ TRIỂN KHAI ĐỀ XUẤT**.
- SHA-256 nguồn: `B3738BB35F9E11244509AD849A439C7563CDD2E0B17B976D0D891F573F660812`.
- Tài liệu nền: `E:\AIdle_openworld\Scene\AIdle World Genesis Blueprint.docx`.
- SHA-256 tài liệu nền: `4FEC25288350C5D965BB4FCB5B0597A93164DAD40B3E61A8B097F9F8E5135692`.
- Control tích hợp: `E:\AIdle_openworld\Control\AIdle Keyboard & Mouse Control Blueprint.docx`.
- SHA-256 Control: `7985470D14B0CACE25AA4EC46981FB8D5096B27369D6122B57591404AB73B8FF`.
- Bản đồ Control: `E:\AIdle_openworld\Control\CONTROL_IMPLEMENTATION_MAP.md`.
- Character Foundry: `E:\AIdle_openworld\game_character\AIdle_Character_Foundry_MD` (28 nhân vật / 7 World Profiles; manifest SHA-256 `BDBA6B53174E1D6671F28302B4AE67275AD22BF3C2E978603791ACD19E6CC4BA`).
- Kế hoạch tích hợp Character Foundry: `E:\AIdle_openworld\game_character\CHARACTER_FOUNDRY_INTEGRATION_PLAN.md`.
- Phạm vi hiện tại: Private Reality 2.5D, Companion text-only, cùng schema/preview/consent/World Commit hiện có.
- Cập nhật gần nhất: `2026-07-21T08:12:38+07:00` bởi Codex.

## Quy tắc đánh dấu

1. Triển khai tuần tự từ 1 đến 7; chỉ một bước được phép hoạt động tại một thời điểm.
2. Bước sau chỉ chuyển từ `TODO` sang `READY` khi bước trước đã `ACCEPTED`.
3. Không dùng lời báo cáo của agent làm bằng chứng hoàn thành. Phải có file, test/log và nghiệm thu độc lập.
4. Grok không tự `ACCEPTED`; Codex là machine acceptor, Human Product Lead giữ các cổng HITL/alpha có liên quan.
5. Không rollback hoặc ghi đè thay đổi chưa rõ chủ sở hữu. Một writer trên mỗi file.
6. Giai đoạn 1 chỉ hoàn tất khi 1A Cozy visual shell, 1B Control Foundation + Cozy controls và 1C Cozy Character Foundation đều `ACCEPTED`, trừ khi Human Product Lead thay đổi cổng này.
7. Control chung được xây một lần ở giai đoạn 1; giai đoạn 2–7 chỉ thêm 20% action riêng của world tương ứng.

## Bảng tiến độ chính

| # | World / mục tiêu kỹ thuật | Phụ thuộc | Trạng thái | Đã triển khai / bằng chứng hiện có | Cổng còn thiếu và việc tiếp theo |
|---:|---|---|---|---|---|
| 1 | **Cozy Cyber-Pixel / Dreamy Low-Poly** — nền tảng AIdle, camera, manifestation, Starter Realm; **Control Foundation + Cozy V/B/farming/robot**; **Character Foundry Cozy quartet** | Nền tảng MVP hiện có | `HITL_REQUIRED / CONTROL_PARTIAL / CHARACTER_QUEUED` | 1A: D2 và D3 machine gates đã qua; Purple verdict `PASS_FOR_HUMAN_REVIEW`, G8 vẫn chưa `ACCEPTED`. 1B: code mới có WASD/Shift/E/Esc/F3/zoom/Q-R; chưa có Input Context, C, `/`, Tab, V/B, safe delete/undo, context HUD và accessibility đầy đủ. 1C: đã khóa nguồn 28 nhân vật; lát cắt đầu tiên gồm Nori-7, Mây Mạch, Bác Bắp và Bụi Mơ, chưa triển khai runtime. | Human Product Lead chạy `HUMAN_ACCEPTANCE_CHECKLIST_014.md` và trả `G8 HUMAN PASS` hoặc `G8 HUMAN FAIL`. Chỉ sau quyết định mới phát work order riêng cho 1B và 1C. |
| 2 | **Tiny Diorama World** — grid, placement, nhấc/đặt, camera giới hạn, recipe; **V Hand Tool / B Collection Tray** | Bước 1 `ACCEPTED` | `TODO` | Chưa bắt đầu triển khai theo kế hoạch Scene. | Khóa grid/elevation socket, preview-only drag/drop, confirm, recipe cụm và Tiny-specific control/camera. |
| 3 | **Solarpunk Haven** — chỉ số môi trường, phụ kiện sinh thái; **V Eco Scan / B Ecosystem Dashboard** | Bước 2 `ACCEPTED` | `TODO` | Chưa bắt đầu. | Xác định metrics, tác động công trình, preview Eco Add-on, control và đường phục hồi. |
| 4 | **Arcane Clockwork** — vật thể hai lớp, điều kiện kích hoạt; **V Layer Shift / B Mechanism Workbench** | Bước 3 `ACCEPTED` | `TODO` | Chưa bắt đầu. | Khóa schema physical/magic layer, socket/link controls, triggers và receipts. |
| 5 | **Spirit Valley** — phản ứng môi trường, creature recipe, phục hồi; **V Spirit Sense / B Spirit Journal** | Bước 4 `ACCEPTED` | `TODO` | Chưa bắt đầu. | Thiết kế ba mức phục hồi, creature/ritual controls có giới hạn và quan hệ nguyên nhân–kết quả rõ. |
| 6 | **Surrealism Canvas** — rule engine, anomaly có kiểm soát; **V Reality Lens / B Anomaly Registry** | Bước 5 `ACCEPTED` | `TODO` | Chưa bắt đầu. | Thiết kế Surreal Rule budget, anomaly/portal controls, preview, accessibility và fail-closed validation. |
| 7 | **Oceanpunk / Bioluminescent Abyss** — chiều sâu, nước, ánh sáng, occlusion/navigation; **V Sonar / B Dive Console** | Bước 6 `ACCEPTED` | `TODO` | Chưa bắt đầu. | Spike depth tiers, submarine/underwater build controls, navigation/collision và cảnh báo ngoài màu sắc. |

## Checkpoint hiện tại

- [x] Đã xác định đúng hai tài liệu nguồn trong `Scene`.
- [x] Đã trích xuất và khóa đúng thứ tự 1 → 7.
- [x] Đã đối chiếu bước 1 với trạng thái repo/Grok hiện tại.
- [x] Đã trích xuất Control Blueprint, kiểm kê InputMap hiện có và ánh xạ control theo đúng thứ tự Scene 1 → 7.
- [x] Đã kiểm kê Character Foundry 28 nhân vật, khóa hash manifest và ánh xạ vào đúng thứ tự Scene 1 → 7.
- [ ] Bước 1 đã qua nghiệm thu máy độc lập của Codex.
- [ ] Control Foundation + Cozy control slice đã có work order, smoke và headed checklist được chấp nhận.
- [ ] Cozy Character Foundation đã có schema intake, work order, bốn nhân vật Scene 1 và authority/headed evidence được chấp nhận.
- [ ] Bước 1 đã qua cổng Human Product Lead nếu checklist alpha yêu cầu.
- [ ] Bước 2 được phát hành work order.
- [ ] Bước 3 được phát hành work order.
- [ ] Bước 4 được phát hành work order.
- [ ] Bước 5 được phát hành work order.
- [ ] Bước 6 được phát hành work order.
- [ ] Bước 7 được phát hành work order.

## Cách cập nhật bảng

Sau mỗi milestone, cập nhật đồng thời:

1. Trạng thái của đúng một hàng.
2. Đường dẫn file/receipt/test/log có thể kiểm tra lại.
3. Blocker hoặc cổng còn thiếu.
4. Một dòng mới trong `SCENE_WORKLOG.md`; không sửa lịch sử cũ để làm đẹp kết quả.
