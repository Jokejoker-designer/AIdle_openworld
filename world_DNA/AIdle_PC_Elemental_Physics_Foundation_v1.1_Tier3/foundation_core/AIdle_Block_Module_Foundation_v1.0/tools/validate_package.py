from pathlib import Path
import json,sys
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def main():
 e=[]
 mods=load(R/"catalogs/module_catalog.json")["modules"]; sockets=load(R/"catalogs/socket_types.json")["socket_types"]; skels=load(R/"catalogs/skeleton_families.json")["skeleton_families"]; anims=load(R/"catalogs/animation_library.json")["animation_sets"]; beh=load(R/"catalogs/behavior_blocks.json")["behavior_blocks"]; gens=load(R/"catalogs/procedural_generators.json")["procedural_generators"]; rules=load(R/"catalogs/world_rules.json")["world_rules"]; vfx=load(R/"catalogs/vfx_blocks.json")["vfx_blocks"]; audio=load(R/"catalogs/audio_blocks.json")["audio_blocks"]
 ms=load(R/"schemas/module_definition.schema.json"); rs=load(R/"schemas/build_recipe.schema.json"); gs=load(R/"schemas/build_graph.schema.json")
 for i,m in enumerate(mods):
  for x in Draft202012Validator(ms).iter_errors(m): e.append(f"module[{i}] {x.message}")
 ids=lambda arr,key:{x[key] for x in arr}
 MID=ids(mods,"module_id"); SID=ids(sockets,"socket_type"); SK=ids(skels,"skeleton_id"); AN=ids(anims,"animation_set_id"); BE=ids(beh,"behavior_id"); GE=ids(gens,"generator_id"); RU=ids(rules,"rule_id"); VX=ids(vfx,"vfx_id"); AU=ids(audio,"audio_id")
 for m in mods:
  for s in m["socket_inputs"]+m["socket_outputs"]:
   if s not in SID:e.append(f"{m['module_id']} unknown socket {s}")
  if m["skeleton_id"] and m["skeleton_id"] not in SK:e.append(f"{m['module_id']} unknown skeleton")
  if m["animation_set_id"] and m["animation_set_id"] not in AN:e.append(f"{m['module_id']} unknown animation")
  for b in m["behavior_blocks"]:
   if b not in BE:e.append(f"{m['module_id']} unknown behavior {b}")
  for v in m["vfx_blocks"]:
   if v not in VX:e.append(f"{m['module_id']} unknown vfx {v}")
  for a in m["audio_blocks"]:
   if a not in AU:e.append(f"{m['module_id']} unknown audio {a}")
 for p in sorted((R/"examples").glob("*.json")):
  d=load(p); schema=rs if "recipe_type" in d else gs
  for x in Draft202012Validator(schema).iter_errors(d):e.append(f"{p.name} {x.message}")
  if "recipe_type" in d:
   if d["root_module_id"] not in MID:e.append(f"{p.name} missing root")
   for i in d["instances"]:
    if i["module_id"] not in MID:e.append(f"{p.name} missing module {i['module_id']}")
  else:
   for n in d["nodes"]:
    if n["module_id"] not in MID:e.append(f"{p.name} missing module {n['module_id']}")
   for g in d["generators"]:
    if g["generator_id"] not in GE:e.append(f"{p.name} missing generator {g['generator_id']}")
   for r in d["world_rules"]:
    if r["rule_id"] not in RU:e.append(f"{p.name} missing rule {r['rule_id']}")
 metrics={"modules":len(mods),"sockets":len(sockets),"skeletons":len(skels),"animation_sets":len(anims),"animation_clips":sum(len(x["clips"]) for x in anims),"behaviors":len(beh),"generators":len(gens),"examples":len(list((R/"examples").glob("*.json")))}
 rep={"passed":not e,"errors":e,"warnings":[],"metrics":metrics}; (R/"validation_report.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(rep,ensure_ascii=False,indent=2)); return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
