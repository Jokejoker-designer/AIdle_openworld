# Kito Thụ Phấn

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SPH-RH-011` |
| World Profile | Solarpunk Haven |
| Character Class | `ROBOT_HELPER` |
| Species/Form | Drone thụ phấn dạng hạt |
| Gameplay Role | Hỗ trợ cây trồng và đa dạng sinh học |
| Rig Family | `Drone-seed-01; 2 cánh + 6 chân gấp.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một drone nhỏ hình hạt giống bay bằng hai cánh lá và phản ứng mạnh với khu vườn đa dạng.

## 3. Vai trò trong thế giới

Kito Thụ Phấn được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Solarpunk Haven**.  
Phong cách thế giới: công nghệ xanh, kiến trúc hữu cơ, sinh thái phản ứng, cộng đồng và phục hồi môi trường.  
Bảng màu nền: xanh lá, vàng mặt trời, trắng kem, gỗ sáng và cyan giao diện.

Vai trò chính của nhân vật là **Hỗ trợ cây trồng và đa dạng sinh học**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân hạt, hai cánh lá lớn, sáu chân gấp và đèn hổ phách.

**Mô tả hình ảnh chi tiết:**  
Bioplastic kem, viền xanh, cánh trong mờ, ánh sáng amber; không giống ong thật.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Hiếu động
- Tò mò
- Nhạy với hoa
- Dễ bị phân tâm

**Phong cách hội thoại:** Không nói; biểu tượng, âm rung và nhịp cánh.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Đánh dấu cây thiếu thụ phấn, mang phấn và theo dõi đa dạng hoa.

### Giới hạn bắt buộc

Không hoạt động ở vùng độc hại; không tự sửa chỉ số sinh thái.

### Vị trí xuất hiện

Vườn hoa, trạm sạc, nhà kính và nông trại.

### Quan hệ gợi ý

Theo Luma khi khảo sát; thường đậu trên mũ Sora; chơi với Mầm Tám.

## 7. Chuyển động và animation

**Locomotion:** Hover, lượn ngắn, đáp bằng sáu chân.

**Idle behaviors:** Quét hoa, rung cánh, lau cảm biến và cuộn chân.

**Signature animation:** Bay vòng xoắn quanh cụm hoa rồi phát biểu tượng hoàn tất.

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

**Audio identity:** Rung cánh mềm, ping amber và tiếng chạm lá.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Drone-seed-01; 2 cánh + 6 chân gấp.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Kito Thụ Phấn, a friendly seed-shaped pollination drone for a solarpunk world. Avoid copying a real bee exactly. Use a smooth seed pod body, two broad translucent leaf wings and six small foldable landing legs. Materials should be matte cream bioplastic, green edges and warm amber lights. Make it playful, non-industrial and readable at small scale.

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
- Original character: Kito Thụ Phấn
- World: Solarpunk Haven
- Function to preserve: Hỗ trợ cây trồng và đa dạng sinh học
- Core silhouette principle: Thân hạt, hai cánh lá lớn, sáu chân gấp và đèn hổ phách.
- Core limitation to preserve: Không hoạt động ở vùng độc hại; không tự sửa chỉ số sinh thái.

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
