# hermes-live-browser

ชุดเครื่องมือทำให้ agent ทำงานบน **Chrome ตัวจริงที่มีหน้าต่างอยู่บนจอผู้ใช้** และ **จำการล็อกอินได้ข้าม session** — ผ่าน Playwright ที่เกาะเบราว์เซอร์เดิมด้วย CDP (ไม่เปิดเบราว์เซอร์ใหม่ ไม่รัน headless)

> ปัญหาที่ชุดนี้แก้: เบราว์เซอร์ของ agent (เช่น `browser_exec` ของ Hermes) รัน Chromium แบบ `--headless=new` ด้วยโปรไฟล์ชั่วคราวใน `%TEMP%\agent-browser-chrome-<uuid>` → **ผู้ใช้มองไม่เห็นหน้าจอ** และ **คุกกี้/ล็อกอินหายทุกครั้งที่เปิดใหม่** ต้องล็อกอินซ้ำตลอด

---

## 1. หลักการทำงาน

```text
┌────────────────────────────┐        ┌──────────────────────────────┐
│ live.sh / live.cmd         │        │ pw.mjs (Playwright)          │
│ เปิด Chrome จริง            │  CDP   │ connectOverCDP(:9222)        │
│ --user-data-dir=<ถาวร>     │◄──────►│ คลิก/พิมพ์/ถ่ายภาพ/อ่าน DOM   │
│ --remote-debugging-port    │        │ browser.close() = ตัดการเชื่อม │
└────────────┬───────────────┘        └──────────────────────────────┘
             │ หน้าต่างจริงบนจอ (ผู้ใช้เห็น + พิมพ์เองได้)
             ▼
   C:\Users\<user>\tools\chrome-live\   ← โปรไฟล์ถาวร
     Default\Network\Cookies            (คุกกี้ทุกเว็บ)
     Default\Login Data                 (รหัสที่บันทึก)
     Default\Extensions, Local Storage  (Prefs, localStorage)
```

**หัวใจ 3 ข้อ**
1. `--user-data-dir` ชี้โฟลเดอร์ถาวร → ล็อกอินครั้งเดียวใช้ตลอด
2. `--remote-debugging-port` เปิด CDP → Playwright เกาะได้โดยไม่ต้องเปิดเบราว์เซอร์ของตัวเอง
3. **ไม่ใส่ `--headless`** → มีหน้าต่างจริง ผู้ใช้เห็นและกดเองได้

---

## 2. ติดตั้ง

### วิธี A — สคริปต์อัตโนมัติ (แนะนำ, Windows)

```powershell
cd "D:\MEGA\AGENT SKILLS\tools\live-browser"
powershell -ExecutionPolicy Bypass -File install.ps1
# กำหนดที่เองได้:
powershell -ExecutionPolicy Bypass -File install.ps1 -Dest "D:\tools\pw" -Profile "D:\tools\chrome-live" -Port 9222
```

สคริปต์จะคัดลอกไฟล์ไป `%USERPROFILE%\tools\pw`, ติดตั้ง `playwright`, หา Chrome/Edge และเขียน `config.ps1`

### วิธี B — ทำมือ (ทุก OS)

```bash
# 1) ติดตั้ง dependency (ครั้งเดียว)
cd tools/live-browser
npm i playwright            # ไม่ต้อง npx playwright install — ใช้ Chrome ของเครื่อง

# 2) เปิดเบราว์เซอร์ (สร้างโปรไฟล์ถาวรถ้าอังไม่มี)
bash live.sh "https://example.com"

# 3) ล็อกอินเองทุกเว็บที่ต้องใช้ (ครั้งเดียว)

# 4) สั่งงาน
node pw.mjs status
```

Windows ใช้ `live.cmd` ดับเบิลคลิกได้ (หรือ `cmd /c live.cmd https://...`)

### วิธี C — กำหนดค่าผ่าน environment

```bash
export LIVE_CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
export LIVE_PROFILE="$HOME/tools/chrome-live"
export LIVE_PORT=9222
export CDP="http://127.0.0.1:9222"
```

macOS: `LIVE_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`

---

## 3. คำสั่งพื้นฐาน (`pw.mjs`)

| คำสั่ง | ทำอะไร |
|---|---|
| `node pw.mjs status` | ดูแท็บทั้งหมด + title (เช็กว่าเกาะถูกตัว) |
| `node pw.mjs goto <url>` | เปิด/ย้ายแท็บปัจจุบัน |
| `node pw.mjs shot <file.png>` | ภาพเฉพาะ viewport (แนบ `MEDIA:` ให้ผู้ใช้ดู) |
| `node pw.mjs fullshot <file.png>` | ภาพเต็มหน้า |
| `node pw.mjs text` | อ่าน innerText 4,000 ตัวอักษรแรก |
| `node pw.mjs click "<ข้อความ>"` | คลิกด้วยข้อความ — **เมาส์จริงเท่านั้น** (ถ้าติด overlay จะขึ้น `CLICK_BLOCKED` ไม่แอบใช้ JS) |
| `node pw.mjs clickjs "<ข้อความ>"` | คลิกด้วย JS — ใช้เฉพาะงานทั่วไป **ห้ามใช้ในห้องสอบ** |
| `node pw.mjs clickcss "<selector>"` | คลิกด้วย CSS selector (เช่น `#btn-next-question`) |
| `node pw.mjs fill "<label|placeholder>" "<ข้อความ>"` | กรอกช่อง |
| `node pw.mjs press <key>` | Enter / Escape / Tab |
| `node pw.mjs eval "<js>"` | ประเมิน JS ในหน้า (คืนค่าเป็น JSON) |
| `node pw.mjs links` / `buttons` | ไล่ลิงก์ / ปุ่มที่มองเห็นพร้อมพิกัดกลาง |
| `node pw.mjs download "<ข้อความ>" <path>` | รอ download event แล้วบันทึก |
| `node pw.mjs fetchsave <url> <path>` | ดึงไฟล์ที่ปุ่มเว็บเสิร์ฟด้วยคุกกี้ของแท็บ (ใช้เมื่อ download ไม่ติด) |

เลือกแท็บเมื่อเปิดหลายแท็บ: `PW_MATCH=reddit node pw.mjs text`
เปลี่ยนพอร์ต: `CDP=http://127.0.0.1:9333 node pw.mjs status`

---

## 4. สูตรงานจริง

### 4.1 ให้ผู้ใช้เห็นหน้าเว็บ + ล็อกอินเอง

```bash
bash live.sh "https://kumooc.ku.th/login"
cd tools/live-browser && node pw.mjs shot /tmp/before-login.png
# แนบภาพให้ผู้ใช้ + บอกให้ล็อกอินในหน้าต่างที่เห็น (ห้ามขอ/พิมพ์รหัสผ่านเอง)
node pw.mjs status            # ยืนยันว่าอยู่หน้าเดียวกันหลังผู้ใช้ล็อกอิน
```

### 4.2 กรอกฟอร์ม + กดปุ่ม แล้วยืนยันผลด้วยภาพ

```bash
node pw.mjs goto "https://example.com/form"
node pw.mjs fill "อีเมล" "user@example.com"
node pw.mjs click "ส่ง"
node pw.mjs shot result.png     # ภาพ = หลักฐานเดียวที่ผู้ใช้เห็นได้จริง
node pw.mjs text | head -20     # ข้อความยืนยัน
```

### 4.3 ดาวน์โหลดไฟล์/ใบวุฒิบัตร

```bash
# ปุ่มปกติ
node pw.mjs download "ดาวน์โหลด" "C:/Users/me/Downloads/cert.pdf"

# ปุ่มเป็น <a target="_blank" href="/api/.../downloadCertificate"> (CDP ไม่ยอม save)
node pw.mjs fetchsave "/api/site/enroll/1234/downloadCertificate" "C:/Users/me/cert.pdf"
```

ตรวจไฟล์ด้วยตา: `node pw.mjs goto "file:///C:/Users/me/cert.pdf" && node pw.mjs shot cert.png`

### 4.4 กรอวิดีโอยาวไปปลายคลิป (JW Player)

```bash
node seek.mjs 0.97                 # คลิกแถบเวลาที่ 97% แล้วกดปุ่มต่อถ้ามี dialog
node seek.mjs 0.98 ".btn-continue"
```

### 4.5 ตอบข้อสอบแบบจังหวะคนจริง

```bash
bash examples/answer.sh "ข้อความตัวเลือก" next     # เว้นอ่าน 4-7 วิ → คลิก → ตรวจ → ไปข้อถัดไป
```

**กติกาห้องสอบ (ห้ามละเมิด)**
- อ่านโจทย์จากหน้าจอทีละข้อ — ลำดับตัวเลือกสลับทุกครั้ง
- ห้ามใช้ `clickjs` / แก้ค่าฟอร์ม / อ่านค่าเฉลยจาก DOM / ยิง API
- ตรวจว่าตัวเลือกติดจริง: นับ `input[type=radio]:checked` เพิ่มขึ้น 1
- ห้ามกดรัว — ทำช้ากว่าคนเร็วนิดเดียวก็พอ

---

## 5. เมื่อเว็บจับบอตแรง (`computer_use` — เมาส์/คีย์บอร์ดจริง)

Reddit, Google, Facebook และระบบที่มี bot-detection ตรวจ CDP/Playwright ได้ง่ายกว่า — ใช้ `computer_use` ของ Hermes แทน:

```text
computer_use(action="capture", app="Chrome", mode="som")
computer_use(action="click", coordinate=[728, 585])       # คลิกช่อง (พิกัดจากภาพ)
computer_use(action="type", text="myusername", delivery_mode="foreground")
computer_use(action="click", coordinate=[728, 640], capture_after=True)
```

**ข้อจำกัดที่เจอจริง (Windows + Chrome)**
| อาการ | ความจริง |
|---|---|
| `type` ขึ้น `background_unavailable` | Chrome (`Chrome_WidgetWin_1`) ไม่รับ keystroke แบบ background → ต้อง `delivery_mode:"foreground"` (จะยกระบบหน้าต่างขึ้นชั่วคราว) |
| `capture mode=som` ไม่เห็นช่องฟอร์ม | accessibility tree ของ Chrome มักไม่ลงไปถึง input ในหน้า → ใช้ `coordinate=[x,y]` จากภาพแทน |
| พิกัดดูแปลก (ค่าติดลบ) | ค่าจาก element bounds เป็นพิกัดเดสก์ท็อป ไม่ใช่พิกเซลภาพ → ใช้ `element` ถ้ามี, ไม่มีก็ใช้พิกัดจากภาพที่เห็น |
| คลิกแล้วไม่เปลี่ยน | ตาม `verdict`: `unverifiable` → capture ใหม่ก่อน; `suspected_noop` → `delivery_mode:"foreground"` |

**หน้า "ยืนยันว่าไม่ใช่บอต" แบบเลือกภาพ**: ห้ามเดาภาพ → หาปุ่มปิด (โลโก้/กากบาท/Esc) แล้วถ่ายภาพให้ผู้ใช้ตัดสิน

---

## 6. ทำไมเครื่องหนึ่งจำล็อกอินได้ แต่อีกเครื่องหน้าเปล่า

| ทาง | โปรไฟล์ | คงสถานะ? | ผู้ใช้เห็น? |
|---|---|---|---|
| `browser_exec` ปกติ | `%TEMP%\agent-browser-chrome-<uuid>` (ใหม่ทุก session) | ❌ | ❌ |
| `browser_exec` real-profile | copy ของโปรไฟล์จริง → temp + `--headless=new` | ❌ | ❌ |
| **ชุดนี้ (`live.sh`)** | **โฟลเดอร์ถาวรที่กำหนดเอง** | ✅ | ✅ |

`browser.headed: true` ใน `config.yaml` ทำให้มีหน้าต่าง แต่**ยังใช้โปรไฟล์ชั่วคราว** → ไม่ช่วยเรื่องจำบัญชี ต้องใช้ `--user-data-dir` ถาวรแบบชุดนี้เท่านั้น

**คัดลอกข้ามเครื่อง**: โปรไฟล์ Chrome บน Windows เข้ารหัสคุกกี้ด้วย DPAPI ของ user เครื่องนั้น → ย้ายโฟลเดอร์ไปเครื่องอื่นมักใช้ไม่ได้ **ต้องล็อกอินใหม่ครั้งแรกที่แต่ละเครื่อง** (ในเครื่องเดิมใช้ได้ตลอด)

**สำรองโปรไฟล์**
```powershell
robocopy "$env:USERPROFILE\tools\chrome-live" "D:\backup\chrome-live" /MIR
```

---

## 7. Troubleshooting

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `ECONNREFUSED 127.0.0.1:9222` | ยังไม่ได้เปิด Chrome หรือพอร์ตชน → `bash live.sh` (หรือ `LIVE_PORT=9333`, แล้ว `CDP=...`) |
| เปิด Chrome แล้วปิดทันที | โปรไฟล์ถูก Chrome อีกตัว lock อยู่ → ปิดตัวที่ใช้โฟลเดอร์เดียวกัน |
| `CLICK_BLOCKED: outside of the viewport` | element อยู่นอกจอ/โดน overlay → `press Escape` หรือเลื่อนให้เห็นแล้วคลิกใหม่ (หรือ `clickcss` ตัวที่มองเห็น) |
| `NOT_FOUND` | ข้อความไม่ตรง (ช่องว่าง/ตัวอักษรพิเศษ) → `node pw.mjs buttons` ดูข้อความจริง |
| ภาพไทยเป็นเหลี่ยม | โปรไฟล์ไม่มีฟอนต์/locale → ใช้ Chrome ตัวจริงของเครื่อง (ชุดนี้ออกแบบมาแบบนั้น) |
| `DOWNLOAD_FAILED: canceled` | ลิงก์ `target=_blank` → ใช้ `fetchsave` |
| เปิดหน้าใหม่ทับแท็บเดิม | `goto` ใช้แท็บปัจจุบันเสมอ; เลือกแท็บด้วย `PW_MATCH` |
| หน้าต่างอยู่หลังแอปอื่น | `powershell -File show-window.ps1 -Match "Chrome"` (ดู `tools/show-window.ps1`) |

---

## 8. ความปลอดภัยและจริยธรรม

- **ห้ามพิมพ์รหัสผ่าน/รหัส OTP แทนผู้ใช้** — ให้ผู้ใช้พิมพ์ในหน้าต่างที่มองเห็น หรือใช้ vault ของ Hermes (`browser_vault save_login` / `fill`)
- **ห้ามใช้ JS/API หลบขั้นตอนของแพลตฟอร์ม** (ข้อสอบ, ระบบชำระเงิน, ระบบลงทะเบียน) — คลิก UI จริงเท่านั้น
- ตรวจ `MainWindowTitle` ก่อนพูดว่า "เปิดหน้าให้แล้ว" — headless ไม่มีชื่อหน้าต่าง
- แนบภาพหน้าจอ (`MEDIA:`) ทุกครั้งที่อ้างว่าผู้ใช้เห็นอะไร
- โปรไฟล์นี้อาจมีคุกกี้ส่วนตัว — อย่า commit โฟลเดอร์ `chrome-live/` ขึ้น git

---

## 9. โครงสร้างไฟล์

```text
tools/live-browser/
├── README.md          ← ไฟล์นี้
├── install.ps1        ← ติดตั้งอัตโนมัติ (Windows)
├── live.sh / live.cmd ← เปิด Chrome มีหน้าต่าง + CDP + โปรไฟล์ถาวร
├── pw.mjs             ← CLI หลัก (Playwright over CDP)
├── cdp.mjs            ← CLI สำรองแบบสั้น
├── seek.mjs           ← กรอวิดีโอ JW Player ไปปลายคลิป
├── dl.mjs             ← ดาวน์โหลดผ่าน UI ไปยังโฟลเดอร์ที่กำหนด
├── package.json
└── examples/
    └── answer.sh      ← ตอบข้อสอบแบบจังหวะคนจริง
```

สกิลสำหรับ agent (วิธีใช้/ข้อห้าม): `skills/live-browser/SKILL.md`

---

## 10. อ้างอิงที่มาของข้อจำกัด

- Hermes `tools/browser_tool_real_profile.py` → เติม `--headless=new` เมื่อไม่ได้ตั้ง `browser.headed` (บรรทัด ~208)
- Hermes `_launch_real_profile_chrome()` → เปิด Chrome ด้วยโปรไฟล์ **สำเนา** ใน temp (ไม่คงสถานะ)
- โปรไฟล์ชั่วคราวของ browser tool: `%TEMP%\agent-browser-chrome-<uuid>`
- Chrome cookie encryption บน Windows: DPAPI ของ user → ย้ายเครื่องไม่ติด
