# Nori-7 Mockup Upgrade v4 — Cute Water

Files:
- `nori7_rigged.glb`
- `nori7_rigged.glb.import`
- `NORI7_MOCKUP_UPGRADE_V4_RECEIPT.json`

## What changed

This version disables the previous rendered mesh and adds a new modular visual
model parented to the existing 15-bone skeleton. All 15 animation names are
preserved.

The `water` animation now contains six visible animated water-droplet nodes.
Each droplet starts at scale zero, appears at the nozzle, falls, and disappears
before the clip ends.

## Install

Copy both replacement files to:

`res://assets/ucbv_001/character/nori7/export/`

Then reopen Godot 4.3 and let it reimport.

## Required headed checks

Play:
- `idle`
- `walk`
- `water`
- `plant_seed`
- `harvest`
- `low_energy`

Check:
- cream body is opaque;
- leaves are large and readable;
- nozzle and hose do not clip badly;
- six droplets appear during `water`;
- droplets are invisible after the clip;
- all 15 animations remain available.

Status: `PATCH_DRAFT`
accepted: `false`
self_accept: `false`
