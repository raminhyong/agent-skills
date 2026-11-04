#!/usr/bin/env bash
# answer.sh — ตอบข้อสอบออนไลน์แบบ "จังหวะคนจริง" หนึ่งข้อต่อครั้ง
#
# ใช้: bash answer.sh "<ข้อความตัวเลือก>" [next|submit|<ข้อความปุ่มเอง>]
#
# สิ่งที่ทำ: เว้นอ่าน 4-7 วิ → คลิกตัวเลือก (เมาส์จริง) → ตรวจว่าติดจริง →
#            เว้น 1.5-3 วิ → กดปุ่มถัดไป/ส่ง
#
# กติกา: ห้ามใช้สคริปต์นี้ตอบรวดโดยไม่อ่านโจทย์ — ตัวเลือกสลับลำดับทุกครั้ง
set -u
OPT="${1:-}"
NEXT="${2:-next}"
case "$NEXT" in
  next) NEXT_LABEL="ถัดไป" ;;
  submit) NEXT_LABEL="ส่ง" ;;
  *) NEXT_LABEL="$NEXT" ;;
esac
sleepp() { python -c "import random,time;time.sleep(random.uniform($1,$2))" 2>/dev/null || sleep 2; }
cd "$(dirname "$0")" || exit 1

sleepp 4 7
node pw.mjs click "$OPT" 2>&1 | tail -2
sleepp 1 2
echo "--- selected check (นับ radio ที่ถูกเลือก ต้องเพิ่มขึ้น 1) ---"
node pw.mjs eval "(() => ({ answered: document.querySelectorAll('input[type=radio]:checked').length }))()"
sleepp 2 3
if [ "$NEXT" = "next" ]; then
  node pw.mjs clickcss "#btn-next-question" 2>&1 | tail -2
else
  node pw.mjs click "$NEXT_LABEL" 2>&1 | tail -2
fi
sleepp 1.5 2.5
echo "--- next question ---"
node pw.mjs text | head -30
