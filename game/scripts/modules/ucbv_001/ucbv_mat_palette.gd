## UCBV-001 MAT_* palette for offline procedural materials (U1 tokens / art bible hex).
## Presentation only — not world truth / not DNA authority.
extends RefCounted

## Canonical cozy MAT_* → albedo (hex from U1 tokens / material_bindings).
const MAT_COLORS := {
	"MAT_CozyCeramic": Color(0.992, 0.953, 0.886),       # #fdf3e2
	"MAT_CozyStoneWarm": Color(0.937, 0.878, 0.784),     # #efe0c8
	"MAT_CozyStone": Color(0.878, 0.835, 0.769),         # #e0d5c4
	"MAT_CozyWood": Color(0.788, 0.541, 0.369),          # #c98a5e
	"MAT_CozyDoor": Color(0.788, 0.541, 0.369),          # #c98a5e
	"MAT_CozyGlass": Color(0.659, 0.863, 0.929, 0.55),   # #a8dced
	"MAT_CozyGlassPreview": Color(0.659, 0.863, 0.929, 0.35),
	"MAT_CozyRoof": Color(0.910, 0.545, 0.435),          # #e88b6f
	"MAT_CozyRoofShade": Color(0.831, 0.471, 0.369),     # #d4785e
	"MAT_CozyLeaf": Color(0.498, 0.788, 0.561),          # #7fc98f
	"MAT_CozyStem": Color(0.420, 0.722, 0.498),
	"MAT_CozyMetal": Color(0.72, 0.74, 0.78),
	"MAT_CozyLampWarm": Color(0.961, 0.769, 0.318),      # #f5c451
	"MAT_CozyFencePost": Color(0.72, 0.50, 0.34),
	"MAT_CozyFenceRail": Color(0.78, 0.56, 0.40),
	"MAT_CozyGround": Color(0.55, 0.68, 0.42),
	"MAT_CozySoil": Color(0.45, 0.34, 0.24),
	"MAT_CozyPreviewMarker": Color(0.25, 0.82, 0.88, 0.45),
	"MAT_CozyBark": Color(0.42, 0.30, 0.20),
	"MAT_CozyWater": Color(0.45, 0.72, 0.88, 0.55),
	"MAT_CozyWaterLight": Color(0.60, 0.82, 0.92, 0.45),
	"MAT_CozyFlowerPink": Color(0.96, 0.63, 0.70),
	"MAT_CozyFlowerYellow": Color(0.96, 0.85, 0.40),
	"MAT_CozyFlowerPurple": Color(0.70, 0.55, 0.88),
	"MAT_BuildPlot": Color(0.55, 0.70, 0.45, 0.35),
}

const SLOT_DEFAULT_MAT := {
	"body": "MAT_CozyCeramic",
	"secondary": "MAT_CozyStone",
	"accent": "MAT_CozyStoneWarm",
	"structure": "MAT_CozyStoneWarm",
	"trim": "MAT_CozyWood",
	"glass": "MAT_CozyGlass",
	"ground": "MAT_CozyGround",
	"emission": "MAT_CozyLampWarm",
	"roof": "MAT_CozyRoof",
	"wood": "MAT_CozyWood",
	"stone": "MAT_CozyStone",
	"water": "MAT_CozyWater",
	"leaf": "MAT_CozyLeaf",
	"metal": "MAT_CozyMetal",
	"soil": "MAT_CozySoil",
	"door": "MAT_CozyDoor",
	"glass_eyes": "MAT_CozyGlass",
	"leaf_joints": "MAT_CozyLeaf",
	"stone_foot_pads": "MAT_CozyStoneWarm",
}


static func color_for_mat(mat_id: String) -> Color:
	if MAT_COLORS.has(mat_id):
		return MAT_COLORS[mat_id]
	return Color(0.85, 0.82, 0.78)


static func color_for_slot(slot: String) -> Color:
	var mat_id := str(SLOT_DEFAULT_MAT.get(slot, "MAT_CozyCeramic"))
	return color_for_mat(mat_id)


static func mat_for_slot(slot: String) -> String:
	return str(SLOT_DEFAULT_MAT.get(slot, "MAT_CozyCeramic"))


static func make_material(mat_id: String, alpha_mul: float = 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var c := color_for_mat(mat_id)
	c.a = clampf(c.a * alpha_mul, 0.0, 1.0)
	m.albedo_color = c
	if c.a < 0.999:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	if mat_id == "MAT_CozyLampWarm":
		m.emission_enabled = true
		m.emission = c
		m.emission_energy_multiplier = 0.8
	if mat_id == "MAT_CozyMetal":
		m.metallic = 0.55
		m.roughness = 0.35
	else:
		m.roughness = 0.72
	return m


static func make_stage_material(base_mat_id: String, stage: String, placement_valid: bool = true) -> StandardMaterial3D:
	## Preview stages tint — cyan reserved for manifestation chrome, not Nori body.
	var m := make_material(base_mat_id)
	var base := m.albedo_color
	var opacity := 1.0
	match stage:
		"wireframe":
			opacity = 0.28
			m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		"hologram":
			opacity = 0.45
			m.emission_enabled = true
			m.emission = Color(0.25, 0.82, 0.88) if placement_valid else Color(0.95, 0.30, 0.22)
			m.emission_energy_multiplier = 0.55
		"materializing":
			opacity = 0.72
			m.emission_enabled = true
			m.emission = Color(0.35, 0.75, 0.85)
			m.emission_energy_multiplier = 0.35
		"complete":
			opacity = 1.0
		_:
			opacity = 0.5
	if not placement_valid and stage != "complete":
		base = base.lerp(Color(0.95, 0.35, 0.28), 0.45)
	base.a = opacity
	m.albedo_color = base
	if opacity < 0.999:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	return m
