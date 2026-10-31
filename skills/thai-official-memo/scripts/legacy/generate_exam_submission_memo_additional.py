import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from pythainlp import word_tokenize
from pythainlp.corpus import thai_words
from pythainlp.util import dict_trie

# คำประสมและศัพท์เฉพาะทางราชการ/โรงเรียนพูลเจริญวิทยาคม ที่ต้องคงไว้เป็นคำเดียว ห้ามผ่าตัดย่อย
MEMO_COMPOUND_WORDS = {
    'บันทึกข้อความ', 'ส่วนราชการ', 'โรงเรียนพูลเจริญวิทยาคม', 'พูลเจริญวิทยาคม',
    'กลุ่มสาระการเรียนรู้', 'กลุ่มสาระการเรียนรู้ภาษาไทย', 'ภาษาไทย', 'ผู้อำนวยการ',
    'รองผู้อำนวยการ', 'หัวหน้ากลุ่มสาระการเรียนรู้', 'หัวหน้างานวัดผลโรงเรียน',
    'การไปราชการ', 'รายงานผลการไปราชการ', 'การจัดการเรียนรู้', 'การส่งข้อสอบ',
    'วัดผลปลายภาคเรียน', 'ปลายภาคเรียน', 'ปีการศึกษา', 'จึงเรียนมาเพื่อโปรดพิจารณา',
    'จึงเรียนมาเพื่อโปรดทราบ', 'จึงเรียนมาเพื่อโปรดทราบและพิจารณา', 'จึงเรียนมาเพื่อโปรดพิจารณาอนุมัติ', 'ขออนุมัติ',
    'ผู้รายงาน', 'ผู้ขออนุมัติ', 'ชำนาญการพิเศษ', 'ชำนาญการ', 'วิทยฐานะ',
    'รูบริก', 'รูบริกรายบุคคล', 'Rubric', 'คะแนนก่อนเรียน', 'คะแนนหลังเรียน',
    'การคิดวิเคราะห์', 'ผลสัมฤทธิ์', 'ความพึงพอใจ', 'ข้อตกลงในการพัฒนางาน', 'ประเด็นท้าทาย',
    'กลุ่มบริหารวิชาการ', 'หลักสูตรสถานศึกษา', 'ต้นฉบับข้อสอบ', 'เพิ่มเติม'
}

_MEMO_TRIE = dict_trie(set(thai_words()) | MEMO_COMPOUND_WORDS)

def insert_thai_zwsp(text: str) -> str:
    """
    แทรก Zero-Width Space (\u200b) ระดับคำที่มีความหมายสมบูรณ์เท่านั้น (Word-Level Only)
    ป้องกันปัญหาสระลอย (◌ั) และวรรณยุกต์หลุดหาย
    """
    if not text:
        return text
    if not any('\u0e00' <= c <= '\u0e7f' for c in text):
        return text

    clean_text = text.replace('\u200b', '')
    if not clean_text or set(clean_text) == {'.'}:
        return text

    raw_tokens = word_tokenize(clean_text, custom_dict=_MEMO_TRIE, engine='newmm')
    if len(raw_tokens) <= 1:
        return clean_text

    tokens = []
    for t in raw_tokens:
        if len(t) == 1 and '\u0e01' <= t <= '\u0e2e':
            if tokens:
                tokens[-1] += t
            else:
                tokens.append(t)
        elif len(t) == 1 and '\u0e30' <= t <= '\u0e4e':
            if tokens:
                tokens[-1] += t
            else:
                tokens.append(t)
        else:
            if tokens and len(tokens[-1]) == 1 and '\u0e01' <= tokens[-1] <= '\u0e2e':
                tokens[-1] += t
            else:
                tokens.append(t)

    if len(tokens) <= 1:
        return clean_text

    res = []
    for i, token in enumerate(tokens):
        res.append(token)
        if i < len(tokens) - 1:
            next_token = tokens[i + 1]
            if token.endswith((' ', '\t', '\n', '\r')) or next_token.startswith((' ', '\t', '\n', '\r')):
                continue
            if token[-1] in 'เแโใไ' or next_token[0] in 'ะัาำิีึืฺุู็่้๊๋์ํ๎':
                continue
            res.append('\u200b')

    out = ''.join(res)
    out = re.sub(r'\u200b+([\u0e30-\u0e3a\u0e47-\u0e4e])', r'\1', out)
    out = re.sub(r'([\u0e40-\u0e44])\u200b+', r'\1', out)
    out = re.sub(r'\u200b+\s+', ' ', out)
    out = re.sub(r'\s+\u200b+', ' ', out)
    out = re.sub(r'[●•\-\.,;:!?()\"\']\u200b+', lambda m: m.group(0).replace('\u200b', ''), out)
    out = re.sub(r'\u200b+[●•\-\.,;:!?()\"\']', lambda m: m.group(0).replace('\u200b', ''), out)
    out = re.sub(r'\u200b{2,}', '\u200b', out)
    out = out.strip('\u200b')
    return out

def set_font(run, name='TH Sarabun New', size=16, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)
    
    sz_val = str(int(size * 2))
    for tag in ['w:sz', 'w:szCs']:
        el = rPr.find(qn(tag))
        if el is None:
            el = parse_xml(f'<{tag} {nsdecls("w")}/>')
            rPr.append(el)
        el.set(qn('w:val'), sz_val)
        
    if bold:
        for b_tag in ['w:b', 'w:bCs']:
            if rPr.find(qn(b_tag)) is None:
                rPr.append(parse_xml(f'<{b_tag} {nsdecls("w")}/>'))
    else:
        for b_tag in ['w:b', 'w:bCs']:
            el = rPr.find(qn(b_tag))
            if el is not None:
                rPr.remove(el)
                
    lang = rPr.find(qn('w:lang'))
    if lang is None:
        lang = parse_xml(f'<w:lang {nsdecls("w")}/>')
        rPr.append(lang)
    lang.set(qn('w:val'), 'th-TH')
    lang.set(qn('w:bidi'), 'th-TH')
    lang.set(qn('w:eastAsia'), 'th-TH')

def set_cell_margins(cell, top=30, bottom=30, left=40, right=40):
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
        f'<w:top w:val="{kwargs.get("top", "single")}" w:sz="{kwargs.get("top_sz", "4")}" w:space="0" w:color="{kwargs.get("top_color", "000000")}"/>'
        f'<w:left w:val="{kwargs.get("left", "single")}" w:sz="{kwargs.get("left_sz", "4")}" w:space="0" w:color="{kwargs.get("left_color", "000000")}"/>'
        f'<w:bottom w:val="{kwargs.get("bottom", "single")}" w:sz="{kwargs.get("bottom_sz", "4")}" w:space="0" w:color="{kwargs.get("bottom_color", "000000")}"/>'
        f'<w:right w:val="{kwargs.get("right", "single")}" w:sz="{kwargs.get("right_sz", "4")}" w:space="0" w:color="{kwargs.get("right_color", "000000")}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def fix_document_root_causes(doc):
    styles_elem = doc.styles.element

    # 1. docDefaults
    docDefaults = styles_elem.find(qn('w:docDefaults'))
    if docDefaults is None:
        docDefaults = parse_xml(f'<w:docDefaults {nsdecls("w")}/>')
        styles_elem.insert(0, docDefaults)
    rPrDefault = docDefaults.find(qn('w:rPrDefault'))
    if rPrDefault is None:
        rPrDefault = parse_xml(f'<w:rPrDefault {nsdecls("w")}/>')
        docDefaults.append(rPrDefault)
    rPr = rPrDefault.find(qn('w:rPr'))
    if rPr is None:
        rPr = parse_xml(f'<w:rPr {nsdecls("w")}/>')
        rPrDefault.append(rPr)

    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), 'TH Sarabun New')
    rFonts.set(qn('w:hAnsi'), 'TH Sarabun New')
    rFonts.set(qn('w:cs'), 'TH Sarabun New')
    rFonts.set(qn('w:eastAsia'), 'TH Sarabun New')

    for sz_tag in ['w:sz', 'w:szCs']:
        el = rPr.find(qn(sz_tag))
        if el is None:
            el = parse_xml(f'<{sz_tag} {nsdecls("w")}/>')
            rPr.append(el)
        el.set(qn('w:val'), '32')

    lang = rPr.find(qn('w:lang'))
    if lang is None:
        lang = parse_xml(f'<w:lang {nsdecls("w")}/>')
        rPr.append(lang)
    lang.set(qn('w:val'), 'th-TH')
    lang.set(qn('w:bidi'), 'th-TH')
    lang.set(qn('w:eastAsia'), 'th-TH')

    # 2. Normal Style
    for s in styles_elem.findall(qn('w:style')):
        if s.attrib.get(qn('w:styleId')) == 'Normal':
            s_rPr = s.find(qn('w:rPr'))
            if s_rPr is None:
                s_rPr = parse_xml(f'<w:rPr {nsdecls("w")}/>')
                s.append(s_rPr)
            s_rFonts = s_rPr.find(qn('w:rFonts'))
            if s_rFonts is None:
                s_rFonts = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
                s_rPr.append(s_rFonts)
            s_rFonts.set(qn('w:ascii'), 'TH Sarabun New')
            s_rFonts.set(qn('w:hAnsi'), 'TH Sarabun New')
            s_rFonts.set(qn('w:cs'), 'TH Sarabun New')
            s_rFonts.set(qn('w:eastAsia'), 'TH Sarabun New')

            for sz_tag in ['w:sz', 'w:szCs']:
                el = s_rPr.find(qn(sz_tag))
                if el is None:
                    el = parse_xml(f'<{sz_tag} {nsdecls("w")}/>')
                    s_rPr.append(el)
                el.set(qn('w:val'), '32')

            s_lang = s_rPr.find(qn('w:lang'))
            if s_lang is None:
                s_lang = parse_xml(f'<w:lang {nsdecls("w")}/>')
                s_rPr.append(s_lang)
            s_lang.set(qn('w:val'), 'th-TH')
            s_lang.set(qn('w:bidi'), 'th-TH')
            s_lang.set(qn('w:eastAsia'), 'th-TH')
            break

    # 3. Synchronize All Paragraphs and Runs
    all_paras = list(doc.paragraphs)
    seen_cells = set()
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                if id(cell) in seen_cells:
                    continue
                seen_cells.add(id(cell))
                all_paras.extend(cell.paragraphs)

    from collections import Counter
    for p in all_paras:
        p_runs = p.runs
        p_bold = False
        p_size_val = '32'

        if p_runs:
            bold_count = 0
            sizes = []
            for r in p_runs:
                rPr = r._r.get_or_add_rPr()

                rFonts = rPr.find(qn('w:rFonts'))
                if rFonts is None:
                    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
                    rPr.append(rFonts)
                rFonts.set(qn('w:ascii'), 'TH Sarabun New')
                rFonts.set(qn('w:hAnsi'), 'TH Sarabun New')
                rFonts.set(qn('w:cs'), 'TH Sarabun New')
                rFonts.set(qn('w:eastAsia'), 'TH Sarabun New')

                lang = rPr.find(qn('w:lang'))
                if lang is None:
                    lang = parse_xml(f'<w:lang {nsdecls("w")}/>')
                    rPr.append(lang)
                lang.set(qn('w:val'), 'th-TH')
                lang.set(qn('w:bidi'), 'th-TH')
                lang.set(qn('w:eastAsia'), 'th-TH')

                has_b = rPr.find(qn('w:b')) is not None or r.bold is True
                if has_b:
                    bold_count += 1
                    bCs = rPr.find(qn('w:bCs'))
                    if bCs is None:
                        bCs = parse_xml(f'<w:bCs {nsdecls("w")}/>')
                        rPr.append(bCs)

                sz = rPr.find(qn('w:sz'))
                szCs = rPr.find(qn('w:szCs'))
                if sz is not None:
                    s_val = sz.attrib.get(qn('w:val'), '32')
                    sizes.append(s_val)
                    if szCs is None:
                        szCs = parse_xml(f'<w:szCs {nsdecls("w")}/>')
                        rPr.append(szCs)
                    szCs.set(qn('w:val'), s_val)
                elif szCs is not None:
                    s_val = szCs.attrib.get(qn('w:val'), '32')
                    sizes.append(s_val)
                    if sz is None:
                        sz = parse_xml(f'<w:sz {nsdecls("w")}/>')
                        rPr.append(sz)
                    sz.set(qn('w:val'), s_val)
                elif r.font.size:
                    s_val = str(int(r.font.size.pt * 2))
                    sizes.append(s_val)
                    if sz is None:
                        sz = parse_xml(f'<w:sz {nsdecls("w")}/>')
                        rPr.append(sz)
                    sz.set(qn('w:val'), s_val)
                    if szCs is None:
                        szCs = parse_xml(f'<w:szCs {nsdecls("w")}/>')
                        rPr.append(szCs)
                    szCs.set(qn('w:val'), s_val)
                else:
                    sizes.append('32')

            if bold_count >= (len(p_runs) / 2):
                p_bold = True
            if sizes:
                p_size_val = Counter(sizes).most_common(1)[0][0]

        pPr = p._p.get_or_add_pPr()
        p_rPr = pPr.find(qn('w:rPr'))
        if p_rPr is None:
            p_rPr = parse_xml(f'<w:rPr {nsdecls("w")}/>')
            pPr.append(p_rPr)

        pr_fonts = p_rPr.find(qn('w:rFonts'))
        if pr_fonts is None:
            pr_fonts = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
            p_rPr.append(pr_fonts)
        pr_fonts.set(qn('w:ascii'), 'TH Sarabun New')
        pr_fonts.set(qn('w:hAnsi'), 'TH Sarabun New')
        pr_fonts.set(qn('w:cs'), 'TH Sarabun New')
        pr_fonts.set(qn('w:eastAsia'), 'TH Sarabun New')

        pr_sz = p_rPr.find(qn('w:sz'))
        if pr_sz is None:
            pr_sz = parse_xml(f'<w:sz {nsdecls("w")}/>')
            p_rPr.append(pr_sz)
        pr_sz.set(qn('w:val'), p_size_val)

        pr_szCs = p_rPr.find(qn('w:szCs'))
        if pr_szCs is None:
            pr_szCs = parse_xml(f'<w:szCs {nsdecls("w")}/>')
            p_rPr.append(pr_szCs)
        pr_szCs.set(qn('w:val'), p_size_val)

        if p_bold:
            if p_rPr.find(qn('w:b')) is None:
                p_rPr.append(parse_xml(f'<w:b {nsdecls("w")}/>'))
            if p_rPr.find(qn('w:bCs')) is None:
                p_rPr.append(parse_xml(f'<w:bCs {nsdecls("w")}/>'))
        else:
            b_el = p_rPr.find(qn('w:b'))
            if b_el is not None: p_rPr.remove(b_el)
            bCs_el = p_rPr.find(qn('w:bCs'))
            if bCs_el is not None: p_rPr.remove(bCs_el)

        pr_lang = p_rPr.find(qn('w:lang'))
        if pr_lang is None:
            pr_lang = parse_xml(f'<w:lang {nsdecls("w")}/>')
            p_rPr.append(pr_lang)
        pr_lang.set(qn('w:val'), 'th-TH')
        pr_lang.set(qn('w:bidi'), 'th-TH')
        pr_lang.set(qn('w:eastAsia'), 'th-TH')

def create_additional_exam_memo():
    doc = Document()
    
    # Hide spelling and grammar errors
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
    # PAGE 1: หนังสือนำส่งบันทึกข้อความ (เพิ่มเติม)
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

    # Garuda Logo
    garuda_cell = header_table.cell(0, 0)
    p_krut = garuda_cell.paragraphs[0]
    p_krut.paragraph_format.space_before = Pt(0)
    p_krut.paragraph_format.space_after = Pt(0)
    p_krut.paragraph_format.line_spacing = 1.0
    r_krut = p_krut.add_run()
    
    # Check multiple possible paths for logo-Krut.png
    possible_krut_paths = [
        r'd:\MEGA\บันทึกข้อความ\logo-Krut.png',
        r'd:\MEGA\บันทึกข้อความ\บันทึกข้อความ\logo-Krut.png',
        r'logo-Krut.png'
    ]
    for kp in possible_krut_paths:
        if os.path.exists(kp):
            r_krut.add_picture(kp, height=Cm(1.5))
            break

    # Center Title "บันทึกข้อความ"
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
    r_g2 = p_gov.add_run(insert_thai_zwsp("กลุ่มสาระการเรียนรู้ภาษาไทย โรงเรียนพูลเจริญวิทยาคม"))
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
    r_dt2 = p_no_date.add_run(insert_thai_zwsp("15 กันยายน 2569"))
    set_font(r_dt2, size=16)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(1)
    p_sub.paragraph_format.space_after = Pt(1)
    p_sub.paragraph_format.line_spacing = 1.0
    r_s1 = p_sub.add_run("เรื่อง  ")
    set_font(r_s1, size=16, bold=True)
    r_s2 = p_sub.add_run(insert_thai_zwsp("ส่งข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569 (เพิ่มเติม)"))
    set_font(r_s2, size=16, bold=False)

    # Divider Line (8 pt paragraph, solid black border)
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(2)
    p_div.paragraph_format.line_spacing = 1.0
    r_div = p_div.add_run()
    set_font(r_div, size=8)
    pPr = p_div._p.get_or_add_pPr()
    pBdr = parse_xml(r'<w:pBdr %s><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>' % nsdecls('w'))
    pPr.append(pBdr)

    # 3. Addressee & Enclosure
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(2)
    p_to.paragraph_format.space_after = Pt(1)
    p_to.paragraph_format.line_spacing = 1.0
    r_t1 = p_to.add_run("เรียน  ")
    set_font(r_t1, size=16, bold=True)
    r_t2 = p_to.add_run(insert_thai_zwsp("ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_t2, size=16)

    p_att = doc.add_paragraph()
    p_att.paragraph_format.space_before = Pt(1)
    p_att.paragraph_format.space_after = Pt(3)
    p_att.paragraph_format.line_spacing = 1.0
    r_a1 = p_att.add_run("สิ่งที่ส่งมาด้วย  ")
    set_font(r_a1, size=16, bold=True)
    r_a2 = p_att.add_run(insert_thai_zwsp("แบบสรุปการส่งข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569 (เพิ่มเติม) จำนวน 1 ชุด"))
    set_font(r_a2, size=16)

    # 4. Body Paragraphs
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b1.paragraph_format.first_line_indent = Cm(2.5)
    p_b1.paragraph_format.space_before = Pt(2)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.paragraph_format.line_spacing = 1.0
    r_b1 = p_b1.add_run(insert_thai_zwsp(
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
    r_b2 = p_b2.add_run(insert_thai_zwsp(
        "บัดนี้ ครูผู้สอนกลุ่มสาระการเรียนรู้ภาษาไทย ที่ยังไม่ได้ส่งต้นฉบับข้อสอบในคราวที่แล้ว "
        "ได้ดำเนินการจัดทำต้นฉบับข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569 เสร็จสิ้นเรียบร้อยแล้ว "
        "จึงขอส่งต้นฉบับข้อสอบวัดผลปลายภาคเรียนดังกล่าว (เพิ่มเติม) ตามแบบสรุปรายการที่แนบมาพร้อมนี้"
    ))
    set_font(r_b2, size=16)

    p_b3 = doc.add_paragraph()
    p_b3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b3.paragraph_format.first_line_indent = Cm(2.5)
    p_b3.paragraph_format.space_before = Pt(2)
    p_b3.paragraph_format.space_after = Pt(6)
    p_b3.paragraph_format.line_spacing = 1.0
    r_b3 = p_b3.add_run(insert_thai_zwsp("จึงเรียนมาเพื่อโปรดทราบและพิจารณา"))
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
    # PAGE 2: ตารางสรุปการส่งข้อสอบ (เพิ่มเติม)
    # -------------------------------------------------------------
    doc.add_page_break()

    # Title on Page 2
    p_p2_t1 = doc.add_paragraph()
    p_p2_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p2_t1.paragraph_format.space_before = Pt(0)
    p_p2_t1.paragraph_format.space_after = Pt(0)
    p_p2_t1.paragraph_format.line_spacing = 1.0
    r_p2_1 = p_p2_t1.add_run(insert_thai_zwsp("แบบสรุปการส่งข้อสอบวัดผลปลายภาคเรียนที่ 1 ปีการศึกษา 2569 (เพิ่มเติม)"))
    set_font(r_p2_1, size=16, bold=True)

    p_p2_t2 = doc.add_paragraph()
    p_p2_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p2_t2.paragraph_format.space_before = Pt(0)
    p_p2_t2.paragraph_format.space_after = Pt(4)
    p_p2_t2.paragraph_format.line_spacing = 1.0
    r_p2_2 = p_p2_t2.add_run(insert_thai_zwsp("กลุ่มสาระการเรียนรู้ภาษาไทย โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_p2_2, size=15, bold=True)

    # Table Data: เฉพาะคนที่ยังไม่ส่งคราวที่แล้ว (5 รายวิชา)
    additional_data = [
        # (Grade, Code, Name, Teachers List)
        ("ม.1", "ท20213", "การอ่านเบื้องต้น", ["นางสาวอิงอร สิทธิจินดา"]),
        ("ม.1", "ท20208", "การเขียนเบื้องต้น", ["นายชินกร ศิริโยธา"]),
        ("ม.3", "ท23101", "ภาษาไทยพื้นฐาน", ["1. นางวรางคณา ศรีม่วง", "2. นายเฉลิมชาติ ภูผันผิน", "3. นายอภิชา พุ่มพวง"]),
        ("ม.4", "ท31101", "ภาษาไทยพื้นฐาน", ["นายสุริยา ก่อบุญ"]),
        ("ม.5", "ท30215", "ภาษาไทยเพื่อการแสดง 1", ["นายจิรวัฒน์ ศรีวโร"]),
    ]

    # Create Table (2 Header rows + 5 Data rows = 7 rows, 8 columns)
    # [ลำดับ: 1.1cm, รหัสวิชา: 1.8cm, ชื่อวิชา: 4.1cm, ระดับชั้น: 1.3cm, ครูผู้สอน: 4.8cm, ส่ง: 1.0cm, ไม่ส่ง: 1.0cm, หมายเหตุ: 1.6cm]
    col_w = [Cm(1.1), Cm(1.8), Cm(4.1), Cm(1.3), Cm(4.8), Cm(1.0), Cm(1.0), Cm(1.6)]

    table = doc.add_table(rows=2 + len(additional_data), cols=8)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Apply Table Borders B&W (Solid Black 0.5 pt)
    tblPr = table._tbl.tblPr
    borders_xml = f'''
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
    </w:tblBorders>
    '''
    tblBorders = parse_xml(borders_xml)
    existing_borders = tblPr.find(qn('w:tblBorders'))
    if existing_borders is not None:
        tblPr.remove(existing_borders)
    tblPr.append(tblBorders)

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

    for col_idx, text in headers_config:
        c0 = hdr0.cells[col_idx]
        c1 = hdr1.cells[col_idx]
        c0.merge(c1)
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c0.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(insert_thai_zwsp(text))
        set_font(r, size=14, bold=True)
        set_cell_margins(c0, top=40, bottom=40, left=30, right=30)
        set_cell_shading(c0, "F2F2F2")
        set_cell_border(c0, top="single", bottom="single", left="single", right="single")

    # Header for Exam Submission (cols 5 & 6)
    c_sub0 = hdr0.cells[5]
    c_sub1 = hdr0.cells[6]
    c_sub_merged = c_sub0.merge(c_sub1)
    c_sub_merged.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_sub_hdr = c_sub_merged.paragraphs[0]
    p_sub_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub_hdr.paragraph_format.space_before = Pt(2)
    p_sub_hdr.paragraph_format.space_after = Pt(2)
    p_sub_hdr.paragraph_format.line_spacing = 1.0
    r_sh = p_sub_hdr.add_run(insert_thai_zwsp("การส่งข้อสอบ"))
    set_font(r_sh, size=14, bold=True)
    set_cell_margins(c_sub_merged, top=30, bottom=30, left=30, right=30)
    set_cell_shading(c_sub_merged, "F2F2F2")
    set_cell_border(c_sub_merged, top="single", bottom="single", left="single", right="single")

    # Sub-headers in Row 1: "ส่ง", "ไม่ส่ง"
    for col_idx, text in [(5, "ส่ง"), (6, "ไม่ส่ง")]:
        c = hdr1.cells[col_idx]
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(insert_thai_zwsp(text))
        set_font(r, size=13.5, bold=True)
        set_cell_margins(c, top=30, bottom=30, left=20, right=20)
        set_cell_shading(c, "F2F2F2")
        set_cell_border(c, top="single", bottom="single", left="single", right="single")

    # Fill Data Rows
    for idx, (grade, code, name, teachers) in enumerate(additional_data, start=1):
        row_idx = 1 + idx
        row = table.rows[row_idx]
        
        # Apply borders and shading (Pure White FFFFFF)
        for c_i, cell in enumerate(row.cells):
            set_cell_border(cell, top="single", bottom="single", left="single", right="single")
            set_cell_margins(cell, top=35, bottom=35, left=35, right=35)
            set_cell_shading(cell, "FFFFFF")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # Col 0: ลำดับ
        c0 = row.cells[0]
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.0
        r0 = p0.add_run(str(idx))
        set_font(r0, size=14)

        # Col 1: รหัสวิชา
        c1 = row.cells[1]
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(code)
        set_font(r1, size=14, bold=True)

        # Col 2: ชื่อวิชา
        c2 = row.cells[2]
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing = 1.0
        r2 = p2.add_run(insert_thai_zwsp(name))
        set_font(r2, size=14)

        # Col 3: ระดับชั้น
        c3 = row.cells[3]
        p3 = c3.paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_before = Pt(0)
        p3.paragraph_format.space_after = Pt(0)
        p3.paragraph_format.line_spacing = 1.0
        r3 = p3.add_run(grade)
        set_font(r3, size=14)

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
            r4 = p4.add_run(insert_thai_zwsp(t_name))
            set_font(r4, size=14)

        # Col 5: ส่ง -> กฎเหล็ก 2: เครื่องหมาย ✓ กึ่งกลาง ทุกรายวิชา (ห้ามใส่ ☐)
        c5 = row.cells[5]
        p5 = c5.paragraphs[0]
        p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p5.paragraph_format.space_before = Pt(0)
        p5.paragraph_format.space_after = Pt(0)
        p5.paragraph_format.line_spacing = 1.0
        r5 = p5.add_run("✓")
        set_font(r5, size=16, bold=True)

        # Col 6: ไม่ส่ง -> กฎเหล็ก 2: ปล่อยว่างไว้ (ห้ามใส่ ☐)
        c6 = row.cells[6]
        p6 = c6.paragraphs[0]
        p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p6.paragraph_format.space_before = Pt(0)
        p6.paragraph_format.space_after = Pt(0)
        p6.paragraph_format.line_spacing = 1.0

        # Col 7: หมายเหตุ
        c7 = row.cells[7]
        p7 = c7.paragraphs[0]
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p7.paragraph_format.space_before = Pt(0)
        p7.paragraph_format.space_after = Pt(0)
        p7.paragraph_format.line_spacing = 1.0

    # Set column widths for all rows
    for r in table.rows:
        for c_i, w in enumerate(col_w):
            r.cells[c_i].width = w

    # Summary Line Below Table
    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.space_before = Pt(8)
    p_sum.paragraph_format.space_after = Pt(10)
    p_sum.paragraph_format.line_spacing = 1.0
    r_sum = p_sum.add_run(insert_thai_zwsp(
        "สรุปผลการส่งข้อสอบ: รวมจำนวนรายวิชาทั้งหมด 5 รายวิชา    "
        "ส่งครบถ้วน 5 รายวิชา    ยังไม่ส่ง 0 รายวิชา"
    ))
    set_font(r_sum, size=14.5, bold=True)

    # Sign-off block on Page 2 (Single block for Head of Dept / Reporter)
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

    # Apply Root Cause Fixes
    fix_document_root_causes(doc)

    # Target save paths
    out_paths = [
        r'd:\MEGA\บันทึกข้อความ\บันทึกข้อความ\บันทึกข้อความส่งข้อสอบปลายภาคเรียน 1-2569 (เพิ่มเติม).docx',
        r'd:\MEGA\บันทึกข้อความ\บันทึกข้อความ\Output\บันทึกข้อความส่งข้อสอบปลายภาคเรียน 1-2569 (เพิ่มเติม).docx',
        r'd:\MEGA\บันทึกข้อความ\บันทึกข้อความส่งข้อสอบปลายภาคเรียน 1-2569 (เพิ่มเติม).docx'
    ]

    for op in out_paths:
        os.makedirs(os.path.dirname(op), exist_ok=True)
        doc.save(op)
        print(f"Saved: {op}")

    return out_paths[0]

if __name__ == '__main__':
    create_additional_exam_memo()
