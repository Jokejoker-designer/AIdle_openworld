# Luma Tán Lá

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SPH-NG-009` |
| World Profile | Solarpunk Haven |
| Character Class | `NPC_GUIDE` |
| Species/Form | Nhà sinh thái học |
| Gameplay Role | Giải thích cân bằng sinh thái |
| Rig Family | `Humanoid-medium-01; tóc canopy là 3 cụm mesh; scanner có rig riêng.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một nhà sinh thái học lạc quan luôn đưa ra nhiều phương án thay vì một đáp án duy nhất.

## 3. Vai trò trong thế giới

Luma Tán Lá được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Solarpunk Haven**.  
Phong cách thế giới: công nghệ xanh, kiến trúc hữu cơ, sinh thái phản ứng, cộng đồng và phục hồi môi trường.  
Bảng màu nền: xanh lá, vàng mặt trời, trắng kem, gỗ sáng và cyan giao diện.

Vai trò chính của nhân vật là **Giải thích cân bằng sinh thái**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Tóc như tán cây, áo choàng ngắn hình lá, cảm biến chồi trên vai và vòng đo sinh thái.

**Mô tả hình ảnh chi tiết:**  
Xanh lá, vàng nắng, kem, kính trong; cyan rất hạn chế ở scanner.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Lạc quan
- Thực tế
- Minh bạch
- Không áp đặt

**Phong cách hội thoại:** Giải thích trade-off bằng câu rõ; luôn nêu lợi ích và chi phí.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Hướng dẫn Eco Scan, đánh giá khu vực và đề xuất phục hồi.

### Giới hạn bắt buộc

Không tự áp dụng eco add-on hoặc che giấu hậu quả môi trường.

### Vị trí xuất hiện

Trạm sinh thái, vườn cộng đồng, khu đất cần phục hồi.

### Quan hệ gợi ý

Làm việc cùng Sora; theo dõi Kito; coi Mầm Tám là chỉ báo sống.

## 7. Chuyển động và animation

**Locomotion:** Đi nhẹ, dừng quan sát cây; scanner xoay theo hướng nhìn.

**Idle behaviors:** Chạm cảm biến vai, xem vòng đo, ghi chú mẫu lá.

**Signature animation:** Mở vòng scanner thành bản đồ sinh thái tròn.

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

**Audio identity:** Chuông gió, tiếng lá và beep mềm.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-medium-01; tóc canopy là 3 cụm mesh; scanner có rig riêng.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Luma Tán Lá, a solarpunk ecologist guide with a canopy-shaped hairstyle, a short leaf-inspired coat and small plant-like environmental sensors on both shoulders. Give her a circular handheld ecosystem scanner. Use leaf green, sunlight yellow, cream and clear glass materials with minimal cyan interface light. She should feel optimistic, competent and practical.

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
- Original character: Luma Tán Lá
- World: Solarpunk Haven
- Function to preserve: Giải thích cân bằng sinh thái
- Core silhouette principle: Tóc như tán cây, áo choàng ngắn hình lá, cảm biến chồi trên vai và vòng đo sinh thái.
- Core limitation to preserve: Không tự áp dụng eco add-on hoặc che giấu hậu quả môi trường.

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
