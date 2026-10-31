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
    'กลุ่มบริหารวิชาการ', 'หลักสูตรสถานศึกษา', 'บันทึกหลังแผนการจัดการเรียนรู้', 'แผนการจัดการเรียนรู้',
    'บันทึกหลังแผนฯ', 'การส่งบันทึกหลังแผนฯ', 'ระดับชั้น', 'เรื่อง', 'เรียน', 'สิ่งที่ส่งมาด้วย',
    'ออนไลน์', 'คิวอาร์โค้ด', 'กูเกิลไดรฟ์', 'Google Drive', 'QR Code',
    'NDLP', 'ndlp', 'เทคโนโลยีดิจิทัล', 'การจัดการเรียนรู้แห่งชาติ', 'แพลตฟอร์ม'
}

_MEMO_TRIE = dict_trie(set(thai_words()) | MEMO_COMPOUND_WORDS)

def insert_thai_zwsp(text: str) -> str:
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
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)
    rPr.append(rFonts)
    
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'th-TH')
    lang.set(qn('w:bidi'), 'th-TH')
    lang.set(qn('w:eastAsia'), 'th-TH')
    rPr.append(lang)
    
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(int(size * 2)))
    rPr.append(szCs)
    
    if bold:
        bCs = OxmlElement('w:bCs')
        rPr.append(bCs)

def set_cell_margins(cell, top=20, bottom=20, left=40, right=40):
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

    # Style Normal
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

def create_post_lesson_memo():
    doc = Document()
    
    settings = doc.settings.element
    settings.append(OxmlElement('w:hideSpellingErrors'))
    settings.append(OxmlElement('w:hideGrammaticalErrors'))

    # Page Margins & Setup
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
    
    # 1. Header Table (Garuda Logo + Center Title "บันทึกข้อความ")
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
    
    krut_paths = [
        'd:/MEGA/บันทึกข้อความ/logo-Krut.png',
        'd:/MEGA/บันทึกข้อความ/บันทึกข้อความ/logo-Krut.png',
        'h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/logo-Krut.png'
    ]
    krut_found = None
    for kp in krut_paths:
        if os.path.exists(kp):
            krut_found = kp
            break
    if krut_found:
        r_krut.add_picture(krut_found, height=Cm(1.5))

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
    r_dt2 = p_no_date.add_run(insert_thai_zwsp("25 กันยายน 2569"))
    set_font(r_dt2, size=16)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(1)
    p_sub.paragraph_format.space_after = Pt(1)
    p_sub.paragraph_format.line_spacing = 1.0
    r_s1 = p_sub.add_run("เรื่อง  ")
    set_font(r_s1, size=16, bold=True)
    r_s2 = p_sub.add_run(insert_thai_zwsp("สรุปรายงานการส่งบันทึกหลังแผนการจัดการเรียนรู้ กลุ่มสาระการเรียนรู้ภาษาไทย ภาคเรียนที่ 1 ปีการศึกษา 2569"))
    set_font(r_s2, size=16, bold=False)

    # Divider Line (8 pt)
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
    r_a2 = p_att.add_run(insert_thai_zwsp("แบบสรุปการส่งบันทึกหลังแผนการจัดการเรียนรู้ กลุ่มสาระการเรียนรู้ภาษาไทย ภาคเรียนที่ 1 ปีการศึกษา 2569 จำนวน 1 ชุด"))
    set_font(r_a2, size=16)

    # 4. Body Paragraphs
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b1.paragraph_format.first_line_indent = Cm(2.5)
    p_b1.paragraph_format.space_before = Pt(2)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.paragraph_format.line_spacing = 1.0
    r_b1 = p_b1.add_run(insert_thai_zwsp(
        "ตามที่ โรงเรียนพูลเจริญวิทยาคม ได้กำหนดให้ครูผู้สอนจัดทำแผนการจัดการเรียนรู้และบันทึกหลังแผนการจัดการเรียนรู้ "
        "เพื่อใช้เป็นแนวทางในการจัดกิจกรรมการเรียนรู้ และประเมินผลการจัดการเรียนรู้เพื่อพัฒนาคุณภาพผู้เรียน "
        "ภาคเรียนที่ 1 ปีการศึกษา 2569 นั้น"
    ))
    set_font(r_b1, size=16)

    p_b2 = doc.add_paragraph()
    p_b2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_b2.paragraph_format.first_line_indent = Cm(2.5)
    p_b2.paragraph_format.space_before = Pt(2)
    p_b2.paragraph_format.space_after = Pt(2)
    p_b2.paragraph_format.line_spacing = 1.0
    r_b2 = p_b2.add_run(insert_thai_zwsp(
        "บัดนี้ ครูผู้สอนกลุ่มสาระการเรียนรู้ภาษาไทย ได้ดำเนินการจัดทำบันทึกหลังแผนการจัดการเรียนรู้ "
        "จึงขอส่งเอกสารดังกล่าวตามแบบสรุปรายการที่แนบมาพร้อมนี้"
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

    # Spacing before signature
    p_sp1 = doc.add_paragraph()
    p_sp1.paragraph_format.space_before = Pt(16)
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
    # PAGE 2: ตารางสรุปการส่งบันทึกหลังแผนการจัดการเรียนรู้
    # -------------------------------------------------------------
    doc.add_page_break()

    # Title on Page 2
    p_p2_t1 = doc.add_paragraph()
    p_p2_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p2_t1.paragraph_format.space_before = Pt(0)
    p_p2_t1.paragraph_format.space_after = Pt(0)
    p_p2_t1.paragraph_format.line_spacing = 1.0
    r_p2_1 = p_p2_t1.add_run(insert_thai_zwsp("แบบสรุปการส่งบันทึกหลังแผนการจัดการเรียนรู้ กลุ่มสาระการเรียนรู้ภาษาไทย ภาคเรียนที่ 1 ปีการศึกษา 2569"))
    set_font(r_p2_1, size=16, bold=True)

    p_p2_t2 = doc.add_paragraph()
    p_p2_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p2_t2.paragraph_format.space_before = Pt(0)
    p_p2_t2.paragraph_format.space_after = Pt(3)
    p_p2_t2.paragraph_format.line_spacing = 1.0
    r_p2_2 = p_p2_t2.add_run(insert_thai_zwsp("กลุ่มสาระการเรียนรู้ภาษาไทย โรงเรียนพูลเจริญวิทยาคม"))
    set_font(r_p2_2, size=15, bold=True)

    # Data definition for 14 Teachers
    teachers_data = [
        (
            "1",
            "นายรามิล ปัญญพัทธ์",
            [
                ("ท30217", "ภาษาไทยกับการผลิตสื่อร่วมสมัย 1", "ม.6", True, "ออนไลน์"),
                ("ท33101", "ภาษาไทยพื้นฐาน 5", "ม.6", True, "ออนไลน์")
            ]
        ),
        (
            "2",
            "นางวรางคณา ศรีม่วง",
            [
                ("ท23101", "ภาษาไทยพื้นฐาน 5", "ม.3", False, "")
            ]
        ),
        (
            "3",
            "นายอภิชา พุ่มพวง",
            [
                ("ท23101", "ภาษาไทยพื้นฐาน 5", "ม.3", True, "")
            ]
        ),
        (
            "4",
            "นางสาวกมลวรรณ สังข์ทอง",
            [
                ("ท32101", "ภาษาไทยพื้นฐาน 3", "ม.5", True, "ออนไลน์")
            ]
        ),
        (
            "5",
            "นายสุริยา ก่อบุญ",
            [
                ("ท31101", "ภาษาไทยพื้นฐาน 1", "ม.4", False, "")
            ]
        ),
        (
            "6",
            "นายชินกร ศิริโยธา",
            [
                ("ท20208", "การเขียนเบื้องต้น", "ม.1", False, ""),
                ("ท21101", "ภาษาไทยพื้นฐาน 1", "ม.1", False, "")
            ]
        ),
        (
            "7",
            "นางสาววนิชญา เชียงน้อย",
            [
                ("ท22101", "ภาษาไทยพื้นฐาน 3", "ม.2", True, "ออนไลน์")
            ]
        ),
        (
            "8",
            "นางสาวชื่นฤดี หรับหลี",
            [
                ("ท20212", "การพูดเบื้องต้น", "ม.3", True, "ออนไลน์"),
                ("ท22101", "ภาษาไทยพื้นฐาน 3", "ม.2", True, "ออนไลน์")
            ]
        ),
        (
            "9",
            "นายเฉลิมชาติ ภูผันผิน",
            [
                ("ท23101", "ภาษาไทยพื้นฐาน 5", "ม.3", False, "")
            ]
        ),
        (
            "10",
            "นางสาวอิงอร สิทธิจินดา",
            [
                ("ท22101", "ภาษาไทยพื้นฐาน 3", "ม.2", True, "ออนไลน์"),
                ("ท20213", "การอ่านเบื้องต้น", "ม.1", True, "ออนไลน์")
            ]
        ),
        (
            "11",
            "นายจิรวัฒน์ ศรีวโร",
            [
                ("ท30215", "ภาษาไทยเพื่อการแสดง 1", "ม.5", False, ""),
                ("ท21101", "ภาษาไทยพื้นฐาน 1", "ม.1", False, "")
            ]
        ),
        (
            "12",
            "นางสาวศุภนุช บุตรดี",
            [
                ("ท30213", "การอ่านวรรณกรรมไทยเชิงวิเคราะห์ 1", "ม.4", False, ""),
                ("ท21101", "ภาษาไทยพื้นฐาน 1", "ม.1", True, "")
            ]
        ),
        (
            "13",
            "นางสาวนันทกาญจน์ เรืองกระจาย",
            [
                ("ท20205", "การศึกษานิทาน", "ม.3", False, ""),
                ("ท20214", "การใช้ห้องสมุดเบื้องต้น 1", "ม.1", False, "")
            ]
        ),
        (
            "14",
            "นางสาววรวัลภ์ นิตยระวีวาร",
            [
                ("ท20210", "ศึกษาวรรณคดี", "ม.2", False, ""),
                ("ท20216", "การส่งเสริมการอ่านและการเรียนรู้ในห้องสมุด 1", "ม.2", False, "")
            ]
        ),
    ]

    col_w = [Cm(0.9), Cm(4.3), Cm(1.7), Cm(5.1), Cm(1.4), Cm(1.0), Cm(1.0), Cm(1.8)]

    table = doc.add_table(rows=2 + len(teachers_data), cols=8)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    hdr0 = table.rows[0]
    hdr1 = table.rows[1]

    for r in [hdr0, hdr1]:
        for i, w in enumerate(col_w):
            r.cells[i].width = w

    headers_vertical = [
        (0, "ลำดับ"),
        (1, "ครูผู้สอน"),
        (2, "รหัสวิชา"),
        (3, "ชื่อวิชา"),
        (4, "ระดับชั้น"),
        (7, "หมายเหตุ"),
    ]

    for col_idx, text in headers_vertical:
        c0 = hdr0.cells[col_idx]
        c1 = hdr1.cells[col_idx]
        c0.merge(c1)
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c0.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(insert_thai_zwsp(text))
        set_font(r, size=14, bold=True)
        set_cell_margins(c0, top=20, bottom=20, left=15, right=15)
        set_cell_shading(c0, "F0F0F0")
        set_cell_border(c0, top="single", bottom="single", left="single", right="single")

    c_sub_parent = hdr0.cells[5]
    c_sub_parent.merge(hdr0.cells[6])
    c_sub_parent.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_sp = c_sub_parent.paragraphs[0]
    p_sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sp.paragraph_format.space_before = Pt(1)
    p_sp.paragraph_format.space_after = Pt(1)
    p_sp.paragraph_format.line_spacing = 1.0
    r_sp = p_sp.add_run(insert_thai_zwsp("การส่งบันทึกหลังแผนฯ"))
    set_font(r_sp, size=13, bold=True)
    set_cell_margins(c_sub_parent, top=20, bottom=20, left=10, right=10)
    set_cell_shading(c_sub_parent, "F0F0F0")
    set_cell_border(c_sub_parent, top="single", bottom="single", left="single", right="single")

    for col_idx, text in [(5, "ส่ง"), (6, "ไม่ส่ง")]:
        c = hdr1.cells[col_idx]
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(insert_thai_zwsp(text))
        set_font(r, size=14, bold=True)
        set_cell_margins(c, top=20, bottom=20, left=10, right=10)
        set_cell_shading(c, "F0F0F0")
        set_cell_border(c, top="single", bottom="single", left="single", right="single")

    total_teachers = len(teachers_data)
    submitted_teachers = 0
    total_courses = 0
    submitted_courses = 0

    for row_idx, (t_no, t_name, courses) in enumerate(teachers_data, start=2):
        row = table.rows[row_idx]
        
        has_submitted_any = any(c[3] for c in courses)
        if has_submitted_any:
            submitted_teachers += 1
        
        total_courses += len(courses)
        submitted_courses += sum(1 for c in courses if c[3])

        for i, w in enumerate(col_w):
            row.cells[i].width = w

        for cell in row.cells:
            set_cell_border(cell, top="single", bottom="single", left="single", right="single")
            set_cell_shading(cell, "FFFFFF")
            set_cell_margins(cell, top=14, bottom=14, left=25, right=25)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # Col 0: ลำดับ
        c0 = row.cells[0]
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.0
        r0 = p0.add_run(t_no)
        set_font(r0, size=14)

        # Col 1: ครูผู้สอน
        c1 = row.cells[1]
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(insert_thai_zwsp(t_name))
        set_font(r1, size=13.5)

        # Col 2: รหัสวิชา
        c2 = row.cells[2]
        c2.paragraphs[0].text = ""
        for ci, c_info in enumerate(courses):
            c_code = c_info[0]
            p2 = c2.paragraphs[0] if ci == 0 else c2.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p2.paragraph_format.space_before = Pt(0)
            p2.paragraph_format.space_after = Pt(0)
            p2.paragraph_format.line_spacing = 1.0
            r2 = p2.add_run(c_code)
            set_font(r2, size=14, bold=True)

        # Col 3: ชื่อวิชา
        c3 = row.cells[3]
        c3.paragraphs[0].text = ""
        for ci, c_info in enumerate(courses):
            c_name = c_info[1]
            p3 = c3.paragraphs[0] if ci == 0 else c3.add_paragraph()
            p3.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p3.paragraph_format.space_before = Pt(0)
            p3.paragraph_format.space_after = Pt(0)
            p3.paragraph_format.line_spacing = 1.0
            r3 = p3.add_run(insert_thai_zwsp(c_name))
            set_font(r3, size=13.5)

        # Col 4: ระดับชั้น
        c4 = row.cells[4]
        c4.paragraphs[0].text = ""
        for ci, c_info in enumerate(courses):
            c_grade = c_info[2]
            p4 = c4.paragraphs[0] if ci == 0 else c4.add_paragraph()
            p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p4.paragraph_format.space_before = Pt(0)
            p4.paragraph_format.space_after = Pt(0)
            p4.paragraph_format.line_spacing = 1.0
            r4 = p4.add_run(c_grade)
            set_font(r4, size=14)

        # Col 5: ส่ง
        c5 = row.cells[5]
        c5.paragraphs[0].text = ""
        for ci, c_info in enumerate(courses):
            is_sub = c_info[3]
            p5 = c5.paragraphs[0] if ci == 0 else c5.add_paragraph()
            p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p5.paragraph_format.space_before = Pt(0)
            p5.paragraph_format.space_after = Pt(0)
            p5.paragraph_format.line_spacing = 1.0
            if is_sub:
                r5 = p5.add_run("✓")
                set_font(r5, size=14, bold=True)

        # Col 6: ไม่ส่ง
        c6 = row.cells[6]
        c6.paragraphs[0].text = ""
        for ci, c_info in enumerate(courses):
            p6 = c6.paragraphs[0] if ci == 0 else c6.add_paragraph()
            p6.text = ""
            p6.paragraph_format.space_before = Pt(0)
            p6.paragraph_format.space_after = Pt(0)
            p6.paragraph_format.line_spacing = 1.0

        # Col 7: หมายเหตุ
        c7 = row.cells[7]
        c7.paragraphs[0].text = ""
        for ci, c_info in enumerate(courses):
            c_note = c_info[4]
            p7 = c7.paragraphs[0] if ci == 0 else c7.add_paragraph()
            p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p7.paragraph_format.space_before = Pt(0)
            p7.paragraph_format.space_after = Pt(0)
            p7.paragraph_format.line_spacing = 1.0
            if c_note:
                r7 = p7.add_run(insert_thai_zwsp(c_note))
                set_font(r7, size=13.5)

    # Summary Paragraph under Table
    unsubmitted_teachers = total_teachers - submitted_teachers
    unsubmitted_courses = total_courses - submitted_courses
    
    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.space_before = Pt(4)
    p_sum.paragraph_format.space_after = Pt(6)
    p_sum.paragraph_format.line_spacing = 1.0
    r_sum1 = p_sum.add_run(insert_thai_zwsp("สรุปผลการส่งบันทึกหลังแผนการจัดการเรียนรู้: "))
    set_font(r_sum1, size=14, bold=True)
    summary_text = f"รวมจำนวนครูผู้สอนทั้งหมด {total_teachers} คน ({total_courses} รายวิชา)    ส่งแล้ว {submitted_teachers} คน ({submitted_courses} รายวิชา)    ยังไม่ส่ง {unsubmitted_teachers} คน ({unsubmitted_courses} รายวิชา)"
    r_sum2 = p_sum.add_run(insert_thai_zwsp(summary_text))
    set_font(r_sum2, size=14, bold=False)

    # Signature Block on Page 2
    sig_p2_table = doc.add_table(rows=1, cols=2)
    sig_p2_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_p2_table.autofit = False

    for row in sig_p2_table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
            tcPr.append(tcBorders)

    sig_p2_table.rows[0].cells[0].width = Cm(6.5)
    sig_p2_table.rows[0].cells[1].width = Cm(10.5)

    cell_sig2 = sig_p2_table.cell(0, 1)
    p_s2_1 = cell_sig2.paragraphs[0]
    p_s2_1.paragraph_format.space_before = Pt(0)
    p_s2_1.paragraph_format.space_after = Pt(0)
    p_s2_1.paragraph_format.line_spacing = 1.0
    r_s2_1 = p_s2_1.add_run("ลงชื่อ..........................................................ผู้รายงาน")
    set_font(r_s2_1, size=15)

    p_s2_2 = cell_sig2.add_paragraph()
    p_s2_2.paragraph_format.space_before = Pt(0)
    p_s2_2.paragraph_format.space_after = Pt(0)
    p_s2_2.paragraph_format.line_spacing = 1.0
    p_s2_2.paragraph_format.left_indent = Cm(1.3)
    r_s2_2 = p_s2_2.add_run("(นายรามิล ปัญญพัทธ์)")
    set_font(r_s2_2, size=15)

    p_s2_3 = cell_sig2.add_paragraph()
    p_s2_3.paragraph_format.space_before = Pt(0)
    p_s2_3.paragraph_format.space_after = Pt(0)
    p_s2_3.paragraph_format.line_spacing = 1.0
    p_s2_3.paragraph_format.left_indent = Cm(0.35)
    r_s2_3 = p_s2_3.add_run("หัวหน้ากลุ่มสาระการเรียนรู้ภาษาไทย")
    set_font(r_s2_3, size=15)

    # -------------------------------------------------------------
    # PAGE 3: ภาคผนวก คิวอาร์โค้ด (QR Code) Google Drive สำหรับส่งออนไลน์
    # -------------------------------------------------------------
    doc.add_page_break()

    # Title Header on Page 3
    p_p3_t1 = doc.add_paragraph()
    p_p3_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p3_t1.paragraph_format.space_before = Pt(0)
    p_p3_t1.paragraph_format.space_after = Pt(2)
    p_p3_t1.paragraph_format.line_spacing = 1.0
    r_p3_1 = p_p3_t1.add_run(insert_thai_zwsp("คิวอาร์โค้ด (QR Code) สำหรับเข้าถึงเอกสารบันทึกหลังแผนการจัดการเรียนรู้"))
    set_font(r_p3_1, size=18, bold=True)

    p_p3_t2 = doc.add_paragraph()
    p_p3_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p3_t2.paragraph_format.space_before = Pt(0)
    p_p3_t2.paragraph_format.space_after = Pt(2)
    p_p3_t2.paragraph_format.line_spacing = 1.0
    r_p3_2 = p_p3_t2.add_run(insert_thai_zwsp("การส่งเอกสารในรูปแบบออนไลน์ผ่านระบบ Google Drive"))
    set_font(r_p3_2, size=16, bold=True)

    p_p3_t3 = doc.add_paragraph()
    p_p3_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_p3_t3.paragraph_format.space_before = Pt(0)
    p_p3_t3.paragraph_format.space_after = Pt(12)
    p_p3_t3.paragraph_format.line_spacing = 1.0
    r_p3_3 = p_p3_t3.add_run(insert_thai_zwsp("กลุ่มสาระการเรียนรู้ภาษาไทย โรงเรียนพูลเจริญวิทยาคม ภาคเรียนที่ 1 ปีการศึกษา 2569"))
    set_font(r_p3_3, size=15, bold=True)

    # QR Code Placeholder Box (Centered Table: 8.5 cm x 8.5 cm)
    qr_table = doc.add_table(rows=1, cols=1)
    qr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    qr_table.autofit = False

    qr_cell = qr_table.cell(0, 0)
    qr_cell.width = Cm(8.5)
    
    # Set explicit row height (8.5 cm = approx 4820 twips)
    tr = qr_table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="4820" w:hRule="atLeast"/>')
    trPr.append(trHeight)

    # Cell styling
    set_cell_border(qr_cell, top="single", bottom="single", left="single", right="single",
                    top_sz="6", bottom_sz="6", left_sz="6", right_sz="6",
                    top_color="000000", bottom_color="000000", left_color="000000", right_color="000000")
    set_cell_shading(qr_cell, "FAFAFA")
    set_cell_margins(qr_cell, top=50, bottom=50, left=50, right=50)
    qr_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Inside QR Placeholder Cell
    p_qr_blank1 = qr_cell.paragraphs[0]
    p_qr_blank1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_qr_blank1.paragraph_format.space_before = Pt(12)
    p_qr_blank1.paragraph_format.space_after = Pt(2)
    p_qr_blank1.paragraph_format.line_spacing = 1.0
    r_q1 = p_qr_blank1.add_run(insert_thai_zwsp("[ พื้นที่สำหรับวางรูปภาพ QR Code ]"))
    set_font(r_q1, size=16, bold=True, color=RGBColor(80, 80, 80))

    p_qr_sub = qr_cell.add_paragraph()
    p_qr_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_qr_sub.paragraph_format.space_before = Pt(2)
    p_qr_sub.paragraph_format.space_after = Pt(12)
    p_qr_sub.paragraph_format.line_spacing = 1.0
    r_q2 = p_qr_sub.add_run(insert_thai_zwsp("(สแกนเพื่อเข้าถึงโฟลเดอร์ Google Drive สำหรับตรวจดูบันทึกหลังแผนฯ)"))
    set_font(r_q2, size=13.5, italic=True, color=RGBColor(100, 100, 100))

    # Spacing after QR Box
    p_sp_after = doc.add_paragraph()
    p_sp_after.paragraph_format.space_before = Pt(10)
    p_sp_after.paragraph_format.space_after = Pt(2)
    p_sp_after.paragraph_format.line_spacing = 1.0

    # Section for Online Teachers List
    p_list_hdr = doc.add_paragraph()
    p_list_hdr.paragraph_format.left_indent = Cm(0.8)
    p_list_hdr.paragraph_format.space_before = Pt(2)
    p_list_hdr.paragraph_format.space_after = Pt(3)
    p_list_hdr.paragraph_format.line_spacing = 1.0
    r_lh = p_list_hdr.add_run(insert_thai_zwsp("รายชื่อครูผู้สอนที่จัดส่งบันทึกหลังแผนการจัดการเรียนรู้ในรูปแบบออนไลน์:"))
    set_font(r_lh, size=14.5, bold=True)

    online_teachers = [
        ("1. นายรามิล ปัญญพัทธ์", "รหัสวิชา ท30217 ภาษาไทยกับการผลิตสื่อร่วมสมัย 1, ท33101 ภาษาไทยพื้นฐาน 5"),
        ("2. นางสาวกมลวรรณ สังข์ทอง", "รหัสวิชา ท32101 ภาษาไทยพื้นฐาน 3"),
        ("3. นางสาววนิชญา เชียงน้อย", "รหัสวิชา ท22101 ภาษาไทยพื้นฐาน 3"),
        ("4. นางสาวชื่นฤดี หรับหลี", "รหัสวิชา ท20212 การพูดเบื้องต้น, ท22101 ภาษาไทยพื้นฐาน 3"),
        ("5. นางสาวอิงอร สิทธิจินดา", "รหัสวิชา ท22101 ภาษาไทยพื้นฐาน 3, ท20213 การอ่านเบื้องต้น"),
    ]

    for t_name, c_desc in online_teachers:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.left_indent = Cm(1.3)
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(1)
        p_t.paragraph_format.line_spacing = 1.0
        
        r_tn = p_t.add_run(insert_thai_zwsp(f"{t_name}  "))
        set_font(r_tn, size=13.5, bold=True)
        
        r_cd = p_t.add_run(insert_thai_zwsp(f"—  {c_desc}"))
        set_font(r_cd, size=13.5, bold=False)

    # Note at the bottom of Page 3 with 2 items
    p_note_hdr = doc.add_paragraph()
    p_note_hdr.paragraph_format.left_indent = Cm(0.8)
    p_note_hdr.paragraph_format.space_before = Pt(8)
    p_note_hdr.paragraph_format.space_after = Pt(2)
    p_note_hdr.paragraph_format.line_spacing = 1.0
    r_nh = p_note_hdr.add_run(insert_thai_zwsp("หมายเหตุ:"))
    set_font(r_nh, size=13.5, bold=True)

    # Note Item 1: Google Drive QR
    p_n1 = doc.add_paragraph()
    p_n1.paragraph_format.left_indent = Cm(1.3)
    p_n1.paragraph_format.space_before = Pt(0)
    p_n1.paragraph_format.space_after = Pt(2)
    p_n1.paragraph_format.line_spacing = 1.0
    r_n1_num = p_n1.add_run(insert_thai_zwsp("1. "))
    set_font(r_n1_num, size=13, bold=True)
    r_n1_txt = p_n1.add_run(insert_thai_zwsp(
        "สามารถสแกนคิวอาร์โค้ด (QR Code) ด้านบน เพื่อตรวจสอบและตรวจดูเอกสารบันทึกหลังแผนการจัดการเรียนรู้ "
        "ของครูผู้สอนแต่ละรายวิชาที่จัดเก็บไว้ในระบบคลาวด์ Google Drive ของกลุ่มสาระการเรียนรู้ภาษาไทย"
    ))
    set_font(r_n1_txt, size=13, bold=False)

    # Note Item 2: NDLP Platform (ตามที่ผู้ใช้สั่งการ)
    p_n2 = doc.add_paragraph()
    p_n2.paragraph_format.left_indent = Cm(1.3)
    p_n2.paragraph_format.space_before = Pt(0)
    p_n2.paragraph_format.space_after = Pt(0)
    p_n2.paragraph_format.line_spacing = 1.0
    r_n2_num = p_n2.add_run(insert_thai_zwsp("2. "))
    set_font(r_n2_num, size=13, bold=True)
    r_n2_txt = p_n2.add_run(insert_thai_zwsp(
        "ครูผู้สอนได้ดำเนินการจัดส่งและบันทึกข้อมูลหลังแผนการจัดการเรียนรู้ไว้ในระบบ NDLP "
        "(แพลตฟอร์มการจัดการเรียนรู้แห่งชาติโดยใช้เทคโนโลยีดิจิทัลเป็นฐาน : National Digital Learning Platform) "
        "ควบคู่เรียบร้อยแล้วด้วยเช่นกัน"
    ))
    set_font(r_n2_txt, size=13, bold=False)

    # Final document root cause fix
    fix_document_root_causes(doc)

    # Save Paths (.docx only)
    out_paths = [
        "d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/บันทึกข้อความส่งบันทึกหลังแผนการจัดการเรียนรู้ 1-2569.docx",
        "d:/MEGA/บันทึกข้อความ/บันทึกข้อความส่งบันทึกหลังแผนการจัดการเรียนรู้ 1-2569.docx",
        "H:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ/บันทึกข้อความส่งบันทึกหลังแผนการจัดการเรียนรู้ 1-2569.docx"
    ]
    for p in out_paths:
        doc.save(p)

    # Verify Page Count via Word COM
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        abs_docx = os.path.abspath(out_paths[0])
        w_doc = word.Documents.Open(abs_docx)
        page_count = w_doc.ComputeStatistics(2)
        w_doc.Close(False)
    finally:
        word.Quit()

    print(f"COMPLETE: Word page count = {page_count} (Saved to all 3 paths)")

if __name__ == '__main__':
    create_post_lesson_memo()
