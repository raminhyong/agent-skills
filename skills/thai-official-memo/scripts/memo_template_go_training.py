import docx
from docx.shared import Cm, Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import subprocess
import os
import shutil
import pymupdf
import pythainlp
import sys

sys.stdout.reconfigure(encoding='utf-8')

# เทมเพลตพอร์ต: หาไฟล์จาก env MEMO_BASE/MEMO_LOGO -> cwd -> assets ของสกิล
_here = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.environ.get('MEMO_BASE') or os.getcwd()
def _find_logo():
    cands = [
        os.environ.get('MEMO_LOGO'),
        os.path.join(BASE_DIR, 'logo-Krut.png'),
        os.path.join(_here, '..', 'assets', 'logo-krut.png'),
    ]
    for c in cands:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    raise SystemExit('ไม่พบตราครุฑ: ตั้ง MEMO_LOGO หรือวาง logo-Krut.png ใน cwd')
LOGO_PATH = _find_logo()
OUTPUT_DIR = os.path.join(BASE_DIR, 'Output')
SCRATCH_DIR = os.path.join(BASE_DIR, 'scratch')

def th_wrap(text):
    if not text:
        return text
    tokens = pythainlp.word_tokenize(text, engine='newmm', keep_whitespace=True)
    return '\u200b'.join(tokens)

def set_font(run, name='TH Sarabun New', size=16, bold=False, italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._r.get_or_add_rPr()
    
    # Fonts for ascii, hAnsi, cs (Complex Scripts - Thai)
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rPr.append(rFonts)
    
    # Disable spelling/grammar error highlighting & set Thai language
    noProof = parse_xml(r'<w:noProof %s/>' % nsdecls('w'))
    rPr.append(noProof)
    lang = parse_xml(r'<w:lang %s w:val="th-TH" w:bidi="th-TH" w:eastAsia="th-TH"/>' % nsdecls('w'))
    rPr.append(lang)

def setup_margins(doc, bottom_in=0.50):
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(bottom_in)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.79)
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'TH Sarabun New'
    font.size = Pt(16)
    font.color.rgb = RGBColor(0, 0, 0)
    
    rPr = style.element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), 'TH Sarabun New')
    rFonts.set(qn('w:hAnsi'), 'TH Sarabun New')
    rFonts.set(qn('w:cs'), 'TH Sarabun New')
    rPr.append(rFonts)
    
    noProof = parse_xml(r'<w:noProof %s/>' % nsdecls('w'))
    rPr.append(noProof)
    lang = parse_xml(r'<w:lang %s w:val="th-TH" w:bidi="th-TH" w:eastAsia="th-TH"/>' % nsdecls('w'))
    rPr.append(lang)

    # Document-wide setting to hide spelling and grammatical errors
    try:
        settings_elm = doc.settings.element
        settings_elm.append(parse_xml(r'<w:hideSpellingErrors %s/>' % nsdecls('w')))
        settings_elm.append(parse_xml(r'<w:hideGrammaticalErrors %s/>' % nsdecls('w')))
    except Exception:
        pass

def add_garuda_header(doc):
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    for row in table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    table.cell(0, 0).width = Cm(3.00)
    table.cell(0, 1).width = Cm(9.92)
    table.cell(0, 2).width = Cm(3.53)
    
    p_img = table.cell(0, 0).paragraphs[0]
    p_img.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_img.paragraph_format.space_before = Pt(0)
    p_img.paragraph_format.space_after = Pt(0)
    run_img = p_img.add_run()
    run_img.add_picture(LOGO_PATH, height=Cm(1.5))
    
    p_title = table.cell(0, 1).paragraphs[0]
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(0)
    run_title = p_title.add_run(th_wrap("บันทึกข้อความ"))
    set_font(run_title, size=20, bold=True)
    return table

def add_divider_line(doc):
    """Creates the 8pt divider line paragraph with a solid bottom border."""
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_before = Pt(0)
    p_line.paragraph_format.space_after = Pt(2)
    p_line.paragraph_format.line_spacing = 1.0
    
    # Set paragraph-level run properties for 8pt font size
    pPr = p_line._p.get_or_add_pPr()
    pPr.append(parse_xml(r'<w:rPr %s><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:sz w:val="16"/><w:szCs w:val="16"/><w:noProof/></w:rPr>' % nsdecls('w')))
    
    # Add an empty run with 8pt font
    r_line = p_line.add_run()
    set_font(r_line, size=8)
    
    # Add bottom border
    pBdr = parse_xml(r'<w:pBdr %s><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>' % nsdecls('w'))
    pPr.append(pBdr)
    return p_line

def generate_request_memo():
    doc = docx.Document()
    setup_margins(doc, bottom_in=0.50)
    add_garuda_header(doc)

    # ส่วนราชการ
    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.space_before = Pt(2)
    p_gov.paragraph_format.space_after = Pt(1)
    p_gov.paragraph_format.line_spacing = 1.0
    r1 = p_gov.add_run(th_wrap("ส่วนราชการ"))
    set_font(r1, size=16, bold=True)
    r2 = p_gov.add_run(th_wrap("  โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r2, size=16, bold=False)

    # ที่ และ วันที่
    p_no_date = doc.add_paragraph()
    p_no_date.paragraph_format.space_before = Pt(0)
    p_no_date.paragraph_format.space_after = Pt(1)
    p_no_date.paragraph_format.line_spacing = 1.0
    
    r_no_lbl = p_no_date.add_run(th_wrap("ที่"))
    set_font(r_no_lbl, size=16, bold=True)
    r_no_val = p_no_date.add_run("  ......................................../....................                            ")
    set_font(r_no_val, size=16)
    
    r_date_lbl = p_no_date.add_run(th_wrap("วันที่  "))
    set_font(r_date_lbl, size=16, bold=True)
    r_date_val = p_no_date.add_run(th_wrap("26 สิงหาคม 2569"))
    set_font(r_date_val, size=16)

    # เรื่อง
    p_subject = doc.add_paragraph()
    p_subject.paragraph_format.space_before = Pt(0)
    p_subject.paragraph_format.space_after = Pt(2)
    p_subject.paragraph_format.line_spacing = 1.0
    r_sub_lbl = p_subject.add_run(th_wrap("เรื่อง"))
    set_font(r_sub_lbl, size=16, bold=True)
    r_sub_val = p_subject.add_run(th_wrap("  ขออนุญาตไปราชการ"))
    set_font(r_sub_val, size=16)

    # Horizontal Divider (8 pt)
    add_divider_line(doc)

    # เรียน
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(0)
    p_to.paragraph_format.space_after = Pt(2)
    p_to.paragraph_format.line_spacing = 1.0
    r_to_lbl = p_to.add_run(th_wrap("เรียน"))
    set_font(r_to_lbl, size=16, bold=True)
    r_to_val = p_to.add_run(th_wrap("  ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_to_val, size=16)

    # Paragraph 1
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b1.paragraph_format.first_line_indent = Cm(2.5)
    p_b1.paragraph_format.space_before = Pt(0)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.paragraph_format.line_spacing = 1.0
    r_b1 = p_b1.add_run(th_wrap(
        "ข้าพเจ้า นางสาวภัทรพร ประมาตร ตำแหน่ง รองผู้อำนวยการโรงเรียน โรงเรียนพูลเจริญวิทยาคม "
        "มีความประสงค์จะขออนุญาตไปราชการตามหนังสือ สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาสมุทรปราการ "
        "ที่ ศธ 04339/ว 3748 ลงวันที่ 24 สิงหาคม 2569 เรื่อง เชิญเข้าร่วมการประชุมเชิงปฏิบัติการขับเคลื่อนการยกระดับคุณภาพการจัดการศึกษาระดับมัธยมศึกษาและการพัฒนาหลักสูตรสถานศึกษาระดับมัธยมศึกษา "
        "ณ ห้องประชุมโรงเรียนหาดอมราอักษรลักษณ์วิทยา ในวันพฤหัสบดีที่ 3 กันยายน 2569 เวลา 08.00 – 16.30 น. "
        "โดยมีข้าราชการครูและบุคลากรทางการศึกษาร่วมเดินทางไปด้วย 2 คน ดังนี้"
    ))
    set_font(r_b1, size=16)

    # Participant List (Names only)
    p_l1 = doc.add_paragraph()
    p_l1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_l1.paragraph_format.left_indent = Cm(3.5)
    p_l1.paragraph_format.space_before = Pt(0)
    p_l1.paragraph_format.space_after = Pt(1)
    p_l1.paragraph_format.line_spacing = 1.0
    r_l1 = p_l1.add_run(th_wrap("1. นางปิยพร ทองก้อน"))
    set_font(r_l1, size=16)

    p_l2 = doc.add_paragraph()
    p_l2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_l2.paragraph_format.left_indent = Cm(3.5)
    p_l2.paragraph_format.space_before = Pt(0)
    p_l2.paragraph_format.space_after = Pt(2)
    p_l2.paragraph_format.line_spacing = 1.0
    r_l2 = p_l2.add_run(th_wrap("2. นายรามิล ปัญญพัทธ์"))
    set_font(r_l2, size=16)

    # Paragraph 2
    p_b2 = doc.add_paragraph()
    p_b2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b2.paragraph_format.first_line_indent = Cm(2.5)
    p_b2.paragraph_format.space_before = Pt(1)
    p_b2.paragraph_format.space_after = Pt(2)
    p_b2.paragraph_format.line_spacing = 1.0
    r_b2 = p_b2.add_run(th_wrap(
        "ข้าพเจ้าขอรับรองว่าการเดินทางไปราชการครั้งนี้จะเป็นประโยชน์ต่อการปฏิบัติหน้าที่ "
        "ของข้าพเจ้าโดยตรง และจะรายงานผลการไปราชการครั้งนี้ให้ทางโรงเรียนทราบ ภายในวันที่ 4 กันยายน 2569"
    ))
    set_font(r_b2, size=16)

    # Paragraph 3
    p_b3 = doc.add_paragraph()
    p_b3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b3.paragraph_format.first_line_indent = Cm(2.5)
    p_b3.paragraph_format.space_before = Pt(1)
    p_b3.paragraph_format.space_after = Pt(3)
    p_b3.paragraph_format.line_spacing = 1.0
    r_b3 = p_b3.add_run(th_wrap("จึงเรียนมาเพื่อโปรดพิจารณา"))
    set_font(r_b3, size=16)

    # Blank line (8pt)
    p_empty = doc.add_paragraph()
    p_empty.paragraph_format.space_before = Pt(0)
    p_empty.paragraph_format.space_after = Pt(0)
    p_empty.paragraph_format.line_spacing = 1.0
    r_empty = p_empty.add_run()
    set_font(r_empty, size=8)

    # Signature Block (Deputy Director directly to Director)
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False
    for row in sig_table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    sig_table.rows[0].cells[0].width = Cm(4.5)
    sig_table.rows[0].cells[1].width = Cm(11.5)

    cell_req = sig_table.cell(0, 1)
    ps1 = cell_req.paragraphs[0]
    ps1.paragraph_format.space_before = Pt(0)
    ps1.paragraph_format.space_after = Pt(0)
    ps1.paragraph_format.line_spacing = 1.0
    rs1 = ps1.add_run(th_wrap("ลงชื่อ..........................................................ผู้ขออนุญาตไปราชการ"))
    set_font(rs1, size=16)

    ps2 = cell_req.add_paragraph()
    ps2.paragraph_format.space_before = Pt(0)
    ps2.paragraph_format.space_after = Pt(0)
    ps2.paragraph_format.line_spacing = 1.0
    ps2.paragraph_format.left_indent = Cm(1.45)
    rs2 = ps2.add_run(th_wrap("(นางสาวภัทรพร ประมาตร)"))
    set_font(rs2, size=16)

    ps3 = cell_req.add_paragraph()
    ps3.paragraph_format.space_before = Pt(0)
    ps3.paragraph_format.space_after = Pt(0)
    ps3.paragraph_format.line_spacing = 1.0
    ps3.paragraph_format.left_indent = Cm(0.0)
    rs3 = ps3.add_run(th_wrap("รองผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(rs3, size=16)

    # Director Approval Section
    p_dir_title = doc.add_paragraph()
    p_dir_title.paragraph_format.space_before = Pt(12)
    p_dir_title.paragraph_format.space_after = Pt(2)
    p_dir_title.paragraph_format.line_spacing = 1.0
    r_dt = p_dir_title.add_run(th_wrap("ความเห็นของผู้อำนวยการโรงเรียน"))
    set_font(r_dt, size=16, bold=True)

    p_dir_chk = doc.add_paragraph()
    p_dir_chk.paragraph_format.left_indent = Cm(2.5)
    p_dir_chk.paragraph_format.space_before = Pt(0)
    p_dir_chk.paragraph_format.space_after = Pt(2)
    p_dir_chk.paragraph_format.line_spacing = 1.0
    r_dc = p_dir_chk.add_run(th_wrap("☐  อนุญาต             ☐  ไม่อนุญาต"))
    set_font(r_dc, size=16)

    p_emp2 = doc.add_paragraph()
    p_emp2.paragraph_format.space_before = Pt(0)
    p_emp2.paragraph_format.space_after = Pt(0)
    p_emp2.paragraph_format.line_spacing = 1.0
    r_emp2 = p_emp2.add_run()
    set_font(r_emp2, size=8)

    dir_table = doc.add_table(rows=1, cols=2)
    dir_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dir_table.autofit = False
    for row in dir_table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)
    
    dir_table.rows[0].cells[0].width = Cm(4.5)
    dir_table.rows[0].cells[1].width = Cm(11.5)

    cell_dir = dir_table.cell(0, 1)
    p_ds1 = cell_dir.paragraphs[0]
    p_ds1.paragraph_format.space_before = Pt(0)
    p_ds1.paragraph_format.space_after = Pt(0)
    p_ds1.paragraph_format.line_spacing = 1.0
    r_ds1 = p_ds1.add_run(th_wrap("ลงชื่อ.........................................................."))
    set_font(r_ds1, size=16)

    p_ds2 = cell_dir.add_paragraph()
    p_ds2.paragraph_format.space_before = Pt(0)
    p_ds2.paragraph_format.space_after = Pt(0)
    p_ds2.paragraph_format.line_spacing = 1.0
    p_ds2.paragraph_format.left_indent = Cm(1.66)
    r_ds2 = p_ds2.add_run(th_wrap("(นางสุภาพร รัตน์น้อย)"))
    set_font(r_ds2, size=16)

    p_ds3 = cell_dir.add_paragraph()
    p_ds3.paragraph_format.space_before = Pt(0)
    p_ds3.paragraph_format.space_after = Pt(0)
    p_ds3.paragraph_format.line_spacing = 1.0
    p_ds3.paragraph_format.left_indent = Cm(0.0)
    r_ds3 = p_ds3.add_run(th_wrap("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_ds3, size=16)

    out_file = os.path.join(BASE_DIR, 'บันทึกข้อความไปราชการ3กย69.docx')
    doc.save(out_file)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(os.path.join(OUTPUT_DIR, 'บันทึกข้อความไปราชการ3กย69.docx'))
    print(f"Request Memo saved to {out_file}")

def generate_report_memo():
    doc = docx.Document()
    setup_margins(doc, bottom_in=0.50)

    # ==========================================
    # PAGE 1: หนังสือนำส่งรายงานผล (Cover Memo)
    # ==========================================
    add_garuda_header(doc)

    # ส่วนราชการ
    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.space_before = Pt(2)
    p_gov.paragraph_format.space_after = Pt(1)
    p_gov.paragraph_format.line_spacing = 1.0
    r1 = p_gov.add_run(th_wrap("ส่วนราชการ"))
    set_font(r1, size=16, bold=True)
    r2 = p_gov.add_run(th_wrap("  โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r2, size=16, bold=False)

    # ที่ และ วันที่
    p_no_date = doc.add_paragraph()
    p_no_date.paragraph_format.space_before = Pt(0)
    p_no_date.paragraph_format.space_after = Pt(1)
    p_no_date.paragraph_format.line_spacing = 1.0
    
    r_no_lbl = p_no_date.add_run(th_wrap("ที่"))
    set_font(r_no_lbl, size=16, bold=True)
    r_no_val = p_no_date.add_run("  ......................................../....................                            ")
    set_font(r_no_val, size=16)
    
    r_date_lbl = p_no_date.add_run(th_wrap("วันที่  "))
    set_font(r_date_lbl, size=16, bold=True)
    r_date_val = p_no_date.add_run(th_wrap("4 กันยายน 2569"))
    set_font(r_date_val, size=16)

    # เรื่อง
    p_subject = doc.add_paragraph()
    p_subject.paragraph_format.space_before = Pt(0)
    p_subject.paragraph_format.space_after = Pt(2)
    p_subject.paragraph_format.line_spacing = 1.0
    r_sub_lbl = p_subject.add_run(th_wrap("เรื่อง"))
    set_font(r_sub_lbl, size=16, bold=True)
    r_sub_val = p_subject.add_run(th_wrap("  รายงานผลการไปราชการ"))
    set_font(r_sub_val, size=16)

    # Horizontal Divider (8 pt)
    add_divider_line(doc)

    # เรียน
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(0)
    p_to.paragraph_format.space_after = Pt(2)
    p_to.paragraph_format.line_spacing = 1.0
    r_to_lbl = p_to.add_run(th_wrap("เรียน"))
    set_font(r_to_lbl, size=16, bold=True)
    r_to_val = p_to.add_run(th_wrap("  ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_to_val, size=16)

    # ย่อหน้า 1
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b1.paragraph_format.first_line_indent = Cm(2.5)
    p_b1.paragraph_format.space_before = Pt(0)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.paragraph_format.line_spacing = 1.0
    r_b1 = p_b1.add_run(th_wrap(
        "ตามที่ ข้าพเจ้า นางสาวภัทรพร ประมาตร ตำแหน่ง รองผู้อำนวยการโรงเรียน โรงเรียนพูลเจริญวิทยาคม "
        "ได้รับอนุมัติให้ไปราชการตามหนังสือ สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาสมุทรปราการ "
        "ที่ ศธ 04339/ว 3748 ลงวันที่ 24 สิงหาคม 2569 เพื่อเข้าร่วมการประชุมเชิงปฏิบัติการขับเคลื่อนการยกระดับคุณภาพการจัดการศึกษาระดับมัธยมศึกษาและการพัฒนาหลักสูตรสถานศึกษาระดับมัธยมศึกษา "
        "ณ ห้องประชุมโรงเรียนหาดอมราอักษรลักษณ์วิทยา ในวันพฤหัสบดีที่ 3 กันยายน 2569 เวลา 08.00 – 16.30 น. "
        "โดยมีข้าราชการครูและบุคลากรทางการศึกษาร่วมเดินทางไปด้วย จำนวน 2 คน ได้แก่ 1. นางปิยพร ทองก้อน และ 2. นายรามิล ปัญญพัทธ์ นั้น"
    ))
    set_font(r_b1, size=16)

    # ย่อหน้า 2
    p_b2 = doc.add_paragraph()
    p_b2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b2.paragraph_format.first_line_indent = Cm(2.5)
    p_b2.paragraph_format.space_before = Pt(1)
    p_b2.paragraph_format.space_after = Pt(2)
    p_b2.paragraph_format.line_spacing = 1.0
    r_b2 = p_b2.add_run(th_wrap(
        "บัดนี้ ข้าพเจ้าได้เข้าร่วมการประชุมเชิงปฏิบัติการดังกล่าวตามกำหนดการเรียบร้อยแล้ว "
        "จึงขอรายงานผลการไปราชการ ดังเอกสารที่แนบมาพร้อมนี้"
    ))
    set_font(r_b2, size=16)

    # ย่อหน้า 3
    p_b3 = doc.add_paragraph()
    p_b3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b3.paragraph_format.first_line_indent = Cm(2.5)
    p_b3.paragraph_format.space_before = Pt(1)
    p_b3.paragraph_format.space_after = Pt(4)
    p_b3.paragraph_format.line_spacing = 1.0
    r_b3 = p_b3.add_run(th_wrap("จึงเรียนมาเพื่อโปรดทราบ"))
    set_font(r_b3, size=16)

    # Signature Block (Page 1)
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(0)
    r_sp = p_sp.add_run()
    set_font(r_sp, size=8)

    sig_p1 = doc.add_table(rows=1, cols=2)
    sig_p1.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_p1.autofit = False
    for row in sig_p1.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    sig_p1.rows[0].cells[0].width = Cm(7.5)
    sig_p1.rows[0].cells[1].width = Cm(8.5)

    c_sig = sig_p1.cell(0, 1)
    ps1 = c_sig.paragraphs[0]
    ps1.paragraph_format.space_before = Pt(0)
    ps1.paragraph_format.space_after = Pt(0)
    ps1.paragraph_format.line_spacing = 1.0
    rs1 = ps1.add_run(th_wrap("ลงชื่อ.........................................................."))
    set_font(rs1, size=16)

    ps2 = c_sig.add_paragraph()
    ps2.paragraph_format.space_before = Pt(0)
    ps2.paragraph_format.space_after = Pt(0)
    ps2.paragraph_format.line_spacing = 1.0
    ps2.paragraph_format.left_indent = Cm(1.45)
    rs2 = ps2.add_run(th_wrap("(นางสาวภัทรพร ประมาตร)"))
    set_font(rs2, size=16)

    ps3 = c_sig.add_paragraph()
    ps3.paragraph_format.space_before = Pt(0)
    ps3.paragraph_format.space_after = Pt(0)
    ps3.paragraph_format.line_spacing = 1.0
    ps3.paragraph_format.left_indent = Cm(0.0)
    rs3 = ps3.add_run(th_wrap("รองผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(rs3, size=16)

    # ความเห็นผู้อำนวยการโรงเรียน (Page 1)
    p_dir_box = doc.add_paragraph()
    p_dir_box.paragraph_format.space_before = Pt(14)
    p_dir_box.paragraph_format.space_after = Pt(2)
    p_dir_box.paragraph_format.line_spacing = 1.0
    r_dth = p_dir_box.add_run(th_wrap("ความเห็นของผู้อำนวยการโรงเรียน"))
    set_font(r_dth, size=16, bold=True)

    p_dline = doc.add_paragraph()
    p_dline.paragraph_format.space_before = Pt(0)
    p_dline.paragraph_format.space_after = Pt(2)
    p_dline.paragraph_format.line_spacing = 1.0
    r_dl = p_dline.add_run("..........................................................................................................................................")
    set_font(r_dl, size=16)

    p_sp_d = doc.add_paragraph()
    p_sp_d.paragraph_format.space_before = Pt(0)
    p_sp_d.paragraph_format.space_after = Pt(0)
    r_spd = p_sp_d.add_run()
    set_font(r_spd, size=8)

    dir_p1 = doc.add_table(rows=1, cols=2)
    dir_p1.alignment = WD_TABLE_ALIGNMENT.CENTER
    dir_p1.autofit = False
    for row in dir_p1.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    dir_p1.rows[0].cells[0].width = Cm(7.5)
    dir_p1.rows[0].cells[1].width = Cm(8.5)

    c_dir = dir_p1.cell(0, 1)
    pds1 = c_dir.paragraphs[0]
    pds1.paragraph_format.space_before = Pt(0)
    pds1.paragraph_format.space_after = Pt(0)
    pds1.paragraph_format.line_spacing = 1.0
    rds1 = pds1.add_run(th_wrap("ลงชื่อ.........................................................."))
    set_font(rds1, size=16)

    pds2 = c_dir.add_paragraph()
    pds2.paragraph_format.space_before = Pt(0)
    pds2.paragraph_format.space_after = Pt(0)
    pds2.paragraph_format.line_spacing = 1.0
    pds2.paragraph_format.left_indent = Cm(1.66)
    rds2 = pds2.add_run(th_wrap("(นางสุภาพร รัตน์น้อย)"))
    set_font(rds2, size=16)

    pds3 = c_dir.add_paragraph()
    pds3.paragraph_format.space_before = Pt(0)
    pds3.paragraph_format.space_after = Pt(0)
    pds3.paragraph_format.line_spacing = 1.0
    pds3.paragraph_format.left_indent = Cm(0.0)
    rds3 = pds3.add_run(th_wrap("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(rds3, size=16)

    pds4 = c_dir.add_paragraph()
    pds4.paragraph_format.space_before = Pt(0)
    pds4.paragraph_format.space_after = Pt(0)
    pds4.paragraph_format.line_spacing = 1.0
    pds4.paragraph_format.left_indent = Cm(1.30)
    rds4 = pds4.add_run(th_wrap("........../........../.........."))
    set_font(rds4, size=16)

    # Page Break to Page 2
    doc.add_page_break()

    # ==========================================
    # PAGE 2: แบบรายงานผลการไปราชการ
    # ==========================================
    p_rep_title = doc.add_paragraph()
    p_rep_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep_title.paragraph_format.space_before = Pt(0)
    p_rep_title.paragraph_format.space_after = Pt(2)
    r_rt = p_rep_title.add_run(th_wrap("รายงานการไปประชุม อบรม สัมมนา"))
    set_font(r_rt, size=18, bold=True)

    # เรื่อง
    p_r_sub = doc.add_paragraph()
    p_r_sub.paragraph_format.space_before = Pt(0)
    p_r_sub.paragraph_format.space_after = Pt(1)
    p_r_sub.paragraph_format.line_spacing = 1.0
    r_rsub_l = p_r_sub.add_run(th_wrap("เรื่อง  "))
    set_font(r_rsub_l, size=16, bold=True)
    r_rsub_v = p_r_sub.add_run(th_wrap("รายงานผลการเข้าร่วมการประชุมเชิงปฏิบัติการขับเคลื่อนการยกระดับคุณภาพการจัดการศึกษาระดับมัธยมศึกษาและการพัฒนาหลักสูตรสถานศึกษาระดับมัธยมศึกษา"))
    set_font(r_rsub_v, size=16)

    # เรียน
    p_r_to = doc.add_paragraph()
    p_r_to.paragraph_format.space_before = Pt(0)
    p_r_to.paragraph_format.space_after = Pt(2)
    p_r_to.paragraph_format.line_spacing = 1.0
    r_rto_l = p_r_to.add_run(th_wrap("เรียน  "))
    set_font(r_rto_l, size=16, bold=True)
    r_rto_v = p_r_to.add_run(th_wrap("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_rto_v, size=16)

    # ข้อมูลทั่วไป
    p_r_intro = doc.add_paragraph()
    p_r_intro.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_r_intro.paragraph_format.first_line_indent = Cm(2.5)
    p_r_intro.paragraph_format.space_before = Pt(0)
    p_r_intro.paragraph_format.space_after = Pt(2)
    p_r_intro.paragraph_format.line_spacing = 1.0
    r_intro = p_r_intro.add_run(th_wrap(
        "ข้าพเจ้า นางสาวภัทรพร ประมาตร ตำแหน่ง รองผู้อำนวยการโรงเรียน โรงเรียนพูลเจริญวิทยาคม "
        "พร้อมด้วย นางปิยพร ทองก้อน และ นายรามิล ปัญญพัทธ์ "
        "ได้เข้าร่วมการประชุมเชิงปฏิบัติการขับเคลื่อนการยกระดับคุณภาพการจัดการศึกษาระดับมัธยมศึกษาและการพัฒนาหลักสูตรสถานศึกษาระดับมัธยมศึกษา "
        "ณ ห้องประชุมโรงเรียนหาดอมราอักษรลักษณ์วิทยา ในวันพฤหัสบดีที่ 3 กันยายน 2569 เวลา 08.00 – 16.30 น. "
        "จัดโดย สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาสมุทรปราการ"
    ))
    set_font(r_intro, size=16)

    # 1. สิ่งที่ได้รับ
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(1)
    p_h1.paragraph_format.space_after = Pt(0)
    p_h1.paragraph_format.line_spacing = 1.0
    r_h1 = p_h1.add_run(th_wrap("สิ่งที่ได้รับ"))
    set_font(r_h1, size=16, bold=True)

    items_1 = [
        "1. แนวทางการพัฒนาหลักสูตรสถานศึกษา \"เรียนที่ชอบ อาชีพที่ใช่ ได้ความสุข\" ที่เน้นส่งเสริมศักยภาพ ความถนัด และความสนใจของผู้เรียนเพื่อเชื่อมโยงสู่อาชีพในอนาคต",
        "2. กลยุทธ์การยกระดับคุณภาพการศึกษาด้วยการจัดการเรียนรู้เชิงรุก (Active Learning) และการวัดประเมินผลตามสภาพจริงเพื่อพัฒนาผู้เรียนอย่างรอบด้าน",
        "3. แนวทางการขับเคลื่อนระบบประกันคุณภาพภายในสถานศึกษา และการประยุกต์ใช้ปัญญาประดิษฐ์ (AI) สนับสนุนการประเมินคุณภาพการศึกษา"
    ]
    for it in items_1:
        p_it = doc.add_paragraph()
        p_it.paragraph_format.left_indent = Cm(1.0)
        p_it.paragraph_format.space_before = Pt(0)
        p_it.paragraph_format.space_after = Pt(0)
        p_it.paragraph_format.line_spacing = 1.0
        r_it = p_it.add_run(th_wrap(it))
        set_font(r_it, size=16)

    # 2. เอกสารที่ได้รับ
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(1)
    p_h2.paragraph_format.space_after = Pt(0)
    p_h2.paragraph_format.line_spacing = 1.0
    r_h2 = p_h2.add_run(th_wrap("เอกสารที่ได้รับ"))
    set_font(r_h2, size=16, bold=True)

    p_doc_it = doc.add_paragraph()
    p_doc_it.paragraph_format.left_indent = Cm(1.0)
    p_doc_it.paragraph_format.space_before = Pt(0)
    p_doc_it.paragraph_format.space_after = Pt(0)
    p_doc_it.paragraph_format.line_spacing = 1.0
    r_dit = p_doc_it.add_run(th_wrap("คู่มือและเอกสารประกอบการประชุมเชิงปฏิบัติการขับเคลื่อนการยกระดับคุณภาพการศึกษาและการพัฒนาหลักสูตรสถานศึกษา"))
    set_font(r_dit, size=16)

    # 3. สิ่งที่คิดว่าจะนำมาปฏิบัติได้
    p_h3 = doc.add_paragraph()
    p_h3.paragraph_format.space_before = Pt(1)
    p_h3.paragraph_format.space_after = Pt(0)
    p_h3.paragraph_format.line_spacing = 1.0
    r_h3 = p_h3.add_run(th_wrap("สิ่งที่คิดว่าจะนำมาปฏิบัติได้"))
    set_font(r_h3, size=16, bold=True)

    items_3 = [
        "1. นำกรอบแนวคิด \"เรียนที่ชอบ อาชีพที่ใช่ ได้ความสุข\" มาปรับปรุงและพัฒนาหลักสูตรสถานศึกษา โรงเรียนพูลเจริญวิทยาคม ให้ยืดหยุ่นและทันสมัย",
        "2. ขยายผลองค์ความรู้แก่คณะครูผ่านกระบวนการ PLC เพื่อร่วมกันยกระดับการจัดการเรียนรู้เชิงรุกและการประเมินตามสภาพจริง",
        "3. ส่งเสริมการนำเทคโนโลยี AI มาช่วยสนับสนุนการประเมินคุณภาพการศึกษาและการบริหารจัดการข้อมูลสารสนเทศ"
    ]
    for it in items_3:
        p_it3 = doc.add_paragraph()
        p_it3.paragraph_format.left_indent = Cm(1.0)
        p_it3.paragraph_format.space_before = Pt(0)
        p_it3.paragraph_format.space_after = Pt(0)
        p_it3.paragraph_format.line_spacing = 1.0
        r_it3 = p_it3.add_run(th_wrap(it))
        set_font(r_it3, size=16)

    # 4. ข้อเสนอแนะ
    p_h4 = doc.add_paragraph()
    p_h4.paragraph_format.space_before = Pt(1)
    p_h4.paragraph_format.space_after = Pt(0)
    p_h4.paragraph_format.line_spacing = 1.0
    r_h4 = p_h4.add_run(th_wrap("ข้อเสนอแนะ"))
    set_font(r_h4, size=16, bold=True)

    p_rec = doc.add_paragraph()
    p_rec.paragraph_format.left_indent = Cm(1.0)
    p_rec.paragraph_format.space_before = Pt(0)
    p_rec.paragraph_format.space_after = Pt(2)
    p_rec.paragraph_format.line_spacing = 1.0
    r_rec = p_rec.add_run(th_wrap("ควรจัดประชุมเชิงปฏิบัติการภายในสถานศึกษาเพื่อร่วมกันพัฒนาหลักสูตรสถานศึกษา และส่งเสริมการนำ AI มาใช้ในการวัดประเมินผลอย่างเป็นรูปธรรม"))
    set_font(r_rec, size=16)

    # Signature Block (Page 2)
    sig_p2 = doc.add_table(rows=1, cols=2)
    sig_p2.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_p2.autofit = False
    for row in sig_p2.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    sig_p2.rows[0].cells[0].width = Cm(7.5)
    sig_p2.rows[0].cells[1].width = Cm(8.5)

    c_sig2 = sig_p2.cell(0, 1)
    ps2_1 = c_sig2.paragraphs[0]
    ps2_1.paragraph_format.space_before = Pt(0)
    ps2_1.paragraph_format.space_after = Pt(0)
    ps2_1.paragraph_format.line_spacing = 1.0
    rs2_1 = ps2_1.add_run(th_wrap("ลงชื่อ..........................................................ผู้รายงาน"))
    set_font(rs2_1, size=16)

    ps2_2 = c_sig2.add_paragraph()
    ps2_2.paragraph_format.space_before = Pt(0)
    ps2_2.paragraph_format.space_after = Pt(0)
    ps2_2.paragraph_format.line_spacing = 1.0
    ps2_2.paragraph_format.left_indent = Cm(1.45)
    rs2_2 = ps2_2.add_run(th_wrap("(นางสาวภัทรพร ประมาตร)"))
    set_font(rs2_2, size=16)

    ps3_2 = c_sig2.add_paragraph()
    ps3_2.paragraph_format.space_before = Pt(0)
    ps3_2.paragraph_format.space_after = Pt(0)
    ps3_2.paragraph_format.line_spacing = 1.0
    ps3_2.paragraph_format.left_indent = Cm(0.0)
    rs3_2 = ps3_2.add_run(th_wrap("รองผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(rs3_2, size=16)

    # Page Break to Page 3 (Activity Photos)
    doc.add_page_break()

    # ==========================================
    # PAGE 3: ภาคผนวก ภาพประกอบกิจกรรม
    # ==========================================
    p_app_t = doc.add_paragraph()
    p_app_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app_t.paragraph_format.space_before = Pt(0)
    p_app_t.paragraph_format.space_after = Pt(1)
    r_apt = p_app_t.add_run(th_wrap("ภาพการร่วมกิจกรรมการประชุมเชิงปฏิบัติการ"))
    set_font(r_apt, size=16, bold=True)

    p_app_sub = doc.add_paragraph()
    p_app_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app_sub.paragraph_format.space_before = Pt(0)
    p_app_sub.paragraph_format.space_after = Pt(8)
    p_app_sub.paragraph_format.line_spacing = 1.0
    r_apsub = p_app_sub.add_run(th_wrap("ขับเคลื่อนการยกระดับคุณภาพการจัดการศึกษาระดับมัธยมศึกษาและการพัฒนาหลักสูตรสถานศึกษาระดับมัธยมศึกษา ณ ห้องประชุมโรงเรียนหาดอมราอักษรลักษณ์วิทยา วันที่ 3 กันยายน 2569"))
    set_font(r_apsub, size=14)

    # Photo Box 1 Table
    p_tbl1 = doc.add_table(rows=1, cols=1)
    p_tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_tbl1.autofit = False
    p_tbl1.rows[0].cells[0].width = Cm(15.0)
    
    c1 = p_tbl1.cell(0, 0)
    tcPr1 = c1._tc.get_or_add_tcPr()
    tcBorders1 = parse_xml(r'<w:tcBorders %s><w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/></w:tcBorders>' % nsdecls('w'))
    tcPr1.append(tcBorders1)
    
    cp1 = c1.paragraphs[0]
    cp1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp1.paragraph_format.space_before = Pt(36)
    cp1.paragraph_format.space_after = Pt(36)
    r_ph1 = cp1.add_run(th_wrap("[ วางภาพถ่ายกิจกรรมที่ 1 ]"))
    set_font(r_ph1, size=15, italic=True)

    p_cap1 = doc.add_paragraph()
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap1.paragraph_format.space_before = Pt(2)
    p_cap1.paragraph_format.space_after = Pt(10)
    r_c1 = p_cap1.add_run(th_wrap("ภาพที่ 1 การเข้าร่วมรับฟังการบรรยายและแลกเปลี่ยนเรียนรู้การพัฒนาหลักสูตรสถานศึกษา \"เรียนที่ชอบ อาชีพที่ใช่ ได้ความสุข\""))
    set_font(r_c1, size=14)

    # Photo Box 2 Table
    p_tbl2 = doc.add_table(rows=1, cols=1)
    p_tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_tbl2.autofit = False
    p_tbl2.rows[0].cells[0].width = Cm(15.0)
    
    c2 = p_tbl2.cell(0, 0)
    tcPr2 = c2._tc.get_or_add_tcPr()
    tcBorders2 = parse_xml(r'<w:tcBorders %s><w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/></w:tcBorders>' % nsdecls('w'))
    tcPr2.append(tcBorders2)
    
    cp2 = c2.paragraphs[0]
    cp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp2.paragraph_format.space_before = Pt(36)
    cp2.paragraph_format.space_after = Pt(36)
    r_ph2 = cp2.add_run(th_wrap("[ วางภาพถ่ายกิจกรรมที่ 2 ]"))
    set_font(r_ph2, size=15, italic=True)

    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap2.paragraph_format.space_before = Pt(2)
    p_cap2.paragraph_format.space_after = Pt(4)
    r_c2 = p_cap2.add_run(th_wrap("ภาพที่ 2 การศึกษาแนวทางการพัฒนาระบบประกันคุณภาพการศึกษาและการใช้เทคโนโลยี AI สนับสนุนการประเมินคุณภาพ"))
    set_font(r_c2, size=14)

    out_file = os.path.join(BASE_DIR, 'บันทึกข้อความรายงานผลการไปราชการ3กย69.docx')
    doc.save(out_file)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(os.path.join(OUTPUT_DIR, 'บันทึกข้อความรายงานผลการไปราชการ3กย69.docx'))
    print(f"Report Memo saved to {out_file}")

if __name__ == '__main__':
    generate_request_memo()
    generate_report_memo()
