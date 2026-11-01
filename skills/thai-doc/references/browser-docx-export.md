# สร้าง .docx ฝั่งเบราว์เซอร์ (JSZip + OOXML เอง)

ใช้เมื่อหน้าเว็บต้องให้ผู้ใช้ "ดาวน์โหลด Word" ต่อจากพรีวิว A4 — เช่นระบบกรอกฟอร์มอัจฉริยะที่ไม่มีเซิร์ฟเวอร์/Worker สร้างไฟล์
ไม่ต้องใช้ CDN ของไลบรารี docx.js ทั้งก้อน: เขียน OOXML เองแล้ว zip ด้วย JSZip (~100KB, โหลดได้จาก `https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js`)

## 1) โครงแพ็กเกจขั้นต่ำ (พอให้ Word เปิดได้)

```
[Content_Types].xml
docProps/core.xml
_rels/.rels
word/document.xml
word/styles.xml
word/_rels/document.xml.rels
```

- `[Content_Types].xml`: Default `rels` + `xml` และ Override ของ `word/document.xml`, `word/styles.xml`, `docProps/core.xml`
- `_rels/.rels`: rId1 → officeDocument (word/document.xml), rId2 → core-properties
- `word/_rels/document.xml.rels`: rId1 → styles.xml (**ลืมไฟล์นี้ = Word ฟ้องไฟล์เสีย**)
- `styles.xml` ต้องมี `w:docDefaults` ครบ 4 script (`ascii`,`hAnsi`,`cs`,`eastAsia`) + `w:sz 32` + `w:lang th-TH` + pPrDefault `spacing before=0 after=0 line=240 lineRule=auto` ไม่งั้นย่อหน้าว่างจะกลับไปเป็น Calibri

```bash
zip.generateAsync({ type:'blob', mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document', compression:'DEFLATE' })
```

## 2) sectPr (A4 + ระยะขอบแบบฟอร์ม)

```xml
<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>
<w:pgMar w:top="720" w:right="1152" w:bottom="720" w:left="1152" w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>
```

พื้นที่พิมพ์กว้าง = `11906 − 1152×2 = 9602` twips — ใช้เป็นฐานคำนวณความกว้างคอลัมน์

## 3) Run / Paragraph

```js
// ทุก run ต้องมี rFonts 4 script + noProof + lang th-TH + sz/szCs
'<w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New" w:eastAsia="TH Sarabun New"/>'
 + (bold?'<w:b/><w:bCs/>':'') + (italic?'<w:i/>':'')
 + '<w:noProof/><w:sz w:val="32"/><w:szCs w:val="32"/><w:lang w:val="th-TH"/></w:rPr>'
 + '<w:t xml:space="preserve">…</w:t></w:r>'
```

- ย่อหน้าปกติ: `spacing before=0 after=0 line=240 lineRule=auto` ·เยื้องบรรทัดแรก `w:ind firstLine="720"` · จัดกึ่งกลาง `w:jc center`
- เส้นคั่นแนวนอนใต้หัวเรื่อง: ย่อหน้าว่าง + `<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>`
- ขนาดต่อเทมเพลต: ชุดกระชับ (ตาราง ≥8 คอลัมน์) `sz 28 / th 24 / td 22` · ชุดปกติ `sz 32 / th 28 / td 26` · ชื่อเรื่อง `sz 36`

### 3.1 บรรทัดเปล่า 8px ใน Word = `w:before="120"` ของย่อหน้าถัดไป

```xml
<w:p><w:pPr><w:spacing w:before="120" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>…เนื้อหา…</w:p>
```

ใส่ที่ **ย่อหน้าถัดจากช่องว่าง** 3 จุดของบันทึกข้อความ: ย่อหน้า `เรียน` · ย่อหน้าเนื้อความแรกหลัง `เรียน` · ย่อหน้า `จึงเรียนมาเพื่อ`
**ห้าม**ทำเป็นย่อหน้าว่างลอย (`<w:br/>` / ย่อหน้าว่าง `after=120`) — ครูลบพลาด, กินพื้นที่กระดาษ, และจำนวนหน้าเปลี่ยน
ตรวจรับ: `grep -c 'w:before="120"' document.xml` ต้องได้ **3**

## 4) ตาราง

```xml
<w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblLayout w:type="fixed"/>
  <w:tblBorders>…6 เส้น single sz=6 color=000000…</w:tblBorders>
  <w:tblCellMar>top/bottom 60 · left/right 80</w:tblCellMar></w:tblPr>
<w:tblGrid><w:gridCol w:w="…"/>…</w:tblGrid>
<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>…
```

- แถวหัวต้องมีทั้ง `cantSplit` + `tblHeader`; แถวข้อมูลทุกแถว `cantSplit`
- หลัง `</w:tbl>` ต้องมี `<w:p>` ว่างเสมอ (Word บังคับ ไม่งั้นย่อหน้าถัดไปเกาะตาราง)
- **ความกว้างคอลัมน์ต้องมาจากชุดตัวเลข % ชุดเดียวกับพรีวิว HTML** (`<colgroup><col style="width:8%">` คู่กับ `gridCol = round(9602*pct/100)`) ไม่งั้นไฟล์ Word กับพรีวิวเรียงคอลัมน์ไม่ตรงกัน

### 4.1 องค์ประกอบเฉพาะบันทึกข้อความ (อย่าสร้างเป็นกล่อง)

| องค์ประกอบ | OOXML ที่ใช้ | ห้าม |
|---|---|---|
| แถว `ที่ … / วันที่ …` | ตาราง **ไร้เส้น** 2 คอลัมน์ 5600 / 4002 twips (วันที่เริ่ม 58%) | ตารางมีเส้น, ใช้ช่องว่างเคาะเอา |
| ช่องลงนาม | ย่อหน้า `w:ind w:left="3600"` + `w:jc center` 3 บรรทัด (ลงชื่อ/ชื่อ/ตำแหน่ง) | `<w:jc center>` กลางหน้ากระดาษ |
| ช่องความเห็น–อนุมัติ (หัวหน้างานวิจัย/รอง ผอ./ผอ.) | ย่อหน้าธรรมดา + หัวข้อ bold + ติ๊กถูก + บรรทัดลงชื่อเยื้องขวา | กรอบ/ตาราง 1 ช่อง (ผู้ใช้สั่งห้าม) |
| เชิงอรรถ/เครดิตที่ระบบสร้าง | ไม่มี | ข้อความ `* สร้างจากระบบ…` |

## 5) พิษที่เจอจริง

1. **`runXml(undefined)` คืน `''` เงียบ ๆ** → กล่อง/บรรทัดที่มีแต่ `{text:...}` (ไม่มี `runs`) ออกมาเปล่าใน Word แต่ HTML ยังถูก ต้อง normalize: `const runs = typeof ln === 'string' ? [{text:ln}] : (ln.runs || [{text: ln.text || ''}])`
2. **`line 240 auto` ของ Word ≠ `line-height: 1.0` ของ CSS** — Word คิดความสูงบรรทัดตามฟอนต์จริง (~1.15–1.2) ถ้าตั้ง CSS 1.0 ตัวอักษรไทยจะเบียดกันบนจอ ให้ CSS ใช้ `1.15–1.2` แต่ DOCX คง `line 240`
3. **หัวตารางที่ไม่มีช่องว่าง** (เช่น `แนวทางแก้ไข`) ตัดบรรทัดไม่ได้ใน `table-layout: fixed` → ใส่ `overflow-wrap:anywhere; word-break:break-word` ที่ `th, td`
4. `table-layout: fixed` + `col` ที่รวมกันเกิน 100% จะดันคอลัมน์สุดท้ายล้นออกนอกขอบแผ่น — ตรวจด้วย `table.scrollWidth - table.clientWidth === 0`
5. ตัวอักษรไทยตัดคำกลางคำได้ (Word และ CSS `anywhere`) — ถ้าหัวคอลัมน์สั้นเกินไปให้เพิ่ม % คอลัมน์นั้น ไม่ใช่ลดฟอนต์ทั้งตาราง
6. **`.a4-sheet div { margin: 0 }` ทับ `margin-left` ของช่องลงนาม** (specificity 0,1,1 ชนะ 0,1,0) → เขียนเป็น `.a4-sheet .doc-sign { margin-left: 55% }` ไม่งั้นพรีวิวกับ Word ไม่ตรงกัน (Word เยื้องถูก แต่จอชิดซ้าย)

## 6) ตรวจไฟล์ที่ดาวน์โหลดออกมาจริง

```js
cdp('Page.setDownloadBehavior', behavior='allow', downloadPath=dl)   // ในเบราว์เซอร์อัตโนมัติ
// คลิกปุ่ม แล้ว poll ไฟล์ที่ไม่ลงท้าย .crdownload
```

```bash
py -3.12 <skill>/scripts/verify_thai_docx.py "ไฟล์.docx" --render
```

- สคริปต์ตรวจฟอนต์/เลขไทย/ZWSP และ render PNG ผ่าน Word COM — **ต้องดู PNG เอง** เพราะโครงสร้างผ่านแต่เนื้อหาอาจหาย (เคสกล่องเปล่าในข้อ 5.1)
- ตรวจซ้ำทุกเทมเพลตที่รองรับ ไม่ใช่แค่ตัวแรก: จำนวน `<w:tbl>`, จำนวนแถว, กล่องความเห็น, และบรรทัดลงชื่อ
- เช็คด้วย regex เพิ่มเติมได้เร็ว: `w:before="120"` = 3 · `w:left="3600"` = 3 × จำนวนช่องลงนาม · ไม่มี `สร้างจากระบบ` ในเอกสาร
