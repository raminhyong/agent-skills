import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import pythainlp

def th_wrap(text):
    if not text:
        return ""
    tokens = pythainlp.word_tokenize(text, engine='newmm')
    return "\u200b".join(tokens)

def _find_krut():
    """หาไฟล์ตราครุฑ: env MEMO_LOGO -> cwd/logo-Krut.png -> assets/ ของสกิล"""
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [
        os.environ.get('MEMO_LOGO'),
        os.path.join(os.getcwd(), 'logo-Krut.png'),
        os.path.join(here, '..', 'assets', 'logo-krut.png'),
    ]
    for c in cands:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    print('WARNING: ไม่พบตราครุฑ (ตั้ง MEMO_LOGO หรือวาง logo-Krut.png ใน cwd)')
    return None


def set_font(run, name='TH Sarabun New', size=16, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)
    rPr.append(rFonts)
    noProof = OxmlElement('w:noProof')
    rPr.append(noProof)
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'th-TH')
    rPr.append(lang)

def set_cell_margins(cell, top=30, bottom=30, left=60, right=60):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="{kwargs.get("top", "single")}" w:sz="{kwargs.get("top_sz", "4")}" w:space="0" w:color="{kwargs.get("top_color", "auto")}"/>'
        f'<w:left w:val="{kwargs.get("left", "single")}" w:sz="{kwargs.get("left_sz", "4")}" w:space="0" w:color="{kwargs.get("left_color", "auto")}"/>'
        f'<w:bottom w:val="{kwargs.get("bottom", "single")}" w:sz="{kwargs.get("bottom_sz", "4")}" w:space="0" w:color="{kwargs.get("bottom_color", "auto")}"/>'
        f'<w:right w:val="{kwargs.get("right", "single")}" w:sz="{kwargs.get("right_sz", "4")}" w:space="0" w:color="{kwargs.get("right_color", "auto")}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def create_exam_memo():
    doc = Document()
    
    # Hide spelling errors
    settings = doc.settings.element
    settings.append(OxmlElement('w:hideSpellingErrors'))
    settings.append(OxmlElement('w:hideGrammaticalErrors'))

    # Section Settings
    section = doc.sections[0]
    section.top_margin = Inches(0.79)     # 2.0 cm
    section.bottom_margin = Inches(0.50)  # 1.27 cm
    section.left_margin = Inches(0.85)    # 2.16 cm
    section.right_margin = Inches(0.65)   # 1.65 cm
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

    # -------------------------------------------------------------
    # PAGE 1: หนังสือนำส่งบันทึกข้อความ
    # -------------------------------------------------------------
    
    # 1. Header Table (Garuda + Center Title "บันทึกข้อความ")
    header_table = doc.add_table(rows=1, cols=3)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False

    for row in header_table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    col_widths = [Cm(3.00), Cm(9.92), Cm(3.53)]
    for row in header_table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    # Cell 0: Garuda Logo
    garuda_cell = header_table.cell(0, 0)
    p_krut = garuda_cell.paragraphs[0]
    p_krut.paragraph_format.space_before = Pt(0)
    p_krut.paragraph_format.space_after = Pt(0)
    p_krut.paragraph_format.line_spacing = 1.0
    r_krut = p_krut.add_run()
    krut_path = _find_krut()
    if krut_path:
        r_krut.add_picture(krut_path, height=Cm(1.5))

    # Cell 1: Center Title "บันทึกข้อความ"
    title_cell = header_table.cell(0, 1)
    p_title = title_cell.paragraphs[0]
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(0)
    p_title.paragraph_format.line_spacing = 1.0
    r_title = p_title.add_run("บันทึกข้อความ")
    set_font(r_title, size=20, bold=True)

    # 2. Metadata Paragraphs
    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.space_before = Pt(2)
    p_gov.paragraph_format.space_after = Pt(1)
    p_gov.paragraph_format.line_spacing = 1.0
    r_g1 = p_gov.add_run("ส่วนราชการ  ")
    set_font(r_g1, size=16, bold=True)
    r_g2 = p_gov.add_run(th_wrap("กลุ่มสาระการเรียนรู้ภาษาไทย โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_g2, size=16)

    p_no_date = doc.add_paragraph()
    p_no_date.paragraph_format.space_before = Pt(1)
    p_no_date.paragraph_format.space_after = Pt(1)
    p_no_date.paragraph_format.line_spacing = 1.0
    r_no1 = p_no_date.add_run("ที่  ")
    set_font(r_no1, size=16, bold=True)
    r_no2 = p_no_date.add_run("........................................................................   ")
    set_font(r_no2, size=16)
    r_dt1 = p_no_date.add_run("วันที่  ")
    set_font(r_dt1, size=16, bold=True)
    r_dt2 = p_no_date.add_run(th_wrap("16 กันยายน 2569"))
    set_font(r_dt2, size=16)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(1)
    p_sub.paragraph_format.space_after = Pt(1)
    p_sub.paragraph_format.line_spacing = 1.0
    r_s1 = p_sub.add_run("เรื่อง  ")
    set_font(r_s1, size=16, bold=True)
    r_s2 = p_sub.add_run(th_wrap("ส่งข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569"))
    set_font(r_s2, size=16, bold=False)

    # Divider Line (8 pt)
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(2)
    p_div.paragraph_format.line_spacing = 1.0
    r_div = p_div.add_run()
    set_font(r_div, size=8)
    pPr = p_div._p.get_or_add_pPr()
    pBdr = parse_xml(r'<w:pBdr %s><w:bottom w:val="single" w:sz="6" w:space="1" w:color="auto"/></w:pBdr>' % nsdecls('w'))
    pPr.append(pBdr)

    # 3. Addressee & Enclosure
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(2)
    p_to.paragraph_format.space_after = Pt(1)
    p_to.paragraph_format.line_spacing = 1.0
    r_t1 = p_to.add_run("เรียน  ")
    set_font(r_t1, size=16, bold=True)
    r_t2 = p_to.add_run(th_wrap("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_t2, size=16)

    p_att = doc.add_paragraph()
    p_att.paragraph_format.space_before = Pt(1)
    p_att.paragraph_format.space_after = Pt(3)
    p_att.paragraph_format.line_spacing = 1.0
    r_a1 = p_att.add_run("สิ่งที่ส่งมาด้วย  ")
    set_font(r_a1, size=16, bold=True)
    r_a2 = p_att.add_run(th_wrap("แบบสรุปการส่งข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569 จำนวน 1 ชุด"))
    set_font(r_a2, size=16)

    # 4. Body Paragraphs
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b1.paragraph_format.first_line_indent = Cm(2.5)
    p_b1.paragraph_format.space_before = Pt(2)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.paragraph_format.line_spacing = 1.0
    r_b1 = p_b1.add_run(th_wrap(
        "ตามที่ กลุ่มบริหารวิชาการ โรงเรียนพูลเจริญวิทยาคม ได้กำหนดให้ครูผู้สอนดำเนินการจัดทำ"
        "และส่งต้นฉบับข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569 เพื่อใช้วัดและประเมินผลสัมฤทธิ์ทางการเรียน"
        "ของผู้เรียนตามหลักสูตรสถานศึกษา นั้น"
    ))
    set_font(r_b1, size=16)

    p_b2 = doc.add_paragraph()
    p_b2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b2.paragraph_format.first_line_indent = Cm(2.5)
    p_b2.paragraph_format.space_before = Pt(2)
    p_b2.paragraph_format.space_after = Pt(2)
    p_b2.paragraph_format.line_spacing = 1.0
    r_b2 = p_b2.add_run(th_wrap(
        "บัดนี้ ครูผู้สอนกลุ่มสาระการเรียนรู้ภาษาไทย ได้ดำเนินการจัดทำต้นฉบับข้อสอบวัดผลปลายภาคเรียนที่ 1 "
        "ปีการศึกษา 2569 เสร็จสิ้นเรียบร้อยแล้ว จึงขอส่งต้นฉบับข้อสอบวัดผลปลายภาคเรียนดังกล่าว "
        "ตามแบบสรุปรายการที่แนบมาพร้อมนี้"
    ))
    set_font(r_b2, size=16)

    p_b3 = doc.add_paragraph()
    p_b3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b3.paragraph_format.first_line_indent = Cm(2.5)
    p_b3.paragraph_format.space_before = Pt(2)
    p_b3.paragraph_format.space_after = Pt(6)
    p_b3.paragraph_format.line_spacing = 1.0
    r_b3 = p_b3.add_run(th_wrap("จึงเรียนมาเพื่อโปรดทราบและพิจารณา"))
    set_font(r_b3, size=16)

    # Empty paragraph spacing before signature
    p_sp1 = doc.add_paragraph()
    p_sp1.paragraph_format.space_before = Pt(6)
    p_sp1.paragraph_format.space_after = Pt(0)
    p_sp1.paragraph_format.line_spacing = 1.0
    set_font(p_sp1.add_run(), size=16)

    # 5. Single Signature Block for Head of Department (Page 1)
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False

    for row in sig_table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    sig_table.rows[0].cells[0].width = Cm(5.5)
    sig_table.rows[0].cells[1].width = Cm(11.5)

    cell_sig = sig_table.cell(0, 1)
    p_s1 = cell_sig.paragraphs[0]
    p_s1.paragraph_format.space_before = Pt(0)
    p_s1.paragraph_format.space_after = Pt(0)
    p_s1.paragraph_format.line_spacing = 1.0
    r_s1 = p_s1.add_run("ลงชื่อ..........................................................")
    set_font(r_s1, size=16)

    p_s2 = cell_sig.add_paragraph()
    p_s2.paragraph_format.space_before = Pt(0)
    p_s2.paragraph_format.space_after = Pt(0)
    p_s2.paragraph_format.line_spacing = 1.0
    p_s2.paragraph_format.left_indent = Cm(1.67)
    r_s2 = p_s2.add_run("(นายรามิล ปัญญพัทธ์)")
    set_font(r_s2, size=16)

    p_s3 = cell_sig.add_paragraph()
    p_s3.paragraph_format.space_before = Pt(0)
    p_s3.paragraph_format.space_after = Pt(0)
    p_s3.paragraph_format.line_spacing = 1.0
    p_s3.paragraph_format.left_indent = Cm(0.7)
    r_s3 = p_s3.add_run("หัวหน้ากลุ่มสาระการเรียนรู้ภาษาไทย")
    set_font(r_s3, size=16)

    # -------------------------------------------------------------
    # PAGE 2: ตารางสรุปการส่งข้อสอบ
    # -------------------------------------------------------------
    doc.add_page_break()

    # Title on Page 2
    p_p2_t1 = doc.add_paragraph()
    p_p2_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p2_t1.paragraph_format.space_before = Pt(0)
    p_p2_t1.paragraph_format.space_after = Pt(0)
    p_p2_t1.paragraph_format.line_spacing = 1.0
    r_p2_1 = p_p2_t1.add_run(th_wrap("แบบสรุปการส่งข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569"))
    set_font(r_p2_1, size=16, bold=True)

    p_p2_t2 = doc.add_paragraph()
    p_p2_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p2_t2.paragraph_format.space_before = Pt(0)
    p_p2_t2.paragraph_format.space_after = Pt(3)
    p_p2_t2.paragraph_format.line_spacing = 1.0
    r_p2_2 = p_p2_t2.add_run(th_wrap("กลุ่มสาระการเรียนรู้ภาษาไทย โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_p2_2, size=15, bold=True)

    # Table Data Definition (16 Distinct Subjects)
    data = [
        # (Grade, Code, Name, Teachers List)
        ("ม.1", "ท21101", "ภาษาไทยพื้นฐาน", ["1. นางสาวศุภนุช บุตรดี", "2. นายชินกร ศิริโยธา", "3. นายจิรวัฒน์ ศรีวโร"]),
        ("ม.1", "ท20214", "การใช้ห้องสมุดเบื้องต้น", ["นางสาวนันทกาญจน์ เรืองกระจาย"]),
        ("ม.1", "ท20213", "การอ่านเบื้องต้น", ["นางสาวอิงอร สิทธิจินดา"]),
        ("ม.1", "ท20208", "การเขียนเบื้องต้น", ["นายชินกร ศิริโยธา"]),
        
        ("ม.2", "ท22101", "ภาษาไทยพื้นฐาน", ["1. นางสาวชื่นฤดี หรับหลี", "2. นางสาววนิชญา เชียงน้อย", "3. นางสาวอิงอร สิทธิจินดา"]),
        ("ม.2", "ท20216", "การส่งเสริมการอ่านและการเรียนรู้ในห้องสมุด 1", ["นางสาววรวัลภ์ นิตยระวีวาร"]),
        ("ม.2", "ท20210", "ศึกษาวรรณคดี", ["นางสาววรวัลภ์ นิตยระวีวาร"]),
        
        ("ม.3", "ท23101", "ภาษาไทยพื้นฐาน", ["1. นางวรางคณา ศรีม่วง", "2. นายเฉลิมชาติ ภูผันผิน", "3. นายอภิชา พุ่มพวง"]),
        ("ม.3", "ท20205", "ศึกษานิทาน", ["นางสาวนันทกาญจน์ เรืองกระจาย"]),
        ("ม.3", "ท20212", "การพูดเบื้องต้น", ["นางสาวชื่นฤดี หรับหลี"]),
        
        ("ม.4", "ท31101", "ภาษาไทยพื้นฐาน", ["นายสุริยา ก่อบุญ"]),
        ("ม.4", "ท30213", "การอ่านวรรณกรรมไทยเชิงวิเคราะห์ 1", ["นางสาวศุภนุช บุตรดี"]),
        
        ("ม.5", "ท32101", "ภาษาไทยพื้นฐาน", ["นางสาวกมลวรรณ สังข์ทอง"]),
        ("ม.5", "ท30215", "ภาษาไทยเพื่อการแสดง 1", ["นายจิรวัฒน์ ศรีวโร"]),
        
        ("ม.6", "ท33101", "ภาษาไทยพื้นฐาน", ["1. นายรามิล ปัญญพัทธ์", "2. นางวรางคณา ศรีม่วง"]),
        ("ม.6", "ท30217", "ภาษาไทยกับการผลิตสื่อร่วมสมัย 1", ["นายรามิล ปัญญพัทธ์"]),
    ]

    # Create Table (2 Header rows + 16 Data rows = 18 rows, 8 columns)
    # [ลำดับ: 1.1cm, รหัสวิชา: 1.8cm, ชื่อวิชา: 4.1cm, ระดับชั้น: 1.3cm, ครูผู้สอน: 4.8cm, ส่ง: 1.0cm, ไม่ส่ง: 1.0cm, หมายเหตุ: 1.6cm]
    col_w = [Cm(1.1), Cm(1.8), Cm(4.1), Cm(1.3), Cm(4.8), Cm(1.0), Cm(1.0), Cm(1.6)]

    table = doc.add_table(rows=2 + len(data), cols=8)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Format Header Row 0 & 1
    hdr0 = table.rows[0]
    hdr1 = table.rows[1]

    headers_config = [
        (0, "ลำดับ"),
        (1, "รหัสวิชา"),
        (2, "ชื่อวิชา"),
        (3, "ระดับชั้น"),
        (4, "ครูผู้สอน"),
        (7, "หมายเหตุ"),
    ]

    # Merge vertical header cells
    for col_idx, text in headers_config:
        c0 = hdr0.cells[col_idx]
        c1 = hdr1.cells[col_idx]
        c0.merge(c1)
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c0.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(th_wrap(text))
        set_font(r, size=14, bold=True)
        set_cell_margins(c0, top=30, bottom=30, left=30, right=30)
        set_cell_shading(c0, "F0F0F0")
        set_cell_border(c0, top="single", bottom="single", left="single", right="single")

    # Header for Exam Submission (cols 5 & 6)
    c_sub0 = hdr0.cells[5]
    c_sub1 = hdr0.cells[6]
    c_sub_merged = c_sub0.merge(c_sub1)
    c_sub_merged.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_sub_hdr = c_sub_merged.paragraphs[0]
    p_sub_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub_hdr.paragraph_format.space_before = Pt(1)
    p_sub_hdr.paragraph_format.space_after = Pt(1)
    p_sub_hdr.paragraph_format.line_spacing = 1.0
    r_sh = p_sub_hdr.add_run(th_wrap("การส่งข้อสอบ"))
    set_font(r_sh, size=14, bold=True)
    set_cell_margins(c_sub_merged, top=20, bottom=20, left=30, right=30)
    set_cell_shading(c_sub_merged, "F0F0F0")
    set_cell_border(c_sub_merged, top="single", bottom="single", left="single", right="single")

    # Sub-headers in Row 1: "ส่ง", "ไม่ส่ง"
    for col_idx, text in [(5, "ส่ง"), (6, "ไม่ส่ง")]:
        c = hdr1.cells[col_idx]
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(th_wrap(text))
        set_font(r, size=13, bold=True)
        set_cell_margins(c, top=20, bottom=20, left=20, right=20)
        set_cell_shading(c, "F0F0F0")
        set_cell_border(c, top="single", bottom="single", left="single", right="single")

    # Fill Data Rows
    for idx, (grade, code, name, teachers) in enumerate(data, start=1):
        row_idx = 1 + idx
        row = table.rows[row_idx]
        
        # Apply borders and shading
        for c_i, cell in enumerate(row.cells):
            set_cell_border(cell, top="single", bottom="single", left="single", right="single")
            set_cell_margins(cell, top=25, bottom=25, left=35, right=35)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # Col 0: ลำดับ
        c0 = row.cells[0]
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.0
        r0 = p0.add_run(str(idx))
        set_font(r0, size=13.5)

        # Col 1: รหัสวิชา
        c1 = row.cells[1]
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(code)
        set_font(r1, size=13.5, bold=True)

        # Col 2: ชื่อวิชา
        c2 = row.cells[2]
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing = 1.0
        r2 = p2.add_run(th_wrap(name))
        set_font(r2, size=13.5)

        # Col 3: ระดับชั้น
        c3 = row.cells[3]
        p3 = c3.paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_before = Pt(0)
        p3.paragraph_format.space_after = Pt(0)
        p3.paragraph_format.line_spacing = 1.0
        r3 = p3.add_run(grade)
        set_font(r3, size=13.5)

        # Col 4: ครูผู้สอน
        c4 = row.cells[4]
        for t_i, t_name in enumerate(teachers):
            if t_i == 0:
                p4 = c4.paragraphs[0]
            else:
                p4 = c4.add_paragraph()
            p4.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p4.paragraph_format.space_before = Pt(0)
            p4.paragraph_format.space_after = Pt(0)
            p4.paragraph_format.line_spacing = 1.0
            r4 = p4.add_run(th_wrap(t_name))
            set_font(r4, size=13.5)

        # Col 5: ส่ง (Check square)
        c5 = row.cells[5]
        p5 = c5.paragraphs[0]
        p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p5.paragraph_format.space_before = Pt(0)
        p5.paragraph_format.space_after = Pt(0)
        p5.paragraph_format.line_spacing = 1.0
        r5 = p5.add_run("☐")
        set_font(r5, size=14)

        # Col 6: ไม่ส่ง (Check square)
        c6 = row.cells[6]
        p6 = c6.paragraphs[0]
        p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p6.paragraph_format.space_before = Pt(0)
        p6.paragraph_format.space_after = Pt(0)
        p6.paragraph_format.line_spacing = 1.0
        r6 = p6.add_run("☐")
        set_font(r6, size=14)

        # Col 7: หมายเหตุ
        c7 = row.cells[7]
        p7 = c7.paragraphs[0]
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p7.paragraph_format.space_before = Pt(0)
        p7.paragraph_format.space_after = Pt(0)
        p7.paragraph_format.line_spacing = 1.0
        r7 = p7.add_run("")
        set_font(r7, size=13.5)

    # Set column widths for all rows
    for r in table.rows:
        for c_i, w in enumerate(col_w):
            r.cells[c_i].width = w

    # Summary Line Below Table
    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.space_before = Pt(6)
    p_sum.paragraph_format.space_after = Pt(8)
    p_sum.paragraph_format.line_spacing = 1.0
    r_sum = p_sum.add_run(th_wrap(
        "สรุปผลการส่งข้อสอบ: รวมจำนวนรายวิชาทั้งหมด 16 รายวิชา    "
        "ส่งครบถ้วน ............ รายวิชา    ยังไม่ส่ง ............ รายวิชา"
    ))
    set_font(r_sum, size=14.5, bold=True)

    # Sign-off block on Page 2 (Single centered / right block for Head of Dept)
    tbl_sign2 = doc.add_table(rows=1, cols=2)
    tbl_sign2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sign2.autofit = False

    for row in tbl_sign2.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    tbl_sign2.rows[0].cells[0].width = Cm(7.0)
    tbl_sign2.rows[0].cells[1].width = Cm(10.0)

    # Right Column: ผู้รายงาน / หัวหน้ากลุ่มสาระฯ
    c_s_right = tbl_sign2.cell(0, 1)
    p_sl1 = c_s_right.paragraphs[0]
    p_sl1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sl1.paragraph_format.space_before = Pt(0)
    p_sl1.paragraph_format.space_after = Pt(0)
    p_sl1.paragraph_format.line_spacing = 1.0
    r_sl1 = p_sl1.add_run("ลงชื่อ..........................................................ผู้รายงาน")
    set_font(r_sl1, size=14.5)

    p_sl2 = c_s_right.add_paragraph()
    p_sl2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sl2.paragraph_format.space_before = Pt(0)
    p_sl2.paragraph_format.space_after = Pt(0)
    p_sl2.paragraph_format.line_spacing = 1.0
    r_sl2 = p_sl2.add_run("(นายรามิล ปัญญพัทธ์)")
    set_font(r_sl2, size=14.5)

    p_sl3 = c_s_right.add_paragraph()
    p_sl3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sl3.paragraph_format.space_before = Pt(0)
    p_sl3.paragraph_format.space_after = Pt(0)
    p_sl3.paragraph_format.line_spacing = 1.0
    r_sl3 = p_sl3.add_run("หัวหน้ากลุ่มสาระการเรียนรู้ภาษาไทย")
    set_font(r_sl3, size=14.5)

    # Save to all target locations
    base = os.environ.get('MEMO_BASE') or os.getcwd()
    out_paths = [os.path.join(base, 'บันทึกข้อความส่งข้อสอบปลายภาคเรียน 1-2569.docx')]

    for op in out_paths:
        os.makedirs(os.path.dirname(op), exist_ok=True)
        doc.save(op)
        print(f"Saved: {op}")

if __name__ == '__main__':
    create_exam_memo()
