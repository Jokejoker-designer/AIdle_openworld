<!-- Faithful markdown transcription (pandoc) of E:/AIdle_openworld/Animation_sculb/AIdle Object DNA & AI Build Card System.docx, made 2026-07-24 by Claude conductor for reliable machine reading. Source docx is the SSOT if they ever disagree; this file is a reading convenience only, not a separate authored document. -->

AIdle Object DNA & AI Build Card System
=======================================

Hướng dẫn triển khai chi tiết v1.0
----------------------------------

1. Mục tiêu hệ thống
====================

Xây dựng một nền tảng để AI có thể tạo:

-   Nhân vật người.
-   Động vật.
-   Robot.
-   Sinh vật tưởng tượng.
-   Cây và thực vật.
-   Cửa, cầu, máy móc.
-   Phương tiện.
-   Vật thể có khớp.
-   Công trình có bộ phận chuyển động.

Thay vì yêu cầu AI tự hiểu toàn bộ cấu trúc của từng vật thể, hệ thống
cung cấp cho AI một thư viện **Object DNA** gồm:

    Node graph
    + Skeleton family
    + Rest pose
    + Joint hierarchy
    + Joint constraints
    + Attachment sockets
    + Animation library
    + Physics profile
    + Validation rules

AI chỉ cần:

    Hiểu yêu cầu
    → chọn Object DNA phù hợp
    → đề xuất thiết kế
    → hiển thị các card mockup
    → người dùng chọn
    → AI lập Build Recipe
    → Blender dựng asset
    → Godot import và chạy

2. Kiến trúc tổng thể
=====================

    Người dùng mô tả vật thể
            ↓
    AI Intent Analyzer
            ↓
    Object Family Classifier
            ↓
    Skeleton / Motion DNA Resolver
            ↓
    Mockup Card Generator
            ↓
    Người dùng chọn thiết kế
            ↓
    Build Recipe Generator
            ↓
    Validation Gate
            ↓
    Blender Production Worker
            ↓
    Rig / Skin / Animation / LOD
            ↓
    Godot 4.3 Import
            ↓
    Runtime Validation
            ↓
    Preview
            ↓
    Human Confirm
            ↓
    Approved Catalog / World Commit

3. Các tầng Object DNA
======================

  Tầng   Thành phần                Chức năng
  ------ ------------------------- -------------------------------------------
  L0     Semantic Nodes            Đánh dấu các điểm cơ thể hoặc cơ cấu
  L1     Bone Graph                Xác định quan hệ cha--con
  L2     Joint Rules               Hướng quay, giới hạn góc, twist
  L3     Contact Markers           Điểm đặt chân, cầm đồ, ngồi, gắn phụ kiện
  L4     Skeleton Family           Bộ khung chuẩn của một loại vật thể
  L5     Animation Library         Các chuyển động dùng lại
  L6     Character/Object Recipe   Thiết kế cụ thể của một vật thể
  L7     Runtime Module            Asset hoàn chỉnh dùng trong Godot

4. Không nên dùng A, B, C làm ID chính
======================================

Có thể hiển thị A, B, C trên hình stickman để dễ nhìn, nhưng dữ liệu
phải dùng ID ngữ nghĩa.

Ví dụ:

  Marker hiển thị   Semantic ID    Ý nghĩa
  ----------------- -------------- ----------------------
  A                 `root`         Gốc toàn bộ skeleton
  B                 `pelvis`       Hông
  C                 `spine_01`     Đốt sống dưới
  D                 `chest`        Ngực
  E                 `neck`         Cổ
  F                 `head`         Đầu
  G                 `upperarm_L`   Cánh tay trái
  H                 `elbow_L`      Khuỷu tay trái
  I                 `hand_L`       Bàn tay trái

Dữ liệu:

    {
      "marker": "A",
      "semantic_id": "root",
      "parent": null
    }

5. Các Skeleton Family cần xây
==============================

5.1 Nhân vật người
------------------

  Skeleton ID              Ứng dụng
  ------------------------ ----------------------
  `humanoid_standard_v1`   Người trưởng thành
  `humanoid_small_v1`      Trẻ em, người lùn
  `humanoid_heavy_v1`      Nhân vật to, thợ rèn
  `humanoid_slender_v1`    Nhân vật cao, mảnh
  `humanoid_robot_v1`      Robot hình người
  `humanoid_four_arm_v1`   Sinh vật bốn tay

Animation cơ bản:

    idle
    walk
    run
    jump
    fall
    land
    sit
    stand
    sleep
    wave
    talk_A
    talk_B
    handshake
    carry
    give_item
    receive_item
    push
    pull
    work
    repair

5.2 Động vật bốn chân
---------------------

  Skeleton ID                Ứng dụng
  -------------------------- --------------------
  `quadruped_small_v1`       Mèo, chó nhỏ
  `quadruped_medium_v1`      Chó lớn, hươu
  `quadruped_heavy_v1`       Trâu, bò, thú cưỡi
  `quadruped_long_body_v1`   Chồn, rồng đất

Animation:

    idle
    walk
    trot
    run
    jump
    sit
    lie
    sleep
    sniff
    dig
    shake
    eat
    drink
    pet_reaction
    carry_rider

5.3 Chim và sinh vật bay
------------------------

  Skeleton ID          Ứng dụng
  -------------------- --------------
  `bird_small_v1`      Chim nhỏ
  `bird_large_v1`      Chim cưỡi
  `origami_bird_v1`    Chim giấy
  `flying_spirit_v1`   Linh hồn bay

Animation:

    idle
    flap
    glide
    takeoff
    land
    turn_left
    turn_right
    perch
    fold_wings
    hover
    dive

5.4 Cá và sinh vật dưới nước
----------------------------

  Skeleton ID               Ứng dụng
  ------------------------- -----------------
  `fish_standard_v1`        Cá
  `ray_v1`                  Cá đuối
  `serpentine_swimmer_v1`   Rắn biển
  `tentacle_swimmer_v1`     Sinh vật xúc tu

Animation:

    idle_swim
    swim
    fast_swim
    turn
    dive
    rise
    glide
    attack
    carry_player
    sleep

5.5 Robot và máy móc
--------------------

  Skeleton ID               Ứng dụng
  ------------------------- ----------------
  `robot_biped_small_v1`    Nori-7
  `robot_biped_heavy_v1`    Robot xây dựng
  `robot_wheeled_v1`        Robot bánh xe
  `golem_modular_v1`        Golem
  `building_mechanism_v1`   Tháp, máy móc
  `door_mechanism_v1`       Cửa
  `water_wheel_v1`          Bánh xe nước

Animation:

    idle
    walk
    rotate
    open
    close
    activate
    shutdown
    repair
    jammed
    broken
    charge
    discharge

5.6 Cây và thực vật
-------------------

  Skeleton ID          Ứng dụng
  -------------------- ------------
  `plant_small_v1`     Cây nhỏ
  `tree_standard_v1`   Cây thường
  `tree_landmark_v1`   Cây lớn
  `vine_v1`            Dây leo
  `flower_v1`          Hoa

Animation:

    seed
    sprout
    grow
    bloom
    fruit
    wind_idle
    wind_medium
    wind_strong
    wither
    restore

5.7 Phương tiện
---------------

  Skeleton ID                  Ứng dụng
  ---------------------------- -----------------
  `vehicle_wheeled_small_v1`   Xe nhỏ
  `vehicle_cart_v1`            Xe kéo
  `vehicle_train_v1`           Tàu
  `vehicle_boat_v1`            Thuyền
  `vehicle_submarine_v1`       Tàu ngầm
  `vehicle_flying_v1`          Phương tiện bay

6. Cấu trúc một Pose DNA Package
================================

    Pose_DNA/
    └── humanoid_standard_v1/
        ├── skeleton_definition.json
        ├── rest_pose.json
        ├── node_markers.json
        ├── bone_orientation.json
        ├── joint_constraints.json
        ├── contact_markers.json
        ├── attachment_sockets.json
        ├── retarget_profile.json
        ├── validation_rules.json
        ├── marker_templates/
        │   ├── front.png
        │   ├── side.png
        │   ├── back.png
        │   └── perspective.png
        └── animations/
            ├── idle.glb
            ├── walk.glb
            ├── run.glb
            ├── jump.glb
            ├── sit.glb
            └── handshake.glb

7. Schema Skeleton DNA đề xuất
==============================

    {
      "schema_version": "1.0",
      "skeleton_family": "humanoid_standard_v1",
      "rest_pose": "A_POSE",
      "nodes": [
        {
          "marker": "A",
          "semantic_id": "root",
          "parent": null,
          "required": true
        },
        {
          "marker": "B",
          "semantic_id": "pelvis",
          "parent": "root",
          "required": true
        },
        {
          "marker": "C",
          "semantic_id": "spine_01",
          "parent": "pelvis",
          "required": true
        }
      ],
      "contact_markers": [
        "foot_contact_L",
        "foot_contact_R",
        "hand_grip_L",
        "hand_grip_R",
        "seat_contact"
      ]
    }

8. Quy trình AI tạo Character từ mockup
=======================================

  Bước   AI thực hiện           Output
  ------ ---------------------- ---------------------
  1      Phân tích prompt       Character brief
  2      Phân loại nhân vật     Object family
  3      Đề xuất skeleton       Skeleton candidates
  4      Tạo nhiều mockup       Mockup cards
  5      Người dùng chọn card   Selected concept
  6      Tạo nhiều góc nhìn     Front/side/back
  7      Match node semantic    Landmark map
  8      Chọn base topology     Mesh template
  9      Tạo Character Recipe   JSON recipe
  10     Blender dựng mesh      Quarantine asset
  11     Gắn skeleton           Rigged mesh
  12     Skinning               Weighted mesh
  13     Gắn animation          Animation bindings
  14     Tạo LOD                LOD0--LOD3
  15     Export GLB             Godot-ready asset
  16     Godot test             Runtime report
  17     Người dùng duyệt       Approved module

9. Giao diện AI Build dạng card bo góc
======================================

9.1 Luồng UX
------------

    Người dùng nhập ý tưởng
    → AI đề xuất 3–6 card
    → mỗi card là một hướng thiết kế
    → người dùng chọn một card
    → AI mở card chi tiết
    → người dùng chỉnh skeleton/màu/phụ kiện
    → nhấn Build

9.2 Card cấp 1 --- Object Family Card
-------------------------------------

Ví dụ prompt:

> Tạo một robot nhỏ chăm sóc vườn, thân tròn, dễ thương.

AI đề xuất:

    ┌──────────────────────────────┐
    │ [Mockup robot]               │
    │                              │
    │ ROBOT HAI CHÂN               │
    │ Skeleton: robot_biped_small  │
    │ Animation: 18 clips          │
    │ Độ khó: Thấp                 │
    │ Tương thích Godot: Tốt       │
    │                              │
    │ [XEM CHI TIẾT]  [CHỌN]       │
    └──────────────────────────────┘
    ┌──────────────────────────────┐
    │ [Mockup robot bánh xe]       │
    │                              │
    │ ROBOT BÁNH XE                │
    │ Skeleton: robot_wheeled      │
    │ Animation: 12 clips          │
    │ Độ khó: Rất thấp             │
    │ Tương thích Godot: Rất tốt   │
    │                              │
    │ [XEM CHI TIẾT]  [CHỌN]       │
    └──────────────────────────────┘
    ┌──────────────────────────────┐
    │ [Mockup robot bốn chân]      │
    │                              │
    │ ROBOT THÚ CƯNG               │
    │ Skeleton: quadruped_small    │
    │ Animation: 16 clips          │
    │ Độ khó: Trung bình           │
    │ Tương thích Godot: Tốt       │
    │                              │
    │ [XEM CHI TIẾT]  [CHỌN]       │
    └──────────────────────────────┘

9.3 Thông tin bắt buộc trên card
--------------------------------

  Trường                 Nội dung
  ---------------------- -------------------------------
  Thumbnail              Hình mockup
  Design ID              ID thiết kế
  Object family          Humanoid, quadruped, robot...
  Skeleton family        Bộ khung đề xuất
  Animation set          Số animation tương thích
  Build path             Template hoặc generative
  Complexity             Low, Medium, High
  Expected quality       Prototype, Game-ready, Hero
  Performance class      XS--XL
  PC/mobile support      Nền tảng phù hợp
  Confidence             Độ tin cậy AI
  Missing requirements   Những phần còn thiếu
  Build time class       Fast, Medium, Slow
  Buttons                Preview, Edit, Select

10. Card cấp 2 --- Skeleton Selection Card
==========================================

Sau khi chọn thiết kế, AI hiển thị skeleton phù hợp.

    ┌────────────────────────────────┐
    │ HUMANOID STANDARD              │
    │                                │
    │ ● 42 bones                     │
    │ ● 28 animation clips           │
    │ ● Handshake supported          │
    │ ● Tool sockets                 │
    │ ● Facial rig optional          │
    │                                │
    │ Fit score: 94%                 │
    │ [CHỌN SKELETON]                │
    └────────────────────────────────┘
    ┌────────────────────────────────┐
    │ HUMANOID SMALL                 │
    │                                │
    │ ● 36 bones                     │
    │ ● 22 animation clips           │
    │ ● Compact proportions          │
    │ ● Farming animations           │
    │                                │
    │ Fit score: 86%                 │
    │ [CHỌN SKELETON]                │
    └────────────────────────────────┘

11. Card cấp 3 --- Visual Style Card
====================================

Người dùng chọn:

-   Hình dạng.
-   Màu sắc.
-   Vật liệu.
-   Mức độ chi tiết.
-   Phong cách thế giới.

Ví dụ:

    Cozy Cyber-Pixel
    Tiny Diorama
    Solarpunk
    Arcane Clockwork
    Spirit Valley
    Surrealism
    Oceanpunk

Mỗi card cho biết:

    Material theme
    Palette
    Shader profile
    LOD target
    VFX compatibility
    World compatibility

12. Card cấp 4 --- Animation Package Card
=========================================

Ví dụ:

    SOCIAL BASIC
    ├── idle
    ├── walk
    ├── wave
    ├── talk_A
    ├── talk_B
    ├── sit
    ├── stand
    └── handshake
    FARMING WORKER
    ├── hoe
    ├── plant_seed
    ├── water
    ├── harvest
    ├── carry
    ├── repair
    └── rest
    ADVENTURE
    ├── run
    ├── jump
    ├── fall
    ├── land
    ├── climb
    ├── push
    └── pull

Người dùng có thể chọn nhiều animation package.

13. Card cấp 5 --- Build Confirmation Card
==========================================

Trước khi build, hệ thống hiển thị bản tóm tắt:

    DESIGN
    Nori-7 Gardener Robot

    SKELETON
    robot_biped_small_v1

    ANIMATION SETS
    robot_core
    gardening
    social_basic

    PARTS
    rounded_body
    display_face
    water_tank
    watering_nozzle
    mechanical_sprout

    MATERIAL
    cozy_cream_leaf_v1

    OUTPUT
    LOD0–LOD3
    GLB
    Godot scene
    AnimationLibrary
    Collision
    Character manifest

Nút:

    [QUAY LẠI]
    [CHỈNH SỬA]
    [TẠO PREVIEW]
    [BẮT ĐẦU BUILD]

14. Trạng thái build
====================

    DRAFT
    → MOCKUP_GENERATED
    → USER_SELECTED
    → RECIPE_CREATED
    → VALIDATION_PENDING
    → BLENDER_BUILDING
    → RIGGING
    → SKINNING
    → ANIMATION_BINDING
    → LOD_GENERATION
    → GODOT_IMPORTING
    → RUNTIME_TESTING
    → REVIEW_REQUIRED
    → APPROVED

AI không được tự chuyển:

    REVIEW_REQUIRED
    → APPROVED

Bước này cần người dùng hoặc reviewer.

15. Character Build Recipe
==========================

    {
      "schema_version": "1.0",
      "character_id": "nori7_gardener_v1",
      "design_card_id": "card_robot_002",
      "world_profile": "cozy_cyber_pixel",
      "skeleton_family": "robot_biped_small_v1",
      "rest_pose": "ROBOT_NEUTRAL",
      "body_modules": [
        "rounded_body_A",
        "display_face_A",
        "short_arm_A",
        "short_leg_A"
      ],
      "attachments": [
        "water_tank_small",
        "watering_nozzle_A",
        "mechanical_sprout_A"
      ],
      "animation_sets": [
        "robot_core_v1",
        "robot_gardener_v1"
      ],
      "material_theme": "mat_cozy_cream_leaf_v1",
      "output": {
        "lod_levels": 4,
        "collision": true,
        "glb": true,
        "godot_scene": true
      }
    }

16. Node Matching Pipeline
==========================

Template Character
------------------

    Base mesh đã biết
    → node đã đăng ký
    → skeleton tự gắn
    → animation chạy ngay

Độ tin cậy cao nhất.

Generated Character
-------------------

    Mockup
    → multiview
    → mesh
    → body segmentation
    → landmark detection
    → node matching
    → skeleton fitting
    → skinning
    → validation

Độ tin cậy thấp hơn, cần quarantine.

17. Các bước matching node
==========================

  Bước   Kiểm tra
  ------ --------------------------------
  1      Xác định hướng trước/sau
  2      Xác định đối xứng trái/phải
  3      Tìm vùng đầu, thân, chi
  4      Match marker node
  5      Fit skeleton vào thể tích mesh
  6      Kiểm tra bone nằm trong mesh
  7      Kiểm tra chiều dài bone
  8      Kiểm tra joint orientation
  9      Kiểm tra constraints
  10     Tạo skin weights
  11     Chạy test animation
  12     Phát hiện mesh xuyên/gãy

18. Validation bắt buộc
=======================

Skeleton validation
-------------------

-   Bone bắt buộc có đủ.
-   Không có bone trùng.
-   Không có cycle.
-   Parent đúng.
-   Scale hợp lệ.
-   Rest pose hợp lệ.

Skin validation
---------------

-   Vertex không bị bỏ weight.
-   Tổng weight gần bằng 1.
-   Không quá nhiều influence.
-   Vai, khuỷu, hông, đầu gối biến dạng đúng.

Animation validation
--------------------

-   Không trượt chân quá mức.
-   Tay không xuyên thân.
-   Đầu không xoay ngược.
-   Root motion đúng.
-   Contact events đúng.

Godot validation
----------------

-   Skeleton3D import thành công.
-   AnimationLibrary import thành công.
-   BoneMap đúng.
-   Collision đúng.
-   AnimationTree chạy.
-   Save/reload hoạt động.
-   Performance đạt budget.

19. Hệ card dành cho vật thể không phải nhân vật
================================================

Cửa
---

Card đề xuất:

    Cửa bản lề
    Cửa trượt
    Cửa xoay
    Cửa cơ khí
    Cửa ma thuật

Skeleton:

    root
    door_leaf
    hinge
    handle
    lock

Animation:

    open
    close
    locked_shake
    break
    repair

Bánh xe nước
------------

Card:

    Bánh xe gỗ nhỏ
    Bánh xe Solarpunk
    Bánh xe Clockwork
    Bánh xe Crystal

Skeleton:

    root
    wheel
    axle
    gear_01
    generator_rotor

Cây
---

Card:

    Cây nhỏ
    Cây ăn quả
    Cây landmark
    Cây tinh linh
    Cây đảo ngược

Skeleton:

    root
    trunk
    branch_01
    branch_02
    leaf_cluster_01
    leaf_cluster_02

20. Phân công AI Agent
======================

  Agent                 Trách nhiệm
  --------------------- -------------------------
  Intent Agent          Hiểu yêu cầu
  Object Classifier     Chọn object family
  Skeleton Resolver     Đề xuất skeleton
  Mockup Agent          Tạo card concept
  Recipe Agent          Tạo Build Recipe
  Node Matching Agent   Match node vào mesh
  Rigging Agent         Tạo skeleton binding
  Animation Agent       Chọn/retarget animation
  Blender Agent         Tạo asset spec
  Godot Agent           Import/runtime setup
  Validator Agent       Kiểm tra độc lập
  Review Agent          Tổng hợp evidence

Không agent nào tự nghiệm thu output của chính nó.

21. Cấu trúc repository đề xuất
===============================

    AIdle_Object_DNA/
    ├── schemas/
    ├── object_families/
    ├── skeleton_families/
    ├── pose_dna/
    ├── animation_library/
    ├── material_themes/
    ├── attachment_modules/
    ├── mockup_cards/
    ├── build_recipes/
    ├── blender_worker/
    ├── godot_4_3/
    ├── validation/
    ├── quarantine/
    ├── approved_catalog/
    └── evidence/

22. Lộ trình triển khai
=======================

  Giai đoạn   Mục tiêu              Output
  ----------- --------------------- -----------------------
  P0          Schema và registry    DNA contracts
  P1          Robot biped           Nori-7
  P2          Humanoid              NPC người
  P3          Quadruped             Bụi Mơ
  P4          Mechanism             Cửa, bánh xe
  P5          Plant rig             Cây và crop
  P6          Mockup card UI        Card selection system
  P7          Blender Bridge        Build tự động
  P8          Godot runtime         AnimationTree
  P9          Generated mesh path   Image-to-character
  P10         Catalog expansion     Nhiều family

23. Vertical Slice đầu tiên
===========================

Nên triển khai trước:

    Prompt:
    “Tạo một robot nhỏ chăm sóc vườn.”

    AI đề xuất ba card:
    1. Robot hai chân
    2. Robot bánh xe
    3. Robot bốn chân

    Người dùng chọn:
    Robot hai chân

    Skeleton:
    robot_biped_small_v1

    AI tạo:
    Nori-7 Character Recipe

    Blender:
    mesh + rig + attachments + LOD

    Godot:
    idle + walk + water + harvest

    Kết quả:
    Character hoạt động trong Cozy Farm

24. Definition of Done
======================

Hệ thống được xem là hoàn thành bản đầu khi:

-   AI tạo ít nhất ba card thiết kế.
-   Mỗi card có skeleton phù hợp.
-   Người dùng chọn được card.
-   AI tạo Build Recipe đúng schema.
-   Blender tạo được asset modular.
-   Skeleton khớp Pose DNA.
-   Ít nhất năm animation hoạt động.
-   Godot import thành công.
-   AnimationTree hoạt động.
-   Character di chuyển và tương tác.
-   Save/reload không mất thiết kế.
-   Không có arbitrary AI code execution.
-   Asset đi qua quarantine.
-   Người dùng phải xác nhận trước khi approved.
-   Recipe và evidence được lưu đầy đủ.

25. Kiến trúc cuối cùng
=======================

    USER INTENT
        ↓
    ROUNDED MOCKUP CARDS
        ↓
    USER SELECTS DESIGN
        ↓
    OBJECT DNA FAMILY
        ↓
    SEMANTIC NODE MATCHING
        ↓
    SKELETON + ANIMATION
        ↓
    MODULAR CHARACTER RECIPE
        ↓
    BLENDER PRODUCTION
        ↓
    GODOT 4.3 RUNTIME
        ↓
    PREVIEW
        ↓
    HUMAN APPROVAL
        ↓
    APPROVED GAME MODULE

Kết luận
--------

Hướng thiết kế card bo góc kết hợp Object DNA là một trong những kiến
trúc phù hợp nhất cho AIdle.

Nó giải quyết đồng thời ba vấn đề:

1.  Người dùng không cần hiểu rigging.
2.  AI không phải tự phát minh skeleton mỗi lần.
3.  Blender và Godot nhận được dữ liệu có cấu trúc, kiểm tra được.

Điểm cốt lõi:

> AI đề xuất nhiều khả năng bằng card. Người dùng chọn ý định thiết kế.
> Object DNA cung cấp cấu trúc chuyển động. Blender sản xuất asset.
> Godot vận hành gameplay.
