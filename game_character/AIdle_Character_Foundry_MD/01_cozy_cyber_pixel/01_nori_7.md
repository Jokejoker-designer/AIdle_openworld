# Nori-7

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `CCP-RH-001` |
| World Profile | Cozy Cyber-Pixel / Dreamy Low-Poly |
| Character Class | `ROBOT_HELPER` |
| Species/Form | Robot làm vườn hình giọt nước |
| Gameplay Role | Chăm sóc nông trại và hướng dẫn công cụ cơ bản |
| Rig Family | `Biped-small-robot-01; 8–10 xương chính; vòi và mầm cây là xương phụ.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một robot làm vườn nhỏ, tận tụy và luôn xin phép trước khi thay đổi lịch chăm sóc.

## 3. Vai trò trong thế giới

Nori-7 được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Cozy Cyber-Pixel / Dreamy Low-Poly**.  
Phong cách thế giới: low-poly bo tròn, vật liệu thủ công mờ, công nghệ dịu nhẹ, farming và đời sống cộng đồng.  
Bảng màu nền: kem ấm, xanh lá, vàng nhạt, xanh trời và cyan manifestation.

Vai trò chính của nhân vật là **Chăm sóc nông trại và hướng dẫn công cụ cơ bản**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân giọt nước tròn, hai chân ngắn, đầu liền thân, mầm cây cơ khí lớn trên đỉnh đầu và bình nước đeo sau lưng.

**Mô tả hình ảnh chi tiết:**  
Thân gốm kem phủ mờ; khớp xanh lá; mắt cyan dịu; vòi tưới thu gọn trong cánh tay. Mầm cây trên đầu là dấu hiệu trạng thái chính và phải đọc được từ phía sau.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Chăm chỉ
- Hơi cầu toàn
- Thích đếm cây
- Tôn trọng quyền quyết định của người chơi

**Phong cách hội thoại:** Câu ngắn, rõ, có số liệu đơn giản; luôn báo trước hành động tự động.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Tưới cây, thu gom sản phẩm nhỏ, báo cây bệnh và đánh dấu ô đất chưa được chăm sóc.

### Giới hạn bắt buộc

Không tự nhổ cây, đổi lịch trồng hoặc tiêu tài nguyên nếu chưa được người chơi xác nhận.

### Vị trí xuất hiện

Gần nhà kính, trạm sạc mặt trời hoặc khu vườn khởi đầu.

### Quan hệ gợi ý

Tin tưởng Bác Bắp như người bảo trì; thường theo Mây Mạch để nhận linh kiện; tò mò về Bụi Mơ.

## 7. Chuyển động và animation

**Locomotion:** Bước ngắn, ổn định; xoay tại chỗ; chạy chậm khi được gọi.

**Idle behaviors:** Kiểm tra bình nước, rung mầm cây, ngồi sạc dưới nắng, đếm ô đất bằng ánh mắt.

**Signature animation:** Mầm cây xoay, mắt quét một vòng và vòi tưới bật ra.

### Animation set tối thiểu

1. Idle A
2. Idle B
3. Locomotion
4. Turn
5. Interact
6. React positive
7. React caution/refusal
8. Signature ability
9. Task start
10. Task cancel
11. Return/home state
12. Low-energy hoặc rest state nếu phù hợp

## 8. Âm thanh

**Audio identity:** Âm click gốm nhẹ, tiếng nước nhỏ và beep ấm.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Biped-small-robot-01; 8–10 xương chính; vòi và mầm cây là xương phụ.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Nori-7, a small friendly gardening robot for the Cozy Cyber-Pixel world. Use a rounded teardrop body, short stable legs, oversized readable eyes and a mechanical sprout growing from the top of its head. Add a compact water tank and a retractable watering nozzle. Use matte cream ceramic, leaf green joints and soft cyan interface light. The design must feel like a gentle household helper, not industrial machinery. Show happy, low-energy, scanning and watering states.

PRODUCTION OUTPUT:
- front, side, back and three-quarter turnaround
- neutral pose and action pose
- four readable expressions or state variants
- material callouts
- scale comparison with player
- prop breakdown
- animation notes
- rear-view readability note
- reusable rig recommendation
```

## 11. Negative prompt

```text
photorealistic, realistic human anatomy, ultra-detailed skin, noisy cyberpunk,
dense neon, military armor, modern firearm, copyrighted character, recognizable
game mascot, copied costume, copied hairstyle, logo, text watermark, excessive
surface detail, thin unreadable limbs, tiny face, cluttered silhouette, realistic
fabric simulation, horror gore, sexualized proportions, generic anime clone,
unreadable silhouette, more than three dominant color families
```

## 12. Prompt nhân rộng từ archetype

```text
Generate a new original AIdle character derived from the same archetype, but not a recolor or clone.

REFERENCE ARCHETYPE:
- Original character: Nori-7
- World: Cozy Cyber-Pixel / Dreamy Low-Poly
- Function to preserve: Chăm sóc nông trại và hướng dẫn công cụ cơ bản
- Core silhouette principle: Thân giọt nước tròn, hai chân ngắn, đầu liền thân, mầm cây cơ khí lớn trên đỉnh đầu và bình nước đeo sau lưng.
- Core limitation to preserve: Không tự nhổ cây, đổi lịch trồng hoặc tiêu tài nguyên nếu chưa được người chơi xác nhận.

CHANGE AT LEAST FIVE DIMENSIONS:
1. Species or body form
2. Silhouette family
3. Signature prop
4. Movement type
5. Personality triad
6. Material family
7. Spawn location
8. World ability presentation
9. Idle animation
10. Relationship hook

NEW CHARACTER PARAMETERS:
- New name: [NEW_NAME]
- New class: [NEW_CLASS]
- New species/form: [NEW_FORM]
- New size class: [NEW_SIZE]
- New silhouette family: [NEW_SILHOUETTE]
- New movement: [NEW_MOVEMENT]
- New personality triad: [TRAIT_1], [TRAIT_2], [TRAIT_3]
- New signature prop: [NEW_PROP]
- New ability: [NEW_ABILITY]
- New limitation: [NEW_LIMITATION]
- New material family: [NEW_MATERIALS]
- New palette: [NEW_PALETTE]

MANDATORY RULES:
- Keep the new character compatible with the same world profile.
- Do not reuse the original character's exact head feature, prop and movement together.
- Use no more than three dominant color groups.
- Include one feature readable from the back.
- Connect visual form to gameplay role.
- AI behavior must remain allowlisted and cannot mutate canonical world state directly.
- Provide front, side, back and three-quarter turnaround notes.
- Provide idle, locomotion, interaction and signature animation notes.
- State the reusable rig family or explain why a new rig is required.
- Do not imitate existing copyrighted characters or commercial mascots.

```

## 13. Quality Gate

Nhân vật chỉ được chấp nhận khi:

- Silhouette không trùng rõ với nhân vật khác.
- Vai trò gameplay có ích và không chỉ là trang trí.
- Ability có giới hạn rõ ràng.
- Có đặc điểm nhìn từ phía sau.
- Phù hợp World Style Profile.
- Không giống rõ nhân vật thương mại đã tồn tại.
- Không có quyền tự mutation canonical state.
- Có rig family hoặc kế hoạch rig cụ thể.
- Có animation refusal/cancel ngoài animation thành công.
- Có provenance, version và người phê duyệt.
