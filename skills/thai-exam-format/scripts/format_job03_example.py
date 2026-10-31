import os
import re
import sys

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import pythainlp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# อินพุต/เอาต์พุตเลือกได้ผ่าน argv: format_job03.py [input.docx] [output.docx]
INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "Job03.docx")

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

NEGATIVE_WORDS = [
    "ไม่ถูกต้องเหมาะสม", "ไม่ถูกต้อง", "ไม่เหมาะสม", "ไม่ใช่", "ไม่มีประสิทธิภาพ", "ไม่มี",
    "ไม่ปรากฏ", "ไม่จำเป็น", "ไม่ได้", "ไม่ควร", "มิได้", "ยกเว้น", "ไม่"
]

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

def build_job03():
    if not os.path.exists(INPUT_PATH):
        sys.exit(
            f"ไม่พบไฟล์ต้นฉบับ: {INPUT_PATH}\n"
            "ต้องมี Job03.docx (ไฟล์ข้อสอบดิบ) ในโฟลเดอร์งาน หรือระบุ path:\n"
            "  py -3.12 scripts/format_job03.py path/to/Job03.docx [out.docx]"
        )
    raw_doc = docx.Document(INPUT_PATH)
    
    # Extract indicator descriptions from p208
    p208 = raw_doc.paragraphs[208].text
    pattern = r'(ว\s*\d+\.\d+\s*ม\.\d+/\d+)\s*(.*?)(?=(?:ว\s*\d+\.\d+\s*ม\.\d+/\d+)|$)'
    matches = re.findall(pattern, p208)
    ind_desc_map = {}
    for ind, desc in matches:
        key = re.sub(r'\s+', ' ', ind.strip())
        ind_desc_map[key] = desc.strip()
    
    # Parse questions
    questions = []
    current_q = None
    
    for i, p in enumerate(raw_doc.paragraphs):
        text = p.text.strip()
        if not text or i == 208:
            continue
        m = re.match(r'^(\d+)\.\s*(?:\[(.*?)\])?\s*(.*)', text)
        if m:
            if current_q:
                questions.append(current_q)
            current_q = {
                'num': int(m.group(1)),
                'indicator': re.sub(r'\s+', ' ', m.group(2).strip()) if m.group(2) else '',
                'text': m.group(3).strip(),
                'choices': []
            }
        elif current_q and re.match(r'^[ก-ฮa-zA-Z1-4][\.\)]\s*', text):
            c_text = re.sub(r'^[ก-ฮa-zA-Z1-4][\.\)]\s*', '', text).strip()
            current_q['choices'].append(c_text)
            
    if current_q:
        questions.append(current_q)
        
    print(f"Parsed {len(questions)} questions from Job03.")

    # ตรวจสุขภาพการ parse: ตัวเลือกที่ขึ้นต้นด้วย "1." จะถูกอ่านเป็นข้อใหม่
    short = [q["num"] for q in questions if len(q["choices"]) < 4]
    if short:
        print(
            "WARNING: มีข้อที่ parse ตัวเลือกได้ไม่ครบ 4 ข้อ: "
            + ", ".join(map(str, short[:15]))
            + (" ..." if len(short) > 15 else "")
            + "\n  สาเหตุที่พบบ่อย: ตัวเลือกขึ้นต้นด้วย '1.' (จุด) ซึ่งชนกับรูปแบบเลขข้อ"
            " — ใช้ '1)' หรือ 'ก.' แทน"
        )
    
    # Group indicators to find range of questions
    from itertools import groupby
    ind_ranges = []
    for ind_key, g in groupby(questions, key=lambda q: q['indicator']):
        q_list = list(g)
        min_q = q_list[0]['num']
        max_q = q_list[-1]['num']
        r_str = f"{min_q}–{max_q}" if min_q != max_q else f"{min_q}"
        ind_ranges.append((ind_key, r_str, min_q, max_q, q_list))
    
    # Start creating formatted docx
    doc = docx.Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.8)
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    
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
    
    # Header Table (3 cols, invisible borders, bottom divider line)
    tbl_hdr = doc.add_table(rows=3, cols=3)
    tbl_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_hdr_data = [
        [("ข้อสอบวัดผลปลายภาคเรียน", WD_ALIGN_PARAGRAPH.LEFT),
         ("ประจำภาคเรียนที่ 1", WD_ALIGN_PARAGRAPH.CENTER),
         ("ปีการศึกษา 2569", WD_ALIGN_PARAGRAPH.RIGHT)],
        [("วิชาวิทยาศาสตร์พื้นฐาน", WD_ALIGN_PARAGRAPH.LEFT),
         ("รหัสวิชา ว23101", WD_ALIGN_PARAGRAPH.CENTER),
         ("ชั้นมัธยมศึกษาปีที่ 3", WD_ALIGN_PARAGRAPH.RIGHT)],
        [("สอบวันที่ ...... กันยายน 2569", WD_ALIGN_PARAGRAPH.LEFT),
         ("เวลาสอบ 60 นาที", WD_ALIGN_PARAGRAPH.CENTER),
         ("คะแนนเต็ม 40 คะแนน", WD_ALIGN_PARAGRAPH.RIGHT)]
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
        f"1. ข้อสอบเป็นแบบปรนัย จำนวน {len(questions)} ข้อ",
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
        
    # Summary Table: มาตรฐานการเรียนรู้/ตัวชี้วัด (3 cols, center table, single borders)
    # Total rows = 1 (header) + 13 (indicators) = 14 rows
    tbl_sum = doc.add_table(rows=len(ind_ranges)+1, cols=3)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_headers = [("มาตรฐานการเรียนรู้/ตัวชี้วัด", Inches(3.2)), ("ข้อสอบข้อที่", Inches(1.1)), ("หมายเหตุ", Inches(1.2))]
    
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
        set_cell_margins(cell, top=20, bottom=20, left=80, right=80)
        
    for r_idx, (ind_key, r_str, _, _, _) in enumerate(ind_ranges, start=1):
        for c_idx, text in enumerate([ind_key, r_str, ""]):
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
            set_cell_margins(cell, top=20, bottom=20, left=80, right=80)
            
    # Blank line
    p_blank = doc.add_paragraph()
    p_blank.paragraph_format.space_before = Pt(0)
    p_blank.paragraph_format.space_after = Pt(0)
    p_blank.paragraph_format.line_spacing = 1.0
    
    # ================= SIGNATURE SECTION =================
    # Format: 1 Exam Creator (Single layout for all 4 roles)
    # Creator: นายณัฐวัตร ทุมคำ
    tbl_sig = doc.add_table(rows=4, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_sig.rows:
        for c in r.cells:
            c.width = Inches(3.4)
            set_cell_border(c, top=dict(val='none'), bottom=dict(val='none'), left=dict(val='none'), right=dict(val='none'))
            set_cell_margins(c, 0, 0, 0, 0)
            
    signers_1person = [
        ("ผู้ออกข้อสอบ", "( นายณัฐวัตร ทุมคำ )", "          "),
        ("หัวหน้ากลุ่มสาระการเรียนรู้", "( นายรามิล ปัญญพัทธ์ )", "          "),
        ("หัวหน้างานวัดผลโรงเรียน", "( นางจิราพรรณ เรืองพุทธ )", "        "),
        ("รองผู้อำนวยการโรงเรียน", "( นางสาวภัทรพร ประมาตร )", "        ")
    ]
    
    for r_idx, (role, name, space_pad) in enumerate(signers_1person):
        cell = tbl_sig.rows[r_idx].cells[0]
        cell.merge(tbl_sig.rows[r_idx].cells[1])
        
        p_top = cell.paragraphs[0]
        p_top.paragraph_format.space_before = Pt(0)
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
    
    # Top instruction on Page 2
    p_cmd = doc.add_paragraph()
    p_cmd.paragraph_format.space_before = Pt(0)
    p_cmd.paragraph_format.space_after = Pt(0)
    p_cmd.paragraph_format.line_spacing = 1.0
    p_cmd.paragraph_format.left_indent = Pt(0)
    
    r_cmd1 = p_cmd.add_run(thai_tokenize("คำสั่ง"))
    set_run_font(r_cmd1, bold=True)
    r_cmd2 = p_cmd.add_run(" " + thai_tokenize("จงเลือกคำตอบที่ถูกต้องที่สุดเพียงคำตอบเดียว"))
    set_run_font(r_cmd2, bold=False)
    
    is_first_ind = True
    for ind_key, r_str, min_q, max_q, q_list in ind_ranges:
        # Standard header
        desc = ind_desc_map.get(ind_key, "")
        header_text = f"มาตรฐาน/ตัวชี้วัด {ind_key} {desc} (ข้อ {r_str.replace('–', ' - ')})"
        
        p_ind = doc.add_paragraph()
        p_ind.paragraph_format.space_before = Pt(0) if is_first_ind else Pt(16)
        p_ind.paragraph_format.space_after = Pt(0)
        p_ind.paragraph_format.line_spacing = 1.0
        p_ind.paragraph_format.left_indent = Pt(0)
        r_ind = p_ind.add_run(thai_tokenize(header_text))
        set_run_font(r_ind, bold=False)
        is_first_ind = False
        
        for q in q_list:
            q_num = q['num']
            q_text = q['text']
            
            # Question paragraph
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(0)
            p_q.paragraph_format.space_after = Pt(0)
            p_q.paragraph_format.line_spacing = 1.0
            p_q.paragraph_format.left_indent = Pt(0)
            p_q.paragraph_format.keep_with_next = True
            p_q.paragraph_format.keep_together = True
            
            full_q_text = f"{q_num}. {q_text}"
            add_formatted_question_runs(p_q, full_q_text)
            
            choices = q['choices']
            sorted_choices = sorted(choices, key=lambda c: visual_length(c))
            max_v_len = max(visual_length(c) for c in sorted_choices) if sorted_choices else 0
            
            if max_v_len <= 10 and len(sorted_choices) == 4:
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
                    
            elif max_v_len <= 25 and len(sorted_choices) == 4:
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
                    
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE_DIR, "Job03_Formatted.docx")
    try:
        doc.save(out_path)
        print(f"Saved {out_path} successfully.")
    except PermissionError:
        out_path = out_path.replace(".docx", "_v2.docx")
        doc.save(out_path)
        print(f"File was locked by Word. Saved as {out_path} instead.")

if __name__ == "__main__":
    build_job03()
