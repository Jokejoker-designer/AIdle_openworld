# Bụi Mơ

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `CCP-CT-004` |
| World Profile | Cozy Cyber-Pixel / Dreamy Low-Poly |
| Character Class | `CREATURE_TAMEABLE` |
| Species/Form | Mèo-bụi cây |
| Gameplay Role | Thú cưng tìm vật liệu nhỏ và hỗ trợ cảm giác gắn bó |
| Rig Family | `Quadruped-small-01; đuôi và ba lá là xương phụ.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một sinh vật nhỏ trông như bụi cây khi ngủ và thường giấu hạt giống ở nơi không ai ngờ.

## 3. Vai trò trong thế giới

Bụi Mơ được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Cozy Cyber-Pixel / Dreamy Low-Poly**.  
Phong cách thế giới: low-poly bo tròn, vật liệu thủ công mờ, công nghệ dịu nhẹ, farming và đời sống cộng đồng.  
Bảng màu nền: kem ấm, xanh lá, vàng nhạt, xanh trời và cyan manifestation.

Vai trò chính của nhân vật là **Thú cưng tìm vật liệu nhỏ và hỗ trợ cảm giác gắn bó**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân tròn như mèo, bốn chân ngắn, đuôi nhánh cây và ba lá lớn trên lưng.

**Mô tả hình ảnh chi tiết:**  
Cụm lá low-poly mềm; mặt kem; đuôi nâu; ba lá đổi sắc nhẹ theo mùa nhưng không nhấp nháy.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Nhút nhát
- Tò mò
- Thích nơi ấm
- Tin tưởng chậm

**Phong cách hội thoại:** Không nói; giao tiếp bằng tiếng rung, đuôi và cử động lá.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Tìm hạt giống rơi, đánh dấu vật liệu nhỏ và ngủ cạnh cây để tạo hiệu ứng trang trí dịu.

### Giới hạn bắt buộc

Không tăng sản lượng bắt buộc, không tự lấy vật phẩm có ownership.

### Vị trí xuất hiện

Bụi cây, cạnh máy móc ấm, bên ao hoặc dưới hiên nhà.

### Quan hệ gợi ý

Thích Nori-7; nhận hạt giống từ Mây Mạch; ngủ trong xưởng Bác Bắp.

## 7. Chuyển động và animation

**Locomotion:** Bước nhỏ, chạy vụt ngắn, cuộn tròn khi sợ.

**Idle behaviors:** Rung lá, đào nhẹ đất, ngửi hạt giống và ngủ thành bụi.

**Signature animation:** Cuộn tròn; các lá khép lại và biến nó thành bụi cây nhỏ.

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

**Audio identity:** Tiếng lá xào xạc, meo rất nhỏ và tiếng hạt lăn.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Quadruped-small-01; đuôi và ba lá là xương phụ.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Bụi Mơ, a tiny tameable plant-cat creature for a cozy low-poly world. Give it a round cat-like body covered in soft stylized leaf clusters, four short legs, a flexible twig tail and three large seasonal leaves growing from its back. When curled up, it should resemble a harmless garden bush. Use warm green, cream and soft peach accents. Keep the face simple, readable and highly original.

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
- Original character: Bụi Mơ
- World: Cozy Cyber-Pixel / Dreamy Low-Poly
- Function to preserve: Thú cưng tìm vật liệu nhỏ và hỗ trợ cảm giác gắn bó
- Core silhouette principle: Thân tròn như mèo, bốn chân ngắn, đuôi nhánh cây và ba lá lớn trên lưng.
- Core limitation to preserve: Không tăng sản lượng bắt buộc, không tự lấy vật phẩm có ownership.

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
