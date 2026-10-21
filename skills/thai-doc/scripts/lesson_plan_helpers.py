import os
import docx
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls
import pythainlp

# ---------------------------------------------------------
# 1. Thai Segmentation & XML Protection Helpers
# ---------------------------------------------------------
def segment_thai(text):
    if not text:
        return ""
    words = pythainlp.word_tokenize(text, engine='newmm')
    return "\u200b".join(words)

def set_run_font_and_lang(run, font_name="TH Sarabun New", font_size=16, bold=False, italic=False, color="000000"):
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    
    rPr = run._r.get_or_add_rPr()
    for child in ['rFonts', 'lang', 'noProof', 'color']:
        elem = rPr.find(docx.oxml.ns.qn(f'w:{child}'))
        if elem is not None:
            rPr.remove(elem)
            
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}" w:eastAsia="{font_name}"/>')
    rPr.append(rFonts)
    lang = parse_xml(f'<w:lang {nsdecls("w")} w:val="th-TH" w:eastAsia="th-TH" w:bidi="th-TH"/>')
    rPr.append(lang)
    no_proof = parse_xml(f'<w:noProof {nsdecls("w")}/>')
    rPr.append(no_proof)
    if color:
        c = parse_xml(f'<w:color {nsdecls("w")} w:val="{color}"/>')
        rPr.append(c)

def format_paragraph(p, space_before=0, space_after=0, line_spacing=240, indent=0, align=None, bottom_border=None):
    """
    Standard Zero Spacing & Optional Bottom Divider Border
    """
    pPr = p._p.get_or_add_pPr()
    for child in ['spacing', 'ind', 'pBdr']:
        elem = pPr.find(docx.oxml.ns.qn(f'w:{child}'))
        if elem is not None:
            pPr.remove(elem)
            
    spacing = parse_xml(f'<w:spacing {nsdecls("w")} w:before="{space_before}" w:after="{space_after}" w:line="{line_spacing}" w:lineRule="auto"/>')
    pPr.append(spacing)
    if indent > 0:
        ind = parse_xml(f'<w:ind {nsdecls("w")} w:firstLine="{indent}" w:left="0"/>')
        pPr.append(ind)
    if align:
        p.alignment = align
        
    if bottom_border:
        sz = bottom_border.get('sz', '8')
        color = bottom_border.get('color', '000000')
        space = bottom_border.get('space', '4')
        pBdr = parse_xml(f'''<w:pBdr {nsdecls("w")}>
            <w:bottom w:val="single" w:sz="{sz}" w:space="{space}" w:color="{color}"/>
        </w:pBdr>''')
        pPr.append(pBdr)

def add_styled_paragraph(doc, text, bold=False, italic=False, font_size=16, space_before=0, space_after=0, indent=0, align=None, color="000000", bottom_border=None):
    p = doc.add_paragraph()
    segmented_text = segment_thai(text)
    run = p.add_run(segmented_text)
    set_run_font_and_lang(run, font_name="TH Sarabun New", font_size=font_size, bold=bold, italic=italic, color=color)
    format_paragraph(p, space_before=space_before, space_after=space_after, line_spacing=240, indent=indent, align=align, bottom_border=bottom_border)
    return p

# ---------------------------------------------------------
# 2. Table & Cell Helpers
# ---------------------------------------------------------
def set_cell_properties(cell, width_dxa=None, shading=None, borders=None, margins=None, v_align=WD_ALIGN_VERTICAL.CENTER):
    cell.vertical_alignment = v_align
    tcPr = cell._tc.get_or_add_tcPr()
    for child in ['tcW', 'shd', 'tcBorders', 'tcMar']:
        elem = tcPr.find(docx.oxml.ns.qn(f'w:{child}'))
        if elem is not None:
            tcPr.remove(elem)
            
    if width_dxa:
        tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{width_dxa}" w:type="dxa"/>'))
    if shading:
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{shading}"/>'))
    if borders:
        b_elm = OxmlElement('w:tcBorders')
        for side in ['top', 'left', 'bottom', 'right']:
            cfg = borders.get(side, {'val': 'none'})
            val = cfg.get('val', 'none')
            if val == 'none':
                b_elm.append(parse_xml(f'<w:{side} {nsdecls("w")} w:val="none"/>'))
            else:
                sz = cfg.get('sz', '6')
                color = cfg.get('color', '000000')
                b_elm.append(parse_xml(f'<w:{side} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'))
        tcPr.append(b_elm)
    if margins:
        top = margins.get('top', 100)
        bottom = margins.get('bottom', 100)
        left = margins.get('left', 140)
        right = margins.get('right', 140)
        tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>''')
        tcPr.append(tcMar)

def format_cell_content(cell, text="", bold=False, italic=False, font_size=14, color="000000", align=WD_ALIGN_PARAGRAPH.LEFT):
    p = cell.paragraphs[0]
    p.text = ""
    p.alignment = align
    segmented_text = segment_thai(text) if text else ""
    run = p.add_run(segmented_text)
    set_run_font_and_lang(run, font_name="TH Sarabun New", font_size=font_size, bold=bold, italic=italic, color=color)
    format_paragraph(p, space_before=0, space_after=0, line_spacing=240, indent=0, align=align)

def apply_table_base_styling(table, col_widths):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    for child in ['tblW', 'tblBorders', 'tblCellMar', 'jc']:
        elem = tblPr.find(docx.oxml.ns.qn(f'w:{child}'))
        if elem is not None:
            tblPr.remove(elem)
            
    tblPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
    tblPr.append(parse_xml(f'''<w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:insideH w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:insideV w:val="single" w:sz="6" w:space="0" w:color="000000"/>
    </w:tblBorders>'''))
    tblPr.append(parse_xml(f'''<w:tblCellMar {nsdecls("w")}>
        <w:top w:w="100" w:type="dxa"/>
        <w:bottom w:w="100" w:type="dxa"/>
        <w:left w:w="140" w:type="dxa"/>
        <w:right w:w="140" w:type="dxa"/>
    </w:tblCellMar>'''))
    tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="{sum(col_widths)}" w:type="dxa"/>'))

# ---------------------------------------------------------
# 3. Safe File Saving Function
# ---------------------------------------------------------
def save_doc_safe(doc, target_path):
    temp_path = target_path.replace('.docx', '_temp.docx')
    doc.save(temp_path)
    try:
        if os.path.exists(target_path):
            os.replace(temp_path, target_path)
        else:
            os.rename(temp_path, target_path)
        print(f"Successfully saved and replaced: {target_path}")
        return True
    except PermissionError:
        print(f"WARNING: File {target_path} is locked by Microsoft Word. Saved to {temp_path} instead.")
        return False
