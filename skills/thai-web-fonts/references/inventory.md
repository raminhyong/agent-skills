# Thai Web Font Inventory — 11 ตระกูลที่ทดสอบแล้ว

อัปเดต: 31 ต.ค. 2026 · ทดสอบบน Windows 11 + Chrome 131 + Next.js 15 / OpenNext บน Cloudflare Workers

| ตระกูล | น้ำหนักที่ใช้ | ที่มา | สัญญาอนุญาต | ขนาดไทย/น้ำหนัก |
|---|---|---|---|---|
| Kanit | 400 500 600 700 | Google Fonts | OFL 1.1 | ~13 KB |
| Prompt | 400 500 600 700 | Google Fonts | OFL 1.1 | ~13 KB |
| Mitr | 400 500 600 | Google Fonts | OFL 1.1 | ~14 KB |
| IBM Plex Sans Thai | 400 500 600 700 | Google Fonts | OFL 1.1 | ~12 KB |
| Sarabun | 400 500 600 700 | Google Fonts | OFL 1.1 | ~10 KB |
| Anuphan | 400 500 600 700 | Google Fonts | OFL 1.1 | ~18 KB |
| Taviraj | 400 500 600 700 | Google Fonts | OFL 1.1 | ~16 KB |
| Trirong | 400 500 600 700 | Google Fonts | OFL 1.1 | ~16 KB |
| Chonburi | 400 | Google Fonts | OFL 1.1 | ~10 KB |
| LINE Seed Sans TH | 400 (Rg) 700 (Bd) 800 (XBd) | `typefaces.chanakancloud.net` (mirror) | OFL 1.1 (LINE Corp.) | ~30 KB ต่อไฟล์ |
| TH Sarabun New | 400 700 | `C:\Windows\Fonts` (ฟอนต์แห่งชาติ) | แจกฟรี (SIPA) | 120 KB / 96 KB (woff2) |

รวมทั้งชุด (ไทย+ลาติน ทุกน้ำหนัก) ≈ **1.6 MB** บนดิสก์ — แต่เบราว์เซอร์โหลดเฉพาะ face ที่ถูกใช้จริง

## URL ที่ทดสอบแล้ว (31 ต.ค. 2026)

| ทรัพยากร | ผล |
|---|---|
| `fonts.googleapis.com/css2?family=...&display=swap` + UA Chrome | ✅ ได้ woff2 + unicode-range |
| `typefaces.chanakancloud.net/LINESeedSansTH_W_Rg.woff2` | ✅ 29,740 B, magic `wOF2` |
| `typefaces.chanakancloud.net/LINESeedSansTH_W_Bd.woff2` | ✅ 29,260 B |
| `typefaces.chanakancloud.net/LINESeedSansTH_W_XBd.woff2` | ✅ 32,368 B |
| `typefaces.chanakancloud.net/LINESeedSansTH_W_Lt.woff2` | ❌ 404 (ไม่มี Lt/Md) |
| `seed.line.me/seedth/download` | ❌ 403 |
| `line/seed` GitHub tree | ❌ มีแต่ LINESeedJP |
| `boomNDS/new_portfolio/public/fonts/*.woff2` | ❌ Git LFS pointer 162 B |
| `raw.githubusercontent.com/*/THSarabunNew.ttf` (repo มือสอง) | ❌ ไฟล์พัง ไม่มี TTF magic |
| `C:\Windows\Fonts\THSarabunNew.ttf` | ✅ 462 KB TTF → 120 KB woff2 |

## ตัวอย่างไฟล์ CSS ที่ generate ได้

`font-tools.py make-css <fonts-dir> src/app/fonts.css` → 64 faces จาก 9 ตระกูล Google
(ถ้าเพิ่ม LINE Seed + TH Sarabun New ผ่าน extra.json จะได้ 69 faces) ≈ 21 KB
