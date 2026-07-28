# Coralyn

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `OA-NS-023` |
| World Profile | Oceanpunk / Bioluminescent Abyss |
| Character Class | `NPC_SOCIAL` |
| Species/Form | Nhà lưu trữ di tích |
| Gameplay Role | Nghiên cứu lịch sử đại dương |
| Rig Family | `Humanoid-medium-01 + swim set; archive-cylinder socket.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một nhà khảo cổ dưới biển luôn ghi provenance trước khi chạm vào hiện vật.

## 3. Vai trò trong thế giới

Coralyn được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Oceanpunk / Bioluminescent Abyss**.  
Phong cách thế giới: thế giới dưới đại dương, ánh sáng sinh học, căn cứ áp suất, di tích và sinh vật biển.  
Bảng màu nền: xanh lam, tím vực sâu, xanh lục sinh thái, vàng di tích và cyan sonar.

Vai trò chính của nhân vật là **Nghiên cứu lịch sử đại dương**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Bộ đồ lặn nhẹ, phiến san hô, mũ kính hở mặt và ống lưu trữ sau lưng.

**Mô tả hình ảnh chi tiết:**  
Xanh biển, cam san hô, kem, visor trong; chi tiết gọn.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Tò mò
- Cẩn trọng
- Có đạo đức
- Đưa nhiều giả thuyết

**Phong cách hội thoại:** Phân biệt dữ kiện và suy luận; nói rõ độ tin cậy.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Giải mã di tích, mở quest khảo cổ, lưu provenance và phân biệt bản sao.

### Giới hạn bắt buộc

Không cho bán hiện vật chưa xác minh hoặc lấy đồ không rõ quyền sở hữu.

### Vị trí xuất hiện

Di tích, archive dome, tàu khảo sát.

### Quan hệ gợi ý

Dùng Nereu-5 để quét; quan sát Lumi Ray; nghiên cứu Bronti mà không xâm hại.

## 7. Chuyển động và animation

**Locomotion:** Bơi bằng thruster nhỏ; đi trong căn cứ.

**Idle behaviors:** Lau tablet, chụp mẫu, ghi chú ống lưu trữ.

**Signature animation:** Quét hiện vật; provenance layers xuất hiện quanh nó.

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

**Audio identity:** Tablet ping, bọt khí và giọng qua comm nhẹ.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-medium-01 + swim set; archive-cylinder socket.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Coralyn, an oceanpunk ruins archivist wearing a light exploration suit with stylized coral-shaped protective plates. Keep the face visible inside a clear partial helmet. Add a cylindrical archive case and a compact scanning tablet. Use sea green, warm coral orange, cream and dark ocean blue.

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
- Original character: Coralyn
- World: Oceanpunk / Bioluminescent Abyss
- Function to preserve: Nghiên cứu lịch sử đại dương
- Core silhouette principle: Bộ đồ lặn nhẹ, phiến san hô, mũ kính hở mặt và ống lưu trữ sau lưng.
- Core limitation to preserve: Không cho bán hiện vật chưa xác minh hoặc lấy đồ không rõ quyền sở hữu.

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
