@echo off
REM live.cmd — เปิด Chrome จริงแบบมีหน้าต่าง + CDP 9222 (ดับเบิลคลิกได้)
REM ใช้: live.cmd [url]
setlocal
set "PORT=%LIVE_PORT%"
if "%PORT%"=="" set "PORT=9222"
set "PROFILE=%USERPROFILE%\tools\chrome-live"
if not "%LIVE_PROFILE%"=="" set "PROFILE=%LIVE_PROFILE%"

set "CHROME=%LIVE_CHROME%"
if "%CHROME%"=="" if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if "%CHROME%"=="" if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if "%CHROME%"=="" if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "CHROME=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if "%CHROME%"=="" (
  echo ERROR: not find Chrome/Edge. Set LIVE_CHROME=path\to\chrome.exe
  pause & exit /b 1
)

if not exist "%PROFILE%" mkdir "%PROFILE%"
echo Chrome: %CHROME%
echo Profile: %PROFILE%
echo CDP: http://127.0.0.1:%PORT%

start "" "%CHROME%" --remote-debugging-port=%PORT% --user-data-dir="%PROFILE%" --no-first-run --no-default-browser-check --window-size=1400,900 %1
echo เปิดแล้ว — ครั้งแรกให้ล็อกอินเองทุกเว็บ คุกกี้จะค้างในโปรไฟล์นี้
