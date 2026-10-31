---
name: thai-web-fonts
description: >
  Use when picking, downloading, self-hosting, subsetting or wiring Thai web fonts
  (ฟอนต์ไทย) into a site: Kanit, Prompt, Mitr, IBM Plex Sans Thai, LINE Seed Sans TH,
  TH Sarabun New, Sarabun, Anuphan, Taviraj, Trirong, Chonburi. Covers the Google Fonts
  woff2 API recipe, working mirrors for the two fonts Google does not host, TTF→woff2
  conversion with fontTools, @font-face generation with unicode-range + font-display,
  licence bookkeeping, and the verification that proves the font is really served.
---

# Thai Web Fonts — เก็บฟอนต์ไทยไว้ในโปรเจกต์เอง (self-host)

โหลดฟอนต์ไทยมาใช้บนเว็บแบบไม่พึ่ง CDN ภายนอก: ได้ subset ไทย+ลาตินแยกไฟล์, โหลดเฉพาะน้ำหนักที่ใช้จริง,
คุมสัญญาอนุญาตได้, และเรนเดอร์เหมือนกันทุกเครื่อง (โรงเรียน/บ้าน/มือถือ)

## เมื่อไหร่ควรใช้

- เว็บ/แอปไทยที่ต้องคุมหน้าตาตัวอักษรให้แน่นอน (dashboard, รายงานราชการ, เอกสาร export)
- ผู้ใช้บอกว่า "โหลดฟอนต์มาให้หมด" / "อยากเปลี่ยนฟอนต์ทั้งเว็บ"
- ต้องเลือกคู่ฟอนต์ให้ผู้ใช้ตัดสินใจ → ทำ **specimen PNG** ด้วยข้อความจริงของระบบก่อน (ดูข้อ 6)

## 1. Google Fonts: ดึง woff2 ตรง ๆ (9 ตระกูลที่เหลือ)

`fonts.googleapis.com/css2` คืน CSS ที่มี URL ของ woff2 แยก subset แล้ว — ขอด้วย User-Agent
ของ Chrome (ถ้าไม่ส่ง จะได้ ttf) แล้วแยกบล็อก `/* thai */` กับ `/* latin */` ออกมา

```python
api = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weights}&display=swap"
req = urllib.request.Request(api, headers={"User-Agent": UA_CHROME})
```

- เก็บชื่อไฟล์เป็น `<slug>-<weight>-<subset>.woff2` → `public/fonts/<slug>/`
- ต้องเก็บ `unicode-range` ไว้ใน CSS ปลายทาง ไม่งั้นเบราว์เซอร์จะโหลดไฟล์ไทยให้ข้อความอังกฤษ
- 9 ตระกูลที่ Google มี: Kanit, Prompt, Mitr, IBM Plex Sans Thai, Sarabun, Taviraj, Anuphan, Chonburi, Trirong
- ขนาดที่ควรได้ (subset ไทย, ต่อน้ำหนัก): Kanit ~13 KB, Sarabun ~10 KB, Anuphan ~18 KB

สคริปต์พร้อมใช้: `scripts/fetch-google-fonts.py <project-root>` (ได้ `manifest.json` ต่อให้ `font-tools.py make-css`)

## 2. LINE Seed Sans TH — ไม่มีบน Google Fonts

สิ่งที่ลองแล้ว **ไม่ work** (อย่าเสียเวลา):
- `line/seed` บน GitHub มีแต่ `LINESeedJP` — ไม่มีไฟล์ไทย
- `seed.line.me/seedth/download` ตอบ **403**
- ไม่มี npm package (`@fontsource/line-seed-*` ไม่มีตระกูลนี้)
- `boomNDS/new_portfolio/public/fonts/LINESeedSansTH_W_Rg.woff2` เป็น Git LFS pointer **162 ไบต์** — เช็คขนาดก่อนโหลด

ที่ work: mirror `https://typefaces.chanakancloud.net/LINESeedSansTH_W_{Rg,Bd,XBd}.woff2`
(มีแค่ 3 น้ำหนัก: Rg=400, Bd=700, XBd=800 · ไม่มี Lt/Md) — ตรวจ magic `wOF2` ทุกไฟล์ก่อนใช้

## 3. TH Sarabun New — ฟอนต์แห่งชาติ เอามาจากเครื่อง Windows

เครื่องไทยส่วนใหญ่ติดตั้งไว้แล้วที่ `C:\Windows\Fonts\THSarabunNew.ttf` และ `THSarabunNew Bold.ttf`
→ แปลงเป็น woff2 (462 KB → 120 KB, 352 KB → 96 KB)

```python
from fontTools.ttLib import TTFont
f = TTFont(src); f.flavor = "woff2"; f.save(dst)
```

- TTF ที่โหลดจาก repo มือสองมักพัง: ไฟล์ขึ้นต้นด้วย `\n\n\n\n` และ **ไม่มี** `\x00\x01\x00\x00`
  → ถ้า `data.find(b"\x00\x01\x00\x00") == -1` ให้ทิ้งทันที
- ใช้คู่กับ `Sarabun` (Google) เมื่ออยากได้เวอร์ชันเว็บของสายราชการ
- ต้องมี `fonttools` + `brotli` (woff2 ต้องใช้ brotli)

สคริปต์พร้อมใช้: `scripts/font-tools.py ttf2woff2 <src.ttf> <dst.woff2>`

## 4. สร้าง @font-face

ไฟล์เดียว `src/app/fonts.css` — 69 faces สำหรับ 11 ตระกูล คือขนาดที่คุมได้ (21 KB)
ทุก face ต้องมี `font-display: swap` และ `unicode-range` (ถ้ามี)

```css
@font-face {
  font-family: "Kanit";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("/fonts/kanit/kanit-400-thai.woff2") format("woff2");
  unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC;
}
```

Next.js: `@import "./fonts.css";` **หลัง** `@import "tailwindcss";` ใน `globals.css`
— `@font-face` เฉย ๆ ไม่ดาวน์โหลดไฟล์จนกว่าจะมี element ใช้ตระกูลนั้น (ต้นทุนตอนยังไม่ใช้ ≈ 21 KB CSS)

## 5. ตรวจว่าใช้งานได้จริง (ห้ามเดา)

```bash
curl -s -o f.woff2 -w '%{http_code}\n' "https://<host>/fonts/kanit/kanit-400-thai.woff2"
head -c 4 f.woff2      # ต้องได้ wOF2
curl -sI ... | grep -i content-type   # ต้องได้ font/woff2
```

⚠️ `curl -w '%{size_download}'` ใน loop อาจรายงาน `0` แม้ไฟล์มาครบ — **วัดจากไฟล์ที่เซฟลงดิสก์** (`ls -l`, `head -c 4`)

ตรวจไฟล์ที่ได้จากทุกแหล่ง: `scripts/font-tools.py check public/fonts/**/*.woff2`

ในเบราว์เซอร์: `getComputedStyle(document.querySelector('h1')).fontFamily` และ
`getComputedStyle(input, '::placeholder').fontSize` เมื่ออยากเช็ก placeholder แยกจากตัว input

## 6. ให้ผู้ใช้เลือกฟอนต์ (specimen)

ผู้ใช้ไทยตัดสินจากภาพ ไม่ใช่ชื่อฟอนต์ → สร้าง HTML หน้าเดียวที่จัดกลุ่มตามการใช้งาน
(Sans หัวข้อ / Body อ่านยาว / Serif–แบรนด์) แล้วเรนเดอร์เป็น PNG

```bash
chrome --headless=new --hide-scrollbars --virtual-time-budget=4000 \
  --window-size=1180,2200 --screenshot=specimen.png "file:///C:/path/type-specimen.html"
```

- ใส่ `@font-face` ชี้ไฟล์ในโปรเจกต์ด้วย path relative — headless โหลด `file://` ได้
  (ต้องวาง HTML ไว้**ใน** repo เพื่อให้ relative path ไปถึง `public/fonts`)
- แต่ละแถว: ชื่อฟอนต์ + ตัวอย่างหัวข้อ 26px + ตัวอย่างเนื้อหา 15px + โน้ตสั้น ๆ ว่าเหมาะกับอะไร

## 7. คู่ฟอนต์ที่แนะนำสำหรับงานโรงเรียน/ราชการสมัยใหม่

| งาน | แนะนำ | เหตุผล |
|---|---|---|
| หัวข้อ + ตัวเลข dashboard | **Kanit 500/600** | ตัวเลขคม อ่านจากไกลได้ |
| เนื้อหา/ตารางยาว | **Anuphan 400** | ออกแบบเพื่อหน้าจอ ตัวโปร่ง |
| รู้สึกเป็นทางการ/คุ้นตา | **TH Sarabun New** | ตรงกับไฟล์ Word ที่ export |
| เป็นมิตร/มือถือ | **LINE Seed Sans TH** | ทรงมน |
| พรีเมียม | Trirong (หัวข้อ) + Anuphan (เนื้อหา) | Serif ไทยมีหัว |
| แบรนด์/แบนเนอร์เท่านั้น | Chonburi | เอกลักษณ์แรง ใช้ยาวจะล้า |

## 8. บันทึกสัญญาอนุญาตเสมอ

สร้าง `public/fonts/SOURCES.md` ระบุ: ตระกูล, ที่มา, สัญญาอนุญาต (Google/LINE = SIL OFL 1.1,
TH Sarabun New = ฟอนต์แห่งชาติแจกฟรี), และวิธีที่มาของแต่ละไฟล์ — กันคนอื่นในทีมเผลอเอาไปใช้ผิด

## กับดักบน Windows (เจอจริงทุกครั้ง)

- `python` ในเชลล์ Hermes คือ venv ที่**ไม่มี pip** → ติดตั้ง/รันสคริปต์ที่ต้องใช้ lib ให้เรียก
  `C:/Python314/python -m pip install ...` แล้วรันด้วย `C:/Python314/python`
- `/tmp/...` มองไม่เห็นจากโปรแกรม native → ใช้ `$LOCALAPPDATA/hermes/cache/scratch/...`
- `curl -o /dev/null` รวมกับ loop อาจทำให้ `size_download` เพี้ยน — เขียนลงไฟล์แล้ววัด
