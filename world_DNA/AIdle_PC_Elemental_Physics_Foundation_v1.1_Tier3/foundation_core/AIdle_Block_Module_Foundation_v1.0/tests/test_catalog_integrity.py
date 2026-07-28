from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1]
def test_validator():
 r=subprocess.run([sys.executable,str(R/"tools/validate_package.py")],cwd=R,capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr
def test_scale():
 assert len(json.loads((R/"catalogs/module_catalog.json").read_text(encoding="utf-8"))["modules"])>=150
def test_examples():assert len(list((R/"examples").glob("*.json")))>=10
