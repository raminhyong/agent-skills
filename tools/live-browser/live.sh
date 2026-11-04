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

RESTORE=0
case "${1:-}" in
  --restore)         RESTORE=1; URL="" ;;
  --restore-persist) RESTORE=1; URL=""; PERSIST=1 ;;
  *)                 URL="${1:-about:blank}"; PERSIST=0 ;;
esac
PORT="${LIVE_PORT:-9222}"
PROFILE="${LIVE_PROFILE:-$HOME/tools/chrome-live}"
CHROME="${LIVE_CHROME:-}"

if [ -z "$CHROME" ]; then
  for c in \
    "C:/Program Files/Google/Chrome/Application/chrome.exe" \
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe" \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "$(command -v google-chrome 2>/dev/null || true)" \
    "$(command -v chromium 2>/dev/null || true)"; do
    [ -n "$c" ] && [ -e "$c" ] && CHROME="$c" && break
  done
fi

# แปลง path แบบ MSYS (/c/...) เป็น Windows (C:/...) — Chrome ที่เป็น native app เปิด path แบบ /c/ ไม่ได้
case "$CHROME" in
  /?/*)
    if command -v cygpath >/dev/null 2>&1; then
      CHROME="$(cygpath -m "$CHROME")"
    else
      CHROME="$(echo "$CHROME" | sed -E 's#^/([a-zA-Z])/#\U\1:/#')"
    fi
    ;;
esac

if [ -z "$CHROME" ]; then
  echo "ERROR: ไม่พบ Chrome/Edge — ตั้ง LIVE_CHROME=<path> เอง" >&2
  exit 1
fi

mkdir -p "$PROFILE"
# แปลงโฟลเดอร์โปรไฟล์เป็น path แบบ Windows ด้วย (Chrome native ไม่รับ /c/...)
PROFILE_NATIVE="$PROFILE"
case "$PROFILE" in
  /?/*)
    if command -v cygpath >/dev/null 2>&1; then
      PROFILE_NATIVE="$(cygpath -m "$PROFILE")"
    else
      PROFILE_NATIVE="$(echo "$PROFILE" | sed -E 's#^/([a-zA-Z])/#\U\1:/#')"
    fi
    ;;
esac

up() { curl -s --max-time 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; }

if up; then
  echo "CDP :$PORT เปิดอยู่แล้ว — ใช้แท็บเดิม"
  if [ "$RESTORE" = "1" ]; then
    echo "หมายเหตุ: --restore ใช้ได้ตอน Chrome ยังไม่เปิด — ตอนนี้ใช้แท็บที่มีอยู่ (ดูด้วย: node pw.mjs status)"
  fi
  if [ -n "${URL:-}" ]; then
    cd "$(dirname "$0")" && node pw.mjs goto "$URL"
  fi
else
  echo "เปิด Chrome: $CHROME"
  echo "โปรไฟล์: $PROFILE"
  LOG="$PROFILE/chrome-live-launch.log"
  rm -f "$PROFILE/DevToolsActivePort" 2>/dev/null || true

  # ตั้งค่า "เปิดแท็บเดิมต่อ" ลงโปรไฟล์ (ทำได้เฉพาะตอน Chrome ปิดอยู่)
  if [ "${PERSIST:-0}" = "1" ]; then
    python - "$PROFILE_NATIVE/Default/Preferences" <<'PY' 2>/dev/null || echo "WARN: ตั้งค่า restore_on_startup ไม่สำเร็จ"
import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
d.setdefault('session', {})['restore_on_startup'] = 4   # 4 = เปิดแท็บที่ค้างไว้ต่อ
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
print('ตั้งค่าแล้ว: restore_on_startup = 4 (เปิดแท็บเดิมทุกครั้ง)')
PY
  fi

  ARGS=()
  [ "$RESTORE" = "1" ] && ARGS+=(--restore-last-session)
  ("$CHROME" \
    --remote-debugging-port="$PORT" \
    --user-data-dir="$PROFILE_NATIVE" \
    --no-first-run --no-default-browser-check \
    --window-size=1400,900 \
    "${ARGS[@]}" ${URL:+"$URL"} >"$LOG" 2>&1 &)
  # รอสูงสุด ~60 วิ (โปรไฟล์ใหญ่/ดิสก์ช้าอาจใช้เวลาเปิดนาน)
  for i in $(seq 1 60); do up && break; sleep 1; done
  if ! up; then
    echo "ERROR: Chrome ไม่ยอมเปิด CDP port $PORT" >&2
    echo "--- log ล่าสุด ($LOG) ---" >&2
    tail -8 "$LOG" 2>/dev/null >&2
    if [ -f "$PROFILE/DevToolsActivePort" ]; then
      echo "พบ DevToolsActivePort: $(head -1 "$PROFILE/DevToolsActivePort") — Chrome อาจเปิดพอร์ตอื่น" >&2
    fi
    exit 1
  fi
fi

# ยืนยันว่ามีหน้าต่างจริงบนจอ (บน Windows) — ถ้าว่าง แปลว่าไม่มีหน้าต่าง อย่าอ้างว่าเปิดให้แล้ว
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    powershell -NoProfile -Command "Get-Process chrome,msedge -EA SilentlyContinue | Where-Object {\$_.MainWindowTitle -ne ''} | Select-Object -First 3 Id,MainWindowTitle | Format-Table -AutoSize" 2>/dev/null
    ;;
esac

echo "พร้อมใช้งาน: node pw.mjs status"
