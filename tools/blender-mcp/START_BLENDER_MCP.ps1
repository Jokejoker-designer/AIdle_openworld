# Open Blender GUI with AIdle cast folder handy; user must click Connect in BlenderMCP tab.
$ErrorActionPreference = "Stop"
$blender = "E:\blender.exe"
$exports = "E:\AIdle_openworld\tools\blender-mcp\exports"
New-Item -ItemType Directory -Force -Path $exports | Out-Null

if (-not (Test-Path $blender)) {
  Write-Error "Blender not found at $blender"
}

Write-Host "Starting Blender..."
Write-Host "Then: N sidebar -> BlenderMCP tab -> Connect"
Write-Host "Then: restart Grok session to load MCP tools"
Write-Host "Check port: python E:\AIdle_openworld\tools\blender-mcp\connect_check.py"
Start-Process -FilePath $blender
