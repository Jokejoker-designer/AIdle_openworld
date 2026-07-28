# Mộc Ông

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SV-SA-020` |
| World Profile | Spirit Valley |
| Character Class | `SPIRIT_ENTITY` |
| Species/Form | Rùa gốc cây cổ |
| Gameplay Role | Ghi nhớ lịch sử khu rừng |
| Rig Family | `Large-turtle-spirit-01; shell garden sockets.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một rùa linh hồn già có khu vườn nhỏ mọc trên mai gốc cây.

## 3. Vai trò trong thế giới

Mộc Ông được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Spirit Valley**.  
Phong cách thế giới: thần thoại phương Đông, tranh thủy mặc low-poly, linh vật, nghi thức và phục hồi thiên nhiên.  
Bảng màu nền: xanh ngọc, xám mực, vàng đèn lồng, hồng sen và trắng mây.

Vai trò chính của nhân vật là **Ghi nhớ lịch sử khu rừng**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân rùa lớn, mai gốc cây, cây non trên lưng và đầu hiền nhỏ.

**Mô tả hình ảnh chi tiết:**  
Nâu vỏ cây, xanh rêu, xám đá; nấm và chồi là cụm lớn.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Điềm tĩnh
- Khôn ngoan
- Chậm
- Không thích vội vàng

**Phong cách hội thoại:** Câu chậm, dài vừa; kể lịch sử qua vật chứng.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Kể lịch sử vùng, mở seed cổ và mang khu vườn mini.

### Giới hạn bắt buộc

Chỉ xuất hiện khi môi trường đạt mức phục hồi; không cho phần thưởng nếu điều kiện chưa đủ.

### Vị trí xuất hiện

Rừng cổ, bờ hồ, nơi phục hồi hoàn chỉnh.

### Quan hệ gợi ý

Cho Vân Hồ nghỉ; trò chuyện với Đăng Tâm; cố vấn Trúc Nhi.

## 7. Chuyển động và animation

**Locomotion:** Rất chậm, ổn định; cây trên mai lay theo bước.

**Idle behaviors:** Ngủ, rêu mọc nhẹ, nấm phát sáng ngắn.

**Signature animation:** Cúi đầu; vòng tuổi gỗ trên mai hiện thành ký ức.

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

**Audio identity:** Gỗ sâu, đất, lá và tiếng thở trầm.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Large-turtle-spirit-01; shell garden sockets.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Mộc Ông, an ancient gentle turtle spirit whose shell resembles an old tree stump. Grow moss, small mushrooms and one young sapling on the shell. Use rounded low-poly forms, muted bark brown, moss green and warm stone gray. The face should be simple, wise and friendly. Avoid realistic reptile detail.

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
- Original character: Mộc Ông
- World: Spirit Valley
- Function to preserve: Ghi nhớ lịch sử khu rừng
- Core silhouette principle: Thân rùa lớn, mai gốc cây, cây non trên lưng và đầu hiền nhỏ.
- Core limitation to preserve: Chỉ xuất hiện khi môi trường đạt mức phục hồi; không cho phần thưởng nếu điều kiện chưa đủ.

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
