# พรีวิวหน้า A4 จริง + การแบ่งหน้า (browser pagination)

ใช้เมื่อหน้าพรีวิวต้อง "เห็นขนาดจริง" เป็นหน้ากระดาษ A4 และเอกสารยาวต้องขึ้นหน้าใหม่ให้เห็นชัด
(ทดสอบกับ `apps/smart-form-filler` — 51 แถว → 3 หน้า 17/20/14 แถว, หัวตารางซ้ำทุกหน้า, ไม่มีเนื้อหาล้น)

## 1. เรขาคณิต (ค่าตายตัว)

| ค่า | ขนาด |
|---|---|
| หน้ากระดาษ | `794 × 1123 px` (A4 @96dpi) |
| ระยะขอบในหน้า | `padding: 48px 76px` (บน/ล่าง 1.27 ซม. · ซ้าย/ขวา 0.8 นิ้ว) |
| ความสูงเนื้อหาต่อหน้า | `1123 − 48×2 = 1027 px` → `CONTENT_H` |
| ความกว้างเนื้อหา | `794 − 76×2 = 642 px` |

```css
.a4-pages { display:flex; flex-direction:column; align-items:center; gap:44px; padding:32px 0 8px; }
.a4-page  { width:794px; min-height:1123px; padding:48px 76px; position:relative; box-sizing:border-box; background:#fff; }
.a4-page .page-body { width:100%; height:1027px; overflow:hidden; }
```

`padding-top` ที่ wrapper จำเป็น — ป้ายเลขหน้าวางที่ `top:-27px` ของหน้า ถ้าไม่มีที่ว่างจะถูก `.a4-scale-wrapper{overflow:hidden}` ตัดหาย

## 2. วัดความสูงด้วย "หน้าเปล่า" นอกจอ (สำคัญ)

```css
.a4-page.page-stage { position:absolute; left:-99999px; top:0; box-shadow:none; }
.a4-page.page-stage .page-body { height:auto !important; overflow:visible !important; }
```

- **ต้องมี override `height:auto; overflow:visible` สำหรับ stage** ไม่งั้น `scrollHeight` จะคืนค่าเท่า `clientHeight` (1027) เสมอ แล้ววัดไม่ได้เลย
- **stage ต้องได้ class scale เดียวกับหน้าแสดงผล** (`doc-compact` / `doc-wide`) เพราะขนาดฟอนต์มาจาก CSS var ที่ประกาศบน `.a4-pages.doc-compact, .a4-stage.doc-compact` — ถ้า stage ไม่ได้ class นี้ ตัววัดจะเรนเดอร์ 16pt แต่ของจริง 14pt → แบ่งหน้าผิดทั้งฉบับ

## 3. อัลกอริทึม

```js
var CONTENT_H = 1123 - 48 * 2;
// stage = <div class="a4-stage <scaleClass>" style="position:absolute;left:-99999px;top:0;width:794px">
nodes.forEach(function (node) {          // เฉพาะ element ลูกชั้นบนสุดของเอกสาร
  body.appendChild(node.cloneNode(true));
  if (used() <= CONTENT_H) return;      // used() = body.scrollHeight
  body.removeChild(body.lastChild);
  if (!body.children.length) {          // บล็อกแรกของหน้าใหญ่เกินเต็มหน้า
    if (node.tagName === 'TABLE') placeTable(node); else body.appendChild(node.cloneNode(true));
    return;
  }
  if (node.tagName === 'TABLE') placeTable(node);   // ตาราง: เติมต่อในหน้าเดิมก่อน
  else { newPage(); body.appendChild(node.cloneNode(true)); }
});
```

**ตารางต้องเติมต่อในหน้าเดิม ไม่ใช่ย้ายทั้งตารางไปหน้าใหม่** — ถ้าย้าย หน้าแรกจะมีแต่หัวเอกสารแล้วเหลือที่ว่างเปล่าค่อนหน้า

```js
function placeTable(tableNode) {
  var thead = tableNode.querySelector('thead');
  var rows = [].slice.call(tableNode.querySelectorAll('tbody tr'));
  var idx = 0;
  while (idx < rows.length) {
    var t = tableNode.cloneNode(false);            // โครงตารางเดิม
    if (thead) t.appendChild(thead.cloneNode(true)); // หัวตารางซ้ำทุกหน้า
    var tbody = document.createElement('tbody'); t.appendChild(tbody); body.appendChild(t);
    var added = 0;
    while (idx < rows.length) {
      tbody.appendChild(rows[idx].cloneNode(true));
      if (used() > CONTENT_H) {
        if (added === 0) { idx++; added++; break; }   // แถวเดียวยังสูงเกินหน้า → ปล่อย กันข้อมูลหาย
        tbody.removeChild(tbody.lastChild); break;
      }
      idx++; added++;
    }
    if (idx < rows.length) newPage();
  }
}
```

## 4. ป้ายบอกหน้า (เห็นชัด ไม่พิมพ์ออก)

```css
.page-chip { position:absolute; top:-27px; left:0; right:0; display:flex; align-items:center; gap:10px; font:700 11px 'Prompt',sans-serif; color:var(--wine); }
.page-chip i { font-style:normal; background:#fff; border:1px solid rgba(131,24,67,.32); border-radius:999px; padding:3px 10px; }
.page-chip span { flex:1; border-top:1.5px dashed rgba(131,24,67,.45); }
```

เนื้อหา: `หน้า {i} / {total}` — ใส่ `<i>` + `<span>`(เส้นประ) เข้าไปในทุก `.a4-page` หลังแบ่งหน้าเสร็จ

## 5. การพิมพ์ — หนึ่งหน้า = หนึ่งกระดาษ

```css
@media print {
  .page-chip { display:none !important; }
  .a4-pages { display:block !important; gap:0 !important; }
  .a4-page { width:100% !important; height:297mm !important; min-height:0 !important;
             padding:12.7mm 20mm !important; margin:0 !important; box-shadow:none !important;
             break-after: page; page-break-after: always; }
  .a4-page:last-child { break-after:auto; page-break-after:auto; }
  .a4-page .page-body { height:271.6mm !important; overflow:hidden !important; }
  @page { size: A4 portrait; margin: 0; }
}
```

**`@page margin` ต้องเป็น 0** เพราะระยะขอบย้ายไปอยู่ใน `padding` ของ `.a4-page` แล้ว — ใส่ทั้งสองที่จะทับกันจนเนื้อหาล้นแผ่น
`1027px = 271.6mm` ทำให้สัดส่วนจอ ↔ กระดาษตรงกันพอดี

## 6. Performance — ห้าม re-paginate ทุกคีย์สโตว์

การแบ่งหน้าคือการ clone DOM ทั้งเอกสาร ถ้าเรียกทุก `input`/ทุกคลิก "เพิ่มแถว" จะเป็น O(n²):

```js
var sheetTimer = null;
function scheduleSheet() {
  if (sheetTimer) return;
  sheetTimer = setTimeout(function () { sheetTimer = null; renderSheet(); }, 90);
}
```

- ใช้ `scheduleSheet()` ในทุก listener ของช่องกรอก/เพิ่ม-ลบแถว
- เรียก `renderSheet()` ตรง ๆ เฉพาะตอนเปลี่ยนเทมเพลต, reset, หรือเปลี่ยน dropdown ที่ต้องเห็นผลทันที
- อาการที่จะเจอถ้าไม่ทำ: เพิ่มแถวรัว ๆ 40 ครั้งแล้วสคริปต์วัด/ทดสอบ timeout (การคลิก 44 ครั้งใช้เกิน 5 วินาที)

## 7. Pitfalls

- **อย่าลืมคง class `a4-sheet` ที่ wrapper** — `MobileKit.applySheetScale()` หา `.a4-sheet` เพื่อย่อหน้าจอมือถือ ถ้าเปลี่ยนชื่อคลาส มือถือจะล้นจอ
- CSS ของแอปมักมี `.a4-sheet div { margin: 0 }` (specificity 0,1,1) ทับคลาสเดี่ยว (0,1,0) → กฎจัดตำแหน่งต้องเขียนเป็น `.a4-pages .doc-sign { … }`
- การวัดต้องทำหลังฟอนต์พร้อม; ถ้าเพิ่งเปลี่ยน `@font-face` ให้วัดซ้ำหลัง `document.fonts.ready`
- เขียนทับไฟล์แอป HTML ไฟล์เดียวที่ใหญ่ ๆ ด้วย `write_file` จะถูกปฏิเสธถ้าเพิ่งอ่านแบบมี offset/limit — เขียนเป็นไฟล์ชื่อใหม่แล้ว `mv -f` ทับ หรืออ่านครั้งเดียวด้วย `offset=1, limit≥จำนวนบรรทัด`

## 8. เกณฑ์ตรวจรับ (วัดจริง ไม่ใช่ดูด้วยตา)

```js
// จำนวนหน้า + ความสูงจริง
[...document.querySelectorAll('.a4-page')].map(p => Math.round(p.getBoundingClientRect().height))  // ทุกหน้าต้อง = 1123
[...document.querySelectorAll('.a4-page .page-body')].map(b => b.scrollHeight - b.clientHeight)      // ทุกหน้าต้อง = 0
[...document.querySelectorAll('.a4-page')].map(p => p.querySelectorAll('thead').length)              // หน้าที่มีตารางต้องมี thead
[...document.querySelectorAll('.page-chip')].map(c => c.innerText.trim())                           // "หน้า 1 / N" … ครบ N
```

โหมดพิมพ์ (`Emulation.setEmulatedMedia media=print`): `.page-chip` ต้อง `display:none` และ `.a4-page` ต้อง `break-after: page`
