# ==============================================================================
# Sync Active Skills & Rules from Repo to Global Antigravity Config
# ==============================================================================
param(
    [string]$GlobalConfigPath = "$HOME\.gemini\config",
    [string]$GlobalSkillsPath = "$HOME\.gemini\config\skills"
)

$RepoSkillsPath = Join-Path $PSScriptRoot "..\skills"
$RepoRulesPath  = Join-Path $PSScriptRoot "..\rules"

if (-not (Test-Path $GlobalSkillsPath)) {
    New-Item -ItemType Directory -Path $GlobalSkillsPath -Force | Out-Null
}

# 1. Sync Rules & GEMINI.md
if (Test-Path $RepoRulesPath) {
    Write-Host "Syncing rules to $GlobalConfigPath..." -ForegroundColor Cyan
    $GlobalRulesPath = Join-Path $GlobalConfigPath "rules"
    if (-not (Test-Path $GlobalRulesPath)) {
        New-Item -ItemType Directory -Path $GlobalRulesPath -Force | Out-Null
    }

    $RepoGemini = Join-Path $RepoRulesPath "GEMINI.md"
    if (Test-Path $RepoGemini) {
        Copy-Item -Path $RepoGemini -Destination (Join-Path $GlobalConfigPath "GEMINI.md") -Force
        Write-Host "  -> Synced GEMINI.md to config root" -ForegroundColor Green
    }

    $Rules = Get-ChildItem -File $RepoRulesPath | Where-Object { $_.Name -ne "GEMINI.md" }
    foreach ($Rule in $Rules) {
        Copy-Item -Path $Rule.FullName -Destination (Join-Path $GlobalRulesPath $Rule.Name) -Force
        Write-Host "  -> Synced rule: $($Rule.Name)" -ForegroundColor Green
    }
}

# 2. Sync Active Skills
$Skills = Get-ChildItem -Directory $RepoSkillsPath

Write-Host "Syncing $($Skills.Count) active skills to $GlobalSkillsPath..." -ForegroundColor Cyan

foreach ($Skill in $Skills) {
    $Target = Join-Path $GlobalSkillsPath $Skill.Name

    # Clean accidental recursive nested folder if present
    $NestedSelf = Join-Path $Target $Skill.Name
    if (Test-Path $NestedSelf) {
        Remove-Item -Path $NestedSelf -Recurse -Force
        Write-Host "  [Fixed] Removed nested duplicate: $NestedSelf" -ForegroundColor Yellow
    }

    if (-not (Test-Path $Target)) {
        New-Item -ItemType Directory -Path $Target -Force | Out-Null
    }

    # Copy contents into target without creating an extra nested level
    Copy-Item -Path (Join-Path $Skill.FullName "*") -Destination $Target -Recurse -Force
    Write-Host "  -> Synced: $($Skill.Name)" -ForegroundColor Green
}

Write-Host "Done! All active skills and rules synced successfully." -ForegroundColor Yellow

