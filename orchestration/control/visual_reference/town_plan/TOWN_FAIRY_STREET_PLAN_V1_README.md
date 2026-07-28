# TOWN_FAIRY_STREET_PLAN_V1 — Thị trấn Cổ tích Thân thiện (+ đường đá & bệ gỗ)

**Có.** Quy hoạch **storybook street town** với:

- **Đường bằng phẳng lát đá** (`STONE_PAVER_FLAT`, slope 0°)
- **Bệ / ván gỗ** (`WOOD_DECK_FLAT`, `WOOD_BOARDWALK`, `WOOD_BRIDGE_DECK`)
- Phương pháp segment [3DStreet](https://github.com/3DStreet/3dstreet) — **không** clone AGPL assets
- Kiến trúc lặp family + palette xen kẽ
- 50 plots MOCKUP_SSOT_V2 · bounds ±12

## Mở

| File | Mô tả |
|------|--------|
| `TOWN_FAIRY_STREET_PLAN_V1.html` | Mockup (có bảng stone/wood) |
| `TOWN_FAIRY_STREET_PLAN_V1.svg` | Bản đồ — paver pattern + wood plank |
| `TOWN_FAIRY_STREET_PLAN_V1.json` | `stone_path_network` + `wood_platforms` + materials |
| `_gen_fairy_street_v1.py` | Generator |

## Bề mặt (v1.1)

### Vật liệu

| Material | Vai trò |
|----------|---------|
| `STONE_PAVER_FLAT` | Lòng đường / vành đai / hẻm — đá lát phẳng |
| `STONE_RING_PLAZA` | Vòng đá quanh gazebo |
| `WOOD_DECK_FLAT` | Bệ gỗ trước cửa, shop, tháp, barn… |
| `WOOD_BOARDWALK` | Lối ván ven nước (WELL) |
| `WOOD_BRIDGE_DECK` | Mặt sàn gỗ cầu vòm |

**Layer:** lawn → stone → wood deck/boardwalk → props → buildings.  
Gỗ cao hơn path ~0.06–0.12m (mép đọc được, vẫn walkable flat). Junction đá–gỗ bo tròn, không bậc cao.

### Mạng đá (13 segment)

- `SP-01` — Storybook Lane — đá lát phẳng (3.0m, flat)
- `SP-02` — Cottage Walk — đá lát phẳng (2.5m, flat)
- `SP-03` — Craft Alley — đá lát phẳng (2.0m, flat)
- `SP-04` — Trục đá ngang plaza (Đông–Tây) (2.5m, flat)
- `SP-05` — Trục đá dọc plaza (Bắc–Nam) (2.5m, flat)
- `SP-06` — Nối đá plaza → boardwalk giếng (1.8m, flat)
- `SP-07` — Mill Road — đá lát phẳng (2.0m, flat)
- `SP-08` — Nhánh đá vườn nghỉ (1.5m, flat)
- `SP-09` — Bridge Approach — đá phẳng (2.0m, flat)
- `SP-10` — Nhánh đá nhà kính (1.5m, flat)
- `SP-11` — Nhánh đá tháp vọng (1.5m, flat)
- `SP-RING` — Vành đai đá phẳng (4 cạnh soft rect) (1.8m, flat)
- `SP-PLAZA-RING` — Vòng đá quanh gazebo (1.2m, flat)

### Bệ gỗ (12)

- `WD-GAZEBO` — Bệ gỗ dưới gazebo (plaza) → cozy_gazebo_A
- `WD-COTTAGE` — Bệ gỗ hiên cottage → cozy_house_small_A
- `WD-SHOP` — Bệ gỗ mặt tiền chợ → cozy_market_stall_A
- `WD-WORKSHOP` — Bệ gỗ sân xưởng → cozy_workshop_A
- `WD-WELL` — Bệ gỗ quanh nhà giếng → cozy_well_house_A
- `WB-01` — Boardwalk gỗ ven nước (N–S) → water_edge_walk
- `WD-GREENHOUSE` — Bệ gỗ cửa nhà kính → cozy_greenhouse_A
- `WD-WINDMILL` — Bệ gỗ chân cối xay → cozy_windmill_A
- `WD-BARN` — Bệ gỗ sân barn → cozy_barn_small_A
- `WD-BRIDGE` — Mặt sàn gỗ cầu vòm → cozy_bridge_arch_A
- `WD-LOOKOUT` — Bệ gỗ chân tháp vọng → cozy_watchtower_A
- `WD-GARDEN` — Bệ gỗ góc vườn nghỉ → bench_nook

### Module production

| Surface | Module |
|---------|--------|
| Đá | `cozy_path_stone_A` (+ strip variants sau) |
| Bệ gỗ | design slot `cozy_wood_deck_A` (chưa GLB) |
| Boardwalk | design slot `cozy_boardwalk_A` (chưa GLB) |
| Cầu | part of `cozy_bridge_arch_A` |

## Architecture families

Cottage / Shop / Workshop / Gazebo / Greenhouse / Well / Windmill / Barn / Bridge / Lookout (`cozy_watchtower_A`).

## Status

**accepted=false** — design only. Không patch `game/**`. Human + wave packet trước import runtime.

## Regenerate

```text
python orchestration/control/visual_reference/town_plan/_gen_fairy_street_v1.py
```
