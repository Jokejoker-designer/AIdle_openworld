# Đề xuất hoàn thiện hệ thống AIdle Openworld

**Bối cảnh:** Đây là tài liệu tiếp nối Báo cáo đánh giá kỹ thuật AIdle_openworld (08/08/2026). Mọi khuyến nghị dưới đây được suy ra trực tiếp từ các phát hiện trong báo cáo đó, được tổ chức theo nguyên tắc "sửa cái sai trước, xây cái mới sau", và gắn với lộ trình giai đoạn G0→G8 hiện có của dự án (Foundation → Contract lock → 2.5D shell → Manifestation → Persist → Companion → Multiplayer authority → Art/perf → Alpha → post-alpha).

**Nguyên tắc chỉ đạo cho toàn bộ đề xuất:**

1. **Một nguồn gốc thật (Single Source of Truth) cho mỗi quyết định kiến trúc** — không còn hai bản authority (GDScript/Python) song song có thể drift; chỉ giữ một bản làm "luật", bản còn lại là thin adapter hoặc bị loại.
2. **Fail-closed được giữ nguyên** — mọi đề xuất mới phải tuân thủ nguyên tắc này, không đề xuất nào được phép mở ngoại lệ ngầm.
3. **Evidence trước, tuyên bố sau** — mọi hạng mục hoàn thiện phải đi kèm acceptance test chạy được (như 57/57 test Python hiện có), không claim completion bằng tài liệu.
4. **Khớp nhịp roadmap** — tận dụng cấu trúc STAGES/ và dispatch workflow hiện tại thay vì xây quy trình mới.

---

## 1. Bản sửa cấp bách (Sprint 0 — trước khi bất kỳ feature nào mới được thêm)

Đây là nhóm hạng mục "technical debt nguy hiểm" — chưa gây lỗi hiện tại nhưng sẽ gây lỗi ngay khi hệ thống được mang lên môi trường thật hoặc thêm người chơi thứ hai.

### 1.1. Thống nhất và nâng cấp bảo mật phiên (ưu tiên P0)

Hiện tại bản GDScript `world_authority_local.gd` dùng UUID và session token deterministik thuần counter-based (`tok_{client_id}_{hex}` với hex từ `ticks_usec + counter * const`), trong khi bản Python dùng `uuid.uuid4()` + `secrets.token_hex(8)`. Đề xuất:

| Việc | Mô tả cụ thể | Acceptance |
|---|---|---|
| Xóa pseudo-UUID GDScript | Thay `_new_uuid()`/`_hex_token()` bằng generator crypto: Godot 4.3 có `CryptographicRandomNumberGenerator` — dùng trực tiếp thay cho `Time.get_ticks_usec()` arithmetic | Không còn chuỗi code nào sinh token từ counter + tick; test replay 10.000 lần không trùng lặp |
| Signed token | Session token = `tok_{client_id}_{random}.{HMAC-SHA256(client_id+random, server_secret_key)}`; authority chỉ nhận token có chữ ký hợp lệ — chặn giả mạo format token | Test: token tự chế bằng tay bị reject `auth_failed` |
| TTL + revoke | Thêm `issued_at`, `ttl_seconds` (mặc định 24h), API `revoke_session` và tự động hết hạn khi reconnect | Test: token hết hạn bị reject; revoke khiến token cũ vô hiệu ngay lập tức |
| Rate limiting | Counter per `client_id`: max N proposal/commit mỗi giây; vượt → `rate_limited` kèm retry-after | Test flood 1.000 request/s không làm sập và không vượt ngân sách |

### 1.2. Sửa logic gift_proposal / enrich — đóng lỗ hổng ownership (P0)

Hiện `gift_proposal` và `enrich` bỏ qua kiểm tra ownership và `_apply_mutation` không thay đổi bất kỳ trạng thái nào. Đề xuất triển khai trọn gói "gift economy" đúng nghĩa:

Máy trạng thái mới cho `gift_proposal`: `pending → accepted/rejected/expired`. Khi submit gift, entity bị **khóa (locked_by)** không thể bị modify/delete bởi bất kỳ ai (kể cả chủ sở hữu) cho đến khi giao dịch kết thúc. Người nhận phải chủ động gọi `accept_gift` (hoặc hệ thống hết hạn sau `rollback_window_seconds`). Transfer ownership là nguyên tử trong cùng một hàm `apply` với revision check — không có trạng thái trung gian "entity không có chủ". Đồng thời `enrich` chỉ được phép bởi chủ sở hữu hoặc người được ủy quyền (whitelist `authorized_by`). Kèm theo là bộ test adversarial mới: gift entity người lạ mà không có consent phải fail; double-accept cùng một gift phải fail (idempotent, không tạo bản sao); gift hết hạn phải mở khóa entity về nguyên trạng.

### 1.3. Đưa schema validation đầy đủ vào authority path (P1)

AGM gateway đã làm đúng (jsonschema Draft 2020-12), nhưng authority lại chỉ validate 7 key tối thiểu. Đề xuất: build sẵn `PackedStringArray` JSON Schema cho `world_prompt` và `commit_request` (dùng thư viện GDScript jsonschema hoặc compile schema thành bộ check tĩnh — cách thứ hai nhanh hơn và phù hợp game), validate `entity.transform/bounds/interaction_tags` về kiểu và range ngay ở `_validate_world_prompt`. Mục tiêu: **mọi thứ lọt qua validation ở phía này đều đã hợp lệ kiểu** — tương đương rule "không lệnh lạ vào matching engine" của trade engine.

### 1.4. Sửa validate_project.py và evidence discipline (P1)

Công cụ tự-validate của repo hiện FAIL (`crew mismatch: declared=8 files=35`). Đề xuất: chuẩn hóa `workflow.json` với cấu trúc worker thực tế, đưa CI chạy `validate_project.py` + 57 test Python trên mỗi push, và đưa rule vào `workflow.json` rằng **một wave không được đóng khi validation tool đỏ**. Đây là việc nhỏ nhưng ý nghĩa lớn: discipline của repo tự tuyên bố "documentation is not implementation" thì công cụ nội tại phải xanh.

## 2. Xây nền kinh tế thật (Sprint 1–2 — chuẩn bị cho post-alpha marketplace)

Sau khi 4 hạng mục trên xong, hệ thống mới đủ điều kiện thêm lớp giao dịch giá trị. Đề xuất theo thứ tự phụ thuộc:

### 2.1. Resource ledger (nền tảng của mọi giao dịch)

Thêm module `resource_ledger` (RefCounted, cùng pattern với authority): tài khoản `balance` per actor per resource (coin, wood, stone…), mutation log có chữ ký, và quan trọng nhất là **balance check nguyên tử trong cùng transaction với world mutation** — một commit chỉ thành công nếu đã trừ đủ chi phí, không đủ thì toàn bộ transaction fail (không có trạng thái "đã xây nhưng chưa trả tiền"). Receipt schema hiện cần bổ sung 3 trường: `cost`, `fee` (cho marketplace sau này), `balance_delta`. UI Proposal Card/Cost Receipt theo DESIGN.md sẽ có dữ liệu thật để hiển thị.

### 2.2. Escrow và atomic transfer (cho gift/marketplace)

Mở rộng 1.2 thành cơ chế escrow tổng quát: `offer → escrowed → accepted → transferred` với compensating undo nếu phía đối ứng thất bại. Quy tắc tối thượng: **một asset tại bất kỳ thời điểm nào chỉ thuộc về đúng một owner** — invariant này phải có test invariant chạy ở cuối mỗi commit (scan toàn bộ entity: sum(owner count) == active entity count).

### 2.3. Anti-abuse cho lớp kinh tế

Khi có tài nguyên thật: rate limit theo giao dịch (ngoài per-request hiện tại), giới hạn `maxItems` của `entity_ids` đồng nhất giữa schema và code (hiện schema ghi 256 nhưng code không kiểm tra), và audit trail timestamp nên chuyển sang monotonic/logical clock + NTP check để chống clock manipulation trong giao dịch nhạy cảm.

## 3. Nâng cấp kiến trúc và hiệu năng (Sprint 2–3)

| Hạng mục | Hiện trạng | Đề xuất |
|---|---|---|
| Persistence | Journal envelope JSON nguyên khối, write nguyên envelope mỗi lần | Chuyển append-only WAL: mỗi mutation append 1 dòng delta; snapshot full chỉ phát sinh theo interval; giảm write amplification rõ rệt |
| Outbox | Mảng tăng vô hạn, poll O(N×M) | Event cursor index (map revision→offset) + compaction định kỳ; client poll chỉ đọc từ cursor của mình |
| Hash checkpoint | Tính lại SHA-256 toàn entity set mỗi commit | Checkpoint hash mỗi K commit; chỉ rehash delta so với checkpoint |
| Dual authority | GDScript mirror + Python POC | Chốt Python service làm source of truth duy nhất cho authority; GDScript giữ bản mirror chỉ với mục đích offline-single-player, đánh dấu rõ `OFFLINE_MIRROR_ONLY` và không mang lên production |
| Transport | Không có (in-process) | Khi lên multiplayer thật: chọn UDP đáng tin cậy (ENet) hoặc WebSocket qua Godot Multiplayer API; mọi receipt vẫn bắt buộc verify ngược server — kiến trúc verify_receipt hiện tại đã sẵn sàng |
| Retry/backoff | Client phải tự poll khi conflicted | SDK client tự động exponential backoff + refetch head revision; server trả `retry_after_ms` trong receipt conflicted |

## 4. Hoàn thiện gameplay và runtime (Sprint 3–4, song song với 2–3)

Thứ nhất, **manifestation host**: log `G3_E2E.log.err` báo warning "No manifestation host; using local fallback" lặp lại — cần triển khai manifestation host chính thức thay vì fallback lặp, vì manifestation (wireframe → hologram → materialize 8–15s) là điểm selling chính của game. Thứ hai, **module voxel**: `ModuleRegistry` báo "No mount for module: voxel" — world_DNA đã có blueprint voxel đầy đủ nhưng runtime chưa mount; cần spike voxel nhỏ trong boundary của một wave trước gate G7. Thứ ba, **perf budget cho town cadastre 50 plots**: dùng frustum culling + LOD theo tài liệu Simulation LOD Standard đã có trong world_DNA; gắn profiler frame budget (~16ms target) vào một trong các smoke test headed hiện có. Thứ tư, **giảm file lớn**: `main.gd` (1.901 dòng) và `block_assembly_controller.gd` (1.823 dòng) nên tách thành nhiều sub-module theo pattern đã có ở các module khác; và hạn chế dùng `duplicate(true)` trên toàn receipt chain ở các path không nhạy tamper để giảm GC pressure.

## 5. Quy trình và quality-of-life cho đội phát triển

Đề xuất bổ sung vào quy trình multi-agent hiện có (vốn đã rất tốt): (a) thêm **adversarial test wave** bắt buộc trước mỗi gate — mỗi gate mới phải kèm ít nhất một test case tấn công (forged/gift-abuse/balance-underflow/replay) mới, không chỉ tái chạy bộ cũ; (b) đưa **invariant checker** chạy headless cuối mỗi session: owner invariant, revision invariant, hash integrity; (c) loại bỏ hoặc chuyển 158 file `.err` rỗng ra khỏi evidence tree (hoặc chuẩn hóa rằng file .err rỗng = pass, có nội dung = fail, và tool validate phải check cả hai); (d) README nên bổ sung quickstart test: `python3 -m pytest services/` — hiện repo chỉ hướng dẫn chạy game, không hướng dẫn chạy bộ test bằng chứng duy nhất hiện chạy được.

## 6. Roadmap tổng hợp theo giai đoạn

| Giai đoạn | Nội dung chính | Đầu ra acceptance |
|---|---|---|
| **Sprint 0** (1–2 tuần) | Crypto RNG, signed token + TTL, sửa gift/enrich ownership, validation đầy đủ phía authority, sửa validate_project.py | 57 test cũ + ≥15 test adversarial mới, toàn xanh; không còn deterministic token |
| **Sprint 1** (2–3 tuần) | Resource ledger + cost trong receipt + balance check nguyên tử; escrow gift | Test balance underflow fail; gift flow 2-client đúng; UI receipt hiển thị cost thật |
| **Sprint 2** (2 tuần) | WAL append-only, event cursor, hash checkpoint; chốt Python authority là source of truth | Headless perf test: 1.000 commit giữ <16ms/commit trung bình; evidence tree sạch |
| **Sprint 3** (2–3 tuần) | Manifestation host chính thức, voxel spike, tách main.gd/block_assembly_controller, reduce duplicate() | Không còn warning manifestation host; module voxel mount được; GC pressure giảm đo được |
| **Sprint 4** (trước alpha) | Invariant checker tự động, adversarial test wave mỗi gate, README test quickstart, transport choice spike (multiplayer thật) | Mọi gate mới đều có invariant + adversarial evidence; multiplayer 2-client chạy trên transport thật |

## 7. Kết luận

Hệ thống AIdle_openworld đã có nền giao dịch thuộc loại **được thiết kế đúng bài hiếm thấy ở quy mô solo dev** — máy trạng thái fail-closed, idempotency payload-bound, revision locking, signed journal. Khoảng cách từ hiện tại đến "hoàn thiện" không phải là xây lại, mà là **đóng bốn lỗ đã xác định** (token xác thực, ownership/gift logic, validation authority, evidence discipline) và **xây đúng thứ tự**: ledger tài nguyên trước, escrow/atomic transfer sau, hiệu năng và gameplay song song. Nếu tuân thủ lộ trình 5 sprint trên, hệ thống sẽ đạt trạng thái sẵn sàng cho lớp kinh tế thật (marketplace, trade) — đúng thời điểm blueprint đã dự kiến cho post-alpha. Nguyên tắc quan trọng nhất cần giữ vững xuyên suốt: **mỗi hạng mục hoàn thiện chỉ được coi là xong khi có test chạy được, không phải khi có tài liệu mô tả.**
