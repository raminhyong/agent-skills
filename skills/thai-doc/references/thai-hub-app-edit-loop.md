# วงจรแก้–ตรวจ–ดีพลอยสำหรับแอปใน Thai PW Hub

แอปส่วนใหญ่เป็นไฟล์เดียว (`apps/<app>/index.html`) ที่มี inline `<script>` ยาว ๆ การแก้ทีละนิดจึงพลาดง่ายและตรวจลำบาก ใช้ลำดับนี้ทุกครั้ง:

## 1. แก้ → ตรวจ syntax ก่อนดีพลอย (ทุกครั้ง)

```bash
cd C:/Users/patti/repos/TH-Hub-App && node -e "
const fs=require('fs');const h=fs.readFileSync('apps/smart-form-filler/index.html','utf8');
const m=[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)];
const inline=m.filter(x=>x[1].includes('Thai Smart Form Filler'));
try{new Function(inline[0][1]);console.log('SYNTAX OK')}catch(e){console.log('ERR:',e.message)}
"
```

`new Function` จับ syntax error ที่เกิดจาก patch สตริงยาว ๆ ได้ก่อนขึ้นเว็บ (เจอจริงบ่อย: เครื่องหมายคำพูด/วงเล็บที่ patch ทำเพี้ยน)

## 2. เขียนทับไฟล์ใหญ่เมื่อ write_file ปฏิเสธ

ถ้า `write_file` ไม่ยอมทับเพราะไฟล์ถูกอ่านแบบแบ่งหน้า (หรือแก้ด้วย patch หลายรอบจนไม่ตรงกับที่อ่านไว้) **อย่าเสียเวลาอ่านใหม่ทั้งไฟล์** — เขียนเนื้อหาใหม่ลงไฟล์ข้าง ๆ แล้วย้ายทับ:

```bash
# write_file → apps/<app>/index_v5.html  แล้ว
cd apps/<app> && mv -f index_v5.html index.html
```

จากนั้นรันข้อ 1 ทันที

## 3. ดีพลอยขึ้น preview ก่อน ไม่ทับ production

```bash
cd C:/Users/patti/repos/TH-Hub-App && npx --no-install wrangler pages deploy . --project-name=thai-hub --branch=mobile --commit-dirty=true
# ตรวจที่ https://mobile.thai-hub.pages.dev/apps/<app>/
```

ตรวจผ่านแล้วค่อย:

```bash
npx --no-install wrangler pages deploy . --project-name=thai-hub --branch=main --commit-dirty=true
git add -A && git commit -q -m "..." && git push -q origin main && git push -q origin main:dev
```

main กับ dev ต้อง push คู่กันเสมอ (repo นี้ใช้สองแบรนช์เป็นตัวเดียวกัน)

## 4. ตรวจด้วยการวัด ไม่ใช่ดูด้วยตา

```python
cdp("Network.setCacheDisabled", cacheDisabled=True)
cdp("Emulation.setDeviceMetricsOverride", width=1500, height=1150, deviceScaleFactor=1, mobile=False)
goto_url(url + "?v=" + unique)   # ใส่ query กัน cache
```

ค่าที่ต้องอ่านจริงต่อการเปลี่ยนหนึ่งครั้ง: จำนวน `<option>` · `getComputedStyle(el).fontSize/height/marginLeft` · `el.getBoundingClientRect()` เทียบ `pageBody.getBoundingClientRect()` · `document.fonts.check('16pt THSarabunNew')` · จำนวน `.a4-page` และ `scrollHeight - clientHeight` ของ `.page-body`

ทดสอบ input: ยิง event เองแล้วอ่าน state ที่สะท้อนออกมา เช่น
```js
const e = document.getElementById('f-studentId');
e.value='27109'; e.dispatchEvent(new Event('input',{bubbles:true}));
```

## 5. ตรวจไฟล์ .docx ที่ผู้ใช้จะได้จริง

```python
cdp("Page.setDownloadBehavior", behavior="allow", downloadPath=r".../scratch/dl")
js("document.getElementById('btn-docx-2').click()")
# รอไฟล์ไม่ให้เหลือ .crdownload แล้ว
```

```bash
py -3.12 "$HOME/AppData/Local/hermes/skills/productivity/thai-doc/scripts/verify_thai_docx.py" *.docx --render
```

แล้วเปิด PNG ที่เรนเดอร์ด้วยตา — สคริปต์บอกได้แค่ฟอนต์/spacing ไม่บอกว่ากล่องความเห็นว่างหรือตารางล้น

## 6. กับดักประสิทธิภา��

- **ทุก `input` ที่เรียก render ใหม่ ต้อง debounce ~90ms** เพราะการเรนเดอร์หนึ่งครั้ง = แบ่งหน้า A4 ใหม่ทั้งเอกสาร ถ้าไม่ debounce การเพิ่ม 40 แถวรัว ๆ จะค้างจน CDP `Runtime.evaluate` timeout (5 วิ)
- การเพิ่ม/ลบแถวให้ rebuild เฉพาะ `#rows-editor` แล้วค่อย debounce การแบ่งหน้า — อย่า rebuild ทั้งหน้าในลูป
- ลูปทดสอบที่ต้องคลิกหลายสิบครั้ง ให้แบ่งเป็น batch ละ ~10 ครั้ง + `sleep(0.4)` ระหว่าง batch
