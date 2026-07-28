from pathlib import Path
import json
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "foundation_core" / "AIdle_Block_Module_Foundation_v1.0"

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_items(items, schema, label):
    errors=[]
    v=Draft202012Validator(schema)
    for i,item in enumerate(items):
        for err in v.iter_errors(item):
            errors.append(f"{label}[{i}]: {err.message}")
    return errors

def main():
    errors=[]; warnings=[]
    core_modules=load(CORE/"catalogs/module_catalog.json")["modules"]
    core_ids={x["module_id"] for x in core_modules}
    elements=load(ROOT/"catalogs/element_catalog.json")["elements"]
    profiles=load(ROOT/"catalogs/physical_property_profiles.json")["profiles"]
    reactions=load(ROOT/"catalogs/reaction_rules.json")["reaction_rules"]
    forces=load(ROOT/"catalogs/force_blocks.json")["force_blocks"]
    pc_profiles=load(ROOT/"catalogs/pc_platform_profiles.json")["profiles"]
    sim_profiles=load(ROOT/"catalogs/simulation_lod_profiles.json")["profiles"]
    pmods=load(ROOT/"catalogs/pc_physics_modules.json")["physics_modules"]
    bindings=load(ROOT/"catalogs/module_physics_bindings.json")["bindings"]

    errors += validate_items(elements,load(ROOT/"schemas/element_definition.schema.json"),"element")
    errors += validate_items(profiles,load(ROOT/"schemas/physical_property_profile.schema.json"),"profile")
    errors += validate_items(reactions,load(ROOT/"schemas/reaction_rule.schema.json"),"reaction")
    errors += validate_items(pc_profiles,load(ROOT/"schemas/pc_platform_profile.schema.json"),"pc_profile")

    element_ids={x["element_id"] for x in elements}
    profile_ids={x["profile_id"] for x in profiles}
    reaction_ids={x["reaction_id"] for x in reactions}
    force_ids={x["force_id"] for x in forces}
    sim_ids={x["profile_id"] for x in sim_profiles}
    pmod_ids={x["physics_module_id"] for x in pmods}
    pc_ids={x["profile_id"] for x in pc_profiles}

    for p in profiles:
        for eid in p["elements"]:
            if eid not in element_ids: errors.append(f'{p["profile_id"]}: unknown element {eid}')
    for r in reactions:
        for eid in r["inputs"]+r["outputs"]:
            if eid not in element_ids: errors.append(f'{r["reaction_id"]}: unknown element {eid}')
    for p in pc_profiles:
        if p["simulation_lod"] not in sim_ids:
            errors.append(f'{p["profile_id"]}: unknown simulation LOD')
    seen=set()
    for b in bindings:
        mid=b["module_id"]
        if mid in seen: errors.append(f"duplicate binding {mid}")
        seen.add(mid)
        if mid not in core_ids: errors.append(f"unknown core module {mid}")
        for eid in b["elements"]:
            if eid not in element_ids: errors.append(f"{mid}: unknown element {eid}")
        pid=b.get("physical_profile_id")
        if pid and pid not in profile_ids: errors.append(f"{mid}: unknown profile {pid}")
        for x in b["physics_modules"]:
            if x not in pmod_ids: errors.append(f"{mid}: unknown physics module {x}")
        for x in b["reaction_allowlist"]:
            if x not in reaction_ids: errors.append(f"{mid}: unknown reaction {x}")
    if seen != core_ids:
        errors.append(f"binding coverage mismatch: core={len(core_ids)} bindings={len(seen)}")

    ext_schema=load(ROOT/"schemas/physics_build_extension.schema.json")
    for path in sorted((ROOT/"examples").glob("*.json")):
        doc=load(path)
        for err in Draft202012Validator(ext_schema).iter_errors(doc):
            errors.append(f"{path.name}: {err.message}")
        if doc["pc_profile_id"] not in pc_ids: errors.append(f"{path.name}: unknown pc profile")
        for b in doc["elemental_bindings"]:
            for eid in b.get("elements",[]):
                if eid not in element_ids: errors.append(f"{path.name}: unknown element {eid}")
            pid=b.get("physical_profile_id")
            if pid and pid not in profile_ids: errors.append(f"{path.name}: unknown physical profile {pid}")
        for f in doc["force_fields"]:
            if f.get("force_id") not in force_ids: errors.append(f"{path.name}: unknown force")
        for rid in doc["reaction_rules"]:
            if rid not in reaction_ids: errors.append(f"{path.name}: unknown reaction {rid}")

    metrics={"inherited_core_modules":len(core_modules),"elements":len(elements),
             "physical_profiles":len(profiles),"reaction_rules":len(reactions),
             "force_blocks":len(forces),"pc_platform_profiles":len(pc_profiles),
             "simulation_lod_profiles":len(sim_profiles),
             "module_physics_bindings":len(bindings),
             "examples":len(list((ROOT/"examples").glob("*.json")))}
    report={"passed":not errors,"errors":errors,"warnings":warnings,"metrics":metrics}
    (ROOT/"evidence/validation_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__=="__main__":
    raise SystemExit(main())
