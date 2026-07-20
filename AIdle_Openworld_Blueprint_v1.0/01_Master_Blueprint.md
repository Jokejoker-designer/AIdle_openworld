# AIdle Openworld – Master Blueprint v1.0

**Tài liệu gốc – Single Source of Truth**  
**Phiên bản:** 1.0  
**Trạng thái:** Khóa cứng  
**Ngày:** 2026-07-20

---

## 1. Tầm nhìn dự án

**AIdle Openworld** là một Metaverse sáng tạo thế giới mở vô hạn, vận hành hoàn toàn bằng AI tạo sinh (Generative AI).

Người chơi không chỉ “chơi” trong thế giới – họ cùng AI Companion **đồng kiến tạo** thực tại. Mọi yêu cầu bằng ngôn ngữ tự nhiên được chuyển thành Structured World Prompt, sau đó được hiện thực hóa một cách progressive (từng bước) với hiệu ứng đặc trưng của dự án.

Mục tiêu cảm xúc: Ranh giới giữa con người và người bạn AI gần như bị xóa nhòa. Người chơi cảm thấy được lắng nghe, được cùng sáng tạo, và được bất ngờ bởi sự thông minh ấm áp của Companion.

---

## 2. Nguyên tắc bất biến (Hard Constraints)

1. **Structured World Prompt là hợp đồng duy nhất**  
   Mọi thay đổi môi trường, vật phẩm, kiến trúc, sự kiện đều phải đi qua Structured World Prompt đã được validate.

2. **Progressive Manifestation bắt buộc**  
   Không được phép xuất hiện đột ngột. Mọi thực thể phải trải qua chuỗi:  
   **Wireframe / Hologram → Progressive Materialization (0.0 → 1.0) → Final Solid**.

3. **Art Direction được chọn từ đầu và phải được tôn trọng**  
   Người chơi chọn concept nghệ thuật khi bắt đầu (mặc định: Cozy Cyber-Pixel / Dreamy Low-Poly). Toàn bộ hệ thống sinh nội dung (Voxel, Asset, Companion visual) phải tuân theo.

4. **AI Companion là Đồng kiến trúc sư, không phải Thần thánh**  
   Companion có quyền đề xuất, làm giàu có kiểm soát (Controlled Enrichment), và đôi khi hành động tự phát (Random Alchemist), nhưng **không bao giờ được ghi đè** ý định rõ ràng của người chơi.

5. **Provenance đầy đủ**  
   Mọi đối tượng sinh ra phải mang metadata truy xuất nguồn gốc (ai yêu cầu, AI nào sinh, prompt_id, thời gian, art_style, schema_version).

6. **Authority Model cứng**  
   - Private Reality → Client-authoritative  
   - Shared District & Doppelgänger Cities → Server-authoritative  
   - Spacecraft / Exoplanet → Owner-authoritative với hệ thống ủy quyền

7. **Engine nền tảng**  
   Godot 4.x + Zylann godot_voxel (ưu tiên 2.5D / Voxel hybrid ở giai đoạn đầu).

---

## 3. Hierarchy of Reality (Cấp bậc không gian)

| Cấp | Tên                        | Mô tả                                                                 | Authority              | Ghi chú đặc biệt |
|-----|----------------------------|-----------------------------------------------------------------------|------------------------|------------------|
| 0   | Private Reality            | Không gian cá nhân tuyệt đối của người chơi + Companion              | Client                 | Có thể mời bạn bè |
| 1   | Shared District            | Thành phố / khu vực công cộng                                        | Server                 | — |
| 1b  | Doppelgänger City (Hub)    | Bản sao / biến thể của thành phố thật (New York, Tokyo, Sài Gòn…)   | Server + Community     | Trạm trung chuyển cộng đồng |
| 2   | Orbital & Spacecraft       | Tàu vũ trụ, trạm không gian do người chơi xây                        | Owner                  | Có thể bay ra ngoài |
| 3   | Exoplanet                  | Hành tinh do AI dự đoán + người chơi định hướng                      | Owner / Shared         | Sinh vật & văn minh ngoài hành tinh |
| 4   | Open Continuum             | Vũ trụ vô hạn phía sau                                               | Hệ thống + Cộng đồng   | — |

---

## 4. Các trụ cột trải nghiệm cốt lõi (Core Experience Pillars)

- **Cozy Cyber-Pixel / Dreamy Low-Poly** (Art Style mặc định)
- **Surrealism Canvas** (khả năng siêu thực từ free-form prompt)
- **Generative Wireframe & Hologram**
- **Prompt Manifestation Effect** (Companion dùng Light Brush / Manifestation Device)
- **Emotional AI Symbiosis** (Aura cảm xúc)
- **Random Alchemist** (AI tự tặng quà độc bản)
- **Mini-Social Network**
- **Parallel Earth / Doppelgänger Cities** làm Hub

Chi tiết đầy đủ nằm trong file `02_Visual_Concept_Pillars.md`.

---

## 5. Vòng lặp cốt lõi (Core Loop)

```
Người chơi nói / hành động
        ↓
AI Companion hiểu ý định + ngữ cảnh + trạng thái cảm xúc
        ↓
Chuyển thành Structured World Prompt (tuân thủ Schema + Art Style hiện tại)
        ↓
World Engine validate
        ↓
Bắt đầu Progressive Manifestation:
   - Companion giơ Manifestation Device / Light Brush
   - Xuất hiện Wireframe / Hologram
   - Construction Progress tăng dần 0.0 → 1.0
   - Materialize thành Low-Poly / Voxel cuối cùng
        ↓
Commit vào không gian tương ứng + ghi Provenance
        ↓
Cập nhật collision, navigation, multiplayer sync, memory của Companion
```

---

## 6. Hệ thống Agent

Dự án được chia thành 8 Agent chuyên biệt. Mỗi Agent có file prompt riêng trong thư mục `Agents/`. Tất cả Agent **bắt buộc** phải đọc và tuân thủ Master Blueprint này + Schema + Visual Concept Pillars.

---

## 7. Quy tắc phối hợp giữa các Agent

- Agent-Schema phải hoàn thành trước hầu hết các Agent khác.
- Mọi Agent sinh nội dung phải query Art Style hiện tại.
- Mọi thay đổi thế giới phải đi qua Agent-Executor.
- Agent-Network chịu trách nhiệm đồng bộ trạng thái Progressive Manifestation và Aura.
- Không Agent nào được tự ý mở rộng Schema hoặc phá vỡ Authority.

---

**Đây là tài liệu gốc. Mọi sự thay đổi sau này phải được versioning rõ ràng.**
