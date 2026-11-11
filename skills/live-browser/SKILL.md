---
name: live-browser
description: >-
  เปิด Chrome ตัวจริงแบบมีหน้าต่างให้ผู้ใช้เห็นและจำการล็อกอินได้ แล้วขับด้วย Playwright ผ่าน CDP — ใช้เมื่อ agent ต้องให้มนุษย์ดูจอเดียวกัน กรอกฟอร์ม/กดปุ่มบนหน้าเว็บจริง หรือเข้าเว็บที่บังคับล็อกอิน (แทน browser headless ที่โปรไฟล์หายทุก session) เรียกใช้ด้วย /live-browser
---
# Live Browser — เบราว์เซอร์ตัวจริงที่ผู้ใช้เห็น และจำล็อกอินได้

> คำสั่งลัด (Slash Command): **/live-browser**
> ปรัชญา: **"หน้าต่างเดียวกับที่มนุษย์เห็น — ไม่ headless, ไม่โปรไฟล์ชั่วคราว, ไม่แอบใช้ JS แทนการคลิก"**

---

## 1. ใช้เมื่อไหร่ (When to Use)

ใช้สกิลนี้เมื่อเข้าเงื่อนไขข้อใดข้อหนึ่ง:
- ผู้ใช้ต้อง **เห็นหน้าจอ** ที่ agent กำลังทำ (ตรวจงาน, สอนใช้เว็บ, ดูสถานะ)
- ผู้ใช้ต้อง **ลงมือเองบางขั้น** เช่น พิมพ์รหัสผ่าน, ยืนยัน OTP, ตัดสินใจ captcha
- เว็บ **บังคับล็อกอิน** และไม่อยากล็อกอินซ้ำทุก session (KU MOOC, Reddit, Facebook, ระบบโรงเรียน, หลังบ้าน CMS)
- ต้องทำงานบน **Chrome ของเครื่องผู้ใช้** ที่มีส่วนขยาย/โปรไฟล์/คุกกี้อยู่แล้ว
- ต้องกดปุ่มที่ CDP/headless ทำไม่ได้ หรือโดน bot-detection สูง → ใช้ `computer_use` ร่วมกับสกิลนี้

**ไม่ใช้** เมื่อ: งานขูดข้อมูลสาธารณะจำนวนมาก (ใช้ `browser_exec` headless จะเร็วกว่า), งาน API ที่มี endpoint ตรง, หรืองานที่ไม่ต้องให้ใครเห็น

---

## 2. กติกาเหล็ก (ทำทุกครั้ง)

1. **ห้ามอ้างว่า "เปิดหน้าให้แล้ว" ถ้าไม่มีหน้าต่างจริง** — เช็ก `MainWindowTitle` ก่อน แล้วแนบภาพ `MEDIA:` ทุกครั้ง
2. **ห้ามพิมพ์รหัสผ่าน / OTP / เลขบัตรแทนผู้ใช้** แม้ผู้ใช้จะส่งมาในแชท — ให้ผู้ใช้พิมพ์เองในหน้าต่างที่เห็น หรือใช้ `browser_vault`
3. **ห้ามใช้ JS แทนการคลิกในงานที่มีความเสี่ยง** (ข้อสอบ, การเงิน, การลงทะเบียน) — `pw.mjs click` ถูกออกแบบให้ไม่ fallback ไป JS เองแล้ว; `clickjs` ใช้เฉพาะงานเบา
4. **ห้ามยิง API หลังบ้าน** เพื่อข้ามขั้นตอนของแพลตฟอร์ม (เรียนจบ, ส่งคำตอบ, ชำระเงิน)
5. **เว้นจังหวะเหมือนคน** — 2–4 วิระหว่างการกระทำ, อ่านก่อนกด, ไม่กดรัว
6. **จดความคืบหน้าลงไฟล์** ทุกครั้งที่จบขั้น (`cache/scratch/<งาน>-progress.md`)

---

## 3. ติดตั้ง (ครั้งเดียวต่อเครื่อง)

```bash
cd "D:\MEGA\AGENT SKILLS\tools\live-browser"
npm i playwright
bash live.sh "https://example.com"   # เปิดหน้าต่างจริง + โปรไฟล์ถาวร
# แล้วล็อกอินเองทุกเว็บที่ต้องใช้ — คุกกี้จะค้างในโฟลเดอร์โปรไฟล์
```

Windows: `install.ps1` ทำให้อัตโนมัติ (คัดลอกไป `%USERPROFILE%\tools\pw`, ติดตั้ง playwright, หา Chrome/Edge, เขียน `config.ps1`)

รายละเอียดเต็ม: `tools/live-browser/README.md`

---

## 4. คำสั่งที่ใช้บ่อย

```bash
bash live.sh "<url>"                       # เปิด/โฟกัสหน้าต่างจริง
bash live.sh --restore                     # เปิดแล้วกู้แท็บที่ค้างไว้ทั้งหมด (กระดานงานไม่หาย)
bash live.sh --restore-persist             # กู้แท็บ + ตั้งโปรไฟล์ให้เปิดแท็บเดิมทุกครั้ง
node pw.mjs status                          # ดูแท็บ + title
node pw.mjs newtab "<url>"                  # เปิดแท็บใหม่ (สร้างกระดานงาน ไม่ทับของเดิม)
node pw.mjs goto "<url>"                    # เปลี่ยนหน้า
node pw.mjs shot out.png                    # ภาพ (แนบ MEDIA: ให้ผู้ใช้)
node pw.mjs text | head -40                 # อ่านเนื้อหา
node pw.mjs click "<ข้อความ>"               # คลิกเมาส์จริง (มีลูกศรชี้ให้เห็นก่อนคลิก)
node pw.mjs point "<ข้อความ>"               # ชี้เฉย ๆ ไม่คลิก
node pw.mjs cursor                          # สาธิตตัวชี้ + ripple
node pw.mjs clickcss "<selector>"           # คลิกด้วย selector
node pw.mjs fill "<label>" "<ข้อความ>"      # กรอกช่อง
node pw.mjs press Escape                    # ปิด overlay
node pw.mjs download "<ปุ่ม>" out.pdf       # ดาวน์โหลด
node pw.mjs fetchsave "<url>" out.pdf       # ดาวน์โหลดเมื่อปุ่มเป็น target=_blank
```

เลือกแท็บ: `PW_MATCH=reddit node pw.mjs text` · เปลี่ยนพอร์ต: `CDP=http://127.0.0.1:9333`

---

## 5. สูตรที่ผ่านการใช้งานจริง

| สถานการณ์ | สูตร |
|---|---|
| ให้ผู้ใช้ล็อกอินเอง | `live.sh <login-url>` → `shot` → บอกให้พิมพ์ในหน้าต่าง → `status` ยืนยัน |
| กรอกฟอร์ม + ยืนยันผล | `fill` → `click` → `shot` → `text` |
| ดาวน์โหลดใบประกาศ | `download` หรือ `fetchsave` → เปิด `file:///...pdf` + `shot` เพื่อตรวจด้วยตา |
| กรอวิดีโอยาว (JW Player) | `node seek.mjs 0.97` (คลิกแถบเวลาจริง) |
| ปรับสปีดวิดีโอทางการ 2x (e-Learning) | `node set_speed.mjs 2` (คลิกปุ่ม Speed บนตัวเล่นวิดีโออย่างเป็นธรรมชาติ) |
| ติดตามจบบทและเรียนบทถัดไป | `node advance_module.mjs` (เฝ้าวิดีโอจบ คลิกป๊อปอัปบทถัดไป + ปรับ 2x อัตโนมัติ) |
| ตรวจสอบจอแสดงผลหลายจอ (Multi-Monitor) | `powershell -ExecutionPolicy Bypass -File ./detect_monitors.ps1` |
| สลับโปรไฟล์ Chrome | `switch_profile.bat` หรือ `open_profile_1.bat` / `open_profile_2.bat` |
| ตอบข้อสอบ | `bash examples/answer.sh "<ตัวเลือก>" next` ทีละข้อ |
| ต้องให้ผู้ใช้เห็นว่า agent ชี้ตรงไหน | `point` / `click` มี overlay เมาส์เรเดียนซ์ออร่าสีทอง+ประกายคลื่นน้ำ+ป้ายชื่อเอเจนต์ (PW_CURSOR=0 ปิด) |
| เว็บจับบอตแรง (Reddit/Google) | `computer_use` (เมาส์+คีย์บอร์ดจริง) ตาม §6 |
| ทำงานค้างหลายหน้า (กระดานงาน) | `node pw.mjs newtab <url>` เปิดใหม่ทีละแท็บ → ปิด Chrome แบบสุภาพ → ครั้งหน้า `bash live.sh --restore` ได้แท็บเดิมคืน |

---

## 6. เมื่อต้องใช้ `computer_use` (เมาส์/คีย์บอร์ดระดับ OS)

```text
computer_use(action="capture", app="Chrome", mode="som")
computer_use(action="click", coordinate=[x, y])                      # พิกัดจากภาพ
computer_use(action="type", text="...", delivery_mode="foreground")  # Chrome ไม่รับ keystroke background
computer_use(action="click", coordinate=[x, y], capture_after=True)  # ยืนยันทุกครั้ง
```

ข้อจำกัดจริง: `type` ต้อง `foreground`; accessibility tree มักไม่เห็นช่องฟอร์มในหน้า → ใช้พิกัดจากภาพ; ถ้าเป็นหน้า "ยืนยันไม่ใช่บอตแบบเลือกภาพ" **ห้ามเดา** ให้หาปุ่มปิด (โลโก้/กากบาท/Esc) หรือถ่ายภาพให้ผู้ใช้ตัดสิน

---

## 7. กับดักที่เจอจริง

| อาการ | สาเหตุ / ทางแก้ |
|---|---|
| `ECONNREFUSED 9222` | ยังไม่เปิด Chrome หรือพอร์ตชน → `bash live.sh` / `LIVE_PORT=9333` |
| `CLICK_BLOCKED: outside of the viewport` | overlay/นอกจากจอ → `press Escape` หรือเลื่อนแล้วคลิกใหม่ |
| `DOWNLOAD_FAILED: canceled` | ปุ่ม `target=_blank` → `fetchsave` |
| เปิดใหม่แล้วล็อกอินหาย | โปรไฟล์อยู่ใน `%TEMP%` หรือใช้ Chromium ของ tool (ไม่ใช่ชุดนี้) |
| คุกกี้ไม่ติดตอนย้ายเครื่อง | DPAPI ผูกกับ user → ล็อกอินใหม่ที่เครื่องนั้น |
| หน้าเป็นแท็บผิด | หลายแท็บเปิดอยู่ → `PW_MATCH=<คำใน url>` |

เพิ่มเติม: `references/troubleshooting.md`

---

## 8. ข้อห้ามด้านความปลอดภัย

- โปรไฟล์ `chrome-live` มีคุกกี้ส่วนตัว → **ห้าม commit ขึ้น git**, ห้าม zip ส่งออกโดยไม่ถาม
- ห้ามรันพร้อม Chrome อีกตัวที่ใช้โฟลเดอร์โปรไฟล์เดียวกัน (จะ lock)
- ห้ามใช้สกิลนี้เลี่ยงข้อกำหนดของแพลตฟอร์ม (ข้อสอบ/ชำระเงิน/ยืนยันตัวตน)
