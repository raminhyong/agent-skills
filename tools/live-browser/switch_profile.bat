@echo off
set "PROFILE_NAME=%~1"
set "URL=%~2"
if "%PROFILE_NAME%"=="" set "PROFILE_NAME=Default"
if "%URL%"=="" set "URL=https://kumooc.ku.th/"

"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\Users\patti\tools\chrome-live" --profile-directory="%PROFILE_NAME%" "%URL%"

