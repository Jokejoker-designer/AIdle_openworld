# AIdle Openworld – Master Blueprint Package v1.0

**Tên dự án:** AIdle Openworld  
**Phiên bản Blueprint:** 1.0  
**Ngày khóa:** 2026-07-20  
**Loại hình:** Infinite Generative Creative Metaverse (AI-Native Open World)

---

## Mục đích của gói này

Gói tài liệu này là **nguồn sự thật duy nhất (Single Source of Truth)** cho toàn bộ dự án AIdle Openworld.

Mọi AI Agent, mọi session phát triển, mọi quyết định kỹ thuật **bắt buộc** phải tuân thủ các tài liệu trong gói này. Khi các Agent hoàn thành đúng output theo hợp đồng, kết quả ghép lại sẽ tạo thành một thế giới mở hoàn chỉnh, đồng bộ và nhất quán về mặt kỹ thuật lẫn thẩm mỹ.

---

## Cấu trúc thư mục

```
AIdle_Openworld_Blueprint_v1.0/
├── 00_README.md                          ← File này
├── 01_Master_Blueprint.md                ← Tài liệu gốc – đọc đầu tiên
├── 02_Visual_Concept_Pillars.md          ← Hệ thống Art Direction & Hiệu ứng đặc trưng
├── 03_Structured_World_Prompt_Schema.md  ← Hợp đồng dữ liệu cốt lõi
├── 04_Reality_Hierarchy.md               ← Private / Shared / Orbital / Exoplanet
├── 05_Authority_and_Multiplayer.md
├── 06_Progressive_Construction_Spec.md
├── Agents/
│   ├── Agent_01_Core.md
│   ├── Agent_02_Schema.md
│   ├── Agent_03_Voxel.md
│   ├── Agent_04_Companion.md
│   ├── Agent_05_Executor.md
│   ├── Agent_06_Network.md
│   ├── Agent_07_Asset.md
│   └── Agent_08_Persist.md
├── Interfaces/
│   ├── Common_Contracts.md
│   └── Event_Bus.md
└── Docs/
    └── Development_Roadmap.md
```

---

## Thứ tự sử dụng khuyến nghị

1. Đọc kỹ `01_Master_Blueprint.md` và `02_Visual_Concept_Pillars.md`
2. Đọc `03_Structured_World_Prompt_Schema.md` (hợp đồng chung)
3. Bắt đầu với **Agent_02_Schema** (phải xong trước hầu hết các Agent khác)
4. Chạy song song: Agent_01_Core + Agent_03_Voxel + Agent_04_Companion
5. Sau đó: Agent_05_Executor → Agent_06_Network → Agent_07_Asset → Agent_08_Persist
6. Dùng `Interfaces/Common_Contracts.md` để kiểm tra sự khớp nối

---

## Nguyên tắc vàng khi sử dụng Agent

- Mỗi Agent **chỉ** được làm đúng phạm vi được giao.
- Mọi thay đổi thế giới phải đi qua Structured World Prompt.
- Progressive Construction là bắt buộc (Wireframe → Hologram → Materialize).
- Art Direction được chọn từ đầu (mặc định: Cozy Cyber-Pixel / Dreamy Low-Poly) và phải được tôn trọng bởi toàn bộ hệ thống sinh nội dung.
- Không được tự ý mở rộng schema hoặc phá vỡ Authority Model.

---

**Chúc bạn xây dựng thành công vũ trụ AIdle Openworld.**
