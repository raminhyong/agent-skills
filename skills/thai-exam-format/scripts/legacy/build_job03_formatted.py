import json
import os
import re
import sys
from collections import Counter
import docx
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import pythainlp
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_words
from pythainlp.util import dict_trie

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

NON_SPACING_CHARS = set([
    '\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
    '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e',
    '\u200b'
])

def visual_length(text: str) -> int:
    return sum(1 for c in text if c not in NON_SPACING_CHARS)

EXAM_COMPOUND_WORDS = {
    'มาตรฐานการเรียนรู้', 'ตัวชี้วัด', 'ผลการเรียนรู้', 'คำชี้แจง', 'ผู้ออกข้อสอบ',
    'หัวหน้ากลุ่มสาระการเรียนรู้', 'หัวหน้างานวัดผลโรงเรียน', 'รองผู้อำนวยการโรงเรียน',
    'โรงเรียนพูลเจริญวิทยาคม', 'โรงเรียนภูซางวิทยาคม', 'แบบสรุป', 'รายวิชา',
    'การวัดและประเมินผล', 'มัธยมศึกษา', 'ประถมศึกษา', 'กลุ่มสาระการเรียนรู้',
    'กลุ่มสาระการเรียนรู้ภาษาไทย', 'ภาษาไทย', 'รูบริก', 'รูบริกรายบุคคล', 'Rubric',
    'คะแนนก่อนเรียน', 'คะแนนหลังเรียน', 'การคิดวิเคราะห์', 'ผลสัมฤทธิ์', 'ความพึงพอใจ',
    'ข้อตกลงในการพัฒนางาน', 'ประเด็นท้าทาย', 'อย่างมีนัยสำคัญ', 'นัยสำคัญ',
    'การวิเคราะห์บริบท', 'การวิเคราะห์องค์ประกอบ', 'การวิเคราะห์ความสัมพันธ์',
    'การวิเคราะห์หลักการ', 'การวิเคราะห์แก่นสาร', 'การวิเคราะห์เปรียบเทียบ',
    'การวิเคราะห์เชิงวิพากษ์', 'ขุนช้างขุนแผน', 'ขุนช้างถวายฎีกา', 'กาพย์เห่เรือ'
}

_EXAM_TRIE = dict_trie(set(thai_words()) | EXAM_COMPOUND_WORDS)

def insert_thai_zwsp(text: str) -> str:
    if not text:
        return text
    if not any('\u0e00' <= c <= '\u0e7f' for c in text):
        return text

    clean_text = text.replace('\u200b', '')
    if not clean_text or set(clean_text) == {'.'}:
        return text

    raw_tokens = word_tokenize(clean_text, custom_dict=_EXAM_TRIE, engine='newmm')
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
        lang = parse_xml(f'<w:lang {nsdecls("w")} w:val="th-TH" w:bidi="th-TH" w:eastAsia="th-TH"/>')
        rPr.append(lang)
    else:
        lang.set(qn('w:val'), 'th-TH')
        lang.set(qn('w:bidi'), 'th-TH')
        lang.set(qn('w:eastAsia'), 'th-TH')

    sz = rPr.find(qn('w:sz'))
    if sz is None:
        sz = parse_xml(f'<w:sz {nsdecls("w")} w:val="{int(size_pt*2)}"/>')
        rPr.append(sz)
    else:
        sz.set(qn('w:val'), str(int(size_pt*2)))

    szCs = rPr.find(qn('w:szCs'))
    if szCs is None:
        szCs = parse_xml(f'<w:szCs {nsdecls("w")} w:val="{int(size_pt*2)}"/>')
        rPr.append(szCs)
    else:
        szCs.set(qn('w:val'), str(int(size_pt*2)))

    if bold:
        if rPr.find(qn('w:b')) is None:
            rPr.append(parse_xml(f'<w:b {nsdecls("w")}/>'))
        if rPr.find(qn('w:bCs')) is None:
            rPr.append(parse_xml(f'<w:bCs {nsdecls("w")}/>'))

NEGATIVE_WORDS = [
    "ไม่ถูกต้องเหมาะสม", "ไม่ถูกต้อง", "ไม่เหมาะสม", "ไม่ใช่", "ไม่มีประสิทธิภาพ", "ไม่มี",
    "ไม่ปรากฏ", "ไม่จำเป็น", "ไม่ได้", "ไม่ควร", "มิได้", "ยกเว้น", "ไม่"
]

def add_stem_runs(paragraph, q_num: int, q_text: str):
    prefix = f"{q_num}. "
    r_pre = paragraph.add_run(prefix)
    set_run_font(r_pre, bold=False)
    
    neg_pattern = "(" + "|".join([re.escape(w) for w in NEGATIVE_WORDS]) + ")"
    # Separate quote blocks so that words inside quotes are NEVER bolded
    parts_by_quote = re.split(r'("[^"]*?"|“[^”]*?”)', q_text)
    
    for chunk in parts_by_quote:
        if not chunk:
            continue
        if (chunk.startswith('"') and chunk.endswith('"')) or (chunk.startswith('“') and chunk.endswith('”')):
            r = paragraph.add_run(insert_thai_zwsp(chunk))
            set_run_font(r, bold=False)
        else:
            sub_parts = re.split(neg_pattern, chunk)
            for sp in sub_parts:
                if not sp:
                    continue
                tokenized = insert_thai_zwsp(sp)
                if sp in NEGATIVE_WORDS:
                    r = paragraph.add_run(tokenized)
                    set_run_font(r, bold=True)
                else:
                    r = paragraph.add_run(tokenized)
                    set_run_font(r, bold=False)

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

    # 2. Style 'Normal'
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

    # 3. All Paragraphs
    for p in doc.paragraphs:
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

def build_job03_formatted():
    json_path = os.path.join(BASE_DIR, 'Job03.json')
    with open(json_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} questions from Job03.json.")

    # Group questions by category preserving order
    categories = []
    current_cat = None
    for d in data:
        cat_name = d.get('category', '').strip()
        if not current_cat or current_cat['name'] != cat_name:
            current_cat = {'name': cat_name, 'questions': []}
            categories.append(current_cat)
        current_cat['questions'].append(d)

    # Initialize Document
    doc = docx.Document()

    # Section & Page Setup
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.8)
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.header_distance = Cm(0.60)

    # Header Page Number: - 1 - (Center, Bold, 16pt)
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(0)
    hp.paragraph_format.line_spacing = 1.0

    hrun1 = hp.add_run("- ")
    set_run_font(hrun1, bold=True)
    fldSimple = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
    hp._p.append(fldSimple)
    hrun2 = hp.add_run(" -")
    set_run_font(hrun2, bold=True)

    # ================= DOCUMENT BODY (NO COVER PAGE) =================

    # Top Lead-in Instruction on Page 1
    p_cmd = doc.add_paragraph()
    p_cmd.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_cmd.paragraph_format.space_before = Pt(0)
    p_cmd.paragraph_format.space_after = Pt(0)
    p_cmd.paragraph_format.line_spacing = 1.0
    p_cmd.paragraph_format.left_indent = Pt(0)
    p_cmd.paragraph_format.keep_with_next = True

    r_cmd1 = p_cmd.add_run(insert_thai_zwsp("คำสั่ง"))
    set_run_font(r_cmd1, bold=True)
    r_cmd2 = p_cmd.add_run(" " + insert_thai_zwsp("จงเลือกคำตอบที่ถูกต้องที่สุดเพียงคำตอบเดียว"))
    set_run_font(r_cmd2, bold=False)

    for cat_idx, cat in enumerate(categories):
        q_list = cat['questions']
        min_q = q_list[0]['no']
        max_q = q_list[-1]['no']
        r_str = f"ข้อ {min_q} - {max_q}" if min_q != max_q else f"ข้อ {min_q}"

        # Category Heading: e.g. "1. การวิเคราะห์บริบท (ข้อ 1 - 6)"
        cat_header_text = f"{cat['name']} ({r_str})"

        p_cat = doc.add_paragraph()
        p_cat.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cat.paragraph_format.left_indent = Pt(0)
        p_cat.paragraph_format.line_spacing = 1.0
        p_cat.paragraph_format.space_before = Pt(0) if cat_idx == 0 else Pt(16)
        p_cat.paragraph_format.space_after = Pt(0)
        p_cat.paragraph_format.keep_with_next = True
        p_cat.paragraph_format.keep_together = True

        r_cat = p_cat.add_run(insert_thai_zwsp(cat_header_text))
        set_run_font(r_cat, bold=False)

        for q in q_list:
            q_num = q['no']
            q_text = q['question'].strip()
            options = q['options']

            # Question paragraph
            p_q = doc.add_paragraph()
            p_q.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_q.paragraph_format.left_indent = Pt(0)
            p_q.paragraph_format.space_before = Pt(0)
            p_q.paragraph_format.space_after = Pt(0)
            p_q.paragraph_format.line_spacing = 1.0
            p_q.paragraph_format.keep_with_next = True
            p_q.paragraph_format.keep_together = True

            add_stem_runs(p_q, q_num, q_text)

            # Choices: Extract and sort by visual length (shortest to longest)
            choice_texts = [options.get(k, '').strip() for k in ['ก', 'ข', 'ค', 'ง'] if k in options]
            sorted_choices = sorted(choice_texts, key=lambda c: visual_length(c))

            # All questions use Layout 1 (4 lines: 1 choice per line)
            for c_idx, c_text in enumerate(sorted_choices):
                p_c = doc.add_paragraph()
                p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_c.paragraph_format.left_indent = Inches(0.2)
                p_c.paragraph_format.space_before = Pt(0)
                p_c.paragraph_format.space_after = Pt(0)
                p_c.paragraph_format.line_spacing = 1.0
                p_c.paragraph_format.keep_together = True
                if c_idx < len(sorted_choices) - 1:
                    p_c.paragraph_format.keep_with_next = True

                choice_line = f"{c_idx + 1}. {insert_thai_zwsp(c_text)}"
                r_c = p_c.add_run(choice_line)
                set_run_font(r_c, bold=False)

    # Apply root causes fixes to xml (4 Pillars)
    fix_document_root_causes(doc)

    out_path = os.path.join(BASE_DIR, "Job03_Formatted.docx")
    try:
        doc.save(out_path)
        print(f"Document successfully created and saved to: {out_path}")
    except PermissionError:
        alt_path = os.path.join(BASE_DIR, "Job03_Formatted_v2.docx")
        doc.save(alt_path)
        print(f"Notice: Main file was locked. Saved as {alt_path} instead.")

if __name__ == "__main__":
    build_job03_formatted()
