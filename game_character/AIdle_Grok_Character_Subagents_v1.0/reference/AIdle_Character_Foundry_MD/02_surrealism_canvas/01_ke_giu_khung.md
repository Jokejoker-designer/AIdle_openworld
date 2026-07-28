# Kẻ Giữ Khung

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SC-NG-005` |
| World Profile | Surrealism Canvas |
| Character Class | `NPC_GUIDE` |
| Species/Form | Thực thể trong khung tranh |
| Gameplay Role | Giải thích portal và Surreal Rule |
| Rig Family | `Humanoid-thin-01 + frame-root; frame là root phụ độc lập.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một người dẫn đường sống bên trong chiếc khung luôn đi cùng mình và chỉ mở cửa khi luật đã được hiểu.

## 3. Vai trò trong thế giới

Kẻ Giữ Khung được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Surrealism Canvas**.  
Phong cách thế giới: siêu thực có kiểm soát, anomaly theo vùng, portal, vật lý biến đổi nhưng vẫn dễ đọc.  
Bảng màu nền: pastel trung tính, xanh nhạt, hồng, vàng và cyan preview.

Vai trò chính của nhân vật là **Giải thích portal và Surreal Rule**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Khung chữ nhật nổi là hình chính; cơ thể mảnh nằm trong khung; một chi có thể bước ra ngoài trước.

**Mô tả hình ảnh chi tiết:**  
Khung ngà mờ, cơ thể xanh phai, mặt như nét cọ chưa hoàn thành; cyan chỉ dùng khi preview.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Kiên nhẫn
- Ẩn dụ
- Cẩn trọng
- Không vội kết luận

**Phong cách hội thoại:** Dùng hình ảnh, câu hỏi quan sát và ví dụ; tránh trả lời thay cho người chơi.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Đăng ký Surreal Rule, giải thích vùng ảnh hưởng và preview portal.

### Giới hạn bắt buộc

Không tự kích hoạt anomaly hoặc mở portal chưa được xác nhận.

### Vị trí xuất hiện

Cạnh portal, khung tranh lớn hoặc trung tâm vùng anomaly.

### Quan hệ gợi ý

Tôn trọng Lụa Ngược; thường tranh luận về tỷ lệ với Ông Nhỏ Lớn; chăm Gấp Bóng.

## 7. Chuyển động và animation

**Locomotion:** Khung lướt; chân bước lệch thời điểm; xoay cả khung khi đổi hướng.

**Idle behaviors:** Lau mép khung, vẽ một nét trong không khí, nhìn qua khung từ hai phía.

**Signature animation:** Một chân bước ra ngoài khung, khung xoay, phần còn lại theo sau.

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

**Audio identity:** Âm giấy căng, gỗ khẽ kêu và tiếng vọng nhẹ.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-thin-01 + frame-root; frame là root phụ độc lập.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create The Framekeeper, an original surreal guide character contained within a floating rectangular picture frame. The frame moves with the character and forms the dominant silhouette. Allow one limb to occasionally extend outside the frame before the body follows. Use matte ivory, faded blue, soft coral and cyan only for preview effects. The face should resemble a minimal unfinished brush drawing. Keep the design poetic but readable for isometric gameplay.

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
- Original character: Kẻ Giữ Khung
- World: Surrealism Canvas
- Function to preserve: Giải thích portal và Surreal Rule
- Core silhouette principle: Khung chữ nhật nổi là hình chính; cơ thể mảnh nằm trong khung; một chi có thể bước ra ngoài trước.
- Core limitation to preserve: Không tự kích hoạt anomaly hoặc mở portal chưa được xác nhận.

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
