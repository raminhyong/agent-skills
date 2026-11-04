# install.ps1 — ติดตั้งชุด live-browser ลงเครื่องนี้ (Windows)
#
# วิธีใช้ (PowerShell):
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Dest "D:\tools\pw" -Profile "D:\tools\chrome-live"
#
# สิ่งที่ทำให้:
#   1) คัดลอกสคริปต์ไปที่ $Dest (ค่าเริ่มต้น %USERPROFILE%\tools\pw)
#   2) ติดตั้ง playwright (npm i) ในโฟลเดอร์นั้น
#   3) ตรวจหา Chrome/Edge และสร้างไฟล์ config.ps1 เก็บค่า CHROME/PROFILE/PORT
#   4) พิมพ์คำสั่งเริ่มใช้งาน

param(
  [string]$Dest = "$env:USERPROFILE\tools\pw",
  [string]$Profile = "$env:USERPROFILE\tools\chrome-live",
  [int]$Port = 9222,
  [switch]$SkipNpm
)

$ErrorActionPreference = 'Stop'
function Say($m) { Write-Host "• $m" -ForegroundColor Cyan }

Say "ปลายทาง: $Dest"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
New-Item -ItemType Directory -Force -Path "$Dest\examples" | Out-Null
New-Item -ItemType Directory -Force -Path $Profile | Out-Null

$files = @('live.sh','live.cmd','pw.mjs','cdp.mjs','seek.mjs','dl.mjs','package.json','README.md')
foreach ($f in $files) {
  $src = Join-Path $PSScriptRoot $f
  if (Test-Path $src) { Copy-Item $src -Destination $Dest -Force; Say "คัดลอก $f" }
}
if (Test-Path (Join-Path $PSScriptRoot 'examples\answer.sh')) {
  Copy-Item (Join-Path $PSScriptRoot 'examples\answer.sh') -Destination "$Dest\examples" -Force
  Say "คัดลอก examples\answer.sh"
}

# หา Chrome / Edge
$cands = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$chrome = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { Write-Warning "ไม่พบ Chrome/Edge — โปรดติดตั้งก่อน แล้วตั้ง LIVE_CHROME เอง" }
else { Say "พบเบราว์เซอร์: $chrome" }

# เก็บค่าลง config.ps1 (ไม่มีความลับ)
@"
# โหลดด้วย: . "$Dest\config.ps1"
`$env:LIVE_CHROME  = '$chrome'
`$env:LIVE_PROFILE = '$Profile'
`$env:LIVE_PORT    = '$Port'
`$env:CDP          = 'http://127.0.0.1:$Port'
"@ | Set-Content -Path "$Dest\config.ps1" -Encoding UTF8
Say "เขียน config.ps1"

if (-not $SkipNpm) {
  if (Get-Command npm -ErrorAction SilentlyContinue) {
    Say "npm i playwright (อาจใช้เวลา 1-2 นาที)"
    Push-Location $Dest
    npm i --no-audit --no-fund | Out-Null
    Pop-Location
  } else {
    Write-Warning "ไม่พบ npm — ติดตั้ง Node.js 20+ ก่อนแล้วรัน: cd `"$Dest`"; npm i playwright"
  }
}

Write-Host ""
Write-Host "ติดตั้งเสร็จ — เริ่มใช้งาน:" -ForegroundColor Green
Write-Host "  1) เปิดเบราว์เซอร์มีหน้าต่าง:  bash `"$($Dest -replace '\\','/')/live.sh`" `"https://example.com`""
Write-Host "     (Windows: ดับเบิลคลิก $Dest\live.cmd ได้เลย)"
Write-Host "  2) ล็อกอินเองทุกเว็บครั้งแรก (คุกกี้จะค้างในโปรไฟล์ $Profile)"
Write-Host "  3) สั่งงาน:  cd `"$Dest`"; node pw.mjs status; node pw.mjs shot x.png"
Write-Host ""
Write-Host "หมายเหตุ: โปรไฟล์นี้เป็นของแต่ละเครื่อง — คัดลอกข้ามเครื่องแล้วคุกกี้มักใช้ไม่ได้ (DPAPI)"
