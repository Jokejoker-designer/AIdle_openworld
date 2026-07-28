# Brassel Thợ Rune

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `AC-NW-013` |
| World Profile | Arcane Clockwork |
| Character Class | `NPC_WORKER` |
| Species/Form | Thợ rune cơ khí |
| Gameplay Role | Kết nối cơ khí và rune |
| Rig Family | `Humanoid-stocky-01; goggles layer rig; glove/tool rig.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một thợ rune kỹ tính không tin vào bất kỳ phép thuật nào chưa qua kiểm tra kết nối.

## 3. Vai trò trong thế giới

Brassel Thợ Rune được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Arcane Clockwork**.  
Phong cách thế giới: cơ khí đồng hồ, rune, tinh thể, vật thể hai lớp Physical/Arcane và chế tạo an toàn.  
Bảng màu nền: đồng cổ, gỗ tối, xanh ngọc, tím tinh thể và cyan manifestation.

Vai trò chính của nhân vật là **Kết nối cơ khí và rune**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân thấp vai rộng, kính tròn nhiều lớp, tạp dề rune và hai tay công cụ khác nhau.

**Mô tả hình ảnh chi tiết:**  
Đồng, gỗ tối, tinh thể teal, da nâu và giấy rune.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Tập trung
- Kỹ tính
- An toàn
- Thích tài liệu hóa

**Phong cách hội thoại:** Nói theo bước; thường hỏi đầu vào, điều kiện và đầu ra.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Kiểm tra socket, xây trigger có cấu trúc và phát hiện kết nối nguy hiểm.

### Giới hạn bắt buộc

Không chấp nhận raw executable code hoặc rune không có giới hạn.

### Vị trí xuất hiện

Workbench, xưởng rune, tháp máy hoặc cầu cơ khí.

### Quan hệ gợi ý

Hợp tác với Oria; bảo trì Cinder-04; dùng Quillix lưu bản vẽ.

## 7. Chuyển động và animation

**Locomotion:** Bước nặng vừa; kính thay lớp khi inspect.

**Idle behaviors:** Lau kính, xếp rune, kiểm tra stylus và gõ khớp đồng.

**Signature animation:** Vẽ rune bằng stylus; rune khóa vào socket như bánh răng.

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

**Audio identity:** Kim loại nhỏ, bút ánh sáng và click khóa.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-stocky-01; goggles layer rig; glove/tool rig.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Brassel, an arcane-clockwork rune mechanic with a short broad silhouette, layered circular goggles, a leather apron fitted with removable rune plates, one mechanical repair glove and one luminous rune stylus. Use brass, dark wood, teal crystal and warm parchment colors. The character should feel methodical, skilled and safe rather than chaotic.

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
- Original character: Brassel Thợ Rune
- World: Arcane Clockwork
- Function to preserve: Kết nối cơ khí và rune
- Core silhouette principle: Thân thấp vai rộng, kính tròn nhiều lớp, tạp dề rune và hai tay công cụ khác nhau.
- Core limitation to preserve: Không chấp nhận raw executable code hoặc rune không có giới hạn.

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
