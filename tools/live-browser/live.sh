#!/usr/bin/env bash
# live.sh — เปิด Chrome/Edge ตัวจริงแบบ "มีหน้าต่างบนจอ" + เปิด CDP port ให้เครื่องมืออื่นเกาะ
#
# ทำไมต้องมี: เบราว์เซอร์ของ agent (browser_exec / Playwright launch) มักรัน headless
# และใช้โปรไฟล์ชั่วคราว → ผู้ใช้มองไม่เห็น และล็อกอินใหม่ทุกครั้ง
# สคริปต์นี้แก้ทั้งสองปัญหา: หน้าต่างจริง + โปรไฟล์ถาวรบนดิสก์
#
# ใช้:
#   bash live.sh [url]                    # เปิด (ถ้ายังไม่เปิด) แล้วไปที่ url
#   LIVE_PORT=9333 bash live.sh https://x # เปลี่ยนพอร์ตเมื่อ 9222 ชน
#   LIVE_PROFILE=~/myprof bash live.sh     # เปลี่ยนโฟลเดอร์โปรไฟล์
#
# ตัวแปรสิ่งแวดล้อม:
#   LIVE_CHROME  path ของ chrome.exe / msedge.exe (ไม่ต้องใส่ก็ได้ ระบบหาเอง)
#   LIVE_PROFILE โฟลเดอร์โปรไฟล์ถาวร (ค่าเริ่มต้น: ~/tools/chrome-live)
#   LIVE_PORT    พอร์ต CDP (ค่าเริ่มต้น: 9222)
set -u

URL="${1:-about:blank}"
PORT="${LIVE_PORT:-9222}"
PROFILE="${LIVE_PROFILE:-$HOME/tools/chrome-live}"
CHROME="${LIVE_CHROME:-}"

if [ -z "$CHROME" ]; then
  for c in \
    "/c/Program Files/Google/Chrome/Application/chrome.exe" \
    "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
    "/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "$(command -v google-chrome 2>/dev/null || true)" \
    "$(command -v chromium 2>/dev/null || true)"; do
    [ -n "$c" ] && [ -e "$c" ] && CHROME="$c" && break
  done
fi

if [ -z "$CHROME" ]; then
  echo "ERROR: ไม่พบ Chrome/Edge — ตั้ง LIVE_CHROME=<path> เอง" >&2
  exit 1
fi

mkdir -p "$PROFILE"

up() { curl -s --max-time 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; }

if up; then
  echo "CDP :$PORT เปิดอยู่แล้ว — ใช้แท็บเดิม"
  if [ -n "${1:-}" ]; then
    PW=/$(dirname "$0") ; cd "$(dirname "$0")" && node pw.mjs goto "$URL"
  fi
else
  echo "เปิด Chrome: $CHROME"
  echo "โปรไฟล์: $PROFILE"
  ("$CHROME" \
    --remote-debugging-port="$PORT" \
    --user-data-dir="$PROFILE" \
    --no-first-run --no-default-browser-check \
    --window-size=1400,900 \
    "$URL" >/dev/null 2>&1 &)
  for i in $(seq 1 30); do up && break; sleep 0.5; done
  up || { echo "ERROR: Chrome ไม่ยอมเปิด CDP port $PORT (โปรไฟล์อาจถูก lock)" >&2; exit 1; }
fi

# ยืนยันว่ามีหน้าต่างจริงบนจอ (บน Windows) — ถ้าว่าง แปลว่าไม่มีหน้าต่าง อย่าอ้างว่าเปิดให้แล้ว
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    powershell -NoProfile -Command "Get-Process chrome,msedge -EA SilentlyContinue | Where-Object {\$_.MainWindowTitle -ne ''} | Select-Object -First 3 Id,MainWindowTitle | Format-Table -AutoSize" 2>/dev/null
    ;;
esac

echo "พร้อมใช้งาน: node pw.mjs status"
