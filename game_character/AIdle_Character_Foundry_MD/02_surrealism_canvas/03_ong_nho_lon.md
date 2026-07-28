# Ông Nhỏ Lớn

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SC-NW-007` |
| World Profile | Surrealism Canvas |
| Character Class | `NPC_WORKER` |
| Species/Form | Kiến trúc sư tỷ lệ |
| Gameplay Role | Điều chỉnh tỷ lệ và không gian bên trong công trình |
| Rig Family | `Humanoid-small-01; scale animation chỉ ở visual layer, không đổi collider trực tiếp.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một kiến trúc sư thấp bé có chiếc mũ luôn giữ nguyên kích thước dù bản thân thay đổi khi đi qua cửa.

## 3. Vai trò trong thế giới

Ông Nhỏ Lớn được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Surrealism Canvas**.  
Phong cách thế giới: siêu thực có kiểm soát, anomaly theo vùng, portal, vật lý biến đổi nhưng vẫn dễ đọc.  
Bảng màu nền: pastel trung tính, xanh nhạt, hồng, vàng và cyan preview.

Vai trò chính của nhân vật là **Điều chỉnh tỷ lệ và không gian bên trong công trình**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân nhỏ, mũ kiến trúc cực cao, thước hai đầu và bước chân ngắn.

**Mô tả hình ảnh chi tiết:**  
Xám ấm, vàng nhạt, teal bụi; thước có hai mặt; mũ cao là nhận diện từ xa.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Chính xác
- Hài hước khô
- Hay phản biện khái niệm kích thước
- Thận trọng

**Phong cách hội thoại:** Dùng câu hỏi như “lớn với ai?”; giải thích bằng so sánh.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Preview tỷ lệ, thiết kế nội thất lớn hơn ngoại thất và cảnh báo navigation/collision.

### Giới hạn bắt buộc

Không cho scale vô hạn hoặc thay đổi kích thước đang ảnh hưởng ownership.

### Vị trí xuất hiện

Cửa phi lý, công trình nhiều lớp hoặc xưởng đo.

### Quan hệ gợi ý

Tranh luận vui với Kẻ Giữ Khung; hay nhờ Lụa Ngược kể lại kích thước cũ; dùng Gấp Bóng làm dấu đo.

## 7. Chuyển động và animation

**Locomotion:** Bước ngắn; thay scale theo cửa trong animation preview.

**Idle behaviors:** Đo mũ, đo bóng, so hai đầu thước và ghi số khác nhau.

**Signature animation:** Đi qua cửa; cơ thể lớn lên nhưng mũ vẫn giữ kích thước.

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

**Audio identity:** Thước gõ, bút chì và âm co giãn mềm.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-small-01; scale animation chỉ ở visual layer, không đổi collider trực tiếp.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Ông Nhỏ Lớn, a surreal scale architect with a very small rounded body and an impossibly tall architectural hat. His measuring tool has two ends that show different valid measurements. The body may appear to change scale when passing through doorways, but the hat remains constant. Use warm gray, pale yellow, dusty teal and restrained cyan preview lines.

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
- Original character: Ông Nhỏ Lớn
- World: Surrealism Canvas
- Function to preserve: Điều chỉnh tỷ lệ và không gian bên trong công trình
- Core silhouette principle: Thân nhỏ, mũ kiến trúc cực cao, thước hai đầu và bước chân ngắn.
- Core limitation to preserve: Không cho scale vô hạn hoặc thay đổi kích thước đang ảnh hưởng ownership.

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
