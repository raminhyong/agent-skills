# ==============================================================================
# Sync Thai School Document Skills: Repo -> Hermes Agent profile
#   skills/thai-doc, thai-project-proposal, thai-official-memo, thai-exam-format, thai-web-fonts
#   -> $env:LOCALAPPDATA\hermes\skills\productivity\<name>
# ใช้เมื่อแก้สกิลใน repo แล้วอยากให้ Hermes (Pancake) เห็นเวอร์ชันล่าสุดทันที
# ==============================================================================
param(
    [string]$HermesSkillsPath = (Join-Path $env:LOCALAPPDATA "hermes\skills"),
    [string]$Category = "productivity",
    [string[]]$Skills = @("thai-doc", "thai-project-proposal", "thai-official-memo", "thai-exam-format", "thai-web-fonts")
)

$RepoSkillsPath = Join-Path $PSScriptRoot "..\skills"
$TargetRoot = Join-Path $HermesSkillsPath $Category

if (-not (Test-Path $TargetRoot)) {
    New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null
}

foreach ($Name in $Skills) {
    $Source = Join-Path $RepoSkillsPath $Name
    if (-not (Test-Path $Source)) {
        Write-Host "  !! not in repo: $Name" -ForegroundColor Red
        continue
    }
    $Target = Join-Path $TargetRoot $Name
    if (Test-Path $Target) {
        Remove-Item -Path $Target -Recurse -Force
    }
    Copy-Item -Path $Source -Destination $Target -Recurse -Force
    Write-Host "  -> synced: $Name -> $Target" -ForegroundColor Green
}

Write-Host "Done. Restart active Hermes sessions to reload the skill catalogue." -ForegroundColor Yellow
