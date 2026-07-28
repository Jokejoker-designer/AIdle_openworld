# Lụa Ngược

## 1. Metadata

| Trường | Giá trị |
|---|---|
| Character ID | `SC-NS-006` |
| World Profile | Surrealism Canvas |
| Character Class | `NPC_SOCIAL` |
| Species/Form | Người kể chuyện siêu thực |
| Gameplay Role | Thu thập ký ức và kể câu chuyện đảo chiều |
| Rig Family | `Humanoid-tall-01; 6–8 xương ribbon; shadow-expression shader độc lập.` |
| Status đề xuất | Concept / Production-ready specification |

## 2. Character Hook

> Một người kể chuyện có tóc và dải lụa luôn bay ngược hướng gió, còn chiếc bóng thể hiện cảm xúc trước cô.

## 3. Vai trò trong thế giới

Lụa Ngược được thiết kế để phục vụ trực tiếp cho vòng lặp gameplay của **Surrealism Canvas**.  
Phong cách thế giới: siêu thực có kiểm soát, anomaly theo vùng, portal, vật lý biến đổi nhưng vẫn dễ đọc.  
Bảng màu nền: pastel trung tính, xanh nhạt, hồng, vàng và cyan preview.

Vai trò chính của nhân vật là **Thu thập ký ức và kể câu chuyện đảo chiều**. Nhân vật phải tạo ra giá trị gameplay rõ ràng, nhưng không được trở thành một hệ thống tự trị có quyền thay đổi world state, ownership, inventory hoặc economy nếu chưa qua authority và confirmation.

## 4. Thiết kế hình thể và silhouette

**Silhouette chủ đạo:** Thân dài mềm, nhiều dải vải hướng lên, tóc kéo ngược và bóng là lớp nhận diện phụ.

**Mô tả hình ảnh chi tiết:**  
Vật liệu watercolor low-poly; tím nhạt, xanh phấn, ngà ấm; không dùng chi tiết nhỏ dày đặc.

### Yêu cầu khả năng đọc

- Nhận diện được ở góc camera three-quarter/isometric.
- Có ít nhất một đặc điểm nhận diện rõ từ phía sau.
- Tối đa ba nhóm màu chính.
- Không dùng chi tiết quá nhỏ làm đặc điểm nhận diện chính.
- Không dùng photorealism hoặc vật liệu phá vỡ style profile.
- Khi thu nhỏ còn khoảng 10–15% chiều cao màn hình, silhouette vẫn phải phân biệt được.

## 5. Tính cách

- Trầm lặng
- Mơ màng
- Quan sát tốt
- Không khẳng định ký ức duy nhất

**Phong cách hội thoại:** Kể từ kết thúc về khởi đầu; ngắt câu có chủ ý; đưa hai cách hiểu.

Tính cách chỉ điều chỉnh cách biểu đạt, nhịp hội thoại và lựa chọn câu chữ. Nó không được thay đổi giá, quyền, chính sách, ownership hoặc dùng cảm xúc để gây áp lực cho người chơi.

## 6. Gameplay

### Năng lực chính

Mở memory scene, cho xem hai phiên bản sự kiện và hỗ trợ nhiệm vụ lựa chọn.

### Giới hạn bắt buộc

Không xác định phiên bản nào đúng thay người chơi và không sửa lịch sử canonical.

### Vị trí xuất hiện

Bờ sông đổi màu, thư viện ký ức hoặc vùng có bóng chuyển động.

### Quan hệ gợi ý

Đồng hành cùng Kẻ Giữ Khung; tò mò về kiến trúc của Ông Nhỏ Lớn; để Gấp Bóng đậu trên vai.

## 7. Chuyển động và animation

**Locomotion:** Bước chậm, dải lụa đi trước; quay đầu sau bóng.

**Idle behaviors:** Chạm bóng, gấp một dải lụa, nhìn lại nơi vừa đi qua.

**Signature animation:** Bóng cười trước; khuôn mặt sau đó mới đổi theo.

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

**Audio identity:** Vải mềm, tiếng nước ngược và giọng có đuôi vang rất ngắn.

Âm thanh phải ngắn, mềm và không gây mệt khi lặp lại. Tránh dùng âm cảnh báo gắt cho trạng thái thông thường.

## 9. Rig và yêu cầu kỹ thuật

- Rig family: `Humanoid-tall-01; 6–8 xương ribbon; shadow-expression shader độc lập.`
- Collision ưu tiên capsule hoặc hull đơn giản.
- VFX/Aura tách khỏi mesh chính.
- Có LOD0, LOD1 và LOD2/billboard.
- Các prop quan trọng cần socket riêng.
- Không nhúng logic gameplay trực tiếp vào animation.
- Animation event chỉ phát signal; hệ thống authority quyết định tác động thật.

## 10. Prompt sản xuất nhân vật

```text
Create Lụa Ngược, a dreamy surreal storyteller whose long fabric ribbons and hair flow upward instead of downward. Her shadow should display an expression a moment before her face does. Use a soft elongated silhouette, watercolor-like low-poly materials, muted lavender, pale blue and warm ivory. She must feel mysterious and calm rather than frightening.

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
- Original character: Lụa Ngược
- World: Surrealism Canvas
- Function to preserve: Thu thập ký ức và kể câu chuyện đảo chiều
- Core silhouette principle: Thân dài mềm, nhiều dải vải hướng lên, tóc kéo ngược và bóng là lớp nhận diện phụ.
- Core limitation to preserve: Không xác định phiên bản nào đúng thay người chơi và không sửa lịch sử canonical.

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
