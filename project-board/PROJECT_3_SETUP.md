# การตั้งค่าและการเชื่อมโยง GitHub Project 3 (Skill Hub)

เอกสารแนะนำการจัดระเบียบและเชื่อมโยง **GitHub Project 3** เข้ากับ Repository [raminhyong/agent-skills](https://github.com/raminhyong/agent-skills)

---

## 1. ผังการจัดบอร์ดใน Project 3

```text
+---------------------------------------------------------------------------------------------------------+
| GITHUB PROJECT 3: ANTIGRAVITY SKILL ECOSYSTEM                                                           |
+--------------------+--------------------+--------------------+--------------------+--------------------+
| 📥 Backlog / New   | 🧪 Testing / W.I.P | 🟢 Active Core     | 🔄 Multi-Machine   | 📦 Archived /      |
|    Skill Ideas     | (New Repos)        | Skills (High Freq) | Sync Verified      | Pruned (No Clutter)|
+--------------------+--------------------+--------------------+--------------------+--------------------+
| - สกิลใหม่จากคอมมู | - แดชบอร์ดทดลอง    | - thai-doc         | - Sync script ran  | - GCP BigQuery     |
|   เช่น browser-use | - card layout v2   | - rea              |   on School PC     | - GCP Airflow      |
| - Claude Code tools|                    | - agent-reach      | - Sync script ran  | - GCP Dataflow     |
|                    |                    | - picseek          |   on Laptop        | - GCP Composer     |
|                    |                    | - human-learner    |                    |   (27 รายการ)      |
|                    |                    | - visual-dev-loop  |                    |                    |
|                    |                    | - /project /memo /exam |                    |                    |
+--------------------+--------------------+--------------------+--------------------+--------------------+
```

> สกิลชุดงานสารบรรณ–โครงการ–ข้อสอบ: `thai-project-proposal` (`/project`) · `thai-official-memo` (`/memo`) · `thai-exam-format` (`/exam`) — ดูรายละเอียดใน [README หมวด 5](../README.md)

---

## 2. วิธีเชื่อมโยง Issues เข้าสู่ Project 3 ในหน้าเว็บ

1. ไปที่ [https://github.com/users/raminhyong/projects/3/settings](https://github.com/users/raminhyong/projects/3/settings)
2. เมนูด้านซ้ายเลือก **Linked repositories** -> กดปุ่ม **Link a repository**
3. ค้นหาและเลือก `raminhyong/agent-skills`
4. เมื่อกลับมาที่หน้ากระดานบอร์ด (Board View):
   - กดปุ่ม **+ Add item** ที่ท้ายคอลัมน์
   - พิมพ์ `#` แล้วเลือก Issue ที่สร้างไว้ล่วงหน้า:
     - `#2`: `[Core-Thai] thai-doc & thai-subapp-blueprint`
     - `#3`: `[Core-Pedagogy] picseek & human-like-learner`
     - `#4`: `[Core-Research] rea & agent-reach`
     - `#5`: `[Core-Dev] visual-dev-loop & webapp-dev`
     - `#6`: `[Core-Media] prepare-piles-print-cards & arrange-card-deck-sheets`
     - `#7`: `[Archive-Pruned] ย้าย 27 Google Cloud Data Skills เข้าโฟลเดอร์ Archive`
     - `#8`: `[Future-Intake] พื้นที่รองรับสกิลใหม่จาก Repos ชุมชน AI Agents`
     - `#9`: `[Core-Thai] thai-project-proposal & thai-official-memo & thai-exam-format (ชุดงานสารบรรณ–โครงการ–ข้อสอบ)`

---

## 3. การเปิดสิทธิ์ GitHub CLI เพื่อจัดการ Project อัตโนมัติในอนาคต

รันคำสั่งนี้ครั้งเดียวใน Terminal เพื่อขอสิทธิ์ `project`:
```powershell
gh auth refresh -s project
```
เมื่ออนุญาตในเบราว์เซอร์แล้ว Agent จะสามารถเพิ่ม แก้ไข และย้ายคอลัมน์ใน Project 3 ได้โดยตรงผ่าน CLI
