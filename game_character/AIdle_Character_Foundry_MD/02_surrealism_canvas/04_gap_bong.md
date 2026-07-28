# Gấp Bóng

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SC-CA-008` |
| World Profile | Surrealism Canvas |
| Character Class | `CREATURE_AMBIENT` |
| Species/Form | Chim origami bằng bóng |
| Gameplay Role | Gấp bóng thành chỉ dẫn tạm thời |
| Rig Family | `Origami-bird-01; blendshape/fold bones; không dùng feather rig.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một con chim không đập cánh mà tự gấp và mở hình dạng để trượt qua thế giới.

## 3. Vai trò trong thế giới

Gấp Bóng được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Surrealism Canvas**.  
Phong cách thế giới: siêu thực có kiểm soát, anomaly theo vùng, portal, vật lý biến đổi nhưng vẫn dễ đọc.  
Bảng màu nền: pastel trung tính, xanh nhạt, hồng, vàng và cyan preview.

Vai trò chính của nhân vật là **Gấp bóng thành chỉ dẫn tạm thời**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân chim giấy nhiều mặt phẳng, đuôi tam giác, cánh gấp lớn và mắt sáng nhỏ.

**Mô tả hình ảnh chi tiết:**  
Xanh xám đậm thay vì đen tuyệt đối; một viền phản chiếu nhạt; không hòa mất vào nền.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Tò mò
- Nhanh
- Khó bắt
- Thích anomaly

**Phong cách hội thoại:** Không nói; giao tiếp bằng gấp hình và hướng nhìn.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Đánh dấu đường bí mật, tạo bóng cầu thang tạm trong preview và dẫn đến anomaly.

### Giới hạn bắt buộc

Không tạo collision lâu dài và không thay đổi geometry canonical.

### Vị trí xuất hiện

Rìa anomaly, portal chưa mở, nơi có bóng bất thường.

### Quan hệ gợi ý

Đi theo Kẻ Giữ Khung; đậu trên vai Lụa Ngược; bị Ông Nhỏ Lớn dùng làm mốc đo.

## 7. Chuyển động và animation

**Locomotion:** Gấp, mở, lướt; không flap.

**Idle behaviors:** Gấp thành tam giác nhỏ, mở thành chim rồi xoay quanh bóng.

**Signature animation:** Tự gấp thành mũi tên bóng chỉ đường.

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

**Audio identity:** Giấy gấp, tiếng gió nhỏ và âm lật trang.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Origami-bird-01; blendshape/fold bones; không dùng feather rig.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Gấp Bóng, a small surreal origami bird made from soft dimensional shadow. It moves by folding and unfolding its body rather than flapping. Use deep blue gray instead of pure black, with one pale reflective edge and tiny luminous eyes. Its silhouette must remain readable against dark and bright backgrounds. Show folded idle, gliding, pointing and unfolding poses.

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
- Original character: Gấp Bóng
- World: Surrealism Canvas
- Function to preserve: Gấp bóng thành chỉ dẫn tạm thời
- Core silhouette principle: Thân chim giấy nhiều mặt phẳng, đuôi tam giác, cánh gấp lớn và mắt sáng nhỏ.
- Core limitation to preserve: Không tạo collision lâu dài và không thay đổi geometry canonical.

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
