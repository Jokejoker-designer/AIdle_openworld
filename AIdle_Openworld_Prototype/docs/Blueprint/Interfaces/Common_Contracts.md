# AIdle Openworld – Common Contracts & Interfaces

**Phiên bản:** 1.0

---

## 1. Hợp đồng chung bắt buộc

Mọi Agent phải tuân thủ các hợp đồng sau khi giao tiếp với nhau:

### 1.1. Structured World Prompt
- Là định dạng dữ liệu duy nhất để yêu cầu thay đổi thế giới.
- Phải được validate bởi Schema trước khi Executor chấp nhận.

### 1.2. Construction Progress
- Giá trị float từ 0.0 đến 1.0.
- Phải được đồng bộ trong multiplayer.
- 0.0 = mới bắt đầu Wireframe
- 1.0 = Materialization hoàn tất + collision active

### 1.3. Provenance
- Mọi object phải mang provenance đầy đủ.
- Không được phép xóa hoặc sửa provenance sau khi đã commit.

### 1.4. Art Style
- Được lưu ở World / Space level.
- Mọi generation phải đọc và tuân thủ.

### 1.5. Temporary Builder Authority
- Được cấp tự động cho người (hoặc Companion) khởi tạo Prompt.
- Thu hồi khi progress = 1.0 hoặc bị hủy / timeout.

---

## 2. Event Bus chính

Các sự kiện quan trọng phải được phát ra qua EventBus:

- `manifestation_started`
- `manifestation_progress_updated`
- `manifestation_completed`
- `manifestation_cancelled`
- `random_alchemist_gift`
- `emotional_state_changed`
- `player_entered_space`
- `visit_requested`
- `visit_accepted`

Tất cả event liên quan đến thế giới phải mang theo `prompt_id` và `provenance` khi có thể.

---

## 3. Quy tắc tích hợp

- Agent-Core cung cấp điểm gắn (nodes / autoloads).
- Agent-Schema cung cấp Validator.
- Agent-Voxel cung cấp API Manifestation.
- Agent-Companion chỉ được gọi Executor, không gọi trực tiếp Voxel.
- Agent-Network chịu trách nhiệm đồng bộ các event và progress.
- Agent-Persist lắng nghe các event completed để lưu trữ.
