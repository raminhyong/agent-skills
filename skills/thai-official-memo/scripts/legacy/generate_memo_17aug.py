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
    # Tokenize words using pythainlp and join with zero-width space
    tokens = pythainlp.word_tokenize(text, engine='newmm', keep_whitespace=True)
    return '\u200b'.join(tokens)

def create_memo():
    doc = docx.Document()
    
    # 1. Page Margins (Page Setup: บน 0.79", ล่าง 0.50", ซ้าย 1", ขวา 0.79")
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.50)
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

    def set_font(run, name='TH Sarabun New', size=16, bold=False):
        run.font.name = name
        run.font.size = Pt(size)
        run.bold = bold
        rPr = run._r.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), name)
        rFonts.set(qn('w:hAnsi'), name)
        rFonts.set(qn('w:cs'), name)
        rPr.append(rFonts)

    # 2. Header Layout: Garuda (1.5 cm) + "บันทึกข้อความ" (20 pt Bold) exact page center X = 10.50 cm
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

    # 3. Headers: ส่วนราชการ, ที่, วันที่, เรื่อง
    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.space_before = Pt(2)
    p_gov.paragraph_format.space_after = Pt(1)
    p_gov.paragraph_format.line_spacing = 1.0
    r1 = p_gov.add_run("ส่วนราชการ")
    set_font(r1, size=16, bold=True)
    r2 = p_gov.add_run(th_wrap("  โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r2, size=16, bold=False)

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
    r_date_val = p_no_date.add_run(th_wrap("13 สิงหาคม 2569"))
    set_font(r_date_val, size=16)

    p_subject = doc.add_paragraph()
    p_subject.paragraph_format.space_before = Pt(0)
    p_subject.paragraph_format.space_after = Pt(2)
    p_subject.paragraph_format.line_spacing = 1.0
    r_sub_lbl = p_subject.add_run("เรื่อง")
    set_font(r_sub_lbl, size=16, bold=True)
    r_sub_val = p_subject.add_run(th_wrap("  ขออนุญาตไปราชการ"))
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

    # Body Paragraph 1
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b1.paragraph_format.first_line_indent = Cm(2.5)
    p_b1.paragraph_format.space_before = Pt(0)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.paragraph_format.line_spacing = 1.0
    r_b1 = p_b1.add_run(th_wrap(
        "ข้าพเจ้า นายรามิล ปัญญพัทธ์ ตำแหน่ง ครู วิทยฐานะ ครูชำนาญการพิเศษ สังกัดกลุ่มสาระการเรียนรู้ภาษาไทย "
        "โรงเรียนพูลเจริญวิทยาคม มีความประสงค์จะขออนุญาตไปราชการตามหนังสือ สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาสมุทรปราการ "
        "ที่ ศธ 04339/3329 ลงวันที่ 11 สิงหาคม 2569 เรื่อง ขอเชิญเข้าร่วมการประชุมคณะทำงานสนับสนุนการตรวจราชการและติดตามประเมินผลการจัดการศึกษาของกระทรวงศึกษาธิการรอบที่ 2 ประจำปีงบประมาณ พ.ศ. 2569 "
        "ณ ห้องประชุมปฏิบัติการชั้น 2 สำนักงานศึกษาธิการจังหวัดสมุทรปราการ ในวันจันทร์ที่ 17 สิงหาคม 2569 เวลา 13.00 – 16.30 น. "
        "โดยมีข้าราชการครูและบุคลากรทางการศึกษาร่วมเดินทางไปด้วย 1 คน ดังนี้"
    ))
    set_font(r_b1, size=16)

    # Participant List
    p_list = doc.add_paragraph()
    p_list.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_list.paragraph_format.left_indent = Cm(3.5)
    p_list.paragraph_format.space_before = Pt(0)
    p_list.paragraph_format.space_after = Pt(2)
    p_list.paragraph_format.line_spacing = 1.0
    r_list = p_list.add_run(th_wrap("1. นายอภิชา พุ่มพวง"))
    set_font(r_list, size=16)

    # Body Paragraph 2 (Guarantee)
    p_b2 = doc.add_paragraph()
    p_b2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b2.paragraph_format.first_line_indent = Cm(2.5)
    p_b2.paragraph_format.space_before = Pt(1)
    p_b2.paragraph_format.space_after = Pt(2)
    p_b2.paragraph_format.line_spacing = 1.0
    r_b2 = p_b2.add_run(th_wrap(
        "ข้าพเจ้าขอรับรองว่าการเดินทางไปราชการครั้งนี้จะเป็นประโยชน์ต่อการปฏิบัติหน้าที่ "
        "ของข้าพเจ้าโดยตรง และจะรายงานผลการไปราชการครั้งนี้ให้ทางโรงเรียนทราบ ภายในวันที่ 18 สิงหาคม 2569"
    ))
    set_font(r_b2, size=16)

    # Body Paragraph 3 (Conclusion)
    p_b3 = doc.add_paragraph()
    p_b3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b3.paragraph_format.first_line_indent = Cm(2.5)
    p_b3.paragraph_format.space_before = Pt(1)
    p_b3.paragraph_format.space_after = Pt(3)
    p_b3.paragraph_format.line_spacing = 1.0
    r_b3 = p_b3.add_run(th_wrap("จึงเรียนมาเพื่อโปรดพิจารณา"))
    set_font(r_b3, size=16)

    # 1 empty line after จึงเรียนมาเพื่อโปรดพิจารณา before signature block
    p_empty = doc.add_paragraph()
    p_empty.paragraph_format.space_before = Pt(0)
    p_empty.paragraph_format.space_after = Pt(0)
    p_empty.paragraph_format.line_spacing = 1.0
    r_empty = p_empty.add_run()
    set_font(r_empty, size=16)

    # 5. Signatures Block
    sig_table = doc.add_table(rows=3, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False
    
    for row in sig_table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    for r in sig_table.rows:
        r.cells[0].width = Cm(4.5)
        r.cells[1].width = Cm(11.5)

    def fill_sig_cell(cell, role_title, name_title):
        p1 = cell.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(f"ลงชื่อ..........................................................{role_title}")
        set_font(r1, size=16)

        p2 = cell.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(1)
        p2.paragraph_format.line_spacing = 1.0
        if "วราพร" in name_title:
            p2.paragraph_format.left_indent = Cm(1.35)
        else:
            p2.paragraph_format.left_indent = Cm(1.67)
        r2 = p2.add_run(f"({name_title})")
        set_font(r2, size=16)

    fill_sig_cell(sig_table.cell(0, 1), "ผู้ขออนุญาตไปราชการ", "นายรามิล ปัญญพัทธ์")
    fill_sig_cell(sig_table.cell(1, 1), "หัวหน้ากลุ่มสาระฯ/งาน/ฝ่าย", "นายรามิล ปัญญพัทธ์")
    fill_sig_cell(sig_table.cell(2, 1), "รองผู้อำนวยการโรงเรียน", "นางสาววราพร ไตรยะสุทธิ์")

    # 6. Director Approval Section
    p_dir_title = doc.add_paragraph()
    p_dir_title.paragraph_format.space_before = Pt(3)
    p_dir_title.paragraph_format.space_after = Pt(0)
    p_dir_title.paragraph_format.line_spacing = 1.0
    r_dt = p_dir_title.add_run("ความเห็นของผู้อำนวยการโรงเรียน")
    set_font(r_dt, size=16, bold=True)

    p_dir_chk = doc.add_paragraph()
    p_dir_chk.paragraph_format.left_indent = Cm(2.5)
    p_dir_chk.paragraph_format.space_before = Pt(0)
    p_dir_chk.paragraph_format.space_after = Pt(1)
    p_dir_chk.paragraph_format.line_spacing = 1.0
    r_dc = p_dir_chk.add_run("☐  อนุญาต             ☐  ไม่อนุญาต")
    set_font(r_dc, size=16)

    # 1 empty line after approval checkboxes before director signature block
    p_emp2 = doc.add_paragraph()
    p_emp2.paragraph_format.space_before = Pt(0)
    p_emp2.paragraph_format.space_after = Pt(0)
    p_emp2.paragraph_format.line_spacing = 1.0
    r_emp2 = p_emp2.add_run()
    set_font(r_emp2, size=16)

    # Director Signature Block
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
    r_ds1 = p_ds1.add_run("ลงชื่อ..........................................................")
    set_font(r_ds1, size=16)

    p_ds2 = cell_dir.add_paragraph()
    p_ds2.paragraph_format.space_before = Pt(0)
    p_ds2.paragraph_format.space_after = Pt(0)
    p_ds2.paragraph_format.line_spacing = 1.0
    p_ds2.paragraph_format.left_indent = Cm(1.66)
    r_ds2 = p_ds2.add_run("(นางสุภาพร รัตน์น้อย)")
    set_font(r_ds2, size=16)

    p_ds3 = cell_dir.add_paragraph()
    p_ds3.paragraph_format.space_before = Pt(0)
    p_ds3.paragraph_format.space_after = Pt(0)
    p_ds3.paragraph_format.line_spacing = 1.0
    p_ds3.paragraph_format.left_indent = Cm(0.0)
    r_ds3 = p_ds3.add_run("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม")
    set_font(r_ds3, size=16)

    out_file = 'h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/บันทึกข้อความไปราชการ17สค69.docx'
    doc.save(out_file)
    os.makedirs('h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/Output', exist_ok=True)
    doc.save('h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/Output/บันทึกข้อความไปราชการ17สค69.docx')
    print("DOCX created successfully.")

if __name__ == '__main__':
    create_memo()
