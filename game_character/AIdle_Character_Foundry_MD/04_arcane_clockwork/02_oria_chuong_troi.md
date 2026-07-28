# Oria Chuông Trời

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `AC-NQ-014` |
| World Profile | Arcane Clockwork |
| Character Class | `NPC_QUEST` |
| Species/Form | Người giữ nhịp thời gian |
| Gameplay Role | Quản lý sự kiện và tháp chuông |
| Rig Family | `Humanoid-tall-01; bell-skirt bones; staff VFX socket.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một người giữ thời gian trang trọng có cây trượng chuông không phát âm mà tạo vòng sáng.

## 3. Vai trò trong thế giới

Oria Chuông Trời được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Arcane Clockwork**.  
Phong cách thế giới: cơ khí đồng hồ, rune, tinh thể, vật thể hai lớp Physical/Arcane và chế tạo an toàn.  
Bảng màu nền: đồng cổ, gỗ tối, xanh ngọc, tím tinh thể và cyan manifestation.

Vai trò chính của nhân vật là **Quản lý sự kiện và tháp chuông**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Váy nhiều lớp chuông, tóc như kim đồng hồ và staff chuông tinh thể.

**Mô tả hình ảnh chi tiết:**  
Navy, vàng cổ, ngà và tím tinh thể; hạn chế chi tiết quá dày.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Trang trọng
- Chính xác
- Hài hước về thời gian
- Không thích sai thứ tự

**Phong cách hội thoại:** Nhịp đều, mốc thời gian rõ; thỉnh thoảng chơi chữ.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Kích hoạt event theo lịch, quản lý tháp chuông và replay sự kiện dạng preview.

### Giới hạn bắt buộc

Không sửa lịch sử canonical hoặc ép người chơi vào sự kiện.

### Vị trí xuất hiện

Tháp chuông, quảng trường, cổng sự kiện.

### Quan hệ gợi ý

Tin Brassel; giao lịch vận hành Cinder-04; nhờ Quillix lưu biên niên.

## 7. Chuyển động và animation

**Locomotion:** Bước nghi lễ; lớp váy chuyển như chuông.

**Idle behaviors:** Kiểm tra vòng sáng, chỉnh kim tóc, đếm nhịp.

**Signature animation:** Nâng staff; chuông im lặng tạo ba vòng sáng lan ra.

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

**Audio identity:** Âm cộng hưởng không lời, tiếng kim đồng hồ và vải dày.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-tall-01; bell-skirt bones; staff VFX socket.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Oria Chuông Trời, an elegant arcane-clockwork timekeeper. Her layered outfit should resemble nested bell forms, and her hair should form two simplified clock-hand shapes. Give her a staff with a silent crystal bell that produces visible rings of light. Use deep navy, antique gold, ivory and violet crystal. Maintain a clear ceremonial silhouette without excessive ornament.

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
- Original character: Oria Chuông Trời
- World: Arcane Clockwork
- Function to preserve: Quản lý sự kiện và tháp chuông
- Core silhouette principle: Váy nhiều lớp chuông, tóc như kim đồng hồ và staff chuông tinh thể.
- Core limitation to preserve: Không sửa lịch sử canonical hoặc ép người chơi vào sự kiện.

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
