# Antigravity Visual Dev Loop: เครื่องมือและแนวทาง "สร้างไป ตรวจไป"

ชุดเครื่องมือและแนวทางปฏิบัติสำหรับ **Google Antigravity** ในการตรวจสอบหน้าจอแอปพลิเคชันแบบ Visual Feedback Loop แบบเรียลไทม์ขณะที่ Agent กำลังเขียนและแก้ไขโค้ด (เทียบเท่าฟีเจอร์ Computer-Use / Live Preview ใน Devin, Cursor, และ Windsurf)

---

## สถาปัตยกรรม Visual Feedback Loop

```mermaid
graph TD
    A[Agent แก้ไขโค้ด UI/Frontend] --> B[Dev Server รัน Hot Module Replacement]
    B --> C{ช่องทางตรวจสอบหน้าจอ}
    C -->|Native Antigravity| D[Browser Subagent + บันทึก WebP Video อัตโนมัติ]
    C -->|MCP Integration| E[@playwright/mcp หรือ chrome-devtools-mcp]
    C -->|IDE Split Panel| F[Simple Browser ภายใน Antigravity IDE]
    D --> G[Agent ตรวจสอบ Layout, Font, Contrast ใน Artifacts]
    E --> G
    F --> G
    G -->|พบข้อบกพร่อง UI| A
    G -->|ผ่านเกณฑ์ Visual Quality| H[Commit & เสร็จสิ้นงาน]
```

### การจัดวางหน้าจอใน Antigravity IDE / 2.0

```text
+-----------------------------------------------------------------------+
|  ANTIGRAVITY IDE / DESKTOP APP                                        |
+-----------------------------------+-----------------------------------+
|  [โค้ด Editor ด้านซ้าย]           |  [หน้าต่างตรวจสอบ UI ด้านขวา]     |
|                                   |                                   |
|  index.html / App.tsx             |  +-----------------------------+  |
|  <header class="navbar">          |  | http://localhost:5173       |  |
|    <h1>คลังสื่อการสอน</h1>        |  +-----------------------------+  |
|    <button class="btn-primary">   |  |                             |  |
|      เข้าสู่ระบบ                  |  |      [ ภาพพรีวิวแอปจริง ]    |  |
|    </button>                      |  |      คลังสื่อการสอน         |  |
|  </header>                        |  |      [ เข้าสู่ระบบ ]        |  |
+-----------------------------------+--+-----------------------------+--+
|  [Terminal: Dev Server Daemon]    |  [Artifacts Pane: Video & Shots]  |
|  $ npm run dev -> 5173 (running)  |  > recording.webp (เห็นคลิกจริง)  |
+-----------------------------------+-----------------------------------+
```

---

## 4 ระดับเครื่องมือในการทำ Visual Dev Loop

| ระดับ | เครื่องมือ | จุดเด่น | การติดตั้ง / วิธีเรียกใช้ |
| :--- | :--- | :--- | :--- |
| **ระดับ 1** (Native) | **`browser_subagent`** | Built-in มากับ Antigravity ทันที บันทึกวิดีโอ WebP และ Screenshot ลง Artifacts อัตโนมัติ | สั่ง Agent: *"เปิด browser_subagent ไปที่ localhost:5173 แล้วทดสอบคลิกปุ่มบันทึก"* |
| **ระดับ 2** (MCP Server) | **`@playwright/mcp`** | ควบคุม Playwright ถ่ายภาพ Multi-viewport (Mobile/Desktop) และแคปเจอร์เฉพาะ DOM element | เพิ่มใน `mcp_config.json` (รันผ่าน `npx @playwright/mcp@latest`) |
| **ระดับ 3** (MCP Protocol) | **`chrome-devtools-mcp`** | เชื่อมต่อ Chrome จริงของผู้ใช้ผ่าน Chrome DevTools Protocol (CDP) ตรวจ Network/Console | เพิ่มใน `mcp_config.json` (รันผ่าน `npx chrome-devtools-mcp@latest`) |
| **ระดับ 4** (IDE View) | **Simple Browser Panel** | เปิดพรีวิวคู่โค้ดในตัว Antigravity IDE ทันทีที่มีการแก้ไฟล์ | กด `Ctrl+Shift+P` -> พิมพ์ `Simple Browser: Show` -> ใส่ `http://localhost:5173` |

---

## ขั้นตอนการติดตั้ง MCP เข้ากับ Antigravity

เปิดไฟล์การตั้งค่า MCP หลักของระบบที่:
`C:\Users\patti\.gemini\config\mcp_config.json`

นำบล็อกต่อไปนี้ไปผสานใน `"mcpServers"`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--image-responses",
        "allow"
      ]
    },
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--auto-connect"
      ]
    }
  }
}
```

---

## เครื่องมืออัตโนมัติประจำโปรเจกต์นี้

ในโฟลเดอร์นี้มีเครื่องมือพร้อมใช้งานทันที:
1. [tools/preview-capture.mjs](file:///d:/MEGA/AGENT%20SKILLS/tools/preview-capture.mjs): สคริปต์ Node.js บันทึกภาพ 3 ขนาดหน้าจอ (Desktop 1440px, Tablet 768px, Mobile 390px) แบบเบ็ดเสร็จ
2. [.agents/skills/visual-dev-loop/SKILL.md](file:///d:/MEGA/AGENT%20SKILLS/.agents/skills/visual-dev-loop/SKILL.md): สกิลฝึกสอน Agent ให้สร้างไป ตรวจไป วนลูป Self-healing อัตโนมัติ
3. [config/mcp-recipes.json](file:///d:/MEGA/AGENT%20SKILLS/config/mcp-recipes.json): เทมเพลตคอนฟิกสำหรับ MCP Servers
