---
name: advanced-slide-design
description: มาตรฐานและแนวทางปฏิบัติการออกแบบสไลด์นำเสนอระดับพรีเมียม (Cinematic & Masterclass Presentation) สำหรับครูและนักวิชาการ ด้วยหลักจิตวิทยาการรู้คิด (Cognitive Load Theory), กฎการดึงสายตา (Leading Lines & Optical Vector), การเฟดภาพไร้รอยต่อ (Seamless Gradient Masking), การตรวจจับและคุ้มครองวัตถุสำคัญ (Subject Saliency & Bounding Box Integrity), การเลือกคู่ฟอนต์ขั้นสูง (ห้ามใช้ Sarabun ทำปก), กฎขนาดฟอนต์สัมพัทธ์ 1.2% Canvas Height (Golden Ratio Floor), การตัดขอบฟอนต์ด้วย Distinct Stroke & Radiance, และการเรนเดอร์ระดับ 4K ด้วย Playwright (ไม่พึ่งพา Canva/Figma)
---

# มาตรฐานการออกแบบสไลด์ระดับมาสเตอร์คลาส (Advanced Slide Design Masterclass)

คู่มือและมาตรฐานการสร้างงานนำเสนอ สื่อการสอน และสไลด์สรุปผลงานระดับผู้บริหาร/วิชาการ ที่เน้นความทรงพลัง สวยงาม คมชัดระดับ 4K ไร้ความเกะกะรกตา (High Signal-to-Noise Ratio) ควบคุมด้วยโค้ด HTML5/CSS3 และประมวลผลผ่าน Playwright Headless Browser โดยไม่พึ่งพา Canva หรือ Figma

---

## 💎 ปรัชญาและจุดยืนของเครื่องยนต์ (Engine Supremacy)
* ❌ **ปฏิเสธ Canva และ Figma โดยเด็ดขาด (Strict No-Canva / No-Figma Policy):** 
  * เทมเพลตสำเร็จรูปขาดความยืดหยุ่นทางโครงสร้างคณิตศาสตร์ มีข้อจำกัดเรื่องการเรนเดอร์สระ/วรรณยุกต์ภาษาไทย และมักส่งออกภาพแบบ Raster ที่สูญเสียความคมชัด
  * ระบบสไลด์ของเราขับเคลื่อนด้วย **Custom Code (HTML5 + Modern CSS Flexbox/Grid)** และเรนเดอร์ผ่าน **Playwright Vector & 4K Retina Rendering Engine** ให้ความคมชัดระดับพิมพ์ออฟเซต ปรับแต่งขนาด อัตราส่วน และลูกเล่นแสงเงาได้ระดับซับพิกเซล

---

## ⚠️ กฎเหล็กขั้นสูงสุด (Non-Negotiable Rules)

### 1. กฎการตรวจจับและคุ้มครองวัตถุสำคัญ (Subject Bounding Box & Focal Integrity Rule)
* ❌ **หลุมพรางการครอปแบบสุ่มสี่สุ่มห้า (Blind Crop & Amputation Trap):**
  * การบีบภาพใส่กล่องคอนเทนเนอร์ขนาดตายตัว (เช่น บังคับ `height: 860px` บนภาพแนวตั้ง 1200px) โดยไม่ตรวจสอบขอบเขตวัตถุ จะทำให้เกิดโศกนาฏกรรมทางสายตา เช่น **หัวไก่ขาด ขาคนขาด อัญมณีพลอยหาย** หรือส่วนสำคัญของเรื่องเล่าถูกตัดทิ้ง
* ✅ **การวิเคราะห์ขอบเขตปลอดภัยของวัตถุ (Subject-Aware Auto-Framing):**
  * **Saliency Bounding Box Detection:** ก่อนจัดวางเลย์เอาต์ ต้องใช้โมเดล AI ตรวจจับขอบเขตของตัวแบบหลัก (เช่น BRIA-RMBG ONNX ในระบบ หรือ Multimodal Inspection) เพื่อหาพิกัด $[X_{\min}, X_{\max}, Y_{\min}, Y_{\max}]$ ของวัตถุสำคัญ
  * **Full-Body Appearance Guarantee:** ตัวแบบหลัก (เช่น ไก่, อัญมณี, ตัวละคร, อุปกรณ์ทดลอง) **ต้องปรากฏครบถ้วนเต็มตัว 100% ห้ามมีส่วนหัว ปาก ขา หรือพร็อพสำคัญหลุดออกนอกจอ**
  * **Zero-Penetration Masking:** การใส่เส้นเฟด Gradient Mask หรือ Vignette ต้องเกิดขึ้นเฉพาะในพื้นที่ว่างรอบนอก (Peripheral Negative Space เช่น ยอดไม้ด้านบน ท้องฟ้า หรือพื้นหินด้านล่าง) **ห้ามให้เส้นเฟดกลืนผ่านกายวิภาคของตัวแบบเด็ดขาด**
  * **Aspect Ratio Harmony:** บนสไลด์แนวตั้ง A4 ($1400 \times 1980\text{ px}$) หากภาพต้นฉบับเป็นแนวตั้ง (เช่น 896x1200) ให้ใช้การวางแบบ Full-Bleed ปูเต็มพื้นที่ จะล็อกสัดส่วนความสูงให้คงอยู่ครบ 100% โดยไม่มีการตัดส่วนสูงทิ้งเลยแม้แต่พิกเซลเดียว

---

### 2. กฎขนาดฟอนต์สัมพัทธ์ความสูงแคนวาส (The 1.2% Canvas Height Rule - Golden Ratio Floor)
* ❌ **หลุมพรางขนาดฟอนต์ตายตัวและฟอนต์ใหญ่เทอะทะ:**
  * การใช้ขนาดฟอนต์คงที่ (เช่น 20px ทุกงาน) ล้มเหลวบนแคนวาสแนวตั้งความละเอียดสูง
  * แต่การตั้งเกณฑ์สูงเกินไป (เช่น 1.8% หรือ 36px) จะทำให้องค์ประกอบรอง เช่น Footer Metadata, รหัสเอกสาร, เครดิตผู้สอน และป้ายกำกับ Eyebrow ใหญ่เทอะทะ แย่งความเด่นจากเนื้อหาหลัก และทำลายความหรูหรา (Visual Sophistication)
* ✅ **สูตรคำนวณขนาดฟอนต์ขั้นต่ำสุดสากล (1.2% Canvas Height Floor):**
  $$\text{Minimum Font Floor} = \text{Canvas Height} \times 1.2\%$$
  * **แคนวาส 21:29.7 แนวตั้ง A4 ($1400 \times 1980\text{ px}$):**
    * ฟอนต์เล็กสุด (Footer Bar, Spec Mark, Author Credits, Eyebrow Tag): **$\ge 24\text{px}$** ($1980 \times 1.2\% = 23.76\text{px}$)
    * คำอ่านสัทอักษรและคำแปล (Phonetics & Translation): **$26\text{px} - 28\text{px}$**
    * เนื้อหาบรรยายเสาหลักและคำอธิบาย (Pillar Descriptions, Definitions): **$25\text{px} - 28\text{px}$**
    * ป้ายกำกับเสาหลัก (Pillar Tags): **$24\text{px}$**
    * หัวข้อเสาหลักและแสตมป์แก่นคิด (Pillar Titles, Focal Motto): **$30\text{px} - 34\text{px}$**
    * คำแถลงแก่นหลัก (Assertion Lead): **$38\text{px} - 44\text{px}$**
    * พาดหัวหลักแนวตั้ง (Hero Display Title): **$110\text{px} - 125\text{px}$**
  * **แคนวาส 16:9 แนวนอน ($1920 \times 1080\text{ px}$):**
    * ฟอนต์เล็กสุด (Footer, Spec Tag, Eyebrow): **$\ge 14\text{px} - 16\text{px}$** (ปรับสมดุลสายตาให้อ่านสบาย)
    * เนื้อหาบรรยาย (Body Text): **$20\text{px} - 24\text{px}$**
    * พาดหัวย่อย / เสาหลัก (Pillars): **$24\text{px} - 28\text{px}$**
    * พาดหัวหลัก (Hero Title): **$95\text{px} - 115\text{px}$**

---

### 3. กฎระยะเว้นชนวรรณยุกต์และสระภาษาไทย (Thai Typographic Collision Buffer)
* อักษรไทยมี 4 มิติแนวตั้ง (พยัญชนะฐาน, สระบน, ไม้เอก/โท/ตรี/จัตวา, และสระล่าง/เชิง)
* เมื่อวางคำอ่านสัทอักษร (Phonetics) หรือ Subtitle ภาษาอังกฤษ ต่อท้ายพาดหัวภาษาไทยขนาดใหญ่ **ต้องเว้นระยะห่างด้านล่าง (Bottom Buffer / Margin) อย่างน้อย $22\text{px} - 28\text{px}$** เพื่อป้องกันไม่ให้หางสระหรือวรรณยุกต์ชนหรือบดบังตัวอักษรแถวถัดไป

---

### 4. กฎการเลือกฟอนต์ระดับพรีเมียม (Typography Policy)
* ❌ **ห้ามใช้ `TH Sarabun New` หรือฟอนต์เอกสารราชการทำหน้าปก หรือสไลด์บรรยายแนวภาพยนตร์เด็ดขาด:** เพราะให้ความรู้สึกเป็นหนังสือราชการ/เอกสารธุรการที่น่าเบื่อ ไร้พลัง
* ✅ **ฟอนต์พรีเมียมประจำเครื่องที่ต้องใช้:**
  * **พาดหัวหลักระดับปรากฏการณ์ (Hero Display Title):**  
    👉 **`Kanit` (Bold / ExtraBold / Black)** ขนาด 95px – 125px  
    👉 **`Prompt` (Bold / ExtraBold)** ขนาด 85px – 105px
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

### 5. โครงสร้างสี สมดุลพลังงานการรับรู้ และ Stroke คมชัด (Contrast, Perceptual Balance & Radiance)
* ❌ **ห้ามใช้สีเทาหม่นๆ หรือสีกลางๆ (No Muddy Muted Grays) ในข้อความสำคัญ:** สีเทาหม่นจะทำให้ฟอนต์กลืนไปกับฉากหลัง สูญเสียจุดโฟกัส และอ่านยากมากในสภาพแสงจริง
* 💡 **กฎความสว่างของตัวอักษรบรรยายบนธีมมืด (Dark-Theme Luminance Threshold):**
  * ในการ์ดหรือแถบนิยามความหมาย ตัวอักษรบรรยายเนื้อหาต้องมีความสว่างสากลอย่างน้อย $90\% - 100\%$ (เช่น `#FFFFFF` หรือ `#F8FAFC`) ห้ามใช้สีฟ้าน้ำทะเลเข้มหรือสีครามทึบกับข้อความบรรยายเพราะทำให้อ่านยากมาก
* ⚡ **กฎสมดุลพลังงานการรับรู้ของสีคู่ตรงข้าม (Perceptual Energy Balancing - Helmholtz-Kohlrausch Effect):**
  * เมื่อออกแบบคอลัมน์เปรียบเทียบสองขั้ว (เช่น *ILLITERACY TRAP* vs *VALUE MASTERY*) ดวงตามนุษย์รับรู้สีโทนเย็น (Cyan `#38BDF8`) ว่าสว่างและเด่นกว่าสีโทนร้อนเสมอ
  * ดังนั้น ขั้วตรงข้ามต้องไม่ใช้สีชมพูหม่นหรือแดงทึบ แต่ต้องใช้ **Electric Neon Coral / Vivid Crimson (`#FF3366` หรือ `#FF2E63`)** เพื่อสร้างสมดุลทางสายตาและน้ำหนักทางจิตวิทยาที่เท่าเทียมกัน
* 🛡️ **เทคนิค Stroke ชัดเจน & Radiance Halo คัดขอบฟอนต์ (The Distinct Stroke Armor):**
  * ใช้ **`paint-order: stroke fill;`** เสมอ เพื่อให้เส้น Stroke อยู่ *ด้านหลัง* เนื้อฟอนต์ ไม่บีบตัวอักษรให้ลีบแบน
  * ขนาด Stroke แนะนำ: `-webkit-text-stroke: 1.5px – 2.5px rgba(0, 0, 0, 0.95);`
  * เสริมด้วย **Radiance Halo ซ้อน 3 ชั้น** (`text-shadow`):
    ```css
    /* เทคนิค Distinct Stroke & Radiance Halo */
    paint-order: stroke fill;
    -webkit-text-stroke: 2px rgba(3, 6, 17, 0.95);
    text-shadow: 
      0 0 2px #000, 0 0 4px #000,          /* Black crisp edge */
      0 0 25px rgba(56, 189, 248, 0.65),    /* Vivid Radiance Glow */
      0 10px 30px rgba(0, 0, 0, 0.95);      /* Deep backing shadow */
    ```

---

### 6. กฎห้ามวางวัตถุบดบังจุดสนใจของภาพ (Strict Zero Subject Occlusion)
* ❌ **ห้ามใช้การ์ดลอย (`position: absolute`) ทับส่วนสำคัญของตัวแบบ:** การวางกล่องข้อความลอยทับหางนก ใบหน้าคน แสงอัญมณี หรือจุดโฟกัสของภาพประกอบ ทำให้สไลด์ดูรก ทำลายงานศิลปะ และตัดขาดลำดับการกวาดสายตา (Cognitive Visual Flow)
* ✅ **การจัดวางแบบต่อเนื่องเชิงเส้น (Linear & Integrated Capsule Flow):**
  * ย้ายป้ายสรุปประเด็น (`.integrated-capsule`) ไปต่อท้ายกล่องนิยามใน Top Zone หรือจัดลำดับให้อยู่นอกขอบเขต Bounding Box ของวัตถุ ช่วยให้งานภาพตรงกลางเปิดโล่งบริสุทธิ์ 100%

---

### 7. การเฟดภาพแบบไร้รอยต่อ (Seamless Gradient Masking & Vignette)
* ❌ **ห้ามขังภาพไว้ในกล่องการ์ดสี่เหลี่ยม (No "Card-in-a-Box Syndrome")**
* ✅ **เทคนิคการเฟดภาพเข้าสู่ความมืด (Cinematic Masking):**
  * ใช้ **Top & Bottom Ambient Vignette** เฉพาะบริเวณที่มีตัวหนังสือพาดผ่าน เพื่อให้อ่านข้อความได้ชัดเจนที่สุด โดยที่ส่วนตรงกลางเปิดโล่งเต็มตา
  * ซ้อน **Lateral Vignette** เพื่อคุมมิติแสงให้อารมณ์ภาพยนตร์และกำจัดขอบตัดของภาพ 100%

---

## 📐 มาตรฐานสัดส่วนแคนวาสทั้ง 2 รูปแบบ

| คุณลักษณะ | แนวนอน 16:9 (Landscape Masterclass) | แนวตั้ง 21:29.7 (A4 Portrait Masterclass) |
| :--- | :--- | :--- |
| **ความละเอียด (Canvas Size)** | `1920 × 1080 px` | `1400 × 1980 px` |
| **วัตถุประสงค์หลัก** | การนำเสนอบนจอโปรเจกเตอร์ / ทีวีในห้องประชุม | ใบสรุปความรู้ (One-Page Executive Summary) / สื่อการสอนรายบุคคล |
| **ขนาดฟอนต์ขั้นต่ำสุด (Floor)** | **14px – 16px** | **24px** (ตามกฎ 1.2% Canvas Height) |
| **พาดหัวหลัก (Hero Title)** | `Kanit` Bold 95px – 110px | `Kanit` Bold 110px – 125px |
| **ระยะเว้นชนวรรณยุกต์ (Collision Buffer)**| $\ge 20\text{px}$ | $\ge 22\text{px} - 28\text{px}$ |
| **การคุ้มครองตัวแบบ (Subject Integrity)** | Bounding Box อยู่ในฝั่งขวา 55% | Bounding Box อยู่ในโซนกลาง ไม่ถูกครอปส่วนสูง |
| **โครงสร้างเนื้อหา** | ซ้าย: เนื้อหา 45% / ขวา: ภาพเฟด 55% | 3 โซนแนวตั้ง: Top (30%) / Middle (45%) / Bottom (25%) |

---

## 🚀 คำสั่งการเรนเดอร์สไลด์คุณภาพสูงสุด (4K Retina Output)

เมื่อสร้างหรือแก้ไขไฟล์สไลด์ ให้ใช้สคริปต์ Playwright เรนเดอร์ด้วยความละเอียดระดับ 2x (3840 × 2160 หรือ 2800 × 3960 px Downsampled) เพื่อความคมชัดสูงสุดบนจอทุกประเภท:

```javascript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1400, height: 1980 }, // หรือ { width: 1920, height: 1080 }
  deviceScaleFactor: 2
});

await page.goto('file:///path/to/slide.html', { waitUntil: 'networkidle' });
await page.screenshot({ path: 'slide.png' });
await page.pdf({ path: 'slide.pdf', width: '1400px', height: '1980px', printBackground: true });
await browser.close();
```

---
*บันทึกมาตรฐานโดย นายรามิล ปัญญพัทธ์ (โรงเรียนพูลเจริญวิทยาคม) & โทนี่ (Antigravity AI Agent)*
