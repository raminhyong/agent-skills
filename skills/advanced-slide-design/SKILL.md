---
name: advanced-slide-design
description: มาตรฐานและแนวทางปฏิบัติการออกแบบสไลด์นำเสนอระดับพรีเมียม (Cinematic & Masterclass Presentation) สำหรับครูและนักวิชาการ ด้วยหลักจิตวิทยาการรู้คิด (Cognitive Load Theory), กฎการดึงสายตา (Leading Lines & Optical Vector), การเฟดภาพไร้รอยต่อ (Seamless Gradient Masking), การเลือกคู่ฟอนต์ขั้นสูง (ห้ามใช้ Sarabun ทำปก), และกฎเหล็กขนาดฟอนต์ขั้นต่ำ 20px บนความละเอียด 1920x1080
---

# มาตรฐานการออกแบบสไลด์ระดับมาสเตอร์คลาส (Advanced Slide Design Masterclass)

คู่มือและมาตรฐานการสร้างงานนำเสนอ สื่อการสอน และสไลด์สรุปผลงานระดับผู้บริหาร/วิชาการ ที่เน้นความทรงพลัง สวยงาม คมชัดระดับ 4K ไร้ความเกะกะรกตา (High Signal-to-Noise Ratio)

---

## ⚠️ กฎเหล็กขั้นสูงสุด (Non-Negotiable Rules)

### 1. กฎขนาดฟอนต์ขั้นต่ำสุด (Minimum Font Floor: 20px)
* **เกณฑ์บังคับ:** บนแคนวาสมาตรฐาน **1920 × 1080 px (16:9 Widescreen)** **ห้ามมีตัวอักษรใดมีขนาดเล็กกว่า 20px เด็ดขาด**
* ครอบคลุมถึงทุกองค์ประกอบ:
  * ป้ายหมวดหมู่ (Kicker / Eyebrow Tag): อย่างน้อย **20px**
  * เนื้อหาคำอธิบาย (Body text / Description): อย่างน้อย **20px – 24px**
  * หัวข้อย่อย / เสาหลัก (Pillars): อย่างน้อย **22px – 26px**
  * เครดิตผู้สอน / สถาบัน / ตัวบอกสเปก (Footer Metadata): อย่างน้อย **20px**
  * แสตมป์ข้อคิด / สรุปประเด็น (Focal Motto): อย่างน้อย **20px – 26px**
* **เหตุผล:** สไลด์ไม่ได้มีไว้อ่านประชิดหน้าจอคอมพิวเตอร์อย่างเดียว แต่ต้องฉายขึ้นโปรเจกเตอร์หรือสมาร์ททีวีในห้องเรียน/ห้องประชุม ซึ่งผู้ชมนั่งห่างออกไป 5–10 เมตร ขนาดต่ำกว่า 20px จะทำลายความสามารถในการเข้าถึงข้อมูลทันที

---

### 2. กฎการเลือกฟอนต์ (Typography Policy)
* ❌ **ห้ามใช้ `TH Sarabun New` หรือฟอนต์ราชการมีเชิงดั้งเดิมทำหน้าปก หรือสไลด์บรรยายแนวภาพยนตร์เด็ดขาด:** เพราะให้ความรู้สึกเป็นหนังสือราชการ/เอกสารธุรการที่น่าเบื่อ
* ✅ **ฟอนต์พรีเมียมประจำเครื่องที่ต้องใช้:**
  * **พาดหัวหลักระดับปรากฏการณ์ (Hero Display Title):**  
    👉 **`Kanit` (Bold / ExtraBold / Black)** ขนาด 90px – 115px  
    👉 **`Prompt` (Bold / ExtraBold)** ขนาด 80px – 100px
  * **สไลด์ห้องเรียน & สื่อการสอน Active Learning:**  
    👉 **`Mitr` (Medium / Bold)** ให้ความรู้สึกเป็นมิตร อบอุ่น มีหัวมนร่วมสมัย
  * **สไลด์ AI, นวัตกรรมดิจิทัล, EdTech:**  
    👉 **`Chakra Petch` (Bold)** เส้นสายเหลี่ยมเท่ สไตล์ไซเบอร์และเทคโนโลยี
  * **เนื้อหาบรรยาย (Body Text):**  
    👉 **`Noto Sans Thai` (Regular / Medium)** หรือ **`Prompt` (Regular)** อ่านสบายตา ลื่นไหลระดับสากล
  * **ฟอนต์เสริมภาษาอังกฤษและตัวเลข:**  
    👉 `Inter`, `Poppins`, `Plus Jakarta Sans`, `Space Grotesk`
* **ข้อห้ามเรื่องฟอนต์:** ห้ามใช้ฟอนต์เกิน 2 ตระกูลในสไลด์เดียวกัน

---

### 3. การเฟดภาพแบบไร้รอยต่อ (Seamless Gradient Masking & Vignette)
* ❌ **ห้ามขังภาพไว้ในกล่องการ์ดสี่เหลี่ยม (No "Card-in-a-Box Syndrome"):** การวางรูปภาพในกรอบสี่เหลี่ยมโค้งมนแล้วใส่เงาลอยๆ ข้างกล่องข้อความ ทำให้สไลด์ดูเหมือนหน้าเว็บสำเร็จรูปราคาถูก
* ✅ **เทคนิคการเฟดภาพเข้าสู่ความมืด (Cinematic Masking):**
  * ให้ภาพครองพื้นที่ 65% – 70% ของแคนวาส หรือปูเต็มแผ่นหลัง
  * ใช้ CSS Masking ไล่ระดับแบบหลายสต็อป (Multi-stop linear mask) ให้ขอบด้านข้อความค่อยๆ ละลายโปร่งใสหายไปในสีพื้นหลัง (เช่น สีดำ Obsidian `#05070F` หรือ Deep Slate):
    ```css
    mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.45) 30%, rgba(0,0,0,1) 85%);
    -webkit-mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.45) 30%, rgba(0,0,0,1) 85%);
    ```
  * ซ้อน **Radial & Linear Vignette** บริเวณขอบบน ล่าง และมุมภาพ เพื่อคุมมิติแสงให้อารมณ์ภาพยนตร์และกำจัดขอบตัดของภาพ 100%

---

### 4. กฎการนำสายตาและลำดับสายตา (Visual Guidance & Leading Lines)
* **Optical Vector (เวกเตอร์นำสายตา):** จัดวางองค์ประกอบในภาพให้มีเส้นนำสายตา (เช่น ลำแสงอาทิตย์, แนวกำแพง, แนวทางเดิน, รอยเท้า) พุ่งตรงจากภาพเข้าหาพาดหัวสไลด์เสมอ
* **Extreme Scale Contrast:** สร้างความต่างของขนาดแบบสุดขั้ว ระหว่างพาดหัวหลัก (100px+) กับข้อความขยายความ เพื่อให้เกิดจุดปะทะสายตาแรกทันทีที่เปิดสไลด์
* **ห้ามใช้อีโมจิการ์ตูนเป็นไอคอนในสไลด์พรีเมียม:** สไลด์ระดับมืออาชีพจะไม่ใช้อีโมจิเด็กเล่น (`💡`, `🎯`, `🛡️`) แต่ใช้ความสง่างามของ Typography, ตัวเลขโรมัน, ป้ายกำกับสากล, และเส้นสีนำสายตา (Accent Hairline Rule)

---

### 5. โครงสร้างสีและการตัดขอบฟอนต์ (High Contrast, Punchy Colors & Radiance Stroke)
* ❌ **ห้ามใช้สีเทาหม่นๆ หรือสีกลางๆ (No Muddy Muted Grays) ในข้อความสำคัญ:** สีเทาหม่นจะทำให้ฟอนต์กลืนไปกับฉากหลัง สูญเสียจุดโฟกัส และอ่านยากมากในสภาพแสงจริง
* ✅ **เลือกใช้สีที่สดเข้ม โดดเด่น ชัดเจน (High-Saturation & Punchy Contrast):**
  * พาดหัวและข้อความนำ: สีขาวสว่างบริสุทธิ์ (`#FFFFFF`), สีเหลืองสะดุดตา (`#FACC15`), หรือสีเขียวมรกตสด (`#10B981`)
  * ป้ายและข้อมูลเปรียบเทียบ: ใช้คู่สีตัดกันสูง เช่น แดงสดปะทะเขียวสด (`#F87171` vs `#34D399`)
* 🛡️ **เทคนิค Stroke & Radiance Halo ป้องกันฟอนต์ถูกกลืน (The Anti-Blend Rule):**
  * เมื่อตัวอักษรพาดผ่านภาพพื้นหลังที่มีเฉดสีซับซ้อน (มีทั้งใบไม้ ลำแสง เปลือกไม้ หรือเงา) **ต้องใส่ Stroke บางๆ หรือ Radiance แสงเรืองรอง/Dark Halo เสมอ**:
    ```css
    /* เทคนิค Radiance Halo ป้องกันตัวหนังสือจม */
    text-shadow: 
      0 0 15px rgba(16, 185, 129, 0.5),  /* แสงเรือง Radiance สีนวลรอบตัวอักษร */
      0 2px 10px rgba(0, 0, 0, 0.95),    /* เงาเข้มคัดขอบให้อักษรลอยเด่น */
      0 0 35px rgba(3, 7, 18, 0.9);      /* Scrim คุ้มกันพื้นที่ด้านหลัง */
    ```
    หรือใช้ `-webkit-text-stroke: 1px rgba(0, 0, 0, 0.7);` เพื่อให้ตัวอักษรคมกริบและไม่โดนภาพกลืนในทุกจังหวะสายตา

---

## 🛠️ สถาปัตยกรรมโค้ดสไลด์ต้นแบบ (HTML5 / CSS Boilerplate)

```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920, height=1080, initial-scale=1.0">
  <title>Masterclass Slide Template</title>
  <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@700;900&family=Noto+Sans+Thai:wght@400;500;600&family=Prompt:wght@500;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      width: 1920px; height: 1080px; overflow: hidden;
      background: #05070f; color: #f1f5f9;
      font-family: 'Noto Sans Thai', 'Prompt', sans-serif;
    }
    .viewport { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
    .hero-image {
      position: absolute; top: 0; right: 0; width: 68%; height: 100%;
      mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.45) 30%, rgba(0,0,0,1) 85%);
      -webkit-mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.45) 30%, rgba(0,0,0,1) 85%);
    }
    .hero-image img { width: 100%; height: 100%; object-fit: cover; }
    .content {
      position: relative; z-index: 5; width: 100%; height: 100%;
      padding: 85px 120px 75px 120px; display: flex; flex-direction: column; justify-content: space-between;
      max-width: 1100px;
    }
    /* กฎเหล็กฟอนต์ขั้นต่ำ 20px */
    .kicker { font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; color: #d97706; }
    .title { font-family: 'Kanit', sans-serif; font-size: 106px; font-weight: 900; line-height: 1.02; }
    .lead { font-family: 'Prompt', sans-serif; font-size: 32px; font-weight: 600; line-height: 1.48; }
    .body { font-size: 21px; line-height: 1.6; color: #94a3b8; }
    .footer { font-size: 20px; color: #64748b; white-space: nowrap; }
  </style>
</head>
<body>
  <div class="viewport">
    <div class="hero-image"><img src="assets/image.png"></div>
    <main class="content">
      <!-- องค์ประกอบสไลด์ตามมาตรฐาน -->
    </main>
  </div>
</body>
</html>
```

---

## 🚀 คำสั่งการเรนเดอร์สไลด์คุณภาพสูงสุด (4K Retina Output)

เมื่อสร้างหรือแก้ไขไฟล์สไลด์ ให้ใช้สคริปต์ Playwright เรนเดอร์ด้วยความละเอียดระดับ 2x (3840 × 2160 px Downsampled) เพื่อความคมชัดสูงสุดบนจอทุกประเภท:

```javascript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 2
});

await page.goto('file:///path/to/slide.html', { waitUntil: 'networkidle' });
await page.screenshot({ path: 'slide.png' });
await page.pdf({ path: 'slide.pdf', width: '1920px', height: '1080px', printBackground: true });
await browser.close();
```

---
*บันทึกมาตรฐานโดย นายรามิล ปัญญพัทธ์ (โรงเรียนพูลเจริญวิทยาคม) & โทนี่ (Antigravity AI Agent)*

