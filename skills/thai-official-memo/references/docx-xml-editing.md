# แก้/ตรวจ `word/document.xml` ในไฟล์ .docx โดยตรง

ใช้เมื่อ (ก) เอกสารออกมาจาก **เทมเพลต** `.docx` (PizZip / docxtemplater) ซึ่งระยะบรรทัดอยู่ในเทมเพลต
ไม่ใช่ใน JS หรือ (ข) ต้อง **ตรวจไฟล์จริง** ที่ผู้ใช้จะได้รับ ว่า spacing ถูกต้อง

## 1. สกัดข้อความย่อหน้าให้ถูก

```python
W_T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
text = "".join(W_T.findall(p_xml)).replace("\u200b", "").strip()
```

ต้องใช้ฟอร์มเข้ม `<w:t(?:\s[^>]*)?>` เท่านั้น — `<w:t[^>]*>` จะไปโดน `<w:tab/>`, `<w:tbl>`, `<w:tc>`,
`<w:tr>`, `<w:top .../>` (ใน `<w:pBdr>`) ทำให้ "ข้อความ" ที่ได้กลายเป็นกองแท็ก ย่อหน้าจริงจึงหาไม่เจอ
หรือถูกจับผิดย่อหน้า อาการที่เจอ: หา `จึงเรียนมาเพื่อ...` ไม่พบทั้งที่ย่อหน้ามีอยู่ และค่าที่พิมพ์ออกมา
เป็น `'</w:r><w:proofErr w:type="spellStart"/>...'`

## 2. เขียน zip กลับแบบรักษาไฟล์อื่นทั้งหมด

```python
with zipfile.ZipFile(path) as z:
    items = [(i, z.read(i.filename)) for i in z.infolist()]
# แทนเฉพาะ entry 'word/document.xml' แล้วเขียนใหม่ทั้งชุด
zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
zi.compress_type = zipfile.ZIP_DEFLATED
```

ห้ามสร้าง zip ใหม่จากรายการไฟล์บางส่วน — `.docx` ต้องมี `[Content_Types].xml`, `_rels/.rels`,
`word/_rels/document.xml.rels`, `word/media/*` ครบ ไม่งั้น Word เปิดไม่ขึ้น

## 3. บวก spacing ของย่อหน้าเป้าหมาย

- ย่อหน้า = `<w:p ...>...</w:p>`; เลือกด้วยข้อความ (`startswith('เรียน')`, `startswith('จึงเรียนมาเพื่อ')`)
- ถ้ามี `<w:spacing .../>` อยู่แล้ว → **บวกเพิ่ม** ค่า `w:before` / `w:after` (ถ้าไม่มี attribute นั้นให้เพิ่มเข้าไป)
- ถ้าไม่มี → ใส่ `<w:spacing w:before="N" w:after="M"/>` เป็นลูกแรกของ `<w:pPr>` (ถ้าไม่มี `<w:pPr>` ให้สร้าง)
- แก้จาก match **สุดท้ายย้อนไปแรก** เพื่อไม่ให้ offset เพี้ยน

**หน่วย:** 96 dpi → 1px = 15 twips, 8px = 120 twips = 6pt. และ **ย่อหน้าว่างใน Word ไม่ใช่ 8px**
เพราะมันสูงเท่า line-height ของฟอนต์ (16pt ≈ 21px) — ต้องใช้ `w:spacing` ไม่ใช่ `<w:p/>` ว่าง

## 4. เอาไฟล์ที่ผู้ใช้จะได้จริงออกมา แม้ปุ่ม Export ถูก gate ด้วยฟอร์ม

เมื่อปุ่มดาวน์โหลดซ่อนจนกว่าจะกรอก/เลือnข้อมูลครบ ให้เรียกตัวสร้างที่หน้าเว็บ expose ไว้แล้วดาวน์โหลด Blob:

```js
// ตั้งโฟลเดอร์รับดาวน์โหลดก่อน: cdp('Browser.setDownloadBehavior', behavior='allow', downloadPath=<scratch>)
const blob = await window.MEMO_DOCX_BUILDER.buildMemoDocx({ semester: '1', year: '2569', roster: [], officials: {} });
const a = document.createElement('a');
a.href = URL.createObjectURL(blob); a.download = 'verify.docx';
document.body.appendChild(a); a.click(); a.remove();
```

ทางเลือกสำรองอีกทาง: คลิกปุ่มจริงหลัง `Browser.setDownloadBehavior` แล้วรอไฟล์ปรากฏในโฟลเดอร์
(ใช้ได้เมื่อปุ่มไม่ถูกซ่อน) — ทั้งสองทางได้ไฟล์เดียวกับที่ครูจะเปิดใน Word

## 5. ตรวจและรายงาน

- พิมพ์ **ข้อความย่อหน้า + spacing ที่อ่านได้** คู่กันทุกครั้ง เพื่อให้เห็นทันทีว่าจับผิดย่อหน้าหรือไม่
- ต้องได้ค่าที่คาดหวังตรงตัว (`before="120"` หรือ ค่าเดิม+120) ไม่ใช่ "น่าจะถูก"
- ตรวจ `w:before` **และ** `w:after` ของย่อหน้า `เรียน` (ต้องมีทั้งคู่) และ `w:before` ของย่อหน้าลงท้าย
