# Magazine Portfolio & Performance Report (v0.5-beta) 📖✨
> **มาตรฐานการสร้างแฟ้มสะสมงานและรายงานผลการปฏิบัติงานสไตล์นิตยสารร่วมสมัย (Contemporary Academic Magazine)**  
> *บันทึกและพัฒนาโดย: นายรามิล ปัญญพัทธ์ (โรงเรียนพูลเจริญวิทยาคม) & โทนี่ (Antigravity AI Agent)*

---

## 📌 สถานะของโปรเจกต์ (Project Status)
> **⚠️ สถานะปัจจุบัน: Version 0.5 (Work in Progress / Beta)**  
> สกิลนี้ยัง**ไม่เป็นเวอร์ชันที่สมบูรณ์ 100%** อยู่ระหว่างขั้นตอนการทดสอบ พัฒนา และฝึกฝน (Training Phase) โดยมีโครงสร้างรากฐานหลักและลูปการทำงานพร้อมใช้งานแล้ว แต่ยังต้องการพัฒนาต่อยอดอีกหลายจุด

---

## 💎 ปรัชญาและจุดยืน (Design Manifesto)
1. ❌ **Strict No-Canva / No-Figma Policy:**  
   ปฏิเสธเทมเพลตกล่องสำเร็จรูปที่ล็อกความคิด ขังภาพในกรอบสี่เหลี่ยมแข็งทื่อ และตัดคำภาษาไทยผิดเพี้ยน ขับเคลื่อนด้วย **Programmatic HTML5/CSS3** และเรนเดอร์ผ่าน **Playwright 4K/8K Retina Engine**
2. 🍃 **ความผ่อนคลายและพื้นที่หายใจ (The Luxury of Air):**  
   งานนำเสนอวิชาการต้อง **"ไม่จัดแน่นจนอึดอัด"** แต่มีช่องไฟที่หายใจได้ สวยงาม ดูเป็นธรรมชาติ
3. 🪟 **สถาปัตยกรรมเลเยอร์ภาพ 3 มิติ (Layered Depth & Organic Overlap):**  
   เลิกใช้ "Card-in-a-Box" เรียงกล่องแยกกัน แต่ใช้ภาพหลัก (Macro Anchor) เป็นระนาบความลึก และให้ภาพเจาะลึก (Detail Insets) ซ้อนเหลื่อม (Overlap) อย่างมีศิลปะ โดยไม่ทับใบหน้าหรือจุดสำคัญของตัวแบบ

---

## 🏆 เสาหลักและกฎเหล็กที่ได้รับการพิสูจน์แล้ว (Core Pillars Locked in v0.5)

### 1. กฎขนาดฟอนต์สัมพัทธ์ 1.2% (The 1.2% Canvas Height Rule)
$$\text{Minimum Font Floor} = \text{Canvas Height} \times 1.2\%$$
* **A4 Portrait ($1400 \times 1980\text{ px}$):** ฟอนต์เล็กสุด (Footer, Tag, Spec) ต้อง **$\ge 24\text{px}$** เสมอ ห้ามมีฟอนต์จิ๋วที่อ่านไม่ออกบนเอกสารจริง
* **16:9 Landscape ($1920 \times 1080\text{ px}$):** ฟอนต์เล็กสุด **$\ge 16\text{px}$**

### 2. กฎคุ้มครองตัวแบบสำคัญ (Subject Saliency & Bounding Box Integrity)
* ตรวจจับพิกัด $[X_{\min}, X_{\max}, Y_{\min}, Y_{\max}]$ ด้วย AI Model (`detect_subject.py` - BRIA-RMBG ONNX)
* **Full-Body / Full-Action Guarantee:** ห้ามครอปโดนศีรษะคน ดวงตา หรืออัญมณีชิ้นงานเด็ดขาด (บทเรียนสำคัญจากภาพ "ไก่ได้พลอย" ที่แคปซูลเคยทับหัวไก่)

### 3. การคุมระดับความเข้มสีของหน้างาน (3 Surface Ink Density Levels)
* **Level 1 (เข้มเด่น 75%–100%):** พื้นสีเข้ม (Obsidian / Burgundy) เหมาะกับหน้าปก (Cover) หรือหน้าเปิดบท (Chapter Opener)
* **Level 2 (ปานกลาง 30%–50%):** พื้นสีครีมทรายอ่อน (Warm Linen Alabaster) อ่านสบายตา ประหยัดหมึก เหมาะกับหน้ารายงานผลการประเมิน (เช่น งาน Task 01 PLC)
* **Level 3 (อ่อน/ขาวคลีน 0%–20%):** พื้นกระดาษขาวบริสุทธิ์ ประหยัดหมึกพิมพ์ 100% เหมาะกับหน้าสถิติ ตาราง และดัชนี

### 4. ลูปการทำงานแบบทีมเอเจนต์อัตโนมัติ (The 4-Stage Sub-Agent Loop)
```text
[Input Word/Raw] 
       │
       ▼
1. editorial-content-agent     --> สกัด Golden Metrics, Title, Deck, 3 Action Pillars
       │
       ▼
2. editorial-visual-director   --> ตรวจสอบ Bounding Box & คำนวณพิกัด Layered Overlap
       │
       ▼
3. Tony Coordinator (Architect)--> ประกอบโค้ด HTML5/CSS3 คุมกฎ 1.2% และความเข้มสี 1-2-3
       │
       ▼
4. editorial-qa-inspector      --> Playwright 4K Retina Render & AI Visual QA Inspection
       │
       ▼
[4K PNG & Vector PDF Output]
```

---

## 📂 ตัวอย่างงานที่ผ่านการทดสอบจริง (Verified Examples)

| รหัสตัวอย่าง | ชื่องาน | สไตล์และเลย์เอาต์ | ความเข้มสี | ไฟล์ตัวอย่าง |
| :--- | :--- | :--- | :--- | :--- |
| **Task 01** | **ชุมชนแห่งการเรียนรู้ทางวิชาชีพ (PLC)** | A4 Portrait Layered Spread (Macro Anchor + Dual Cascading Inset + Weekly Timetable Ribbon) | **Level 2** (ปานกลาง) | `Tony-task 01 - Magazine Spread Layered.png` / `.pdf` |
| **Niagara** | **น้ำตกไนแองการ่า (Hydrology Spread)** | A4 Portrait Asymmetrical Spread | **Level 2** (ปานกลาง) | `niagara_portrait_magazine_level2.png` / `.pdf` |
| **Sahara** | **ทะเลทรายซาฮาร่า (Geology Feature)** | 16:9 Landscape & A4 Portrait Editorial Spread | **Level 1** (เข้มเด่น) | `sahara_portrait_magazine.png` / `.pdf` |
| **Proverb** | **ไก่ได้พลอย (Focal Integrity Study)** | A4 Portrait Full-Bleed Subject Protection | **Level 1** (เข้มเด่น) | `kai_dai_ploy.png` / `.pdf` |

---

## 🚀 แผนงานและจุดที่ต้องการพัฒนาต่อ (Roadmap & Future Enhancements)

- [ ] **1. Benchmark แม่แบบระดับความเข้มสี 3 (Level 3 Pure White / Ink-Saver):** สร้างเทมเพลตขาวบริสุทธิ์ที่มีลูกเล่น Typographic Luxury สำหรับพิมพ์ลงกระดาษ 80 แกรม
- [ ] **2. สถาปัตยกรรม Process Grid 6 ขั้นตอน (Type 3):** สำหรับรายงานกระบวนการ Active Learning และวงรอบ PDCA แบบภาพต่อเนื่อง $1 \rightarrow 6$
- [ ] **3. ตารางข้อมูลสไตล์นิตยสาร (Type 5 Structured Data Matrix):** ตารางเปรียบเทียบผลสัมฤทธิ์ Pre/Post Test และเกณฑ์รูบริกส์ที่ไร้เส้นทึบตัน
- [ ] **4. ระบบรวมเล่มหลายหน้า (Multi-Page Magazine Booklet Pipeline):** รวมหน้าปก สารบัญ หน้าคั่นบท และหน้าเนื้อหา เข้าเป็นไฟล์ PDF เล่มเดียวสมบูรณ์
- [ ] **5. คำสั่งเรียกใช้งานอัตโนมัติ (CLI One-Click Automation):** เช่น คำสั่ง `/mag-report <docx-path>` เพื่อเรียกใช้งาน Sub-Agent loop ทำงานรวดเดียวจบ

---
*Last Updated: 12 พฤศจิกายน 2569*  
*บันทึกโดย โทนี่ (Antigravity AI Agent) คู่หูโปรแกรมเมอร์ของครูรามิล*
