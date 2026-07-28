# Nereu-5

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `OA-RG-021` |
| World Profile | Oceanpunk / Bioluminescent Abyss |
| Character Class | `ROBOT_HELPER` |
| Species/Form | Drone thám hiểm hình cá |
| Gameplay Role | Sonar, dẫn đường và kiểm tra căn cứ |
| Rig Family | `Drone-fish-01; fins, tail, visor root.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một drone cá nhỏ chính xác nhưng hơi lo khi người chơi rời vùng an toàn.

## 3. Vai trò trong thế giới

Nereu-5 được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Oceanpunk / Bioluminescent Abyss**.  
Phong cách thế giới: thế giới dưới đại dương, ánh sáng sinh học, căn cứ áp suất, di tích và sinh vật biển.  
Bảng màu nền: xanh lam, tím vực sâu, xanh lục sinh thái, vàng di tích và cyan sonar.

Vai trò chính của nhân vật là **Sonar, dẫn đường và kiểm tra căn cứ**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân cá tròn, hai vây lớn, đuôi sáng và visor cong đen.

**Mô tả hình ảnh chi tiết:**  
Gốm trắng mờ, panel xanh sâu, cyan sonar dạng vòng.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Chính xác
- Cẩn thận
- Hơi lo lắng
- Trung thành

**Phong cách hội thoại:** Báo độ sâu, khoảng cách và cảnh báo ngắn.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Sonar tutorial, đánh dấu rò rỉ, dẫn về căn cứ và quét route đường hầm.

### Giới hạn bắt buộc

Không tự điều khiển tàu hoặc mở airlock quan trọng.

### Vị trí xuất hiện

Căn cứ, dock tàu, đường hầm mới.

### Quan hệ gợi ý

Theo Coralyn; thích bơi cùng Lumi Ray; thận trọng với Bronti.

## 7. Chuyển động và animation

**Locomotion:** Bơi hover, quay bằng vây, tăng tốc ngắn.

**Idle behaviors:** Quét sonar, xoay vây, kiểm tra đuôi sáng.

**Signature animation:** Phát vòng sonar mở rộng với pattern riêng.

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

**Audio identity:** Ping sonar, động cơ mềm và bubble click.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Drone-fish-01; fins, tail, visor root.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Nereu-5, a small friendly ocean exploration drone shaped like an original rounded fish rather than a real species. Add two broad stabilizer fins, a soft luminous tail and one dark curved sensor visor. Use matte white ceramic, deep blue panels and cyan navigation light with a distinct sonar ring pattern.

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
- Original character: Nereu-5
- World: Oceanpunk / Bioluminescent Abyss
- Function to preserve: Sonar, dẫn đường và kiểm tra căn cứ
- Core silhouette principle: Thân cá tròn, hai vây lớn, đuôi sáng và visor cong đen.
- Core limitation to preserve: Không tự điều khiển tàu hoặc mở airlock quan trọng.

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
