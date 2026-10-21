# ==============================================================================
# Sync Active Skills from Repo to Global Antigravity Config
# ==============================================================================
param(
    [string]$GlobalSkillsPath = "$HOME\.gemini\config\skills"
)

$RepoSkillsPath = Join-Path $PSScriptRoot "..\skills"

if (-not (Test-Path $GlobalSkillsPath)) {
    New-Item -ItemType Directory -Path $GlobalSkillsPath -Force | Out-Null
}

$Skills = Get-ChildItem -Directory $RepoSkillsPath

Write-Host "Syncing $($Skills.Count) active skills to $GlobalSkillsPath..." -ForegroundColor Cyan

foreach ($Skill in $Skills) {
    $Target = Join-Path $GlobalSkillsPath $Skill.Name
    Copy-Item -Path $Skill.FullName -Destination $Target -Recurse -Force
    Write-Host "  -> Synced: $($Skill.Name)" -ForegroundColor Green
}

Write-Host "Done! All active skills synced successfully." -ForegroundColor Yellow
