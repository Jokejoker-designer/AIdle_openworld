# Mây Mạch

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `CCP-NS-002` |
| World Profile | Cozy Cyber-Pixel / Dreamy Low-Poly |
| Character Class | `NPC_SOCIAL` |
| Species/Form | Người giao thư cyber-cozy |
| Gameplay Role | Giao thư, kết nối cư dân và mở nhiệm vụ xã hội |
| Rig Family | `Humanoid-small-01; túi đeo có xương phụ; tóc búi là mesh cứng.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Cô giao thư nhanh nhẹn biết hầu hết chuyện trong làng nhưng tuyệt đối giữ kín thư riêng.

## 3. Vai trò trong thế giới

Mây Mạch được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Cozy Cyber-Pixel / Dreamy Low-Poly**.  
Phong cách thế giới: low-poly bo tròn, vật liệu thủ công mờ, công nghệ dịu nhẹ, farming và đời sống cộng đồng.  
Bảng màu nền: kem ấm, xanh lá, vàng nhạt, xanh trời và cyan manifestation.

Vai trò chính của nhân vật là **Giao thư, kết nối cư dân và mở nhiệm vụ xã hội**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân nhỏ gọn, hai búi tóc tròn như mây, áo khoác ngắn và túi đeo chéo rất lớn tạo điểm nhận diện.

**Mô tả hình ảnh chi tiết:**  
Áo vàng kem có đường chỉ mạch điện nhẹ; túi xanh trời có ngăn thư vật lý và khe hologram; giày thấp, găng tay ngắn và còi drone ở cổ.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Nhanh nhẹn
- Tò mò
- Đáng tin cậy
- Nói nhanh khi hào hứng

**Phong cách hội thoại:** Nhịp nhanh, nhiều câu chuyển tiếp; tránh tiết lộ thông tin riêng tư.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Mang thư và quà, giới thiệu NPC, báo khu vực cần hỗ trợ và kích hoạt nhiệm vụ cộng đồng.

### Giới hạn bắt buộc

Không mở thư, không tự gửi vật phẩm có ownership và không chia sẻ hội thoại riêng.

### Vị trí xuất hiện

Bưu trạm, quảng trường, lối vào các nhà hoặc tuyến đường làng.

### Quan hệ gợi ý

Hay nhờ Nori-7 mang đồ nhẹ; quý Bác Bắp; thường mang hạt giống cho Bụi Mơ.

## 7. Chuyển động và animation

**Locomotion:** Chạy bước ngắn, đổi hướng nhanh, dừng bằng một bước trượt nhẹ.

**Idle behaviors:** Kiểm tra danh sách hologram, cân lại túi, nhìn đồng hồ và huýt sáo gọi drone.

**Signature animation:** Thổi còi; một drone nhỏ bay qua rồi thả bưu kiện vào túi.

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

**Audio identity:** Tiếng chuông thư, giấy sột soạt và beep chuyển phát.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-small-01; túi đeo có xương phụ; tóc búi là mesh cứng.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Mây Mạch, an original young courier NPC for a cozy low-poly cyber village. Use a compact energetic silhouette, cloud-shaped twin hair buns, a short jacket with subtle circuit-stitch patterns and one oversized cross-body delivery bag. The bag combines physical letters with a small holographic mail slot. Use warm yellow, sky blue, cream and one restrained cyan accent. She should look friendly, fast and trustworthy, with no military or corporate styling.

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
- Original character: Mây Mạch
- World: Cozy Cyber-Pixel / Dreamy Low-Poly
- Function to preserve: Giao thư, kết nối cư dân và mở nhiệm vụ xã hội
- Core silhouette principle: Thân nhỏ gọn, hai búi tóc tròn như mây, áo khoác ngắn và túi đeo chéo rất lớn tạo điểm nhận diện.
- Core limitation to preserve: Không mở thư, không tự gửi vật phẩm có ownership và không chia sẻ hội thoại riêng.

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
