"""ตรวจ DOCX ภาษาไทยก่อนส่งมอบ (และแปลงเป็นภาพเพื่อตรวจด้วยตา)

usage:
    py -3.12 verify_thai_docx.py <file.docx>            # ตรวจอย่างเดียว
    py -3.12 verify_thai_docx.py <file.docx> --render   # ตรวจ + แปลง PDF/PNG หน้าละภาพ

ตรวจ 4 อย่างที่พลาดบ่อยที่สุด:
  1) ฟอนต์ explicit ของทุก run ต้องเป็น TH Sarabun New (ค่า None = สืบทอดจาก style ไม่ถือว่าผิด)
  2) ต้องไม่มีเลขไทย [๐-๙]
  3) \\u200b ต้องไม่ถูกแทรกก่อนสระ/วรรณยุกต์/ทัณฑฆาต (ตรวจทั้ง 2 ทิศ)
  4) นับจำนวน \\u200b แยกส่วน (รายงานเป็นตัวเลข ไม่ใช่คำว่า 'checked')

exit code: 0 = ผ่าน, 1 = พบปัญหา
"""
import os
import re
import sys

import docx

ZW = "\u200b"
FONT = "TH Sarabun New"
COMBINING = "\u0e31\u0e33\u0e34\u0e35\u0e36\u0e37\u0e38\u0e39\u0e3a\u0e47\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e4d\u0e4e"
THAI_DIGITS = "๐๑๒๓๔๕๖๗๘๙"


def run_fonts(document):
    """คืน dict: font -> จำนวน run (รวม run ในตาราง)"""
    from docx.oxml.ns import qn

    counts = {}
    for run_el in document.element.body.iter(qn("w:r")):
        rPr = run_el.find(qn("w:rPr"))
        font = None
        if rPr is not None:
            rFonts = rPr.find(qn("w:rFonts"))
            if rFonts is not None:
                font = rFonts.get(qn("w:ascii"))
        counts[font] = counts.get(font, 0) + 1
    return counts


def all_text(document):
    from docx.oxml.ns import qn

    parts = []
    for t in document.element.body.iter(qn("w:t")):
        if t.text:
            parts.append(t.text)
    return "".join(parts)


def render(docx_path):
    """DOCX -> PDF (Word COM) -> PNG หน้าละไฟล์; คืน list path"""
    import win32com.client as win32
    import pymupdf

    base = os.path.splitext(docx_path)[0]
    pdf_path = base + ".verify.pdf"

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(os.path.abspath(docx_path), ReadOnly=True)
    doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # 17 = wdFormatPDF
    doc.Close(False)
    word.Quit()

    pdf = pymupdf.open(pdf_path)
    out = []
    for i in range(len(pdf)):
        png = f"{base}.page{i + 1}.png"
        pdf[i].get_pixmap(dpi=100).save(png)
        out.append(png)
    return pdf_path, out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    do_render = "--render" in sys.argv[2:]
    if not os.path.exists(path):
        sys.exit(f"ไม่พบไฟล์: {path}")

    d = docx.Document(path)
    text = all_text(d)
    problems = []

    fonts = run_fonts(d)
    wrong = {f: n for f, n in fonts.items() if f not in (None, FONT)}
    print("fonts:", {str(k): v for k, v in sorted(fonts.items(), key=lambda kv: str(kv[0]))})
    if wrong:
        problems.append(f"มี run ที่ฟอนต์ไม่ใช่ {FONT}: {wrong}")

    digits = re.findall(f"[{THAI_DIGITS}]+", text)
    print("Thai numerals:", digits[:10] if digits else "none")
    if digits:
        problems.append(f"พบเลขไทย {len(digits)} จุด")

    bad_after = re.findall(ZW + f"([{COMBINING}])", text)
    bad_before = re.findall(f"([{COMBINING}]){ZW}", text)
    print(f"ZWSP total: {text.count(ZW)} | ก่อนสระ/วรรณยุกต์: {len(bad_after)} | หลังสระ: {len(bad_before)}")
    if bad_after or bad_before:
        problems.append(f"ZWSP แทรกผิดตำแหน่ง: {len(bad_after) + len(bad_before)} จุด")

    if do_render:
        try:
            pdf_path, pngs = render(path)
            print("rendered:", pdf_path)
            for p in pngs:
                print("  png:", p)
            print("-> เปิด PNG ตรวจด้วยตา: ตารางล้น ช่องลงนามแตกหน้า หัวข้อค้างท้ายหน้า")
        except Exception as exc:  # Word ไม่พร้อมใช้
            print(f"render ข้าม: {exc}")

    if problems:
        print("\nFAIL")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("\nPASS (ยังต้องดูภาพเองถ้าเป็นงานส่งมอบ)")


if __name__ == "__main__":
    main()
