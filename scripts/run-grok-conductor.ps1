param(
    [int]$MaxTurns = 80
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$promptFile = Join-Path $projectRoot "orchestration\CONDUCTOR_PROMPT.md"
$agentProfile = Join-Path $projectRoot ".grok\agents\lead-orchestrator.md"

if (-not (Get-Command grok -ErrorAction SilentlyContinue)) {
    throw "grok CLI is not available on PATH"
}
if (-not (Test-Path -LiteralPath $promptFile)) {
    throw "Missing conductor prompt: $promptFile"
}

& grok --cwd $projectRoot --agent $agentProfile --prompt-file $promptFile `
    --check --max-turns $MaxTurns --permission-mode acceptEdits
exit $LASTEXITCODE
