# AIdle Openworld – Vertical Slice Prototype v0.1

**Cozy Cyber + Companion + Progressive Building**

Đây là bản prototype chạy được ngay, tập trung vào cảm giác gần gũi (Stardew-like) kết hợp cyber, AI Companion và hiệu ứng xây dựng progressive.

---

## Yêu cầu

- Godot **4.2** trở lên (bạn đã có)
- Không cần asset ngoài, không cần plugin

---

## Cách chạy (rất nhanh)

1. Giải nén file ZIP
2. Mở **Godot 4.2+**
3. Bấm **Import** → chọn thư mục `AIdle_Openworld_Prototype`
4. Mở project
5. Nhấn **F5** (hoặc nút Play)

---

## Cách chơi prototype

- Di chuyển: **WASD** hoặc **phím mũi tên**
- Nói chuyện với Companion **AIda**: Gõ vào ô chat phía dưới rồi nhấn **Enter**
- Thử các câu lệnh:
  - `chào`
  - `xây nhà nhỏ` hoặc `xây nhà`
  - `cảm ơn`
  - `tâm sự`

Khi bạn nhờ xây nhà, AIda sẽ kích hoạt **Progressive Manifestation**:
1. Wireframe (khung ánh sáng)
2. Hologram
3. Materialize dần thành ngôi nhà solid

Mood / Aura của AIda sẽ thay đổi theo cuộc trò chuyện.

---

## Cấu trúc thư mục

```
AIdle_Openworld_Prototype/
├── project.godot
├── README.md
├── scenes/
│   └── Main.tscn
├── scripts/
│   ├── main.gd
│   ├── player.gd
│   ├── companion.gd
│   └── building_system.gd
└── docs/          ← (có thể copy Blueprint vào đây)
```

---

## Những gì đã có trong bản này

- Player điều khiển được
- Companion AIda có cá tính cơ bản + phản hồi theo ngữ cảnh
- Mood system đơn giản (Calm / Happy / Excited / Empathetic) + Aura đổi màu
- Progressive Building (Wireframe → Hologram → Solid)
- UI chat hoàn chỉnh
- Kiến trúc sẵn sàng mở rộng theo Master Blueprint

---

## Hướng mở rộng tiếp theo (theo Blueprint)

1. Thay ColorRect bằng Sprite / Voxel thật
2. Kết nối local LLM (Ollama) vào `companion.gd`
3. Thêm Voice (STT + TTS)
4. Thêm godot_voxel cho xây dựng thật
5. Multiplayer + Shared District

---

Chúc bạn chơi vui và tiếp tục xây dựng AIdle Openworld!
