# -*- coding: utf-8 -*-
"""verify_docx_spacing.py — ตรวจ "บรรทัดเปล่า 8px" ในไฟล์ .docx ที่สร้างจริง

ใช้เมื่อ: ต้องยืนยันว่าบันทึกข้อความใน Word มีระยะก่อน/หลัง «เรียน» และก่อน «จึงเรียนมาเพื่อ»
ตามมาตรฐาน 8px (= 6pt = 120 twips) จริง ไม่ใช่แค่เห็นในโค้ด

    py -3.12 verify_docx_spacing.py path/to/memo.docx
    py -3.12 verify_docx_spacing.py *.docx --expect-before 120 --min-before 100

อ่าน word/document.xml ใน zip → หาย่อหน้าที่ขึ้นต้นด้วย เรียน / จึงเรียนมาเพื่อ →
พิมพ์ w:spacing และ flag ถ้า w:before ต่ำกว่า --min-before (แปลว่าลืมใส่บรรทัดเปล่า)
ออกด้วย exit code 1 ถ้ามีข้อที่ไม่ผ่าน เพื่อใช้ใน CI ได้
"""
import argparse
import glob
import re
import sys
import zipfile

W_T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
W_P = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
W_SPACING = re.compile(r"<w:spacing[^>]*/>")
TARGETS = ("เรียน", "จึงเรียนมาเพื่อ")


def para_text(p_xml: str) -> str:
    return "".join(W_T.findall(p_xml)).replace("\u200b", "").strip()


def spacing_attr(p_xml: str, attr: str):
    tag = W_SPACING.search(p_xml)
    if not tag:
        return None
    m = re.search(r'w:%s="(-?\d+)"' % attr, tag.group(0))
    return int(m.group(1)) if m else None


def check(path: str, min_before: int) -> bool:
    print("==", path)
    ok = True
    seen = 0
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    for p in W_P.findall(xml):
        t = para_text(p)
        if not t.startswith(TARGETS):
            continue
        seen += 1
        before, after = spacing_attr(p, "before"), spacing_attr(p, "after")
        flag = ""
        if before is None or before < min_before:
            flag = "FAIL: before น้อยกว่า %d (ลืมบรรทัดเปล่า 8px)" % min_before
            ok = False
        print(f"   {t[:42]!r}  before={before} after={after}  {flag}")
    if seen == 0:
        print("   FAIL: ไม่พบย่อหน้า เรียน/จึงเรียนมาเพื่อ ในไฟล์นี้")
        ok = False
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--min-before", type=int, default=120,
                    help="ค่าน้อยสุดที่ยอมรับของ w:before (120 = 8px)")
    args = ap.parse_args()

    paths = []
    for pattern in args.files:
        paths.extend(sorted(glob.glob(pattern)) or [pattern])

    results = [check(p, args.min_before) for p in paths]
    print("\nสรุป:", "ผ่านทั้งหมด" if all(results) else "มีไฟล์ที่ไม่ผ่าน")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
