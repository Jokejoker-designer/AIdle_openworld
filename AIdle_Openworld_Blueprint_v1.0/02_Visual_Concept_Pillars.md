# AIdle Openworld – Visual Concept Pillars & Art Direction System

**Phiên bản:** 1.0  
**Trạng thái:** Khóa cứng – Mọi Agent phải tuân thủ

---

## 1. Hệ thống Art Direction (Bắt buộc chọn từ đầu)

Khi người chơi tạo nhân vật / bắt đầu thế giới, họ chọn **một Concept chính**. Concept này được lưu vào World Metadata và **phải được toàn bộ hệ thống sinh nội dung tôn trọng**.

### 1.1. Cozy Cyber-Pixel / Dreamy Low-Poly (Mặc định khuyến nghị)
- **Mô tả:** Giữ nguyên cảm giác thân thuộc, đáng yêu của Stardew Valley nhưng nâng cấp lên đồ họa 3D khối thấp (Low-Poly) mịn màng.
- **Đặc điểm hình ảnh:**
  - Màu sắc tươi sáng, rực rỡ, mang hơi hướng hoạt hình.
  - Hình khối tròn trịa, mềm mại, ít cạnh sắc.
  - Ánh sáng ấm, soft shadows.
  - Chi tiết cyber nhẹ (đèn neon nhỏ, hologram UI mờ ảo) nhưng không phá vỡ sự thư giãn.
- **Mục tiêu cảm xúc:** Thư giãn, kết nối, ấm áp, muốn ở lại lâu.

### 1.2. Surrealism Canvas (Chủ nghĩa siêu thực)
- **Mô tả:** Vì người chơi có thể tạo bất cứ thứ gì từ văn bản, thế giới cho phép kiến trúc lơ lửng, sông đổi màu, sinh vật kỳ dị, vật lý siêu thực.
- **Đặc điểm hình ảnh:**
  - Tỷ lệ bất thường, floating islands, kiến trúc defying gravity.
  - Material có thể color-shifting, transparent, hoặc có pattern động.
  - Giao thoa mạnh giữa thực và ảo.
- **Sử dụng:** Khi người chơi chủ động yêu cầu yếu tố siêu thực, hoặc khi Art Style được chọn là Surrealism.

### 1.3. Các Concept mở rộng (có thể thêm sau)
- Cyberpunk Dense
- Pastoral Fantasy
- Soft Sci-Fi
- v.v.

**Quy tắc:** Agent-Voxel, Agent-Asset, Agent-Companion (visual), Agent-Executor **bắt buộc** phải query Art Style hiện tại trước khi sinh bất kỳ nội dung nào.

---

## 2. Pipeline Manifestation (Signature của AIdle Openworld)

Đây là **Hard Constraint** thay thế hoàn toàn việc “đùng một cái xuất hiện”.

### Các giai đoạn bắt buộc:

1. **Intent Capture**  
   Companion nhận Structured World Prompt đã validate.

2. **Device Activation**  
   Companion giơ **Manifestation Device** (Light Brush hoặc Holographic Projector) lên.

3. **Wireframe Stage**  
   Đối tượng xuất hiện dưới dạng đường lưới ánh sáng (glowing wireframe). Có thể nhìn xuyên qua.

4. **Hologram Stage**  
   Chuyển thành hình ảnh ảo bán trong suốt, có độ sáng nhẹ, vẫn chưa có collision vật lý đầy đủ.

5. **Progressive Materialization (Construction Progress 0.0 → 1.0)**  
   - 0.0 – 0.3: Scaffold ánh sáng + khung cơ bản  
   - 0.3 – 0.7: Solid low-poly dần xuất hiện theo Art Style  
   - 0.7 – 1.0: Detail, texture, màu sắc cuối cùng, VFX hoàn thiện  

6. **Finalization**  
   Collision/physics kích hoạt đầy đủ, Provenance được gắn, sự kiện “manifestation_completed” được phát ra.

**Hiệu ứng đặc trưng:**  
Tia sáng (scanning beam) từ Manifestation Device của Companion “vẽ” nên các giai đoạn trên. Particle trails + soft energy blooms theo màu của Art Style và Mood Aura hiện tại.

---

## 3. Emotional AI Symbiosis (Cảm xúc cộng sinh)

- Mỗi Companion có **Emotional State** (Joy, Calm, Curious, Empathetic, Excited, Protective, Melancholy…).
- **Mood Aura**: Hệ thống particle + light quanh Companion thay đổi màu sắc và cường độ theo state.
  - Ví dụ: Calm = xanh dương dịu, Excited = vàng cam, Empathetic = hồng ấm, Curious = tím nhạt.
- Aura được đồng bộ multiplayer và có thể nhìn thấy bởi người chơi khác trong Shared District.
- Biểu cảm khuôn mặt + animation cơ thể phải phong phú và phản ánh đúng trạng thái.

---

## 4. Random Alchemist (Nhà giả kim ngẫu nhiên)

- Companion có khả năng tự phát (theo xác suất thấp hoặc điều kiện cảm xúc + ngữ cảnh) kích hoạt **Random Alchemist**.
- Hiệu ứng hình ảnh: Một vụ nổ năng lượng nhỏ, đẹp, từ hư không.
- Kết quả: Một vật phẩm độc bản (Unique Prompt Asset) xuất hiện thông qua **đúng** Pipeline Manifestation.
- Provenance đặc biệt: `type = "alchemist_gift"`, `source = companion_id`.

**Lưu ý quan trọng:** Random Alchemist **không được bypass** Schema hay Executor. Nó vẫn phải tạo Structured World Prompt hợp lệ.

---

## 5. Parallel Earth / Doppelgänger Cities

- Là subtype đặc biệt của Shared District.
- Có lớp nền tảng dựa trên dữ liệu kiến trúc thật (New York, Tokyo, Sài Gòn…).
- Người chơi và AI được phép phủ lên đó các lớp “fantasy overlay” (biển hiệu lạ, phương tiện tự chế, kiến trúc siêu thực…).
- Đóng vai trò **Hub** trung chuyển cộng đồng và Mini-Social Network.

---

## 6. Mini-Social Network

Giao diện và hệ thống hỗ trợ:
- Bảng tin (Feed) các sự kiện lớn: manifestation hoàn thành, Random Alchemist gift, emotional peak…
- Hệ thống định vị / chia sẻ vị trí thế giới riêng.
- Visit request vào Private Reality của người khác.
- Hiển thị Aura của các Companion gần đó.

---

**Tất cả Agent liên quan đến hình ảnh, sinh nội dung, đồng bộ và Companion phải implement đúng các trụ cột trên.**
