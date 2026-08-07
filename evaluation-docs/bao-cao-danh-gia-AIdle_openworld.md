# Báo cáo đánh giá kỹ thuật hệ thống AIdle Openworld

**Nguồn đánh giá:** [github.com/Jokejoker-designer/AIdle_openworld](https://github.com/Jokejoker-designer/AIdle_openworld) (clone tại thời điểm 08/08/2026, 26 commits, tác giả duy nhất)

**Người đánh giá:** Chuyên gia đánh giá hệ thống (theo vai trò yêu cầu của dự án)

**Ngày đánh giá:** 08/08/2026

---

## 1. Xác định phạm vi và tính chất hệ thống — một điều chỉnh cần thiết về định danh

Trước khi đi vào chi tiết, cần nói thẳng một điểm quan trọng: **AIdle_openworld không phải là một trade engine** theo nghĩa hệ thống khớp lệnh / thanh khoản / định giá như trong tài chính hoặc marketplace. Đây là một **monorepo game Godot 4.3** (~50.500 dòng GDScript, ~4.700 dòng Python, ~3.580 file, 701 file tài liệu Markdown) xây dựng một game open-world "cozy cyber-pixel" 2.5D theo mô hình **player speaks → structured proposal → validate → preview → human confirm → authority commit**.

Tuy nhiên, trong phạm vi hệ thống này tồn tại **một lớp giao dịch (transaction layer) thực sự** — chính là luồng *preview → confirm → commit → receipt* của module World Authority, cùng các cơ chế đi kèm như idempotency, revision concurrency, ownership, artifact hashing, journal sealing (HMAC-SHA256 chained log), và budget ledger của AGM gateway. Đây là phần mang tính "transaction engine" rõ nhất, và tôi sẽ đánh giá nó với tiêu chuẩn khắt khe của một trade engine: tính nguyên tử, tính nhất quán, khả năng chống gian lận, chống double-spend, và bằng chứng tái tạo (provenance). Báo cáo dưới đây đánh giá toàn hệ thống, nhưng tập trung trọng lượng vào lớp giao dịch này.

| Hạng mục | Nội dung |
|---|---|
| Stack chính | Godot 4.3 (GDScript 2.0) + Python 3 dịch vụ hỗ trợ (không bundle binary engine) |
| Kiến trúc mạng | Client-authoritative local (offline) + World Authority in-process; không có socket/HTTP thật trong game runtime |
| Ngôn ngữ | GDScript (~50.5K dòng), Python (~4.7K dòng), JSON schema 2020-12 (~1.100 contract files) |
| Trạng thái giao dịch | Preview → Pending → Confirmed → Committed / Rejected / Conflicted / Idempotent replay |
| Multiplayer | POC 2-client chạy trong-process; chưa phải production |
| Test | 57 test Python (100% pass); ~45 smoke test GDScript (định dạng evidence, chưa chạy được trong sandbox do thiếu Godot 4.3) |

## 2. Tổng quan kiến trúc

Hệ thống được tổ chức theo nguyên tắc **single source of truth per domain** rất chặt chẽ: blueprints v1.0/v1.1 là tài liệu định hướng, `contracts/` chứa schema ràng buộc (world_prompt, commit_request, commit_receipt, event_envelope, AGM snapshot/decision), `game/` chứa runtime Godot, `services/` chứa hai service Python (world_authority_poc và agm_gateway), `orchestration/` chứa work orders và evidence, `STAGES/` đóng gói theo giai đoạn phát triển G0→G8.

Luồng giao dịch cốt lõi (G6 authority) hoạt động như sau: client gọi `connect_client` nhận session token → submit world_prompt (bắt buộc `preview_required=true`, trạng thái `pending`) → preview wireframe/hologram không có collision → người chơi giữ nút xác nhận → `confirm_proposal` chuyển trạng thái sang `confirmed` → `commit` với `expected_world_revision` → authority kiểm tra toàn bộ điều kiện → áp dụng mutation nguyên tử → phát hành receipt kèm artifact hashes SHA-256 → đưa event vào outbox để các client khác sync.

Về mặt concept, đây là một thiết kế **server-authoritative, fail-closed** được áp dụng nhất quán: mọi đường ghi trực tiếp (`client_write_entity`, `client_set_world_revision`, `client_issue_receipt`, `client_publish_event`) đều bị từ chối với mã `client_forged`, và client không bao giờ được tự tuyên bố thành công — chỉ World Commit service mới phát hành receipt hợp lệ. Đây là nền tảng đúng đắn cho bất kỳ hệ thống có giá trị kinh tế nào sau này (marketplace money được blueprint chủ động xếp vào post-alpha).

## 3. Đánh giá lớp giao dịch (transaction layer) — điểm mạnh

### 3.1. Máy trạng thái giao dịch rõ ràng và fail-closed đúng hướng

Máy trạng thái `pending → confirmed → committed` được bảo vệ ở cả ba tầng: pipeline executor (`prompt_pipeline.gd`), authority GDScript (`world_authority_local.gd`) và bản Python (`server.py`). Một điểm đáng khen là defense-in-depth thực sự: ngay cả khi prompt vào pipeline đã được đánh dấu `confirmed` trước (tấn công replay xác nhận giả mạo), cả pipeline lẫn server đều từ chối và trả về `rejected`/`client_forged` kèm `retryable: false`. Cơ chế `confirmation.state=confirmed không được chấp nhận trên submit; chỉ confirm_proposal mới xác nhận được` được chú thích rõ ngay trong mã với nhãn `INV-CONFIRM-SERVER-TRANSITION` — đây là cách viết phòng thủ rất chuyên nghiệp, hiếm thấy ở dự án solo.

### 3.2. Idempotency gắn payload, không chỉ gắn request_id

Khác với nhiều hệ thống chỉ dedupe theo request_id, fingerprint ở đây là **SHA-256 của toàn bộ payload đã xác nhận** (request_id, prompt_id, space_id, mutation_class, actor, và toàn bộ confirmed_world_prompt) qua một bộ canonical JSON riêng (`aidle_canonical_json_v1` — sort keys, escape chuẩn, float deterministic). Nếu client gửi lại cùng request_id với payload khác, hệ thống trả `rejected` thay vì ghi đè — loại bỏ đúng lớp tấn công "replay request_id + đổi nội dung". Bản Python dùng `secrets`/`uuid4`, bản GDScript dùng counter-based pseudo-UUID (xem phần nhược điểm 4.1).

### 3.3. Concurrency và conflict handling đúng bài kinh điển

`expected_world_revision` hoạt động như optimistic locking: hai client sửa cùng lúc, người đến sau nhận `conflicted` kèm `diff_ref` trỏ đến sự khác biệt — không silent merge. Test suite có các ca adversarial đầy đủ: forged actor, forged owner, forged client_id, client_authoritative schema bypass, stale revision, altered receipt. **100% trong 57 test Python pass**, bao gồm cả test `test_tm_altered_receipt` xác nhận client không thể áp dụng receipt bị sửa.

### 3.4. Client mirror với verify_receipt toàn diện

`authority_client.gd` không chỉ tin receipt trả về mà còn gọi `get_receipt` ngược lại server để đối chiếu từng trường (`status`, `request_id`, `old/new_world_revision`, `entity_ids`, `space_id`, `artifact_hashes`) qua canonical stringify. receipt bị sửa bị bắt với mã `integrity_fail` và mirror không cập nhật. Đây chính là thiết kế phòng **man-in-the-middle nội tiến trình** — mức nghiêm ngặt cao hơn đa số game indie.

### 3.5. Persistence có signing (journal_store) — điểm hiếm có

`journal_store.gd` (1.341 dòng) lưu mutation log dạng envelope JSON với **chuỗi seal HMAC-SHA256** (mỗi entry seal bao gồm entry trước + sequence_index + space_id + journal_id), có key provider tách biệt, hỗ trợ `verify_integrity` và `apply_compensation` (undo dạng compensating mutation thay vì xóa history). Thiết kế "history is not erased, undo is a compensating entry" khớp đúng nguyên tắc sổ kế toán của một transaction engine.

### 3.6. AGM gateway có discipline chi phí và redaction

AGM gateway (531 dòng) kiểm tra budget **trước khi dispatch** với caps cứng (per-request 100, session 1.000), reject `NaN`/`Infinity`/`bool` trong trường budget (check `isinstance(value, bool)` trước `numbers.Real` — xử lý đúng bẫy bool-subclass của int trong Python), client không thể tự nâng cap server, và deny-list key nhạy cảm (api_key, system_prompt, credentials…) được redact khỏi cả snapshot lẫn decision. Provider được khóa ở `fixture` duy nhất — real provider là HITL path riêng.

### 3.7. Contract-first development có thật

Schema JSON 2020-12 với `additionalProperties: false`, enum status, maxLength, uuid format; fixtures có cả bộ `valid/` và `invalid/` (invalid_decision_unknown_event, invalid_snapshot_unknown_player_action); pipeline executor có **FORBIDDEN_KEYS whitelist chống code injection** (`script`, `code`, `shader`, `executable`, `commit_request`, `direct_world_write`…). Đây là văn hóa "contract là luật" được thực thi bằng máy, không chỉ bằng lời.

## 4. Nhược điểm và lỗ hổng xâm phạm logic (vấn đề nghiêm trọng)

Đây là phần quan trọng nhất. Phân theo mức nghiêm trọng:

### 4.1. NHIỆM TRỌNG (HIGH) — Hệ thống nhận dạng/phiên phiên yếu: predictable UUID + token không ký

Bản GDScript in-game (`world_authority_local.gd` và `_new_uuid`, `_hex_token`) dùng **counter arithmetic thuần túy**:

> `a := "%08x" % (0x10000000 + (_uuid_counter * 17) % 0x0fffffff)`

Session token có dạng `tok_{client_id}_{hex}` với hex được tạo từ `Time.get_ticks_usec() + counter * const`. Nghĩa là **ai đoán được thời điểm khởi tạo và client_id đều tái tạo được UUID và session token** trong cùng tiến trình/bản sao deterministik. Trong bối cảnh hiện tại (in-process, một người chơi) rủi ro thấp, nhưng nếu code này được copy nguyên lên server multiplayer thật (đúng với mô hình "GDScript mirror → production") thì đây là lỗ hổng **session hijack + receipt forgery deterministik** — mức nghiêm trọng tương đương lỗ hổng signature trong trade engine. Bản Python dùng `uuid.uuid4()` + `secrets.token_hex(8)` đúng, nhưng hai bản **không đồng nhất bảo mật** — một nguy cơ divergence kinh điển khi có hai implementation của một authority.

Ngoài ra: session không có TTL, không có cơ chế revoke token (reconnect chỉ ghi đè session cũ của cùng client_id), không có rate limiting. Một authority server mà không có giới hạn phiên và giới hạn tần suất thì không đạt chuẩn đưa vào production.

### 4.2. NHIỆM TRỌNG (HIGH) — Không có lớp kinh tế nào được thực thi: ownership sơ khai, không có balance/transfer

Đây là nhận định trung tâm từ góc nhìn trade engine. Hệ thống có `owner_id` trên entity và kiểm tra ownership cho `modify`/`delete`, nhưng:

- **`enrich` và `gift_proposal` bỏ qua hoàn toàn kiểm tra ownership** — bất kỳ ai cũng có thể "gift" hoặc enrich entity của người khác mà không cần sự đồng ý của chủ sở hữu. Tên operation là `gift_proposal` nhưng mã không chứa bất kỳ logic trao ownership, chấp nhận/giữ từ chối, hay chuyển giao tài sản nào: `_apply_mutation` với op này chỉ đơn thuần trả về `entity_ids` nếu entity tồn tại, **không thay đổi trạng thái gì**. Đây là lỗ hổng logic kiểu "chưa triển khai nhưng đã mở surface" — trong một trade engine, một operation tên "transfer" mà không khóa tài sản sẽ gây double-spend.
- **Không có ledger tài nguyên/tiền tệ** (`coin`, `gold`, `balance` không xuất hiện trong game scripts), không có kiểm tra chi phí (cost) tại thời điểm commit, không có reserve/refund. Receipt có `entity_ids` nhưng không có trường `cost`, `fee`, `balance_delta` — mặc dù UI (Proposal Card, Cost/Permission Receipt theo DESIGN.md) hứa hẹn hiển thị chi phí. Khoảng cách giữa "contract hứa receipt chi phí" và "mã không thực thi chi phí" là một **gap thiết kế tài chính** cần được xử lý trước khi bật bất kỳ lớp economy nào.
- Không có cơ chế escrow, atomic swap, hay bất kỳ ràng buộc ACID nào ngoài single-entity mutation. Mutation áp dụng tuần tự trong một hàm, không rollback nếu half-applied (tuy hiện tại mỗi commit chỉ tạo 1 entity nên chưa lộ, nhưng sẽ lộ ngay khi batch mutation xuất hiện).

### 4.3. CAO (MEDIUM-HIGH) — Validation schema "min" quá lỏng ở phía authority

`_validate_world_prompt_min` chỉ kiểm tra sự hiện diện của 7 key (`schema_version, prompt_id, request_id, operation, target, entity, confirmation`) và `preview_required=true`. **Nội dung `entity` payload hoàn toàn không được validate** — `transform`, `bounds`, `interaction_tags` không kiểm tra kiểu. Một world_prompt với `transform.x = "abc"` hoặc object kỳ lạ vẫn lọt qua validation và chỉ gãy khi `_apply_mutation` dựng entity record. Trong trade engine, tương đương việc nhận lệnh mà không validate khối lượng/giá trước khi đưa vào matching. Bản Python `validators.py` chặt hơn chút nhưng vẫn ở mức field-presence. Đáng chú ý là phía gateway AGM lại dùng jsonschema đầy đủ (Draft 2020-12, 88 dòng validators) — **chênh lệch chất lượng validation giữa hai thành phần giao dịch là bất nhất quán kiến trúc**.

### 4.4. CAO (MEDIUM-HIGH) — Race conditions trong GDScript do không có locking

Toàn bộ GDScript authority chạy trong Godot single-threaded nên không có race thực tế — nhưng chính mô tả "mirror of production rules" lại là bẫy: khi migrate sang architecture có luồng (Godot workers, hoặc server Python thật nhận nhiều kết nối bất đồng bộ), các hàm hiện tại **không có mutex/transaction boundary** nào xung quanh chuỗi `check ownership → check revision → apply → increment revision → append outbox`. Revision check và apply không nguyên tử theo nghĩa "đường dẫn đồng thời": client nhận `conflicted` nhưng không được cấp cơ chế retry/backoff tự động — client phải tự polling. Bản Python POC cũng là in-process single-thread, nên vấn đề này mang tính **kỹ nợ kiến trúc** hơn là bug hiện hữu, nhưng phải ghi nhận trước khi production.

### 4.5. TRUNG BÌNH (MEDIUM) — Outbox không bao giờ được dọn; không có compaction/snapshotting server-side

`_outbox` tăng không giới hạn và `poll_events` duyệt toàn bộ mảng từ đầu với filter `rev <= after_world_revision` mỗi lần poll — độ phức tạp O(N×M) với N là số event lịch sử, M là số lần poll. `verify_receipt` gọi `get_receipt` với linear scan qua dictionary (ổn) nhưng `_replay` flow duyệt lại toàn bộ chain. Tương tự `_build_snapshot` và `entity_set_hash` duyệt toàn bộ `_entities` mỗi lần commit. Với POC vài trăm entity thì không vấn đề, nhưng đây là **anti-pattern kinh điển** mà bất kỳ transaction store nào cũng phải tránh: cần WAL compaction, hash checkpoint theo interval, và event cursor index.

### 4.6. TRUNG BÌNH (MEDIUM) — Dual-implementation divergence (GDScript ↔ Python)

Hai bản authority (GDScript 878 dòng, Python 867 dòng) được đồng bộ bằng tay. Đã phát hiện divergence: UUID/token generation (deterministic vs cryptographic), và quan trọng hơn là **behavioral drift tiềm ẩn** khi bất kỳ bên nào sửa một mình. Có 158 file `.err` trong `orchestration/evidence/` (hầu hết rỗng — dấu hiệu smoke chạy qua, nhưng một số như `G3_E2E.log.err` chứa warning `No manifestation host; using local fallback` lặp lại nhiều lần). Hơn nữa, script `validate_project.py` của chính repo **thất bại** khi chạy: `AIDLE_VALIDATION=FAIL - crew mismatch: declared=8 files=35` — công cụ tự-validate của dự án báo lỗi về chính trạng thái repo. Một hệ thống tôn thờ evidence mà công cụ validate nội tại không sạch là điểm trừ đáng kể về discipline.

### 4.7. THẤP-NHƯNG-LƯU-Ý (LOW-MEDIUM) — Các điểm còn lại

Thứ nhất, `_utcnow_iso()` dùng đồng hồ hệ thống không sync: timestamp receipt phụ thuộc clock server local, ảnh hưởng audit trail nếu có nhiều máy. Thứ hai, entity_id sinh từ `request_id.substr(0,8)` → không gian ID 16^8 ≈ 4 tỷ, ổn nhưng collision check chỉ so trực tiếp không dùng prefix namespace — nếu hai request_id khác nhau cùng tiền tố 8 ký tự thì va chạm (hiếm nhưng không được xử lý ngoài việc trả "entity id collision"). Thứ ba, journal_store nhận cả `entity_delta` nhưng `_build_entity_record` merge delta không kiểm tra kiểu trường delta — nếu delta chứa key lạ sẽ trở thành entity record lạ. Thứ tư, `maxItems: 256` cho `entity_ids` trong receipt schema nhưng không có giới hạn tương ứng ở phía GDScript authority. Thứ năm, không có đơn vị test nào cho logic "gift_proposal" — bởi vì nó gần như không làm gì; absence of test cho operation quan trọng về ownership là khoảng trống coverage có ý nghĩa.

## 5. Mức độ tối ưu (performance & resource)

| Hạng mục | Đánh giá | Ghi chú |
|---|---|---|
| CPU path commit | Ổn cho <1K entity | Hash toàn entity set mỗi commit; cần checkpoint hash |
| Memory | Rò rỉ dài hạn | Outbox + receipts + proposals không compact; POC không vấn đề, production phải sửa |
| I/O persistence | JSON file nguyên khối | Journal envelope lưu nguyên envelope mỗi lần — write amplification cao; nên append-only WAL |
| Network | N/A hiện tại | Không có real transport; authority_client dùng trực tiếp RefCounted |
| GDScript purity | Khá tốt | RefCounted logic tách khỏi SceneTree ở executor/authority; smoke chạy headless |
| Python services | Tốt | deepcopy cẩn thận khi trả về; không mutate input |

Điểm tối ưu đáng khen: executor là pure `RefCounted` (không dính SceneTree), dùng `load()` thay vì preload trong smoke test để module hỏng không chặn test, hash material dùng canonical JSON deterministic, và `get_last_receipt()` trả `duplicate(true)` (deep copy) để caller không mutate state server. Điểm chưa tối ưu đáng nói: mọi `duplicate(true)` lặp lại nhiều lớp trên mỗi commit/receipt path — overhead nhân bản sâu không cần thiết ở các đường không nhạy tamper; có thể giảm bằng read-only wrapper.

## 6. Ưu điểm tổng hợp

Nói công bằng, đây là một trong những monorepo game solo có **kỷ luật kiến trúc giao dịch thuộc hàng tốt nhất tôi từng thấy ở quy mô này**. Năm ưu điểm nền tảng: (1) nguyên tắc server-authoritative fail-closed được thực thi nhất quán xuyên suốt 50K+ dòng, không có ngoại lệ ngầm nào tôi tìm thấy — kể cả trong 1.901 dòng `main.gd`, confirm của người chơi cũng chỉ handoff đến authority; (2) contract-first với jsonschema 2020-12 và fixture bộ valid/invalid; (3) idempotency + fingerprint payload + revision locking + receipt verification bốn lớp bảo vệ chống double-commit; (4) persistence signed journal với compensating undo thay vì xóa lịch sử; (5) quy trình multi-agent có HITL gate, self-accept bị cấm, ba lần fail giống nhau phải chuyển NEED_HUMAN — discipline mà nhiều team 20 người còn không có.

## 7. Nhược điểm tổng hợp và xếp hạng rủi ro

| # | Vấn đề | Mức | Hạng mục liên quan | Khuyến nghị |
|---|---|---|---|---|
| 1 | UUID/token deterministic, không ký, không TTL session | **High** | Security/Auth | Đổi sang crypto RNG thống nhất giữa GDScript và Python; thêm token signature (HMAC server key) và TTL |
| 2 | gift_proposal/enrich bỏ qua ownership, không có transfer/accept logic | **High** | Logic giao dịch | Thêm trạng thái `gift_pending → accepted`, khóa entity trong lúc pending, transfer ownership nguyên tử |
| 3 | Không có ledger chi phí/cân bằng tại commit | **High** | Economy readiness | Thêm `cost/fee` vào receipt schema + balance check nguyên tử trước mutation; escrow cho giao dịch đa bên |
| 4 | Validation authority chỉ min-key, payload entity không validate | **Medium-High** | Integrity | Áp jsonschema đầy đủ cho world_prompt phía authority (như AGM gateway đã làm) |
| 5 | Chênh lệch bảo mật GDScript/Python authority | **Medium-High** | Divergence | Chốt một implementation duy nhất là source of truth; bản kia là thin adapter |
| 6 | Outbox/receipt không compact, O(N) poll | **Medium** | Performance | WAL append-only + hash checkpoint + event cursor |
| 7 | validate_project.py FAIL trên chính repo (crew mismatch 8 vs 35) | **Medium** | Discipline | Sửa workflow.json hoặc chuẩn hóa cấu trúc workers; công cụ tự-validate phải xanh trước khi claim evidence |
| 8 | Không rate limit, không retry/backoff cho conflict | **Low-Medium** | Resilience | Thêm exponential backoff + rate limit per client_id |
| 9 | entity_id 8-char prefix từ request_id, collision không namespace | **Low** | ID space | Dùng UUID đầy đủ hoặc prefix theo space |
| 10 | Clock receipt dựa giờ hệ thống, không sync | **Low** | Audit | NTP check / server monotonic clock + logical timestamp |

## 8. Kết luận

Nhìn tổng thể, AIdle_openworld là một **hệ thống game-runtime có nền giao dịch được thiết kế đúng bài hơn đa số dự án cùng quy mô**: máy trạng thái fail-closed, idempotency payload-bound, revision locking, receipt verification, signed append-only journal, và contract-driven development. Nếu chấm điểm lớp giao dịch trên thang trade-engine: **kiến trúc 8.5/10, thực thi hiện tại 6.5/10** — khoảng cách chủ yếu nằm ở (a) bảo mật phiên/UUID deterministik, (b) ownership/gift logic danh nghĩa chưa thực thi, (c) vắng bóng hoàn toàn ledger chi phí-tài sản, và (d) divergence giữa hai implementation authority.

Đối với câu hỏi "hệ thống này có sẵn sàng cho lớp kinh tế thật (marketplace, trade) không?", câu trả lời ngắn gọn là **chưa — và may là blueprint đã chủ động xếp marketplace money vào post-alpha**. Trước khi bật bất kỳ giao dịch giá trị nào, ba việc bắt buộc là: thống nhất một implementation authority với crypto RNG và signed token; triển khai transaction ledger (balance + escrow + atomic transfer với compensating undo); và đưa schema validation đầy đủ vào authority path. Sau đó hệ thống này có nền đủ tốt để mở rộng thành trade engine thật sự.

---

*Báo cáo này được thực hiện bằng phân tích tĩnh toàn bộ mã nguồn (50.508 dòng GDScript + 4.723 dòng Python), thực thi bộ test Python (57/57 pass), và thẩm định contract schema. Các smoke test GDScript yêu cầu Godot 4.3 binary (không có trong repo và không được cài trong môi trường đánh giá) nên được hiểu là "evidence đã cam kết trong repo, chưa tái kiểm chứng runtime độc lập".*
