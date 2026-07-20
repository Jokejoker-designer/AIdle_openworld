param(
    [int]$MaxTurns = 80
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$promptFile = Join-Path $projectRoot "orchestration\CONDUCTOR_PROMPT.md"

if (-not (Get-Command grok -ErrorAction SilentlyContinue)) {
    throw "grok CLI is not available on PATH"
}
if (-not (Test-Path -LiteralPath $promptFile)) {
    throw "Missing conductor prompt: $promptFile"
}

& grok --cwd $projectRoot --agent aidle-conductor --prompt-file $promptFile `
    --check --max-turns $MaxTurns --permission-mode acceptEdits
exit $LASTEXITCODE

