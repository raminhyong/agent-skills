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

def th_wrap(text):
    tokens = pythainlp.word_tokenize(text, engine='newmm', keep_whitespace=True)
    return '\u200b'.join(tokens)

def set_font(run, name='TH Sarabun New', size=16, bold=False, italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rPr.append(rFonts)

def create_report_memo():
    doc = docx.Document()
    
    # 1. Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.59)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.79)
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

    # Base Normal style with TH Sarabun New
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

    # ==========================================
    # PAGE 1: บันทึกข้อความ (Memo Cover Sheet)
    # ==========================================
    # Garuda + Header Table
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
    run_img.add_picture('h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/.agents/LOGO Krut.jpg', height=Cm(1.5))
    
    p_title = table.cell(0, 1).paragraphs[0]
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(0)
    run_title = p_title.add_run("บันทึกข้อความ")
    set_font(run_title, size=20, bold=True)

    # ส่วนราชการ
    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.space_before = Pt(2)
    p_gov.paragraph_format.space_after = Pt(1)
    p_gov.paragraph_format.line_spacing = 1.0
    r1 = p_gov.add_run("ส่วนราชการ")
    set_font(r1, size=16, bold=True)
    r2 = p_gov.add_run(th_wrap("  โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r2, size=16, bold=False)

    # ที่ และ วันที่
    p_no_date = doc.add_paragraph()
    p_no_date.paragraph_format.space_before = Pt(0)
    p_no_date.paragraph_format.space_after = Pt(1)
    p_no_date.paragraph_format.line_spacing = 1.0
    
    r_no_lbl = p_no_date.add_run("ที่")
    set_font(r_no_lbl, size=16, bold=True)
    r_no_val = p_no_date.add_run("  ......................................../....................                            ")
    set_font(r_no_val, size=16)
    
    r_date_lbl = p_no_date.add_run("วันที่  ")
    set_font(r_date_lbl, size=16, bold=True)
    r_date_val = p_no_date.add_run(th_wrap("18 สิงหาคม 2569"))
    set_font(r_date_val, size=16)

    # เรื่อง
    p_subject = doc.add_paragraph()
    p_subject.paragraph_format.space_before = Pt(0)
    p_subject.paragraph_format.space_after = Pt(2)
    p_subject.paragraph_format.line_spacing = 1.0
    r_sub_lbl = p_subject.add_run("เรื่อง")
    set_font(r_sub_lbl, size=16, bold=True)
    r_sub_val = p_subject.add_run(th_wrap("  รายงานผลการไปราชการ"))
    set_font(r_sub_val, size=16)

    # Divider Line
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_before = Pt(0)
    p_line.paragraph_format.space_after = Pt(3)
    pBdr = parse_xml(r'<w:pBdr %s><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>' % nsdecls('w'))
    p_line._p.get_or_add_pPr().append(pBdr)

    # เรียน
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(0)
    p_to.paragraph_format.space_after = Pt(2)
    p_to.paragraph_format.line_spacing = 1.0
    r_to_lbl = p_to.add_run("เรียน")
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
        "ตามที่ ข้าพเจ้า นายรามิล ปัญญพัทธ์ ตำแหน่ง ครู วิทยฐานะ ครูชำนาญการพิเศษ สังกัดกลุ่มสาระการเรียนรู้ภาษาไทย "
        "โรงเรียนพูลเจริญวิทยาคม ได้รับอนุมัติให้ไปราชการตามหนังสือ สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาสมุทรปราการ "
        "ที่ ศธ 04339/3329 ลงวันที่ 11 สิงหาคม 2569 เรื่อง ขอเชิญเข้าร่วมการประชุมคณะทำงานสนับสนุนการตรวจราชการและติดตามประเมินผลการจัดการศึกษาของกระทรวงศึกษาธิการรอบที่ 2 ประจำปีงบประมาณ พ.ศ. 2569 "
        "ณ ห้องประชุมปฏิบัติการชั้น 2 สำนักงานศึกษาธิการจังหวัดสมุทรปราการ ในวันจันทร์ที่ 17 สิงหาคม 2569 เวลา 13.00 – 16.30 น. "
        "โดยมีข้าราชการครูและบุคลากรทางการศึกษาร่วมเดินทางไปด้วย 1 คน ได้แก่ นายอภิชา พุ่มพวง นั้น"
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
        "บัดนี้ ข้าพเจ้าได้เข้าร่วมการประชุมดังกล่าวตามกำหนดการเรียบร้อยแล้ว "
        "และจัดทำรายงานผลการไปราชการ ดังเอกสารที่แนบมาพร้อมนี้"
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
    for _ in range(2):
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(0)
        p_sp.paragraph_format.line_spacing = 1.0

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
    rs1 = ps1.add_run("ลงชื่อ..........................................................")
    set_font(rs1, size=16)

    ps2 = c_sig.add_paragraph()
    ps2.paragraph_format.space_before = Pt(0)
    ps2.paragraph_format.space_after = Pt(0)
    ps2.paragraph_format.line_spacing = 1.0
    ps2.paragraph_format.left_indent = Cm(1.66)
    rs2 = ps2.add_run("(นายรามิล ปัญญพัทธ์)")
    set_font(rs2, size=16)

    ps3 = c_sig.add_paragraph()
    ps3.paragraph_format.space_before = Pt(0)
    ps3.paragraph_format.space_after = Pt(0)
    ps3.paragraph_format.line_spacing = 1.0
    ps3.paragraph_format.left_indent = Cm(0.0)
    rs3 = ps3.add_run("ตำแหน่ง ครู วิทยฐานะ ครูชำนาญการพิเศษ")
    set_font(rs3, size=16)

    # Page Break to Page 2
    doc.add_page_break()

    # ==========================================
    # PAGE 2: แบบรายงานผลการไปราชการ
    # ==========================================
    p_rep_title = doc.add_paragraph()
    p_rep_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep_title.paragraph_format.space_before = Pt(0)
    p_rep_title.paragraph_format.space_after = Pt(4)
    r_rt = p_rep_title.add_run("รายงานการไปประชุม อบรม สัมมนา")
    set_font(r_rt, size=18, bold=True)

    # เรื่อง
    p_r_sub = doc.add_paragraph()
    p_r_sub.paragraph_format.space_before = Pt(0)
    p_r_sub.paragraph_format.space_after = Pt(1)
    p_r_sub.paragraph_format.line_spacing = 1.0
    r_rsub_l = p_r_sub.add_run("เรื่อง  ")
    set_font(r_rsub_l, size=16, bold=True)
    r_rsub_v = p_r_sub.add_run(th_wrap("รายงานผลการเข้าร่วมการประชุมคณะทำงานสนับสนุนการตรวจราชการและติดตามประเมินผลการจัดการศึกษาของกระทรวงศึกษาธิการรอบที่ 2 ประจำปีงบประมาณ พ.ศ. 2569"))
    set_font(r_rsub_v, size=16)

    # เรียน
    p_r_to = doc.add_paragraph()
    p_r_to.paragraph_format.space_before = Pt(0)
    p_r_to.paragraph_format.space_after = Pt(3)
    p_r_to.paragraph_format.line_spacing = 1.0
    r_rto_l = p_r_to.add_run("เรียน  ")
    set_font(r_rto_l, size=16, bold=True)
    r_rto_v = p_r_to.add_run(th_wrap("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_rto_v, size=16)

    # ข้อมูลทั่วไป
    p_r_intro = doc.add_paragraph()
    p_r_intro.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_r_intro.paragraph_format.first_line_indent = Cm(2.5)
    p_r_intro.paragraph_format.space_before = Pt(0)
    p_r_intro.paragraph_format.space_after = Pt(3)
    p_r_intro.paragraph_format.line_spacing = 1.0
    r_intro = p_r_intro.add_run(th_wrap(
        "ข้าพเจ้า นายรามิล ปัญญพัทธ์ ตำแหน่ง ครู วิทยฐานะ ครูชำนาญการพิเศษ กลุ่มสาระการเรียนรู้ภาษาไทย "
        "โรงเรียนพูลเจริญวิทยาคม ได้เข้าร่วมการประชุมคณะทำงานสนับสนุนการตรวจราชการและติดตามประเมินผลการจัดการศึกษาของกระทรวงศึกษาธิการรอบที่ 2 ประจำปีงบประมาณ พ.ศ. 2569 "
        "ณ ห้องประชุมปฏิบัติการชั้น 2 สำนักงานศึกษาธิการจังหวัดสมุทรปราการ ในวันจันทร์ที่ 17 สิงหาคม 2569 เวลา 13.00 – 16.30 น. "
        "โดยมีข้าราชการครูและบุคลากรทางการศึกษาร่วมเดินทางไปด้วย 1 คน ได้แก่ นายอภิชา พุ่มพวง"
    ))
    set_font(r_intro, size=16)

    # สิ่งที่ได้รับ
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(2)
    p_h1.paragraph_format.space_after = Pt(1)
    p_h1.paragraph_format.line_spacing = 1.0
    r_h1 = p_h1.add_run("สิ่งที่ได้รับ")
    set_font(r_h1, size=16, bold=True)

    items_1 = [
        "1. รับทราบแนวทางและรูปแบบการนำเสนอรายงานผลการตรวจราชการและติดตามประเมินผลการจัดการศึกษาของกระทรวงศึกษาธิการ รอบที่ 2 ประจำปีงบประมาณ พ.ศ. 2569 ของผู้ตรวจราชการกระทรวงศึกษาธิการ (นายพิเชษฐ์ วันทอง) ณ จังหวัดสมุทรปราการ ซึ่งกำหนดลงพื้นที่ตรวจราชการในวันจันทร์ที่ 24 สิงหาคม 2569",
        "2. แนวทางการจัดเตรียมข้อมูลและรูปแบบเอกสารรายงานของสถานศึกษาหน่วยรับตรวจ (โรงเรียนพูลเจริญวิทยาคม) ให้ถูกต้อง ครบถ้วน และเป็นไปตามเกณฑ์มาตรฐานการตรวจราชการ",
        "3. แนวทางการประสานงานและแนวปฏิบัติร่วมกันระหว่างสำนักงานศึกษาธิการจังหวัดสมุทรปราการ สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาสมุทรปราการ และหน่วยรับตรวจ"
    ]
    for it in items_1:
        p_it = doc.add_paragraph()
        p_it.paragraph_format.left_indent = Cm(1.25)
        p_it.paragraph_format.space_before = Pt(0)
        p_it.paragraph_format.space_after = Pt(1)
        p_it.paragraph_format.line_spacing = 1.0
        r_it = p_it.add_run(th_wrap(it))
        set_font(r_it, size=16)

    # เอกสารที่ได้รับ
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(2)
    p_h2.paragraph_format.space_after = Pt(1)
    p_h2.paragraph_format.line_spacing = 1.0
    r_h2 = p_h2.add_run("เอกสารที่ได้รับ")
    set_font(r_h2, size=16, bold=True)

    p_doc_it = doc.add_paragraph()
    p_doc_it.paragraph_format.left_indent = Cm(1.25)
    p_doc_it.paragraph_format.space_before = Pt(0)
    p_doc_it.paragraph_format.space_after = Pt(1)
    p_doc_it.paragraph_format.line_spacing = 1.0
    r_dit = p_doc_it.add_run(th_wrap("เอกสารประกอบการประชุมและแนวทางการจัดทำรายงานสนับสนุนการตรวจราชการ รอบที่ 2"))
    set_font(r_dit, size=16)

    # สิ่งที่คิดว่าจะนำมาปฏิบัติได้
    p_h3 = doc.add_paragraph()
    p_h3.paragraph_format.space_before = Pt(2)
    p_h3.paragraph_format.space_after = Pt(1)
    p_h3.paragraph_format.line_spacing = 1.0
    r_h3 = p_h3.add_run("สิ่งที่คิดว่าจะนำมาปฏิบัติได้")
    set_font(r_h3, size=16, bold=True)

    p_app_it = doc.add_paragraph()
    p_app_it.paragraph_format.left_indent = Cm(1.25)
    p_app_it.paragraph_format.space_before = Pt(0)
    p_app_it.paragraph_format.space_after = Pt(1)
    p_app_it.paragraph_format.line_spacing = 1.0
    r_ait = p_app_it.add_run(th_wrap("1. นำรูปแบบและกรอบแนวทางการนำเสนอรายงานมาใช้ในการเตรียมความพร้อมรับการตรวจราชการของโรงเรียนพูลเจริญวิทยาคม ในวันจันทร์ที่ 24 สิงหาคม 2569 ให้มีความสมบูรณ์เรียบร้อย"))
    set_font(r_ait, size=16)

    p_app_it2 = doc.add_paragraph()
    p_app_it2.paragraph_format.left_indent = Cm(1.25)
    p_app_it2.paragraph_format.space_before = Pt(0)
    p_app_it2.paragraph_format.space_after = Pt(1)
    p_app_it2.paragraph_format.line_spacing = 1.0
    r_ait2 = p_app_it2.add_run(th_wrap("2. ประสานงานและถ่ายทอดข้อมูลแก่คณะครูและบุคลากรที่เกี่ยวข้อง เพื่อจัดเตรียมเอกสารข้อมูลและหลักฐานเชิงประจักษ์ให้ตรงตามประเด็นการตรวจราชการ"))
    set_font(r_ait2, size=16)

    # ข้อเสนอแนะ
    p_h4 = doc.add_paragraph()
    p_h4.paragraph_format.space_before = Pt(2)
    p_h4.paragraph_format.space_after = Pt(1)
    p_h4.paragraph_format.line_spacing = 1.0
    r_h4 = p_h4.add_run("ข้อเสนอแนะ")
    set_font(r_h4, size=16, bold=True)

    p_rec = doc.add_paragraph()
    p_rec.paragraph_format.left_indent = Cm(1.25)
    p_rec.paragraph_format.space_before = Pt(0)
    p_rec.paragraph_format.space_after = Pt(3)
    p_rec.paragraph_format.line_spacing = 1.0
    r_rec = p_rec.add_run(th_wrap("ควรจัดการประชุมซักซ้อมความพร้อมของคณะทำงานภายในโรงเรียน เพื่อตรวจทานความถูกต้องสมบูรณ์ของเอกสารและนิทรรศการก่อนวันรับการตรวจราชการจริง"))
    set_font(r_rec, size=16)

    # Signature Block (Page 2)
    p_sp_r = doc.add_paragraph()
    p_sp_r.paragraph_format.space_before = Pt(0)
    p_sp_r.paragraph_format.space_after = Pt(0)

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
    rs2_1 = ps2_1.add_run("ลงชื่อ..........................................................")
    set_font(rs2_1, size=16)

    ps2_2 = c_sig2.add_paragraph()
    ps2_2.paragraph_format.space_before = Pt(0)
    ps2_2.paragraph_format.space_after = Pt(0)
    ps2_2.paragraph_format.line_spacing = 1.0
    ps2_2.paragraph_format.left_indent = Cm(1.66)
    rs2_2 = ps2_2.add_run("(นายรามิล ปัญญพัทธ์)")
    set_font(rs2_2, size=16)

    ps2_3 = c_sig2.add_paragraph()
    ps2_3.paragraph_format.space_before = Pt(0)
    ps2_3.paragraph_format.space_after = Pt(0)
    ps2_3.paragraph_format.line_spacing = 1.0
    ps2_3.paragraph_format.left_indent = Cm(0.0)
    rs2_3 = ps2_3.add_run("ตำแหน่ง ครู วิทยฐานะ ครูชำนาญการพิเศษ")
    set_font(rs2_3, size=16)

    # Page Break to Page 3 (Activity Photos)
    doc.add_page_break()

    # ==========================================
    # PAGE 3: ภาคผนวก ภาพประกอบกิจกรรม
    # ==========================================
    p_app_t = doc.add_paragraph()
    p_app_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app_t.paragraph_format.space_before = Pt(0)
    p_app_t.paragraph_format.space_after = Pt(1)
    r_apt = p_app_t.add_run("ภาพการร่วมกิจกรรมการประชุมคณะทำงานสนับสนุนการตรวจราชการ")
    set_font(r_apt, size=16, bold=True)

    p_app_sub = doc.add_paragraph()
    p_app_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app_sub.paragraph_format.space_before = Pt(0)
    p_app_sub.paragraph_format.space_after = Pt(8)
    p_app_sub.paragraph_format.line_spacing = 1.0
    r_apsub = p_app_sub.add_run(th_wrap("การประชุมคณะทำงานสนับสนุนการตรวจราชการและติดตามประเมินผลการจัดการศึกษาของกระทรวงศึกษาธิการรอบที่ 2 ประจำปีงบประมาณ พ.ศ. 2569 ณ ห้องประชุมปฏิบัติการชั้น 2 สำนักงานศึกษาธิการจังหวัดสมุทรปราการ"))
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
    r_ph1 = cp1.add_run("[ วางภาพถ่ายกิจกรรมที่ 1 ]")
    set_font(r_ph1, size=15, italic=True)

    p_cap1 = doc.add_paragraph()
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap1.paragraph_format.space_before = Pt(2)
    p_cap1.paragraph_format.space_after = Pt(10)
    r_c1 = p_cap1.add_run(th_wrap("ภาพที่ 1 การเข้าร่วมรับฟังการชี้แจงแนวทางการตรวจราชการและติดตามประเมินผลการจัดการศึกษา"))
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
    r_ph2 = cp2.add_run("[ วางภาพถ่ายกิจกรรมที่ 2 ]")
    set_font(r_ph2, size=15, italic=True)

    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap2.paragraph_format.space_before = Pt(2)
    p_cap2.paragraph_format.space_after = Pt(4)
    r_c2 = p_cap2.add_run(th_wrap("ภาพที่ 2 การร่วมประชุมและประสานงานแนวทางการจัดทำรายงานของสถานศึกษาหน่วยรับตรวจ"))
    set_font(r_c2, size=14)

    # Save to files
    out_root = 'h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/บันทึกข้อความรายงานผลการไปราชการ17สค69.docx'
    doc.save(out_root)
    os.makedirs('h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/Output', exist_ok=True)
    out_output = 'h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/Output/บันทึกข้อความรายงานผลการไปราชการ17สค69.docx'
    doc.save(out_output)
    print("Report docx saved successfully.")

if __name__ == '__main__':
    create_report_memo()
