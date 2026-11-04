param(
  [Parameter(Mandatory=$true)][string]$Match,
  [switch]$All
)
# show-window.ps1 — ยกหน้าต่าง Chrome/Edge ที่ชื่อแท็บตรงกับ $Match ขึ้นมาหน้าจอ
# ใช้: powershell -NoProfile -ExecutionPolicy Bypass -File show-window.ps1 -Match "Reddit"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
$procs = Get-Process chrome, msedge -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -and $_.MainWindowTitle -match $Match }
if (-not $procs) { Write-Output "NO_MATCH"; exit 1 }
foreach ($p in $procs) {
  $h = $p.MainWindowHandle
  if ($h -eq 0) { continue }
  [void][W]::ShowWindowAsync($h, 9)             # SW_RESTORE
  Start-Sleep -Milliseconds 250
  $ok = [W]::SetForegroundWindow($h)
  if (-not $ok) {
    try { Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate($p.Id) | Out-Null; $ok = $true } catch {}
  }
  "PID=$($p.Id) HWND=$h FOREGROUND=$ok TITLE=$($p.MainWindowTitle.Substring(0,[Math]::Min(60,$p.MainWindowTitle.Length)))"
  if (-not $All) { break }
}
