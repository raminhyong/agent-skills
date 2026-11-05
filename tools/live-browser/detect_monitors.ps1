<#
.SYNOPSIS
    detect_monitors.ps1 — Enumerate all connected displays and detect Chrome window position.
.DESCRIPTION
    Crucial for multi-monitor setups where Chrome may be running on a secondary screen
    with negative coordinates (e.g. left of primary screen).
#>
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class User32 {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
}
public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}
"@

Write-Host "================== DISPLAY MONITORS ==================" -ForegroundColor Cyan
$screens = [System.Windows.Forms.Screen]::AllScreens
$idx = 1
foreach ($s in $screens) {
    $primary = if ($s.Primary) { "[PRIMARY]" } else { "[SECONDARY]" }
    Write-Host "Monitor $idx $primary :" -ForegroundColor Yellow
    Write-Host "  DeviceName : $($s.DeviceName)"
    Write-Host "  Bounds     : Left=$($s.Bounds.Left), Top=$($s.Bounds.Top), Width=$($s.Bounds.Width), Height=$($s.Bounds.Height)"
    Write-Host "  WorkingArea: Left=$($s.WorkingArea.Left), Top=$($s.WorkingArea.Top), Width=$($s.WorkingArea.Width), Height=$($s.WorkingArea.Height)"
    $idx++
}

Write-Host "`n================== CHROME WINDOW LOCATION ==================" -ForegroundColor Cyan
$chromeProc = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne "" } | Select-Object -First 1
if ($chromeProc) {
    $rect = New-Object RECT
    [User32]::GetWindowRect($chromeProc.MainWindowHandle, [ref]$rect) | Out-Null
    Write-Host "Chrome Title : $($chromeProc.MainWindowTitle)" -ForegroundColor Green
    Write-Host "Window Rect  : Left=$($rect.Left), Top=$($rect.Top), Right=$($rect.Right), Bottom=$($rect.Bottom)"
    
    # Identify which screen Chrome is on
    $matched = $false
    $sIdx = 1
    foreach ($s in $screens) {
        if ($rect.Left -ge $s.Bounds.Left -and $rect.Left -lt $s.Bounds.Right) {
            Write-Host "Chrome is currently on: Monitor $sIdx ($($s.DeviceName))" -ForegroundColor Green
            $matched = $true
            break
        }
        $sIdx++
    }
    if (-not $matched) {
        Write-Host "Chrome spans across displays or offscreen." -ForegroundColor Yellow
    }
} else {
    Write-Host "No Chrome window with visible title found." -ForegroundColor Red
}
Write-Host "============================================================" -ForegroundColor Cyan
