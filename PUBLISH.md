# Publish AIdle Openworld to GitHub (public)

Local monorepo is **already committed** on branch `main`:

- `e6b72e2` — full public snapshot (STAGES 00–06, blueprints, DNA, game, Lightkeep…)
- `ef44de5` — `scripts/publish_github_public.ps1`

## One-command publish (after login)

```powershell
cd E:\AIdle_openworld
E:\AIdle_openworld\tools\gh\bin\gh.exe auth login --hostname github.com --git-protocol https --web
# Browser: https://github.com/login/device  → enter code shown in terminal

powershell -ExecutionPolicy Bypass -File .\scripts\publish_github_public.ps1
# Optional:
#   -RepoName "AIdle_openworld" -Owner "YourUser"
```

Script will:

1. Create **public** repo (if missing)
2. Set `origin`
3. `git push -u origin main`

## Manual alternative

```powershell
cd E:\AIdle_openworld
# After: create empty public repo on github.com named AIdle_openworld
git remote add origin https://github.com/<YOU>/AIdle_openworld.git
git push -u origin main
```

## What is packaged

See [`STAGES/README.md`](STAGES/README.md) and root [`README.md`](README.md).

**Excluded** (gitignore): Godot/Blender exe, `.env`, BACKUP blends, intermediate PASS8 densify blends, large logs, `.godot/` cache.
