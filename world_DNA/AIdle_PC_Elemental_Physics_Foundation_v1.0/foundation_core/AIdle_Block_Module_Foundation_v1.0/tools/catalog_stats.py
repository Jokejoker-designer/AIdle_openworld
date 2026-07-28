from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
m=json.loads((R/"catalogs/module_catalog.json").read_text(encoding="utf-8"))["modules"]
d={}
for x in m:d[x["domain"]]=d.get(x["domain"],0)+1
print("Total modules",len(m))
for k,v in sorted(d.items()):print(k,v)
