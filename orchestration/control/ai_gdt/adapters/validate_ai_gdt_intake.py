#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate AI-GDT / Text-to-3D quarantine intake before promote to game/**.

Usage:
  python validate_ai_gdt_intake.py --job-dir E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/JOB
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_glb(p: Path) -> dict:
    data = p.read_bytes()
    if data[:4] != b"glTF":
        return {"ok": False, "error": "not_glb"}
    _ver, length = struct.unpack_from("<II", data, 4)
    off = 12
    chunk_len, chunk_type = struct.unpack_from("<I4s", data, off)
    off += 8
    js = data[off : off + chunk_len]
    try:
        gltf = json.loads(js)
    except Exception as e:
        return {"ok": False, "error": f"json_parse:{e}"}
    anims = [a.get("name") for a in gltf.get("animations", [])]
    mats = [m.get("name") for m in gltf.get("materials", [])]
    skins = gltf.get("skins", [])
    meshes = gltf.get("meshes", [])
    return {
        "ok": True,
        "animations": anims,
        "animation_count": len(anims),
        "materials": mats,
        "skin_count": len(skins),
        "mesh_count": len(meshes),
        "node_count": len(gltf.get("nodes", [])),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--max-mb", type=float, default=80.0)
    args = ap.parse_args()
    job = Path(args.job_dir)
    if not job.is_dir():
        print(json.dumps({"ok": False, "error": "job_dir_missing", "path": str(job)}))
        return 2

    glbs = list(job.rglob("*.glb")) + list(job.rglob("*.gltf"))
    results = []
    ok_all = True
    for g in glbs:
        mb = g.stat().st_size / (1024 * 1024)
        item = {
            "path": str(g).replace("\\", "/"),
            "sha256": sha256_file(g),
            "bytes": g.stat().st_size,
            "mb": round(mb, 3),
        }
        if mb > args.max_mb:
            item["ok"] = False
            item["error"] = "file_too_large"
            ok_all = False
        elif g.suffix.lower() == ".glb":
            item.update(parse_glb(g))
            if not item.get("ok"):
                ok_all = False
        else:
            item["ok"] = True
            item["note"] = "gltf_not_deep_parsed"
        results.append(item)

    report = {
        "ok": ok_all and len(results) > 0,
        "job_dir": str(job).replace("\\", "/"),
        "asset_count": len(results),
        "assets": results,
        "policy": {
            "promote_requires_wo": True,
            "game_write_forbidden_here": True,
            "source": "ai_gdt_intake",
        },
        "accepted": False,
        "self_accept": False,
    }
    out = job / "ai_gdt_validation.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "report": str(out), "assets": len(results)}))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
