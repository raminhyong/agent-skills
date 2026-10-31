import os
import sys
import time
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import pythainlp
import re
import json
import win32com.client
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NON_SPACING_CHARS = set([
    '\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
    '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e',
    '\u200b'
])

def visual_length(text):
    return sum(1 for c in text if c not in NON_SPACING_CHARS)

def thai_tokenize(text):
    if not text:
        return ""
    words = pythainlp.word_tokenize(text, engine="newmm")
    res = "\u200b".join(words)
    for c in NON_SPACING_CHARS:
        res = res.replace(f"\u200b{c}", c)
    res = re.sub(r'\u200b+', '\u200b', res)
    return res

def set_run_font(run, font_name="TH Sarabun New", size_pt=16, bold=False, italic=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}" w:eastAsia="{font_name}"/>')
        rPr.append(rFonts)
    else:
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)
        rFonts.set(qn('w:eastAsia'), font_name)
    
    lang = rPr.find(qn('w:lang'))
    if lang is None:
        lang = parse_xml(f'<w:lang {nsdecls("w")} w:val="th-TH" w:bidi="th-TH"/>')
        rPr.append(lang)
    else:
        lang.set(qn('w:val'), 'th-TH')
        lang.set(qn('w:bidi'), 'th-TH')

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn('w:tcBorders'))
    if tcBorders is None:
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        tcPr.append(tcBorders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data is not None:
            tag = f'w:{edge}'
            element = tcBorders.find(qn(tag))
            if element is None:
                element = parse_xml(f'<{tag} {nsdecls("w")}/>')
                tcBorders.append(element)
            for key, val in edge_data.items():
                element.set(qn(f'w:{key}'), str(val))

def set_cell_margins(cell, top=0, bottom=0, left=50, right=50):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

NEGATIVE_WORDS = sorted([
    "ไม่ถูกต้องเหมาะสม", "ไม่ถูกต้อง", "ไม่เหมาะสม", "ไม่สร้างสรรค์", "ไม่เห็นด้วย",
    "ไม่ใช่", "ไม่มีประสิทธิภาพ", "ไม่มี", "ไม่ปรากฏ", "ไม่จำเป็น", "ไม่ได้",
    "ไม่ควร", "มิได้", "ยกเว้น", "ไม่"
], key=len, reverse=True)

def add_formatted_question_runs(paragraph, q_text):
    pattern = "(" + "|".join([re.escape(w) for w in NEGATIVE_WORDS]) + ")"
    parts = re.split(pattern, q_text)
    for part in parts:
        if not part:
            continue
        tokenized = thai_tokenize(part)
        if part in NEGATIVE_WORDS:
            run = paragraph.add_run(tokenized)
            set_run_font(run, bold=True)
        else:
            run = paragraph.add_run(tokenized)
            set_run_font(run, bold=False)

def build_job02_docx():
    doc = docx.Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.8)
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.header_distance = Inches(0.3)
    section.footer_distance = Inches(0.3)
    
    # Document default font
    docDefaults = doc._body._element.xpath('//w:docDefaults')
    if docDefaults:
        rPrDef = docDefaults[0].find(qn('w:rPrDefault'))
        if rPrDef is not None:
            rPr = rPrDef.find(qn('w:rPr'))
            if rPr is not None:
                rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New" w:eastAsia="TH Sarabun New"/>')
                rPr.append(rFonts)
    
    # Page number: - 1 - (Bold, 16pt, Center)
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(0)
    
    hrun1 = hp.add_run("- ")
    set_run_font(hrun1, bold=True)
    fldSimple = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
    hp._p.append(fldSimple)
    hrun2 = hp.add_run(" -")
    set_run_font(hrun2, bold=True)
    
    # ================= PAGE 1 =================
    
    # Logo
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(0)
    p_logo.paragraph_format.space_after = Pt(0)
    p_logo.paragraph_format.line_spacing = 1.0
    logo_p = os.path.join(BASE_DIR, "school logo.JPG")
    if os.path.exists(logo_p):
        p_logo.add_run().add_picture(logo_p, width=Inches(0.95))
    
    # School Name: โรงเรียนพูลเจริญวิทยาคม (Bold, 16pt, Center)
    p_school = doc.add_paragraph()
    p_school.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_school.paragraph_format.space_before = Pt(0)
    p_school.paragraph_format.space_after = Pt(0)
    p_school.paragraph_format.line_spacing = 1.0
    r_sch = p_school.add_run(thai_tokenize("โรงเรียนพูลเจริญวิทยาคม"))
    set_run_font(r_sch, bold=True)
    
    # Header Table (3 cols, invisible borders, bottom divider line on row 3)
    tbl_hdr = doc.add_table(rows=3, cols=3)
    tbl_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_hdr_data = [
        [("ข้อสอบวัดผลปลายภาคเรียน", WD_ALIGN_PARAGRAPH.LEFT),
         ("ประจำภาคเรียนที่ 1", WD_ALIGN_PARAGRAPH.CENTER),
         ("ปีการศึกษา 2569", WD_ALIGN_PARAGRAPH.RIGHT)],
        [("วิชาภาษาไทยกับการผลิตสื่อร่วมสมัย 1", WD_ALIGN_PARAGRAPH.LEFT),
         ("รหัสวิชา ท30217", WD_ALIGN_PARAGRAPH.CENTER),
         ("ชั้นมัธยมศึกษาปีที่ 6", WD_ALIGN_PARAGRAPH.RIGHT)],
        [("สอบวันที่ ...... กันยายน 2569", WD_ALIGN_PARAGRAPH.LEFT),
         ("เวลาสอบ 60 นาที", WD_ALIGN_PARAGRAPH.CENTER),
         ("คะแนนเต็ม 20 คะแนน", WD_ALIGN_PARAGRAPH.RIGHT)]
    ]
    col_widths = [Inches(2.5), Inches(2.2), Inches(2.1)]
    for r_idx, row in enumerate(tbl_hdr.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]
            text, align = tbl_hdr_data[r_idx][c_idx]
            p = cell.paragraphs[0]
            p.alignment = align
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(thai_tokenize(text))
            set_run_font(r, bold=False)
            set_cell_margins(cell, top=0, bottom=0, left=50, right=50)
            set_cell_border(cell, top=dict(val='none'), bottom=dict(val='none'), left=dict(val='none'), right=dict(val='none'))
            if r_idx == 2:
                set_cell_border(cell, bottom=dict(val='single', sz=6, color='auto'))
    
    # Instructions Heading: คำชี้แจง (Bold, 16pt, space_before=6pt)
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.space_before = Pt(6)
    p_inst.paragraph_format.space_after = Pt(0)
    p_inst.paragraph_format.line_spacing = 1.0
    p_inst.paragraph_format.left_indent = Pt(0)
    r_inst = p_inst.add_run(thai_tokenize("คำชี้แจง"))
    set_run_font(r_inst, bold=True)
    
    # Instructions Items
    inst_items = [
        "1. ข้อสอบเป็นแบบปรนัย จำนวน 40 ข้อ",
        "2. ไม่อนุญาตให้นักเรียนออกจากห้องสอบจนกว่าจะหมดเวลาสอบ",
        "3. ไม่อนุญาตให้นักเรียนนำข้อสอบและกระดาษคำตอบออกนอกห้องสอบ"
    ]
    for item in inst_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_before = Pt(0)
        p_item.paragraph_format.space_after = Pt(0)
        p_item.paragraph_format.line_spacing = 1.0
        p_item.paragraph_format.left_indent = Inches(0.2)
        r_it = p_item.add_run(thai_tokenize(item))
        set_run_font(r_it, bold=False)
    
    # Summary Table: ผลการเรียนรู้ (3 cols, center table, single borders)
    tbl_sum = doc.add_table(rows=5, cols=3)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_headers = [("ผลการเรียนรู้", Inches(3.2)), ("ข้อสอบข้อที่", Inches(1.1)), ("หมายเหตุ", Inches(1.2))]
    sum_rows = [
        ("ผลการเรียนรู้ที่ 5", "1–8", ""),
        ("ผลการเรียนรู้ที่ 6", "9–16", ""),
        ("ผลการเรียนรู้ที่ 7", "17–32", ""),
        ("ผลการเรียนรู้ที่ 8", "33–40", "")
    ]
    
    for c_idx, (h_text, w) in enumerate(sum_headers):
        cell = tbl_sum.rows[0].cells[c_idx]
        cell.width = w
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(thai_tokenize(h_text))
        set_run_font(r, bold=True)
        set_cell_border(cell, top=dict(val='single', sz=4, color='auto'),
                              bottom=dict(val='single', sz=4, color='auto'),
                              left=dict(val='single', sz=4, color='auto'),
                              right=dict(val='single', sz=4, color='auto'))
        set_cell_margins(cell, top=40, bottom=40, left=100, right=100)
    
    for r_idx, (lo, items, note) in enumerate(sum_rows, start=1):
        for c_idx, text in enumerate([lo, items, note]):
            cell = tbl_sum.rows[r_idx].cells[c_idx]
            cell.width = sum_headers[c_idx][1]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(thai_tokenize(text))
            set_run_font(r, bold=False)
            set_cell_border(cell, top=dict(val='single', sz=4, color='auto'),
                                  bottom=dict(val='single', sz=4, color='auto'),
                                  left=dict(val='single', sz=4, color='auto'),
                                  right=dict(val='single', sz=4, color='auto'))
            set_cell_margins(cell, top=40, bottom=40, left=100, right=100)
    
    # Blank line
    p_blank = doc.add_paragraph()
    p_blank.paragraph_format.space_before = Pt(0)
    p_blank.paragraph_format.space_after = Pt(0)
    p_blank.paragraph_format.line_spacing = 1.0
    
    # ================= SIGNATURE SECTION =================
    tbl_sig = doc.add_table(rows=4, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_sig.rows:
        for c in r.cells:
            c.width = Inches(3.4)
            set_cell_border(c, top=dict(val='none'), bottom=dict(val='none'), left=dict(val='none'), right=dict(val='none'))
            set_cell_margins(c, 0, 0, 0, 0)
    
    signers_1person = [
        ("ผู้ออกข้อสอบ", "( นายรามิล ปัญญพัทธ์ )", "          "),
        ("หัวหน้ากลุ่มสาระการเรียนรู้", "( นายรามิล ปัญญพัทธ์ )", "          "),
        ("หัวหน้างานวัดผลโรงเรียน", "( นางจิราพรรณ เรืองพุทธ )", "          "),
        ("รองผู้อำนวยการโรงเรียน", "( นางสาวภัทรพร ประมาตร )", "          ")
    ]
    
    for r_idx, (role, name, space_pad) in enumerate(signers_1person):
        cell = tbl_sig.rows[r_idx].cells[0]
        cell.merge(tbl_sig.rows[r_idx].cells[1])
        
        p_top = cell.paragraphs[0]
        p_top.paragraph_format.space_before = Pt(6) if r_idx > 0 else Pt(0)
        p_top.paragraph_format.space_after = Pt(0)
        p_top.paragraph_format.line_spacing = 1.0
        p_top.paragraph_format.left_indent = Inches(1.1)
        r_top = p_top.add_run(thai_tokenize(f"ลงชื่อ........................................................ {role}"))
        set_run_font(r_top)
        
        p_bot = cell.add_paragraph()
        p_bot.paragraph_format.space_before = Pt(0)
        p_bot.paragraph_format.space_after = Pt(0)
        p_bot.paragraph_format.line_spacing = 1.0
        p_bot.paragraph_format.left_indent = Inches(1.1)
        r_bot = p_bot.add_run(f"{space_pad}{name}")
        set_run_font(r_bot)
    
    # Page Break to Page 2
    doc.add_page_break()
    
    # ================= PAGE 2+: EXAM QUESTIONS =================
    
    p_cmd = doc.add_paragraph()
    p_cmd.paragraph_format.space_before = Pt(0)
    p_cmd.paragraph_format.space_after = Pt(0)
    p_cmd.paragraph_format.line_spacing = 1.0
    p_cmd.paragraph_format.left_indent = Pt(0)
    
    r_cmd1 = p_cmd.add_run(thai_tokenize("คำสั่ง"))
    set_run_font(r_cmd1, bold=True)
    r_cmd2 = p_cmd.add_run(" " + thai_tokenize("จงเลือกคำตอบที่ถูกต้องที่สุดเพียงคำตอบเดียว"))
    set_run_font(r_cmd2, bold=False)
    
    lo_map = {
        5: "ผลการเรียนรู้ที่ 5 ผลิตสื่อในรูปแบบต่าง ๆ โดยใช้ภาษาไทยอย่างถูกต้องและเหมาะสม (ข้อ 1 - 8)",
        6: "ผลการเรียนรู้ที่ 6 นำเสนอผลงานสื่อที่สร้างขึ้นอย่างมีประสิทธิภาพและชัดเจนต่อกลุ่มเป้าหมาย (ข้อ 9 - 16)",
        7: "ผลการเรียนรู้ที่ 7 ให้และรับคำติชมเชิงสร้างสรรค์เกี่ยวกับผลงานสื่อของตนเองและผู้อื่น (ข้อ 17 - 32)",
        8: "ผลการเรียนรู้ที่ 8 ใช้ภาษาไทยและสื่อเพื่อสื่อสารความคิดอย่างสร้างสรรค์ มีวิจารณญาณและมีจริยธรรม (ข้อ 33 - 40)"
    }
    
    with open(os.path.join(BASE_DIR, "scripts", "job02_new_parsed.json"), "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    current_lo = None
    
    for q in questions:
        q_num = q['num']
        
        if 1 <= q_num <= 8:
            target_lo = 5
        elif 9 <= q_num <= 16:
            target_lo = 6
        elif 17 <= q_num <= 32:
            target_lo = 7
        elif 33 <= q_num <= 40:
            target_lo = 8
        else:
            target_lo = None
        
        if target_lo != current_lo:
            is_first_lo = (current_lo is None)
            current_lo = target_lo
            lo_text = lo_map[current_lo]
            p_lo = doc.add_paragraph()
            p_lo.paragraph_format.space_before = Pt(0) if is_first_lo else Pt(16)
            p_lo.paragraph_format.space_after = Pt(0)
            p_lo.paragraph_format.line_spacing = 1.0
            p_lo.paragraph_format.left_indent = Pt(0)
            p_lo.paragraph_format.keep_with_next = True
            
            r_lo = p_lo.add_run(thai_tokenize(lo_text))
            set_run_font(r_lo, bold=False)
        
        # Question paragraph
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(0)
        p_q.paragraph_format.space_after = Pt(0)
        p_q.paragraph_format.line_spacing = 1.0
        p_q.paragraph_format.left_indent = Pt(0)
        p_q.paragraph_format.keep_with_next = True
        p_q.paragraph_format.keep_together = True
        
        full_q_text = f"{q_num}. {q['text']}"
        add_formatted_question_runs(p_q, full_q_text)
        
        sorted_choices = q['sorted_choices']
        
        # Choice layout decision:
        # Col 1 is choice 0 and choice 2 (width ~3.2 in)
        # Col 2 is choice 1 and choice 3 (width ~3.37 in)
        col1_max = max(visual_length(sorted_choices[0]), visual_length(sorted_choices[2])) if len(sorted_choices) >= 3 else 0
        col2_max = max(visual_length(sorted_choices[1]), visual_length(sorted_choices[3])) if len(sorted_choices) >= 4 else 0
        overall_max = max(visual_length(c) for c in sorted_choices) if sorted_choices else 0
        
        # Format 3 (1-line: 4 cols): if overall_max <= 10
        # Format 2 (2-line: 2 cols with Tab at 3.4"): if col1_max <= 33 and col2_max <= 36 and overall_max <= 35
        # Format 1 (4-line: 1 col): otherwise
        if overall_max <= 10 and len(sorted_choices) == 4:
            p_c = doc.add_paragraph()
            p_c.paragraph_format.space_before = Pt(0)
            p_c.paragraph_format.space_after = Pt(0)
            p_c.paragraph_format.line_spacing = 1.0
            p_c.paragraph_format.left_indent = Inches(0.2)
            p_c.paragraph_format.keep_together = True
            
            p_c.paragraph_format.tab_stops.add_tab_stop(Inches(1.8), WD_TAB_ALIGNMENT.LEFT)
            p_c.paragraph_format.tab_stops.add_tab_stop(Inches(3.4), WD_TAB_ALIGNMENT.LEFT)
            p_c.paragraph_format.tab_stops.add_tab_stop(Inches(5.0), WD_TAB_ALIGNMENT.LEFT)
            
            runs_data = [
                ("1. " + thai_tokenize(sorted_choices[0]), False),
                ("\t2. " + thai_tokenize(sorted_choices[1]), False),
                ("\t3. " + thai_tokenize(sorted_choices[2]), False),
                ("\t4. " + thai_tokenize(sorted_choices[3]), False)
            ]
            for t_run, b_run in runs_data:
                r_c = p_c.add_run(t_run)
                set_run_font(r_c, bold=b_run)
                
        elif col1_max <= 33 and col2_max <= 36 and overall_max <= 35 and len(sorted_choices) == 4:
            # รูปแบบที่ 2 (2 บรรทัด Tab 3.4")
            p_c1 = doc.add_paragraph()
            p_c1.paragraph_format.space_before = Pt(0)
            p_c1.paragraph_format.space_after = Pt(0)
            p_c1.paragraph_format.line_spacing = 1.0
            p_c1.paragraph_format.left_indent = Inches(0.2)
            p_c1.paragraph_format.keep_with_next = True
            p_c1.paragraph_format.keep_together = True
            p_c1.paragraph_format.tab_stops.add_tab_stop(Inches(3.4), WD_TAB_ALIGNMENT.LEFT)
            
            r1 = p_c1.add_run("1. " + thai_tokenize(sorted_choices[0]))
            set_run_font(r1, bold=False)
            r2 = p_c1.add_run("\t2. " + thai_tokenize(sorted_choices[1]))
            set_run_font(r2, bold=False)
            
            p_c2 = doc.add_paragraph()
            p_c2.paragraph_format.space_before = Pt(0)
            p_c2.paragraph_format.space_after = Pt(0)
            p_c2.paragraph_format.line_spacing = 1.0
            p_c2.paragraph_format.left_indent = Inches(0.2)
            p_c2.paragraph_format.keep_together = True
            p_c2.paragraph_format.tab_stops.add_tab_stop(Inches(3.4), WD_TAB_ALIGNMENT.LEFT)
            
            r3 = p_c2.add_run("3. " + thai_tokenize(sorted_choices[2]))
            set_run_font(r3, bold=False)
            r4 = p_c2.add_run("\t4. " + thai_tokenize(sorted_choices[3]))
            set_run_font(r4, bold=False)
            
        else:
            # รูปแบบที่ 1 (4 บรรทัด)
            for c_idx, c_text in enumerate(sorted_choices):
                p_c = doc.add_paragraph()
                p_c.paragraph_format.space_before = Pt(0)
                p_c.paragraph_format.space_after = Pt(0)
                p_c.paragraph_format.line_spacing = 1.0
                p_c.paragraph_format.left_indent = Inches(0.2)
                p_c.paragraph_format.keep_together = True
                if c_idx < len(sorted_choices) - 1:
                    p_c.paragraph_format.keep_with_next = True
                
                r = p_c.add_run(f"{c_idx+1}. " + thai_tokenize(c_text))
                set_run_font(r, bold=False)

    out_path = os.path.join(BASE_DIR, "Job02_Formatted.docx")
    os.system('taskkill /f /im WINWORD.EXE 2>nul')
    time.sleep(0.5)
    doc.save(out_path)
    print(f"Saved {out_path} successfully.")

if __name__ == "__main__":
    build_job02_docx()
