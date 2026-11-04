# Troubleshooting — live-browser

บันทึกจากหน้างานจริง (Windows 11 + Chrome 156, พ.ย. 2569)

## 1. เชื่อมต่อ / เปิดเบราว์เซอร์

| อาการ | สาเหตุ | ทางแก้ |
|---|---|---|
| `connectOverCDP: connect ECONNREFUSED 127.0.0.1:9222` | Chrome ไม่ได้เปิด หรือเปิดโดยไม่มี `--remote-debugging-port` | `bash live.sh` (สคริปต์เปิดให้) — ถ้าเปิด Chrome เองต้องใส่แฟล็กเอง |
| เปิด Chrome แล้วหน้าต่างไม่ขึ้น | มี Chrome อีกอินสแตนซ์ถือโปรไฟล์เดียวกัน | ปิดตัวเดิม (`taskkill /IM chrome.exe` เฉพาะกรณีที่ผู้ใช้อนุญาต) หรือใช้ `LIVE_PROFILE` อีกโฟลเดอร์ |
| `bash live.sh` ค้างที่รอพอร์ต | Chrome ตายตอนสตาร์ท (โปรไฟล์เสีย/lock) | ดู log: เปิด Chrome แบบมี console, หรือสร้างโปรไฟล์ใหม่ |
| อยากใช้ Edge | — | `LIVE_CHROME="/c/Program Files/Microsoft/Edge/Application/msedge.exe"` (CDP ใช้ได้เหมือนกัน) |

## 2. ควบคุมหน้าเว็บ

| อาการ | สาเหตุ | ทางแก้ |
|---|---|---|
| `NOT_FOUND: <ข้อความ>` | ข้อความบนปุ่มมีช่องว่าง/ตัวอักษรพิเศษ/ไม่แสดง | `node pw.mjs buttons` หรือ `links` เพื่อดูข้อความจริง แล้วคลิกด้วยข้อความนั้น |
| `CLICK_BLOCKED: outside of the viewport` | element อยู่นอกจอ หรือมี overlay (cookie banner/modal) | `node pw.mjs press Escape` หรือ `clickcss` ปุ่มปิด overlay ก่อน |
| `CLICK_BLOCKED: intercepts pointer events` | มี layer ทับอยู่ | ปิด layer นั้น หรือใช้ `set_value` ผ่าน `computer_use` |
| คลิกแล้วไม่มีอะไรเกิดขึ้น แต่ไม่ error | ปุ่มเป็น JS handler ที่ต้องรอ AJAX | `wait 1500` แล้ว `shot` ยืนยัน; ถ้ายังไม่ไป ให้ดูว่ามี dialog ยืนยันซ้อน |
| `PW_MATCH` ไม่เจอแท็บ | URL ไม่มีคำที่ให้ | `status` ดูรายการ URL ก่อน |

## 3. ดาวน์โหลด

| อาการ | สาเหตุ | ทางแก้ |
|---|---|---|
| `DOWNLOAD_FAILED: download.saveAs: canceled` | ปุ่มเป็น `<a target="_blank">` ที่ Chrome เปิดแท็บแล้วปิด — Playwright ไม่ได้ event | ใช้ `fetchsave` กับ href ของลิงก์ (คุกกี้ของแท็บถูกใช้ให้) |
| `NO_FILE` จาก `dl.mjs` | โฟลเดอร์ปลายทางไม่มีสิทธิ์ หรือ CDP behavior ไม่ถูกส่ง | ตรวจ path, ลอง `download` ของ `pw.mjs` ก่อน |
| ไฟล์โหลดแต่ชื่อเพี้ยน | ฝั่งเซิร์ฟเวอร์ตั้งชื่อไทย | `fetchsave` ไปชื่อที่ต้องการเอง |

## 4. วิดีโอ / คอร์สออนไลน์

| อาการ | สาเหตุ | ทางแก้ |
|---|---|---|
| `NO_SEEKBAR` | คอนโทรล JW Player ยังไม่โผล่ | `seek.mjs` มี hover ให้แล้ว — ถ้ายังไม่พบ ให้ `shot` ดูว่ามี player หรือเป็น iframe |
| กรอแล้วไม่ไปต่อ | dialog "เรียนจบ" ยังไม่ขึ้น (video ยังไม่ ended) | รอ 5–10 วิ หรือกรอชิดปลายกว่าเดิม (0.99) |
| กด "หัวข้อถัดไป" ด้วยข้อความไม่ติด | ปุ่มใน dialog มีคลาสเฉพาะ | `button.btn-continue-playing` (pw.mjs clickcss) หรือ `#btn-next-question` ในห้องสอบ |

## 5. ข้อสอบออนไลน์

| อาการ | สาเหตุ | ทางแก้ |
|---|---|---|
| ตอบแล้วได้ 0 คะแนน | กดถัดไปโดยที่ยังไม่เลือก (ตัวเลือกสลับลำดับ) | อ่านโจทย์ทีละข้อ, ตรวจ `answered` เพิ่มขึ้นก่อนกดถัดไป |
| `querySelector('input:checked')` คืนข้อเก่า | เว็บเรนเดอร์ทุกข้อในหน้าเดียว | นับ **จำนวน** `:checked` แทนการอ่านตัวแรก |
| ปุ่ม "ส่ง" ไม่ทำงาน | ปุ่มจริงคือ `#btn-submit-question` | ใช้ `clickcss` |

## 6. computer_use (เมื่อเว็บจับบอตแรง)

| อาการ | ความจริง |
|---|---|
| `background_unavailable` ตอน `type` | Chrome ไม่รับ keystroke background → `delivery_mode:"foreground"` |
| AX ไม่มีช่อง input | tree ของ Chrome ไม่ลงถึงฟอร์มในหน้า → คลิกด้วย `coordinate` จากภาพ |
| element bounds ติดลบ/แปลก | เป็นพิกัดเดสก์ท็อปหลายจอ → ใช้ `element` ถ้าได้ ไม่งั้นใช้พิกัดจากภาพ |
| คลิกแล้วไม่เปลี่ยน (`suspected_noop`) | ยกระดับเป็น `delivery_mode:"foreground"` ตาม verdict |

## 7. โปรไฟล์ / ล็อกอิน

| อาการ | สาเหตุ | ทางแก้ |
|---|---|---|
| เปิดใหม่แล้วต้องล็อกอินทุกครั้ง | โปรไฟล์อยู่ใน `%TEMP%` หรือใช้ Chromium ของ tool | ชี้ `LIVE_PROFILE` ไปโฟลเดอร์ถาวร (เช่น `~/tools/chrome-live`) |
| ย้ายเครื่องแล้วคุกกี้หาย | Chrome เข้ารหัสคุกกี้ด้วย DPAPI ของ user | ล็อกอินใหม่ที่เครื่องนั้น (ครั้งเดียว) |
| โปรไฟล์บวมหลาย GB | cache/ media ในโปรไฟล์ | ลบ `Default/Cache`, `Default/Code Cache`, `Default/Service Worker/CacheStorage` |
