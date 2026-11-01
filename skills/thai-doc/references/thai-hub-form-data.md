# Thai PW Hub — แหล่งข้อมูลกลางของแอปกรอกฟอร์ม

ใช้เมื่อต้องต่อข้อมูล (นักเรียน / ปี-ภาคเรียน / คลังฟอร์ม) เข้ากับแอปใน Thai Hub แทนการให้ผู้ใช้พิมพ์เอง
ทุกอย่างที่มีอยู่แล้วใน repo — **ห้ามสร้างชุดข้อมูลใหม่หรือก๊อปไฟล์** ให้ค้นของเดิมก่อน

## 1. ฐานข้อมูลนักเรียน

`TH-Hub-App/data/students_master_2569.json` · 2,629 คน

```json
{ "no": 1, "student_id": "27109", "grade": 1, "room": "1", "class": "ม.1/1",
  "prefix": "เด็กชาย", "first_name": "กฤษกร", "last_name": "หมวกเปียะ",
  "fullname": "เด็กชายกฤษกร หมวกเปียะ" }
```

รูปร่างไฟล์: `{ academic_year, total_students, students: [...] }` — ต้องรองรับทั้งแบบ object และ array ตรง ๆ

### รูปแบบ lookup ที่ผู้ใช้ต้องการ

- ช่อง "รหัสนักเรียน" รับ **5 หลัก** (`inputMode="numeric"`, `maxLength=5`) → เติม ชื่อ-สกุล (`fullname`) · ชั้น (`grade`) · ห้อง (`room`) ให้ทันที
- **ตารางหลายคน** (เช่น แบบปรับ-ร): ใส่รหัสในแถว → เติม `studentName` + `classRoom` + เลขลำดับ (`no` = index+1) ของแถวนั้น
- ใต้ช่องมีสถานะ: `✓ <ชื่อ> · ม.3/1` (เขียว) / `✗ ไม่พบรหัสนี้ในฐานข้อมูล` (แดง)
- **รหัสครบ 5 หลักแต่ไม่พบ → ล้างค่าที่เคยเติมอัตโนมัติออก** (จำค่า autofill ครั้งก่อนไว้เทียบ อย่าล้างค่าที่ผู้ใช้พิมพ์เอง) ไม่งั้นเอกสารออกมาพร้อมชื่อผิดคน
- โหลดไม่สำเร็จ = ยังกรอกเองได้ (ห้ามบล็อก/ซ่อนฟอร์มเพราะเหตุนี้)

### โหลดแบบหลาย path (แอปอยู่ลึก `apps/<app>/`)

```js
var STUDENT_PATHS = ['../../data/students_master_2569.json', '../data/students_master_2569.json', 'data/students_master_2569.json'];
// for-loop + await fetch ทีละ path, เช็ค res.ok และ list.length ก่อนใช้
```

## 2. ปีการศึกษา / ภาคเรียน

`TH-Hub-App/assets/js/academic-calendar.js` (UMD → `window.AcademicCalendar`, WO#23)

| ช่วงวันที่ | ภาคเรียน | ปีการศึกษา |
|---|---|---|
| 1 พ.ค. – 31 ต.ค. | 1 | ปี พ.ศ. ปัจจุบัน |
| 1 พ.ย. – 31 ธ.ค. | 2 | ปี พ.ศ. ปัจจุบัน |
| 1 ม.ค. – 30 เม.ย. | 2 | ปี พ.ศ. ปัจจุบัน − 1 |

- API: `getNow()`, `getTerm(date)`, `buildYearOptions(select, minYear, maxYearsAhead)`
- ดรอปดาวน์แสดง **เฉพาะค่า** (`1`, `2`, `2569`) — ห้ามใส่ช่วงวันที่ใน `<option>` และห้ามใส่บรรทัด "ช่วงเวลา: …" ใต้แถว (ผู้ใช้บอกครูรู้อยู่แล้ว)
- ขอบล่างของปี = **2569** (ปีแรกที่เริ่มใช้ระบบ)
- เติมค่าอัตโนมัติ + เติมวันที่วันนี้ (`toLocaleDateString('th-TH', {day:'numeric',month:'long',year:'numeric'})` → "1 พฤศจิกายน 2569")

## 2.1 คลังรายวิชา (31 วิชา)

`TH-Hub-App/data/courses_master_2569.json` — **เป็น object ที่ key = รหัสวิชา ไม่ใช่ array**

```json
{ "ท20205": { "code": "ท20205", "name": "การศึกษานิทาน", "level": "ม.3",
               "levelFull": "ชั้นมัธยมศึกษาปีที่ 3", "type": "เพิ่มเติม" } }
```

- โหลด: `Object.keys(data).map(function(k){return data[k];}).filter(function(c){return c && c.code;})` แล้วเรียงตาม `code`
- `<select>` แสดง `รหัส · ชื่อ (ม.X)` → เลือกแล้วเติม `code` · `subject` · `courseLevel` ใน state
- ฟอร์มหลายคน (เช่น แบบปรับ-ร) **ไม่ต้องมีช่อง "ชั้น/ห้องที่สอน"** — ดึงจากนักเรียนแถวแรกที่กรอก

## 2.2 ข้อมูลครู (14 คน)

`TH-Hub-App/data/teachers_master_2569.json` — สกัดจาก `apps/grade-r-memo/js/grade-r-data.js → TEACHERS` (อย่าพิมพ์รายชื่อใหม่)

```json
{ "no": 1, "name": "นายรามิล ปัญญพัทธ์", "position": "ครู", "standing": "ครูชำนาญการพิเศษ" }
```

- ครู = `<select>` เท่านั้น (แสดง `ชื่อ · วิทยฐานะ`) · `position` / `standing` = ช่อง **read-only** (`.is-locked`) ห้ามให้แก้
- เลือกครูแล้วตั้งผู้ลงนามให้อัตโนมัติ: `signerName = name` · `signerPos = "ครู" + (standing !== "-" ? " วิทยฐานะ" + standing : "")`
- `standing` เป็น `"-"` = ยังไม่มีวิทยฐานะ → ใส่สตริงว่าง อย่าพิมพ์ `ครู วิทยฐานะ-`
- **ไม่ต้องมีส่วน "ผู้ลงนาม" ในแผงกรอก** — ผู้ใช้ยืนยันว่าซ้ำซ้อน เพราะยึดตามครูที่เลือกอยู่แล้ว

## 4. รูปแบบช่องกรอกที่ใช้ซ้ำ (field `type` ต่อเทมเพลต)

| type | ใช้กับ | พฤติกรรม |
|---|---|---|
| `term` / `year` | ภาคเรียน · ปีการศึกษา | `<select>` แถวเดียวกัน · ค่าเริ่มต้น = ปัจจุบัน (`AcademicCalendar`) · ปีพื้น 2569 |
| `selectYears` | ปีที่ตกค้าง | ลิสต์ `year−1 … year−4` (แยกจาก `yearList()`), ค่าเริ่มต้น = ปีก่อน |
| `select` | ตัวเลือกสั้น (เช่น ภาคเรียนที่ตกค้าง) | ใช้ `options:[{v,t}]` ในนิยามเทมเพลต |
| `studentId` | รหัสนักเรียน 5 หลัก | lookup + สถานะ ✓/✗ + ล้าง autofill เมื่อไม่พบ |
| `studentInfo` | สรุปนักเรียน | `<div>` read-only: `ชื่อ · ชั้น ม.x/y` |
| `course` | วิชา | `<select>` 31 วิชา → เติมรหัส/ชื่อ/ระดับ |
| `teacher` | ครู | `<select>` 14 คน → เติมตำแหน่ง/วิทยฐานะ/ผู้ลงนาม |
| `locked` | ตำแหน่ง · วิทยฐานะ | `<input readOnly class="is-locked">` |
| `autoTotal` | ยอดรวมคะแนน | read-only + คำนวณจาก 4 ส่วนเมื่อมีการพิมพ์ |
| `consts` (ระดับเทมเพลต) | ค่าคงที่ของเอกสาร | ใส่ใน `state.data` ตอน reset ไม่เรนเดอร์เป็นช่องกรอก |

- ตารางหลายแถว: `total` ของแถวเป็น read-only + คำนวณใหม่ใน listener ของช่องคะแนน · `no` เติมลำดับให้อัตโนมัติ
- ทุกช่องต้องมี `id = 'f-' + key` และช่องในตารางมี `data-key` — ใช้ทั้งสำหรับการตรวจอัตโนมัติและการอัปเดตข้ามช่อง

**กับดักที่ทำให้ค่าหายเงียบ ๆ**

1. `yearList()` มีพื้น 2569 → ถ้าเอาลิสต์นี้ไปใช้กับ "ปีที่ตกค้าง" ค่าเริ่มต้น `year−1` จะไม่มีในลิสต์ แล้ว `<select>` เลือกตัวแรกเอง (ผิดปี) → ต้องมี `yearBackList()`
2. ยอดรวม: ต้องเรียกคำนวณใน listener เดียวกับที่เขียนค่า (`if (/^score(Before|Mid|After|Final)$/.test(key)) autoTotalExtra();`) — ผูกผิดที่แล้วตัวเลขว่างและหลุดลงเอกสาร (`รวมคะแนน .....`)

## 3. คลังฟอร์ม + D1 (เมื่อต้อง “เลิกใช้ฟอร์ม”)

ฟอร์ม 1 ฉบับกระจายอยู่ 6 ที่ — ลบไม่ครบ = ฟอร์มโผล่กลับมา:

1. `apps/<app>/index.html` → `OPTIONS` (dropdown) + `TEMPLATES` (นิยามฟอร์ม) + ฟังก์ชันเรนเดอร์/`docBlocks`
2. `data/forms/manifest.json` → `items[]` และปรับ `count` + `totalBytes`
3. `db/seeds/forms_library_seed.sql` → `INSERT INTO form_documents` (ถ้าไม่ลบ รัน seed ซ้ำแล้วฟื้นคืน)
4. **D1 `thai_hub_forms_db`** (id `2766a4ae-389b-473e-b1db-fb270fa45ee4`) — `form_fields` อ้าง FK ต้องลบก่อน:
   ```bash
   npx wrangler d1 execute thai_hub_forms_db --remote --command \
     "DELETE FROM form_fields WHERE document_id IN ('acad-form-12','acad-form-13');
      DELETE FROM form_documents WHERE id IN ('acad-form-12','acad-form-13');"
   ```
5. ไฟล์สำเนา `data/forms/<category>/*` (ต้นฉบับอยู่เว็บโรงเรียน — ลบสำเนาได้)
6. `data/apps_registry.json` → `description` ของแอปที่ยังพรรณนาถึงฟอร์มที่ถูกเลิกใช้

ตรวจหลังลบ: `SELECT c.id, COUNT(d.id) FROM form_categories c LEFT JOIN form_documents d ON d.category_id=c.id GROUP BY c.id`
ครั้งที่ยืนยันแล้ว: achievement 3 · exam-format 3 · curriculum 5 · academic-forms 4 = **15 ไฟล์**

## 4. เกณฑ์ตรวจรับของงานชนิดนี้

- เปิดแอปจริงด้วยเบราว์เซอร์ แล้ววัด ไม่ใช่เดา: จำนวน `<option>`, `getComputedStyle`, `getBoundingClientRect` (แถวเดียวกัน → `top` เท่ากัน), `document.fonts.check('16pt THSarabunNew')`
- ทดสอบ lookup ด้วยรหัสจริงจากไฟล์ (เช่น `27109`) **และรหัสที่ไม่มีอยู่** (เช่น `99999`)
- ดาวน์โหลด `.docx` จริงทุกเทมเพลต แล้วตรวจว่าเนื้อหา (ชื่อ/รหัส/ปี/ภาค) ติดไปครบ
- ทดสอบที่ 390px: `lostCount 0` · `smallPct 0` · `tinyText 0` · `bodyScrollW ≤ 392`
