#!/usr/bin/env python3
"""รวมสคริปต์ช่วยงานฟอนต์ 3 งาน

1) ttf2woff2 <src.ttf> <dst.woff2>
   แปลงฟอนต์ TTF/OTF เป็น woff2 (ต้องมี fonttools + brotli)
   ใช้กับ TH Sarabun New ที่ติดมากับ Windows: C:/Windows/Fonts/THSarabunNew.ttf

2) make-css <fonts-dir> <out.css> [extra.json]
   สร้าง @font-face ทั้งหมดจาก manifest.json (+ ไฟล์เสริม เช่น LINE Seed / TH Sarabun New)
   extra.json ตัวอย่าง:
   [{"family":"LINE Seed Sans TH","faces":[
      {"subset":"all","weight":"400","file":"line-seed-sans-th/line-seed-sans-th-Rg.woff2","unicodeRange":null}]}]

3) check <file.woff2> ...
   ตรวจ magic + ขนาด (wOF2 = ถูก, 162 ไบต์ = LFS pointer, ขึ้นต้น \n = ไฟล์พัง)
"""
import json
import os
import sys


def cmd_ttf2woff2(src: str, dst: str) -> int:
    from fontTools.ttLib import TTFont  # pip install fonttools brotli

    f = TTFont(src, lazy=False)
    f.flavor = "woff2"
    f.save(dst)
    f.close()
    print(f"{os.path.basename(src):28s} -> {os.path.basename(dst)}  "
          f"{os.path.getsize(src)//1024}KB -> {os.path.getsize(dst)//1024}KB")
    return 0


def cmd_make_css(fonts_dir: str, out_css: str, extra_json: str | None = None) -> int:
    with open(os.path.join(fonts_dir, "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    if extra_json and os.path.exists(extra_json):
        with open(extra_json, encoding="utf-8") as f:
            man.extend(json.load(f))

    lines = ["/* ฟอนต์ไทย self-host — สร้างอัตโนมัติจาก public/fonts (ดู SOURCES.md) */", ""]
    for fam in man:
        for face in fam["faces"]:
            lines += ["@font-face {",
                      f'  font-family: "{fam["family"]}";',
                      "  font-style: normal;",
                      f'  font-weight: {face["weight"]};',
                      "  font-display: swap;",
                      f'  src: url("/fonts/{face["file"]}") format("woff2");']
            if face.get("unicodeRange"):
                lines.append(f'  unicode-range: {face["unicodeRange"]};')
            lines += ["}", ""]

    os.makedirs(os.path.dirname(out_css) or ".", exist_ok=True)
    with open(out_css, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"faces={sum(len(m['faces']) for m in man)} -> {out_css}")
    return 0


def cmd_check(*paths: str) -> int:
    bad = 0
    for p in paths:
        if not os.path.exists(p):
            print(f"MISSING  {p}")
            bad += 1
            continue
        size = os.path.getsize(p)
        with open(p, "rb") as f:
            head = f.read(4)
        if head == b"wOF2":
            print(f"OK       {p}  {size//1024}KB")
        elif b"version https://git-lfs" in head or size < 400:
            print(f"LFS/PTR  {p}  {size}B  (เป็น pointer ไม่ใช่ฟอนต์)")
            bad += 1
        else:
            print(f"BROKEN   {p}  {size}B  head={head!r}")
            bad += 1
    return 1 if bad else 0


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "ttf2woff2" and len(sys.argv) >= 4:
        return cmd_ttf2woff2(sys.argv[2], sys.argv[3])
    if cmd == "make-css" and len(sys.argv) >= 4:
        return cmd_make_css(sys.argv[2], sys.argv[3],
                            sys.argv[4] if len(sys.argv) > 4 else None)
    if cmd == "check":
        return cmd_check(*sys.argv[2:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
