from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def test_validator_passes():
    r=subprocess.run([sys.executable,str(ROOT/"tools/validate_package.py")],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0, r.stdout+r.stderr

def test_all_core_modules_have_bindings():
    core=json.loads((ROOT/"foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/module_catalog.json").read_text(encoding="utf-8"))["modules"]
    bindings=json.loads((ROOT/"catalogs/module_physics_bindings.json").read_text(encoding="utf-8"))["bindings"]
    assert {x["module_id"] for x in core} == {x["module_id"] for x in bindings}

def test_pc_profiles_reference_sim_lod():
    profiles=json.loads((ROOT/"catalogs/pc_platform_profiles.json").read_text(encoding="utf-8"))["profiles"]
    sim=json.loads((ROOT/"catalogs/simulation_lod_profiles.json").read_text(encoding="utf-8"))["profiles"]
    ids={x["profile_id"] for x in sim}
    assert all(x["simulation_lod"] in ids for x in profiles)

def test_reactions_use_known_elements():
    elements=json.loads((ROOT/"catalogs/element_catalog.json").read_text(encoding="utf-8"))["elements"]
    reactions=json.loads((ROOT/"catalogs/reaction_rules.json").read_text(encoding="utf-8"))["reaction_rules"]
    ids={x["element_id"] for x in elements}
    assert all(e in ids for r in reactions for e in r["inputs"]+r["outputs"])

def test_examples_are_preview_only():
    for p in (ROOT/"examples").glob("*.json"):
        d=json.loads(p.read_text(encoding="utf-8"))
        assert d["simulation"]["preview_only"] is True
        assert d["rollback"]["allowed"] is True
