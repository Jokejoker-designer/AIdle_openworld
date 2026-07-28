"""Trace pond material through GLB JSON chunks."""
import json
import os
import struct
from pathlib import Path


def parse_glb(path: str) -> dict:
    data = open(path, "rb").read()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF", (magic, path)
    off = 12
    json_chunk = None
    while off < length:
        clen, ctype = struct.unpack_from("<I4s", data, off)
        off += 8
        chunk = data[off : off + clen]
        off += clen
        if ctype.startswith(b"JSON"):
            json_chunk = json.loads(chunk.decode("utf-8"))
    return json_chunk or {}


def report(path: str) -> None:
    print("FILE", path, "bytes", os.path.getsize(path))
    j = parse_glb(path)
    mats = j.get("materials", [])
    print(" materials", len(mats))
    for i, m in enumerate(mats):
        pbr = m.get("pbrMetallicRoughness", {})
        print(
            f"  [{i}] name={m.get('name')!r} base={pbr.get('baseColorFactor')} "
            f"emissive={m.get('emissiveFactor')} alpha={m.get('alphaMode')} "
            f"doubleSided={m.get('doubleSided')}"
        )
    for mi, mesh in enumerate(j.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            print(f"  mesh{mi} prim{pi} material={prim.get('material')}")


lib = r"E:/AIdle_Blender_Bridge_P0/libraries/environments/cozy_cyber_pixel/cozy_pond_small_A.glb"
report(lib)
pkg = r"E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-10A9DEB39E8E"
for root, _ds, fs in os.walk(pkg):
    for f in fs:
        if "pond" in f.lower() and f.endswith(".glb"):
            report(os.path.join(root, f))
