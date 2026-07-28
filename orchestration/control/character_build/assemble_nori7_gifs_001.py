# -*- coding: utf-8 -*-
"""Assemble multi-frame PNG sequences into real animated GIFs via Pillow.

Reads manifest from nori7_anim_gif_frames_manifest.json (Godot capture step).
Writes GIFs under orchestration/evidence/nori7_anim_15clip_001/gifs/
and receipt nori7_anim_gif_proof_001.json.

Encode tool: Pillow (PIL) Image.save(..., save_all=True, append_images=..., duration=..., loop=0)
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

RECEIPT_MANIFEST = Path(
    r"E:\AIdle_openworld\orchestration\receipts\nori7_anim_15clip_001\nori7_anim_gif_frames_manifest.json"
)
GIFS_DIR = Path(r"E:\AIdle_openworld\orchestration\evidence\nori7_anim_15clip_001\gifs")
OUT_RECEIPT = Path(
    r"E:\AIdle_openworld\orchestration\receipts\nori7_anim_15clip_001\nori7_anim_gif_proof_001.json"
)
GARDENER = ("water", "plant_seed", "harvest", "charge", "low_energy")
CONTEXT = ("idle", "walk")


def _rgba_to_rgb(im: Image.Image, bg=(32, 36, 48)) -> Image.Image:
    """Flatten RGBA onto solid background. quantize requires RGB/L (not RGBA)."""
    rgba = im.convert("RGBA")
    base = Image.new("RGB", rgba.size, bg)
    base.paste(rgba, mask=rgba.split()[3])
    return base


def load_frames(paths: list[str]) -> list[Image.Image]:
    """Load all PNGs as RGB then palette-quantize; keep 1:1 source frame count.

    Shared adaptive palette from the first frame keeps colors coherent across the
    clip; each subsequent frame remaps into that palette so GIF save cannot drop
    frames via per-frame palette mismatch.
    """
    if not paths:
        return []
    rgb_frames = [_rgba_to_rgb(Image.open(p)) for p in paths]
    # Build a shared palette from the first frame (covers character + backdrop).
    master = rgb_frames[0].quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    palette = master.getpalette()
    out: list[Image.Image] = [master]
    for rgb in rgb_frames[1:]:
        # Remap into the shared palette so every source frame is retained.
        p = rgb.quantize(palette=master, dither=Image.Dither.FLOYDSTEINBERG)
        if palette is not None and p.getpalette() is None:
            p.putpalette(palette)
        out.append(p)
    return out


def _coalesce_identical(frames: list[Image.Image], duration_ms: int) -> tuple[list[Image.Image], list[int]]:
    """Pillow GIF writer collapses consecutive pixel-identical frames.

    Merge hold frames into one frame with summed duration so total playback
    time still matches source_frame_count * duration_ms.
    """
    if not frames:
        return [], []
    out_frames: list[Image.Image] = [frames[0]]
    out_durs: list[int] = [duration_ms]
    prev_bytes = frames[0].tobytes()
    for fr in frames[1:]:
        b = fr.tobytes()
        if b == prev_bytes:
            out_durs[-1] += duration_ms
        else:
            out_frames.append(fr)
            out_durs.append(duration_ms)
            prev_bytes = b
    return out_frames, out_durs


def write_gif(frames: list[Image.Image], out: Path, duration_ms: int) -> dict:
    if len(frames) < 2:
        return {"ok": False, "error": "need_at_least_2_frames", "path": str(out)}
    out.parent.mkdir(parents=True, exist_ok=True)
    coalesced, durations = _coalesce_identical(frames, duration_ms)
    if len(coalesced) < 2:
        return {
            "ok": False,
            "error": "after_coalesce_need_at_least_2_unique_frames",
            "path": str(out),
            "n_frames_input": len(frames),
        }
    coalesced[0].save(
        out,
        save_all=True,
        append_images=coalesced[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )
    size = out.stat().st_size
    # Verify multi-frame
    verify = Image.open(out)
    n = getattr(verify, "n_frames", 1)
    total_ms = sum(durations)
    return {
        "ok": n >= 2 and size > 500,
        "path": str(out).replace("\\", "/"),
        "bytes": size,
        "n_frames_in_gif": n,
        "n_frames_input": len(frames),
        "n_frames_coalesced": len(coalesced),
        "duration_ms_per_source_sample": duration_ms,
        "total_playback_ms": total_ms,
        "encode": "Pillow.Image.save save_all=True append_images duration=list disposal=2 shared_palette_quantize coalesce_identical_holds",
    }


def main() -> int:
    if not RECEIPT_MANIFEST.exists():
        print(f"FAIL missing manifest {RECEIPT_MANIFEST}")
        return 1
    man = json.loads(RECEIPT_MANIFEST.read_text(encoding="utf-8"))
    clips = {c["clip_id"]: c for c in man.get("clips", [])}
    frame_dt = float(man.get("frame_dt_s", 0.1))
    duration_ms = max(40, int(round(frame_dt * 1000)))

    GIFS_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    gardener_frames: list[Image.Image] = []
    gardener_meta = []

    for clip_id in list(CONTEXT) + list(GARDENER):
        if clip_id not in clips:
            results.append({"clip_id": clip_id, "ok": False, "error": "not_in_manifest"})
            continue
        c = clips[clip_id]
        paths = c.get("frame_paths") or []
        # Prefer sorted pngs in clip_dir if paths empty
        if not paths and c.get("clip_dir"):
            d = Path(c["clip_dir"])
            paths = [str(p) for p in sorted(d.glob("*.png"))]
        frames = load_frames(paths)
        out = GIFS_DIR / f"{clip_id}.gif"
        meta = write_gif(frames, out, duration_ms)
        meta.update(
            {
                "clip_id": clip_id,
                "source_duration_s": c.get("duration_s"),
                "source_frame_count": c.get("frame_count", len(paths)),
                "source_frame_dt_s": c.get("frame_dt_s", frame_dt),
            }
        )
        results.append(meta)
        print(
            f"  {clip_id}: frames={meta.get('n_frames_in_gif')} bytes={meta.get('bytes')} ok={meta.get('ok')}"
        )
        if clip_id in GARDENER and meta.get("ok"):
            gardener_frames.extend(frames)
            gardener_meta.append(clip_id)

    # Combined gardener sequence
    combined = None
    if len(gardener_frames) >= 2:
        cout = GIFS_DIR / "gardener_5clips_sequence.gif"
        combined = write_gif(gardener_frames, cout, duration_ms)
        combined["clips_in_order"] = list(GARDENER)
        print(
            f"  combined: frames={combined.get('n_frames_in_gif')} bytes={combined.get('bytes')} ok={combined.get('ok')}"
        )

    # Context sequence idle→walk
    ctx_frames: list[Image.Image] = []
    for clip_id in CONTEXT:
        if clip_id in clips:
            paths = clips[clip_id].get("frame_paths") or []
            if paths:
                ctx_frames.extend(load_frames(paths))
    ctx_combined = None
    if len(ctx_frames) >= 2:
        ctx_combined = write_gif(ctx_frames, GIFS_DIR / "idle_walk_context.gif", duration_ms)
        print(
            f"  idle_walk: frames={ctx_combined.get('n_frames_in_gif')} bytes={ctx_combined.get('bytes')}"
        )

    ok_gifs = [r for r in results if r.get("ok")]
    receipt = {
        "schema_version": "nori7_anim_gif_proof/1.0",
        "work_order": "WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001",
        "directive_id": 99,
        "purpose": "motion_proof_for_Human — multi-frame GIF not static freeze-frame",
        "accepted": False,
        "self_accept": False,
        "encode_tool": "Pillow",
        "encode_tool_version": Image.__version__,
        "encode_api": "RGBA->RGB flatten; shared-palette quantize; coalesce consecutive identical holds into duration; PIL.Image.save(save_all=True, append_images=..., duration=list, loop=0, disposal=2)",
        "frame_source": "Godot headed capture game/tests/nori7_anim_gif_frames_qa_001.gd",
        "duration_source": "nori7_presenter.get_clip_duration (runtime) + nori7_full_anim_v1_receipt.json SSOT",
        "frame_dt_s": frame_dt,
        "fps_approx": round(1.0 / frame_dt, 2) if frame_dt > 0 else None,
        "duration_ms_per_source_sample": duration_ms,
        "per_clip": results,
        "combined_gardener_5clips": combined,
        "combined_idle_walk": ctx_combined,
        "ok_gif_count": len(ok_gifs),
        "honesty": (
            "Evidence only. Not a product-quality animation claim. "
            "Source samples every frame_dt_s over real clip duration_s. "
            "n_frames_in_gif may be < source_frame_count because consecutive pixel-identical "
            "hold frames are coalesced with summed duration (Pillow drops pure duplicates). "
            "total_playback_ms still tracks source sample count * frame_dt."
        ),
        "manifest": str(RECEIPT_MANIFEST).replace("\\", "/"),
    }
    OUT_RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"receipt={OUT_RECEIPT}")
    if len(ok_gifs) < 5:
        print("FAIL fewer than 5 ok gifs")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
