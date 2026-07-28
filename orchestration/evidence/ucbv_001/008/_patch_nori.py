from pathlib import Path
p = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001/008/capture_ucbv_c4r_headed.gd")
t = p.read_text(encoding="utf-8")
old = '''\t_honesty = {
\t\t"production_mode": str(nori_st.get("production_mode", "glb")),
\t\t"procedural_fallback": bool(nori_st.get("procedural_fallback", true)),
\t\t"glb_path": "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb",
\t\t"nori_status": nori_st,
\t\t"clip_ids": Array(clip_ids),
\t\t"scan_happy": _scan_happy_proof,
\t\t"tier3_optional": _tier3_deferred,
\t\t"block_kit_presentation": "procedural meshdesc (C3-F04 honesty)",
\t\t"c3_f02_provenance": "OPEN_NON_BLOCKING_HYGIENE — C4 does not rewrite",
\t}
\tprint("[UCBV_C4R_HEADED] honesty=%s" % JSON.stringify(_honesty))
'''
new = '''\tvar prod_mode := str(nori_st.get("production_mode", nori_st.get("mode", "")))
\tvar char_id := str(nori_st.get("character_id", ""))
\tvar bone_report := int(nori_st.get("bone_count", nori_st.get("bones", -1)))
\tif bone_report < 0 and _nori != null and _nori.has_method("get_bone_count"):
\t\tbone_report = int(_nori.call("get_bone_count"))
\t_honesty = {
\t\t"character_id": char_id,
\t\t"bones": bone_report,
\t\t"mode": prod_mode,
\t\t"production_mode": prod_mode,
\t\t"procedural_fallback": bool(nori_st.get("procedural_fallback", true)),
\t\t"glb_path": "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb",
\t\t"nori_status": nori_st,
\t\t"clip_ids": Array(clip_ids),
\t\t"scan_happy": _scan_happy_proof,
\t\t"tier3_optional": _tier3_deferred,
\t\t"block_kit_presentation": "procedural meshdesc (C3-F04 honesty)",
\t\t"c3_f02_provenance": "OPEN_NON_BLOCKING_HYGIENE — C4R does not rewrite",
\t\t"not_svg_staging_concept_art": true,
\t}
\tif char_id != "CCP-RH-001":
\t\t_fail("nori_character_id", "got=%s expected=CCP-RH-001" % char_id)
\tif bone_report != 14:
\t\t_fail("nori_bones_status", "bones=%d" % bone_report)
\tif prod_mode != "glb_c1r" and prod_mode.find("glb_c1r") < 0:
\t\t_fail("nori_mode_not_glb_c1r", "mode=%s" % prod_mode)
\tif bool(nori_st.get("procedural_fallback", false)):
\t\t_fail("nori_procedural_fallback", str(nori_st))
\tprint("[UCBV_C4R_HEADED] nori_runtime_proof character_id=%s bones=%d mode=%s" % [char_id, bone_report, prod_mode])
\tprint("[UCBV_C4R_HEADED] honesty=%s" % JSON.stringify(_honesty))
'''
if old not in t:
    raise SystemExit('OLD BLOCK NOT FOUND')
p.write_text(t.replace(old, new), encoding='utf-8', newline='\n')
print('honesty gate patched')
