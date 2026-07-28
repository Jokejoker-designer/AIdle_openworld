# Publish AIdle Openworld monorepo to a NEW public GitHub repository.
# Prerequisites: internet; GitHub account.
# Usage (PowerShell, from repo root):
#   powershell -ExecutionPolicy Bypass -File scripts\publish_github_public.ps1
# Optional: -RepoName "AIdle_openworld" -Owner "YourGitHubUser"

param(
  [string]$RepoName = "AIdle_openworld",
  [string]$Owner = "",
  [string]$Visibility = "public",
  [string]$GhPath = "E:\AIdle_openworld\tools\gh\bin\gh.exe"
)

$ErrorActionPreference = "Stop"
# This script lives at <repo>/scripts/publish_github_public.ps1
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path ".\game\project.godot")) {
  throw "Expected AIdle_openworld root (game/project.godot missing). CWD=$(Get-Location)"
}

if (-not (Test-Path $GhPath)) {
  throw "gh not found at $GhPath — install GitHub CLI or update -GhPath"
}

Write-Host "==> Checking GitHub auth..."
& $GhPath auth status 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "Not logged in. Starting device login..."
  Write-Host "1) Browser: https://github.com/login/device"
  Write-Host "2) Enter the one-time code shown below"
  Write-Host ""
  & $GhPath auth login --hostname github.com --git-protocol https --web
  if ($LASTEXITCODE -ne 0) { throw "gh auth login failed" }
}

if ([string]::IsNullOrWhiteSpace($Owner)) {
  $Owner = (& $GhPath api user --jq .login).Trim()
}
Write-Host "Owner=$Owner Repo=$RepoName Visibility=$Visibility"

# Ensure main
git branch -M main

# Create repo if missing
$full = "$Owner/$RepoName"
$exists = $false
& $GhPath repo view $full 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { $exists = $true }

if (-not $exists) {
  Write-Host "==> Creating public repo $full ..."
  & $GhPath repo create $full --public --source=. --remote=origin --description "AIdle Openworld — blueprints, World DNA, Godot 4.3 runtime, orchestration & landmarks" --push
  if ($LASTEXITCODE -ne 0) { throw "gh repo create/push failed" }
} else {
  Write-Host "==> Repo exists; setting remote and pushing..."
  $url = "https://github.com/$full.git"
  git remote remove origin 2>$null
  git remote add origin $url
  git push -u origin main
  if ($LASTEXITCODE -ne 0) { throw "git push failed" }
}

Write-Host ""
Write-Host "DONE: https://github.com/$full"
Write-Host "Stages map: STAGES/README.md"
