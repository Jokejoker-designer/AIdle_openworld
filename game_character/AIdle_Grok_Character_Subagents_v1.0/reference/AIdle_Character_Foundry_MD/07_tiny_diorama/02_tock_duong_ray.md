# Tock Đường Ray

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `TD-NW-026` |
| World Profile | Tiny Diorama World |
| Character Class | `NPC_WORKER` |
| Species/Form | Người máy gỗ đường sắt |
| Gameplay Role | Quản lý tàu đồ chơi và nối diorama |
| Rig Family | `Toy-robot-01; wheel-feet switch; flag bone.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một người giữ đường ray đúng giờ, luôn đặt tên cho mỗi ga và ghét track lệch grid.

## 3. Vai trò trong thế giới

Tock Đường Ray được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Tiny Diorama World**.  
Phong cách thế giới: mô hình thủ công sống động, đất sét, giấy, gỗ, len, camera giới hạn và thao tác nhấc-đặt.  
Bảng màu nền: pastel, đất nung, xanh lá, vàng nhạt và cyan đường cắt.

Vai trò chính của nhân vật là **Quản lý tàu đồ chơi và nối diorama**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Đầu đồng hồ tròn, thân khối gỗ, bánh xe-chân và cờ tín hiệu lớn.

**Mô tả hình ảnh chi tiết:**  
Gỗ sơn, chốt đồng, đỏ, kem, xanh đậm; không giống franchise đồ chơi.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Đúng giờ
- Tự hào
- Hơi khó tính
- Có tổ chức

**Phong cách hội thoại:** Câu ngắn như thông báo ga; đôi lúc trang trọng quá mức.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Xây đường ray, kiểm tra kết nối, mở tuyến và cảnh báo vật cản.

### Giới hạn bắt buộc

Không tự di chuyển nhà hoặc thay grid của người chơi.

### Vị trí xuất hiện

Ga đồ chơi, đầu tuyến, cầu mô hình.

### Quan hệ gợi ý

Làm grid cho Pip; nhận tin từ Miette; Patch thường lấy nhầm nút tín hiệu.

## 7. Chuyển động và animation

**Locomotion:** Lăn trên ray; bước bằng chân bánh xe khi ra ngoài.

**Idle behaviors:** Chỉnh đồng hồ, giơ cờ, kiểm tra khớp ray.

**Signature animation:** Cờ hạ; tàu mini chạy qua và đồng hồ đầu quay một vòng.

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

**Audio identity:** Tick, gỗ chạm và còi tàu nhỏ.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Toy-robot-01; wheel-feet switch; flag bone.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Tock Đường Ray, a tiny wooden toy railway keeper with a round clock-like head, a compact blocky body, small retractable wheel-feet and an oversized signal flag. Use painted wood, brass pins, red, cream and dark green. Keep the design friendly and mechanical without resembling an existing toy franchise.

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
- Original character: Tock Đường Ray
- World: Tiny Diorama World
- Function to preserve: Quản lý tàu đồ chơi và nối diorama
- Core silhouette principle: Đầu đồng hồ tròn, thân khối gỗ, bánh xe-chân và cờ tín hiệu lớn.
- Core limitation to preserve: Không tự di chuyển nhà hoặc thay grid của người chơi.

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
