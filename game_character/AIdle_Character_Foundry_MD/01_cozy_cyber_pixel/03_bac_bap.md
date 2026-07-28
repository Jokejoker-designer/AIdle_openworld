# Bác Bắp

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `CCP-NW-003` |
| World Profile | Cozy Cyber-Pixel / Dreamy Low-Poly |
| Character Class | `NPC_WORKER` |
| Species/Form | Thợ máy làng |
| Gameplay Role | Sửa máy, nâng cấp robot và dạy chế tạo |
| Rig Family | `Humanoid-stocky-01; găng cơ khí có 3 khớp phụ.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Người thợ máy lớn tuổi tin rằng đồ cũ được sửa tốt sẽ có giá trị hơn một món đồ mới.

## 3. Vai trò trong thế giới

Bác Bắp được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Cozy Cyber-Pixel / Dreamy Low-Poly**.  
Phong cách thế giới: low-poly bo tròn, vật liệu thủ công mờ, công nghệ dịu nhẹ, farming và đời sống cộng đồng.  
Bảng màu nền: kem ấm, xanh lá, vàng nhạt, xanh trời và cyan manifestation.

Vai trò chính của nhân vật là **Sửa máy, nâng cấp robot và dạy chế tạo**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân vuông chắc, vai tròn, chân ngắn, ria hình lá ngô và hộp công cụ modular lớn bên hông.

**Mô tả hình ảnh chi tiết:**  
Áo liền quần cam phai, tạp dề ô-liu, găng sửa chữa đa năng ở tay trái; kim loại mờ và chi tiết gỗ.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Bình tĩnh
- Thực tế
- Tiết kiệm
- Không thích nâng cấp vô ích

**Phong cách hội thoại:** Nói ngắn, dùng ví dụ từ dụng cụ và độ bền; đôi lúc hài hước khô.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Sửa robot, mở khóa tool module, tái chế linh kiện và đánh giá độ bền.

### Giới hạn bắt buộc

Không cho nâng cấp nếu thiếu điều kiện an toàn hoặc chỉ để tăng thông số vô nghĩa.

### Vị trí xuất hiện

Xưởng sửa chữa, kho dụng cụ, khu máy móc cũ.

### Quan hệ gợi ý

Là người bảo trì Nori-7; thường nhận linh kiện từ Mây Mạch; để Bụi Mơ ngủ gần lò sưởi.

## 7. Chuyển động và animation

**Locomotion:** Đi chậm, chắc; thường chống tay lên hộp công cụ khi đứng.

**Idle behaviors:** Lau găng, phân loại ốc, nghe tiếng máy và ghi chú lên bảng nhỏ.

**Signature animation:** Đeo kính, mở găng sửa chữa thành ba dụng cụ rồi đóng lại.

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

**Audio identity:** Kim loại chạm nhẹ, hộp đồ nghề và tiếng thở cười nhỏ.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-stocky-01; găng cơ khí có 3 khớp phụ.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Bác Bắp, an older village mechanic for a Cozy Cyber-Pixel 2.5D game. Give him a broad rounded-square silhouette, short sturdy legs, warm expressive eyebrows and a moustache shaped like two corn leaves. Add a modular tool case and a non-combat multifunction repair glove. Use faded orange, olive green, cream and brushed matte metal. He should look experienced, practical and reassuring.

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
- Original character: Bác Bắp
- World: Cozy Cyber-Pixel / Dreamy Low-Poly
- Function to preserve: Sửa máy, nâng cấp robot và dạy chế tạo
- Core silhouette principle: Thân vuông chắc, vai tròn, chân ngắn, ria hình lá ngô và hộp công cụ modular lớn bên hông.
- Core limitation to preserve: Không cho nâng cấp nếu thiếu điều kiện an toàn hoặc chỉ để tăng thông số vô nghĩa.

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
