import sys, os, io
import docx
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import pythainlp

sys.stdout.reconfigure(encoding='utf-8')

def thai_text(text):
    if not text:
        return ''
    if set(text).issubset(set(' .-_/():[]1234567890,\n\t')):
        return text
    words = pythainlp.word_tokenize(text, engine='newmm')
    return '\u200b'.join([w for w in words if w])

def add_styled_run(p, text, font_name='TH Sarabun New', size_pt=16, bold=False, italic=False, underline=False, color=None):
    tokenized = thai_text(text)
    r = p.add_run(tokenized)
    r.font.name = font_name
    r.font.size = Pt(size_pt)
    r.bold = bold
    r.italic = italic
    r.underline = underline
    if color:
        r.font.color.rgb = color
    
    rPr = r._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    
    lang = rPr.find(qn('w:lang'))
    if lang is None:
        lang = OxmlElement('w:lang')
        rPr.append(lang)
    lang.set(qn('w:val'), 'th-TH')
    
    szCs = rPr.find(qn('w:szCs'))
    if szCs is None:
        szCs = OxmlElement('w:szCs')
        rPr.append(szCs)
    szCs.set(qn('w:val'), str(int(size_pt * 2)))
    
    if bold:
        bCs = rPr.find(qn('w:bCs'))
        if bCs is None:
            bCs = OxmlElement('w:bCs')
            rPr.append(bCs)
            
    noProof = rPr.find(qn('w:noProof'))
    if noProof is None:
        noProof = OxmlElement('w:noProof')
        rPr.append(noProof)
        
    return r

def add_para(doc, text="", font_name='TH Sarabun New', size_pt=16, bold=False, italic=False,
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=Pt(0), space_after=Pt(0), line_spacing=1.0,
             first_line_indent=Pt(0), left_indent=Pt(0), keep_with_next=False):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    p.paragraph_format.line_spacing = line_spacing
    if keep_with_next:
        p.paragraph_format.keep_with_next = True
    if first_line_indent != Pt(0):
        p.paragraph_format.first_line_indent = first_line_indent
    if left_indent != Pt(0):
        p.paragraph_format.left_indent = left_indent
    if text:
        add_styled_run(p, text, font_name=font_name, size_pt=size_pt, bold=bold, italic=italic)
    return p

def add_divider_line(doc, space_before=Pt(0), space_after=Pt(2), sz="6"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.keep_with_next = True
    
    r = p.add_run()
    r.font.name = 'TH Sarabun New'
    r.font.size = Pt(2)
    
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'''
    <w:pBdr {nsdecls("w")}>
        <w:bottom w:val="single" w:sz="{sz}" w:space="1" w:color="000000"/>
    </w:pBdr>
    ''')
    existing_pBdr = pPr.find(qn('w:pBdr'))
    if existing_pBdr is not None:
        pPr.remove(existing_pBdr)
    pPr.append(pBdr)
    return p

def apply_table_bw_borders(table):
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

def apply_invisible_borders(table):
    tblPr = table._tbl.tblPr
    borders_xml = f'''
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>
    </w:tblBorders>
    '''
    tblBorders = parse_xml(borders_xml)
    existing_borders = tblPr.find(qn('w:tblBorders'))
    if existing_borders is not None:
        tblPr.remove(existing_borders)
    tblPr.append(tblBorders)

def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def set_cell_properties(cell, text="", font_name='TH Sarabun New', size_pt=15, bold=False, 
                        align=WD_ALIGN_PARAGRAPH.LEFT, shading="FFFFFF", width_cm=None,
                        space_before=Pt(0.5), space_after=Pt(0.5), line_spacing=1.0):
    tcPr = cell._tc.get_or_add_tcPr()
    if shading:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{shading}" w:val="clear"/>')
        existing_shd = tcPr.find(qn('w:shd'))
        if existing_shd is not None:
            tcPr.remove(existing_shd)
        tcPr.append(shd)
    
    if width_cm:
        cell.width = Cm(width_cm)
        
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    
    tcMar = parse_xml(f'''
    <w:tcMar {nsdecls("w")}>
        <w:top w:w="35" w:type="dxa"/>
        <w:left w:w="70" w:type="dxa"/>
        <w:bottom w:w="35" w:type="dxa"/>
        <w:right w:w="70" w:type="dxa"/>
    </w:tcMar>
    ''')
    existing_tcMar = tcPr.find(qn('w:tcMar'))
    if existing_tcMar is not None:
        tcPr.remove(existing_tcMar)
    tcPr.append(tcMar)

    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    p.paragraph_format.line_spacing = line_spacing
    if text:
        add_styled_run(p, text, font_name=font_name, size_pt=size_pt, bold=bold)
    return p

def create_activity_schedule_doc():
    """
    Generates a standalone Activity Schedule document with 2 separate tables:
    - Table 1: ม.3, ม.5, ม.6 (อบรมเพลงพื้นบ้าน + แนะแนว)
    - Table 2: ม.1, ม.2, ม.4 (อบรมพัฒนาบุคลิกภาพ [เว้นรายละเอียดไว้] + แนะแนว)
    """
    doc = docx.Document()
    
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(1.2)
        section.bottom_margin = Cm(1.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(1.5)

    logo_path = os.path.abspath("school logo.png")

    # ==================== PAGE 1: กลุ่ม ม.3, ม.5, ม.6 ====================
    if os.path.exists(logo_path):
        p_logo1 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(0), space_after=Pt(0), keep_with_next=True)
        run_logo1 = p_logo1.add_run()
        run_logo1.add_picture(logo_path, height=Cm(1.5), width=Cm(1.28))

    p1_1 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(0), keep_with_next=True)
    add_styled_run(p1_1, "กำหนดการกิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิต", size_pt=17, bold=True)

    p1_2 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(0), keep_with_next=True)
    add_styled_run(p1_2, "กลุ่มที่ 1 : ระดับชั้นมัธยมศึกษาปีที่ 3, 5 และ 6 (กิจกรรมอบรมเพลงพื้นบ้านและแนะแนว)", size_pt=15, bold=True)

    p1_3 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(1), keep_with_next=True)
    add_styled_run(p1_3, "โรงเรียนพูลเจริญวิทยาคม  กลุ่มบริหารวิชาการ  ปีการศึกษา 2569", size_pt=14, italic=True)

    add_divider_line(doc, space_before=Pt(0), space_after=Pt(1), sz="6")

    # Schedule Table 1: [เวลา (2.8 cm), กิจกรรม (9.4 cm), วิทยากร / ผู้รับผิดชอบ (5.3 cm)]
    t1 = doc.add_table(rows=7, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_table_bw_borders(t1)
    col_w = [2.8, 9.4, 5.3]

    # Header
    set_cell_properties(t1.cell(0, 0), "เวลา", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w[0], size_pt=14)
    set_cell_properties(t1.cell(0, 1), "กิจกรรม (กลุ่ม ม.3, ม.5, ม.6)", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w[1], size_pt=14)
    set_cell_properties(t1.cell(0, 2), "วิทยากร / ผู้รับผิดชอบ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w[2], size_pt=14)

    # Row 1: Opening
    set_cell_properties(t1.cell(1, 0), "08.00 – 08.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    set_cell_properties(t1.cell(1, 1), "- พิธีเปิดกิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิต\n- ชี้แจงวัตถุประสงค์และข้อตกลงในการจัดกิจกรรม", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=13)
    set_cell_properties(t1.cell(1, 2), "กลุ่มบริหารวิชาการ /\nหัวหน้าระดับ ม.3, ม.5, ม.6", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=13)

    # Row 2: Base 1
    set_cell_properties(t1.cell(2, 0), "08.30 – 09.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    base1_text = (
        "ฐานละครไทยในวรรณคดี\n"
        "• ชมการแสดงละคร เพลงฉ่อย วรรณคดีไทยจากคณะวิทยากร\n"
        "  - ม.3 ชมเรื่อง พระอภัยมณี ตอน พระอภัยหนีนางผีเสื้อ\n"
        "  - ม.5 ชมเรื่อง มัทนะพาธา ตอน ตำนานรักดอกกุหลาบ\n"
        "  - ม.6 ชมเรื่อง ขุนช้างขุนแผน ตอน ขุนช้างถวายฎีกา"
    )
    set_cell_properties(t1.cell(2, 1), base1_text, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=12.5)
    v_text1 = "คณะวิทยากร:\n1. นายประภาส บัวบาน\n2. นายจักรพงศ์ โพธิ์สุวรรณ\n3. นายศุภกร มนต์อ่อน\n4. น.ส.สิริลักษณ์ บุญมี\n5. น.ส.ณิชชา ชรัลโชติสิน"
    set_cell_properties(t1.cell(2, 2), v_text1, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[2], size_pt=12)

    # Row 3: Base 2
    set_cell_properties(t1.cell(3, 0), "09.30 – 10.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    base2_text = (
        "ฐานเพลงพื้นบ้าน เรียนรู้เพลงฉ่อย\n"
        "• เรียนรู้ฉันทลักษณ์เพลงฉ่อย ฝึกแต่งฉ่อยตามแผนผัง\n"
        "• การเกริ่นเพลงฉ่อย แบบชาย-หญิง\n"
        "• ฝึกร้องทำนองเพลงฉ่อย และแบ่งกลุ่มแต่งเพลงฉ่อย / นำเสนอผลงาน"
    )
    set_cell_properties(t1.cell(3, 1), base2_text, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=12.5)
    set_cell_properties(t1.cell(3, 2), "คณะวิทยากรเพลงพื้นบ้าน /\nครูประจำระดับชั้น", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=12.5)

    # Row 4: Base 3
    set_cell_properties(t1.cell(4, 0), "10.30 – 11.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    base3_text = (
        "ฐานการละเล่นไทย\n"
        "• เรียนรู้ประวัติความเป็นมาและกติกาการละเล่นไทยโบราณ\n"
        "• สาธิตและปฏิบัติการละเล่นไทย เช่น กระโดดเชือก มอญซ่อนผ้า ฯลฯ"
    )
    set_cell_properties(t1.cell(4, 1), base3_text, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=12.5)
    set_cell_properties(t1.cell(4, 2), "คณะวิทยากร /\nครูกลุ่มบริหารวิชาการ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=12.5)

    # Row 5: Lunch
    set_cell_properties(t1.cell(5, 0), "11.30 – 12.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    set_cell_properties(t1.cell(5, 1), "พักรับประทานอาหารกลางวัน (อาหารกลางวันและเครื่องดื่ม)", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=13)
    set_cell_properties(t1.cell(5, 2), "คณะครูและนักเรียน", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=13)

    # Row 6: Afternoon
    set_cell_properties(t1.cell(6, 0), "12.30 – 16.00 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    aft_text1 = (
        "กิจกรรมแนะแนวการศึกษาต่อและเส้นทางอาชีพ\n"
        "• บรรยายเปิดโลกทัศน์การศึกษาต่อระดับอุดมศึกษา / สายอาชีพ\n"
        "• Workshop สำรวจตนเอง แนะนำแนวทางการเตรียมตัวสู่อาชีพในอนาคต\n"
        "• สรุปองค์ความรู้ / ทำแบบประเมินความพึงพอใจ / พิธีปิดกิจกรรม"
    )
    set_cell_properties(t1.cell(6, 1), aft_text1, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=12.5)
    set_cell_properties(t1.cell(6, 2), "วิทยากรสถาบันภายนอก /\nกลุ่มบริหารวิชาการ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=12.5)

    for row in t1.rows:
        prevent_row_split(row)

    # Date note for Group 1
    p_dates_g1 = add_para(doc, space_before=Pt(2), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_dates_g1, "กำหนดวันจัดกิจกรรมกลุ่มที่ 1 : ", bold=True, size_pt=13.5)
    add_styled_run(p_dates_g1, "• ม.3: วันพฤหัสบดีที่ 10 ก.ย. 2569 (514 คน)   • ม.5: วันศุกร์ที่ 11 ก.ย. 2569 (324 คน)   • ม.6: วันจันทร์ที่ 14 ก.ย. 2569 (314 คน)", size_pt=13)

    # ==================== PAGE 2: กลุ่ม ม.1, ม.2, ม.4 ====================
    doc.add_page_break()

    if os.path.exists(logo_path):
        p_logo2 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(0), space_after=Pt(0), keep_with_next=True)
        run_logo2 = p_logo2.add_run()
        run_logo2.add_picture(logo_path, height=Cm(1.5), width=Cm(1.28))

    p2_1 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(0), keep_with_next=True)
    add_styled_run(p2_1, "กำหนดการกิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิต", size_pt=17, bold=True)

    p2_2 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(0), keep_with_next=True)
    add_styled_run(p2_2, "กลุ่มที่ 2 : ระดับชั้นมัธยมศึกษาปีที่ 1, 2 และ 4 (กิจกรรมอบรมพัฒนาบุคลิกภาพและแนะแนว)", size_pt=15, bold=True)

    p2_3 = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(1), keep_with_next=True)
    add_styled_run(p2_3, "โรงเรียนพูลเจริญวิทยาคม  กลุ่มบริหารวิชาการ  ปีการศึกษา 2569", size_pt=14, italic=True)

    add_divider_line(doc, space_before=Pt(0), space_after=Pt(1), sz="6")

    # Schedule Table 2: [เวลา (2.8 cm), กิจกรรม (9.4 cm), วิทยากร / ผู้รับผิดชอบ (5.3 cm)]
    t2 = doc.add_table(rows=5, cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_table_bw_borders(t2)

    # Header
    set_cell_properties(t2.cell(0, 0), "เวลา", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w[0], size_pt=14)
    set_cell_properties(t2.cell(0, 1), "กิจกรรม (กลุ่ม ม.1, ม.2, ม.4)", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w[1], size_pt=14)
    set_cell_properties(t2.cell(0, 2), "วิทยากร / ผู้รับผิดชอบ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w[2], size_pt=14)

    # Row 1: Opening
    set_cell_properties(t2.cell(1, 0), "08.00 – 08.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    set_cell_properties(t2.cell(1, 1), "- พิธีเปิดกิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิต\n- ชี้แจงวัตถุประสงค์และข้อตกลงในการจัดกิจกรรม", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=13)
    set_cell_properties(t2.cell(1, 2), "กลุ่มบริหารวิชาการ /\nหัวหน้าระดับ ม.1, ม.2, ม.4", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=13)

    # Row 2: Morning Personality Development (Reserved/Blanked for details)
    set_cell_properties(t2.cell(2, 0), "08.30 – 11.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    base_pers_text = (
        "กิจกรรมอบรมพัฒนาบุคลิกภาพและมารยาททางสังคม\n"
        "• การพัฒนาบุคลิกภาพภายนอกและภายในสำหรับวัยเรียน\n"
        "• มารยาทและการสื่อสารเชิงบวกในชีวิตประจำวัน\n"
        "• (รอกำหนดรายละเอียดกิจกรรมและขั้นตอนการปฏิบัติเพิ่มเติม)"
    )
    set_cell_properties(t2.cell(2, 1), base_pers_text, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=13)
    set_cell_properties(t2.cell(2, 2), "วิทยากรผู้เชี่ยวชาญด้านการพัฒนาบุคลิกภาพ /\nคณะครูประจำระดับชั้น", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=13)

    # Row 3: Lunch
    set_cell_properties(t2.cell(3, 0), "11.30 – 12.30 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    set_cell_properties(t2.cell(3, 1), "พักรับประทานอาหารกลางวัน (อาหารกลางวันและเครื่องดื่ม)", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=13)
    set_cell_properties(t2.cell(3, 2), "คณะครูและนักเรียน", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=13)

    # Row 4: Afternoon Guidance
    set_cell_properties(t2.cell(4, 0), "12.30 – 16.00 น.", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[0], size_pt=13.5)
    aft_text2 = (
        "กิจกรรมแนะแนวการศึกษาต่อและเส้นทางอาชีพ\n"
        "• บรรยายเปิดโลกทัศน์การศึกษาต่อระดับอุดมศึกษา / สายอาชีพ\n"
        "• Workshop สำรวจตนเอง แนะนำแนวทางการเตรียมตัวสู่อาชีพในอนาคต\n"
        "• สรุปองค์ความรู้ / ทำแบบประเมินความพึงพอใจ / พิธีปิดกิจกรรม"
    )
    set_cell_properties(t2.cell(4, 1), aft_text2, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w[1], size_pt=12.5)
    set_cell_properties(t2.cell(4, 2), "วิทยากรสถาบันภายนอก /\nกลุ่มบริหารวิชาการ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w[2], size_pt=12.5)

    for row in t2.rows:
        prevent_row_split(row)

    # Date note for Group 2
    p_dates_g2 = add_para(doc, space_before=Pt(2), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_dates_g2, "กำหนดวันจัดกิจกรรมกลุ่มที่ 2 : ", bold=True, size_pt=13.5)
    add_styled_run(p_dates_g2, "• ม.4: วันจันทร์ที่ 7 ก.ย. 2569 (335 คน)   • ม.2: วันอังคารที่ 8 ก.ย. 2569 (561 คน)   • ม.1: วันพุธที่ 9 ก.ย. 2569 (580 คน)", size_pt=13)

    p_footer_note = add_para(doc, space_before=Pt(1), space_after=Pt(0))
    add_styled_run(p_footer_note, "หมายเหตุ: กำหนดการอาจปรับเปลี่ยนได้ตามความเหมาะสม โดยคำนึงถึงประโยชน์สูงสุดของผู้เรียนเป็นสำคัญ", italic=True, size_pt=12.5)

    out_file = "ตารางกิจกรรม โครงการ 01.docx"
    doc.save(out_file)
    print(f"File created successfully: '{out_file}'")

def update_main_project_doc():
    """Updates the main proposal with the verified scan data + equipment cost + Deputy Academic Name."""
    doc = docx.Document()
    
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.0)

    # 1. School Logo (Centered)
    logo_path = os.path.abspath("school logo.png")
    if os.path.exists(logo_path):
        p_logo = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(0), space_after=Pt(0), keep_with_next=True)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, height=Cm(1.8), width=Cm(1.54))

    # Header Titles
    p_head = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_head, "โรงเรียนพูลเจริญวิทยาคม", size_pt=18, bold=True)
    
    p_subhead = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_subhead, "กลุ่มบริหารวิชาการ   ปีการศึกษา 2569", size_pt=16, bold=True)

    # Semester Line
    p_term = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_term, "( / ) ภาคเรียนที่ 1   1 เม.ย. 2569 – 30 ก.ย. 2569       (   ) ภาคเรียนที่ 2   1 ต.ค. 2569 – 31 มี.ค. 2570", size_pt=15, bold=False)

    add_divider_line(doc, space_before=Pt(0), space_after=Pt(2), sz="6")

    # Strategic & Policy Mapping
    def add_label_val(label, val, space_after=Pt(0)):
        p = add_para(doc, space_after=space_after)
        add_styled_run(p, label, bold=True)
        if val:
            add_styled_run(p, " " + val, bold=False)
        return p

    add_label_val("ชื่อกลยุทธ์ :", "กลยุทธ์ที่ 2 การพัฒนาคุณภาพนักเรียนตามมาตรฐานการศึกษา")
    add_label_val("ชื่อโครงการหลัก :", "โครงการที่ 4. โครงการพัฒนาศักยภาพผู้เรียน")
    add_label_val("ชื่อโครงการ :", "กิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิต")
    add_label_val("ลักษณะโครงการ :", "( / ) ใหม่       (   ) ต่อเนื่อง")

    # นโยบายของ สพฐ.
    p_np = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_np, "นโยบายของ สพฐ.", bold=True)
    
    p_np1 = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_np1, "7. ส่งเสริมศักยภาพผู้เรียนรายบุคคลสู่ความเป็นเลิศ", bold=False)
    p_np1_sub = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0))
    add_styled_run(p_np1_sub, "7.1 ส่งเสริมและพัฒนาศักยภาพผู้เรียนตามความถนัดและความสนใจตามแนวทางพหุปัญญาเพื่อความเป็นเลิศในด้านต่าง ๆ ทั้งคณิตศาสตร์ วิทยาศาสตร์ ภาษา ทัศนศิลป์ ดนตรี นาฏศิลป์ และกีฬา", bold=False)

    p_np2 = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_np2, "11. จัดการเรียนรู้และวัดประเมินผลที่มุ่งเน้นพัฒนาการตามศักยภาพผู้เรียนรายบุคคล", bold=False)
    p_np2_sub = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0))
    add_styled_run(p_np2_sub, "11.1 สร้างความเข้มแข็งระบบแนะแนว การชี้แนะ (Coaching) การให้การปรึกษา และพัฒนาผู้เรียนอย่างรอบด้าน มีการสื่อสารทำงานร่วมกับภาคีเครือข่ายและผู้ปกครอง", bold=False)

    # นโยบาย Quick Win
    p_qw = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_qw, "นโยบาย Quick Win", bold=True)
    
    p_qw1 = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_qw1, "3. ส่งเสริมการเรียนดี มีความสุข", bold=False)
    p_qw1_sub = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0))
    add_styled_run(p_qw1_sub, "3.2 พัฒนาผู้บริหาร ครูและบุคลากรทางการศึกษา ให้สามารถส่งเสริม สนับสนุน จัดการเรียนรู้วัดและประเมินผล ตามศักยภาพ ความถนัด และความสามารถที่หลากหลายของผู้เรียนรายบุคคล", bold=False)

    # มาตรฐานการศึกษาขั้นพื้นฐาน
    p_std = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_std, "มาตรฐานการศึกษาขั้นพื้นฐาน", bold=True)
    
    p_std_m1 = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_std_m1, "มาตรฐานที่ 1 คุณภาพของผู้เรียน", bold=False)
    p_std_m1_1 = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_std_m1_1, "1.1 ผลสัมฤทธิ์ทางวิชาการของผู้เรียน", bold=False)
    p_std_m1_1_item = add_para(doc, left_indent=Cm(1.5), space_after=Pt(0))
    add_styled_run(p_std_m1_1_item, "6) มีความรู้ ทักษะพื้นฐาน และเจตคติที่ดีต่องานอาชีพ", bold=False)
    
    p_std_m1_2 = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_std_m1_2, "1.2 คุณลักษณะที่พึงประสงค์ของผู้เรียน", bold=False)
    p_std_m1_2_item = add_para(doc, left_indent=Cm(1.5), space_after=Pt(0))
    add_styled_run(p_std_m1_2_item, "2) ความภูมิใจในท้องถิ่นและความเป็นไทย", bold=False)

    # นโยบายของโรงเรียน
    p_sch_pol = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_sch_pol, "นโยบายของโรงเรียน", bold=True)
    for pol_item in [
        "3. ส่งเสริมและพัฒนาศักยภาพนักเรียนด้านทักษะวิชาการ",
        "8. ส่งเสริมให้นักเรียนมีความภาคภูมิใจในท้องถิ่นและความเป็นไทย",
        "12. ส่งเสริมพัฒนาระบบดูแลช่วยเหลือนักเรียน และเพิ่มโอกาสทางการศึกษา"
    ]:
        p_item = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0))
        add_styled_run(p_item, pol_item, bold=False)

    # เป้าหมายของโรงเรียน
    p_sch_tgt = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_sch_tgt, "เป้าหมายของโรงเรียน", bold=True)
    for tgt_item in [
        "2. นักเรียนมีสมรรถนะและทักษะในศตวรรษที่ 21",
        "8. โรงเรียนมีระบบแนะแนวที่เข้มแข็งในการชี้แนะ (Coaching) การดูแลสุขภาพกายและสุขภาพจิตของนักเรียน"
    ]:
        p_item = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0))
        add_styled_run(p_item, tgt_item, bold=False)

    # 1. หลักการและเหตุผล (3 Paragraphs)
    p_sec1 = add_para(doc, space_before=Pt(3), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_sec1, "1. หลักการและเหตุผล", bold=True)

    para1_text = "ปัจจุบันการจัดการศึกษามุ่งเน้นการพัฒนาผู้เรียนให้มีสมรรถนะที่จำเป็นในศตวรรษที่ 21 ทั้งด้านวิชาการ ทักษะชีวิต และการวางแผนอนาคต สอดคล้องกับนโยบายของสำนักงานคณะกรรมการการศึกษาขั้นพื้นฐานที่มุ่งสร้างความเข้มแข็งของระบบแนะแนว ส่งเสริมศักยภาพผู้เรียนตามความถนัดและความสนใจ รวมถึงการปลูกฝังความภาคภูมิใจในความเป็นไทยผ่านศิลปวัฒนธรรมท้องถิ่น ซึ่งเป็นสิ่งจำเป็นอย่างยิ่งในการเตรียมความพร้อมให้ผู้เรียนสามารถปรับตัวและดำรงชีวิตในสังคมได้อย่างมีความสุข"
    p_bg1 = add_para(doc, first_line_indent=Cm(1.25), space_after=Pt(1), line_spacing=1.0)
    add_styled_run(p_bg1, para1_text)

    para2_text = "โรงเรียนพูลเจริญวิทยาคมมีเป้าหมายในการพัฒนานักเรียนให้มีสมรรถนะและทักษะในศตวรรษที่ 21 ควบคู่ไปกับการมีระบบแนะแนวที่เข้มแข็งในการชี้แนะ (Coaching) และดูแลนักเรียนอย่างรอบด้าน การบริหารจัดการและการจัดกิจกรรมพัฒนาผู้เรียนจึงต้องสนับสนุนให้ผู้เรียนได้รับการพัฒนาบุคลิกภาพ การเรียนรู้ศิลปะพื้นบ้าน และได้รับข้อมูลสารสนเทศด้านการศึกษาต่อจากสถาบันภายนอก เพื่อเปิดโลกทัศน์และสร้างแรงบันดาลใจในการเรียนรู้"
    p_bg2 = add_para(doc, first_line_indent=Cm(1.25), space_after=Pt(1), line_spacing=1.0)
    add_styled_run(p_bg2, para2_text)

    para3_text = "ด้วยเหตุนี้ กลุ่มบริหารวิชาการจึงได้จัดทำโครงการกิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิตขึ้น เพื่อพัฒนานักเรียนระดับชั้นมัธยมศึกษาปีที่ 1-6 ให้มีบุคลิกภาพที่ดี มีความรู้ความเข้าใจในเพลงพื้นบ้าน และได้รับการแนะแนวการศึกษาต่อจากสถาบันภายนอก ซึ่งผลลัพธ์จากการดำเนินโครงการจะช่วยยกระดับคุณภาพการจัดการศึกษาของสถานศึกษา และส่งเสริมให้ผู้เรียนบรรลุตามเป้าหมายของหลักสูตรได้อย่างมีประสิทธิภาพ"
    p_bg3 = add_para(doc, first_line_indent=Cm(1.25), space_after=Pt(2), line_spacing=1.0)
    add_styled_run(p_bg3, para3_text)

    # 2. วัตถุประสงค์
    p_sec2 = add_para(doc, space_before=Pt(2), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_sec2, "2. วัตถุประสงค์", bold=True)
    
    objs = [
        "1. เพื่อพัฒนาบุคลิกภาพและทักษะชีวิตของนักเรียนชั้นมัธยมศึกษาปีที่ 1-6",
        "2. เพื่อปลูกฝังความภาคภูมิใจในท้องถิ่นและความเป็นไทยผ่านการอบรมเพลงพื้นบ้าน",
        "3. เพื่อให้นักเรียนได้รับข้อมูลและแนวทางการศึกษาต่อจากสถาบันการศึกษาภายนอก"
    ]
    for obj in objs:
        p_obj = add_para(doc, left_indent=Cm(0.75), space_after=Pt(0))
        add_styled_run(p_obj, obj)

    # 3. เป้าหมาย
    p_sec3 = add_para(doc, space_before=Pt(2), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_sec3, "3. เป้าหมาย", bold=True)

    p_tgt_qty_lbl = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_tgt_qty_lbl, "เชิงปริมาณ", bold=True)
    p_tgt_qty = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0))
    add_styled_run(p_tgt_qty, "นักเรียนชั้นมัธยมศึกษาปีที่ 1-6 จำนวนทั้งสิ้น 2,628 คน เข้าร่วมกิจกรรมส่งเสริมวิชาการและพัฒนาทักษะชีวิตระดับละ 1 วัน (คิดเป็นร้อยละ 100 ของกลุ่มเป้าหมาย)")

    p_tgt_ql_lbl = add_para(doc, left_indent=Cm(0.5), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_tgt_ql_lbl, "เชิงคุณภาพ", bold=True)
    ql_items = [
        "1. นักเรียนมีบุคลิกภาพที่ดีขึ้น มีความรู้ความเข้าใจและตระหนักถึงคุณค่าของเพลงพื้นบ้านและศิลปวัฒนธรรมไทย",
        "2. นักเรียนมีแนวทางในการวางแผนการศึกษาต่อและเส้นทางอาชีพในอนาคตได้อย่างเหมาะสม"
    ]
    for ql in ql_items:
        p_ql = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0))
        add_styled_run(p_ql, ql)

    # 4. กิจกรรมและการดำเนินการ (Table)
    p_sec4 = add_para(doc, space_before=Pt(2), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_sec4, "4. กิจกรรมและการดำเนินการ", bold=True)

    # Table 4: กิจกรรม (9.5 cm, 3.2 cm, 3.76 cm = 16.46 cm)
    t4 = doc.add_table(rows=11, cols=3)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_table_bw_borders(t4)
    
    col_w4 = [9.5, 3.2, 3.76]
    
    # Header
    set_cell_properties(t4.cell(0, 0), "กิจกรรม", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w4[0])
    set_cell_properties(t4.cell(0, 1), "ระยะเวลา", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w4[1])
    set_cell_properties(t4.cell(0, 2), "ผู้รับผิดชอบ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w4[2])
    set_table_header(t4.rows[0])

    # Row 1: ขั้นเตรียมการ
    t4.cell(1, 0).merge(t4.cell(1, 2))
    set_cell_properties(t4.cell(1, 0), "ขั้นเตรียมการ", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, shading="F2F2F2", width_cm=sum(col_w4))

    # Row 2:
    set_cell_properties(t4.cell(2, 0), "1. ประชุมวางแผน เขียนโครงการและเสนอขออนุมัติ", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(2, 1), "5-13 มี.ค. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(2, 2), "กลุ่มบริหารวิชาการ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    # Row 3:
    set_cell_properties(t4.cell(3, 0), "2. ประสานงานวิทยากร สถาบันการศึกษาภายนอก และเตรียมสถานที่", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(3, 1), "ส.ค. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(3, 2), "กลุ่มบริหารวิชาการ /\nหัวหน้าระดับ ม.1-ม.6", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    # Row 4: ขั้นดำเนินการ
    t4.cell(4, 0).merge(t4.cell(4, 2))
    set_cell_properties(t4.cell(4, 0), "ขั้นดำเนินการ (บรรยายขั้นตอน/ลักษณะของงานโดยสังเขป)", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, shading="F2F2F2", width_cm=sum(col_w4))

    # Row 5: Group 1 (ม.3, 5, 6)
    set_cell_properties(t4.cell(5, 0), "1. จัดกิจกรรมช่วงเช้า (08.00-11.30 น.) สำหรับ ม.3, ม.5, ม.6:\n   - ฐานละครไทยในวรรณคดี, ฐานเพลงพื้นบ้าน (เพลงฉ่อย) และฐานการละเล่นไทย", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(5, 1), "10, 11, 14 ก.ย. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(5, 2), "คณะวิทยากรเพลงพื้นบ้าน /\nหัวหน้าระดับ ม.3, 5, 6", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    # Row 6: Group 2 (ม.1, 2, 4)
    set_cell_properties(t4.cell(6, 0), "2. จัดกิจกรรมช่วงเช้า (08.00-11.30 น.) สำหรับ ม.1, ม.2, ม.4:\n   - กิจกรรมอบรมพัฒนาบุคลิกภาพ มารยาททางสังคม และทักษะชีวิต", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(6, 1), "7, 8, 9 ก.ย. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(6, 2), "วิทยากรพัฒนาบุคลิกภาพ /\nหัวหน้าระดับ ม.1, 2, 4", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    # Row 7: Afternoon Guidance (ม.1 - ม.6)
    set_cell_properties(t4.cell(7, 0), "3. จัดกิจกรรมช่วงบ่าย (12.30-16.00 น.) สำหรับ ม.1 - ม.6:\n   - กิจกรรมแนะแนวการศึกษาต่อและเส้นทางอาชีพจากสถาบันภายนอก", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(7, 1), "7-14 ก.ย. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(7, 2), "วิทยากรภายนอก /\nหัวหน้าระดับ ม.1-ม.6", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    # Row 8: ขั้นติดตามและประเมินผล
    t4.cell(8, 0).merge(t4.cell(8, 2))
    set_cell_properties(t4.cell(8, 0), "ขั้นติดตามและประเมินผล", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, shading="F2F2F2", width_cm=sum(col_w4))

    # Row 9:
    set_cell_properties(t4.cell(9, 0), "1. ครู-นักเรียน ร่วมกันประเมินผลโครงการ", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(9, 1), "15 ก.ย. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(9, 2), "คณะครูกลุ่มบริหารวิชาการ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    # Row 10:
    set_cell_properties(t4.cell(10, 0), "2. จัดทำรูปเล่มและสรุปรายงานผลการดำเนินโครงการ", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w4[0])
    set_cell_properties(t4.cell(10, 1), "20 ก.ย. 2569", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[1])
    set_cell_properties(t4.cell(10, 2), "คณะครูกลุ่มบริหารวิชาการ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w4[2])

    for row in t4.rows:
        prevent_row_split(row)

    # 5. ผู้รับผิดชอบโครงการ
    p_sec5 = add_para(doc, space_before=Pt(2), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_sec5, "5. ผู้รับผิดชอบโครงการ", bold=True)
    p_resp1 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(1))
    add_styled_run(p_resp1, "1. หัวหน้าระดับ ม.1 – ม.6")

    # 6. หน่วยงาน/บุคลากรที่เกี่ยวข้อง
    p_sec6 = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_sec6, "6. หน่วยงาน/บุคลากรที่เกี่ยวข้อง (ถ้ามี)", bold=True)
    p_rel1 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(0))
    add_styled_run(p_rel1, "1. กลุ่มบริหารวิชาการ")
    p_rel2 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(0))
    add_styled_run(p_rel2, "2. กลุ่มบริหารทั่วไป")
    p_rel3 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(1))
    add_styled_run(p_rel3, "3. กลุ่มบริหารงบประมาณ")

    # 7. งบประมาณ
    p_sec7 = add_para(doc, space_before=Pt(1), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_sec7, "7. งบประมาณ (โดยประมาณ)", bold=True)
    
    p_bg_item1 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(0))
    add_styled_run(p_bg_item1, "1. เงินอุดหนุน (กิจกรรมพัฒนาผู้เรียน)\t\t363,880\tบาท")
    p_bg_item2 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(0))
    add_styled_run(p_bg_item2, "2. เงินรายได้สถานศึกษา\t\t\t\t-\tบาท")
    p_bg_item3 = add_para(doc, left_indent=Cm(0.75), space_after=Pt(0))
    add_styled_run(p_bg_item3, "3. เงินอื่น ๆ ระบุ - \t\t\t\t-\tบาท")
    p_bg_total = add_para(doc, left_indent=Cm(0.75), space_after=Pt(1))
    add_styled_run(p_bg_total, "รวมทั้งสิ้น\t\t\t\t\t363,880\tบาท", bold=True)

    # 8. รายละเอียดการใช้วัสดุและงบประมาณดำเนินงาน (ตารางที่ 8)
    doc.add_page_break()
    p_sec8 = add_para(doc, space_before=Pt(0), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_sec8, "8. รายละเอียดการใช้วัสดุและงบประมาณดำเนินงาน", bold=True)

    # Table 8: (1.2 cm, 7.8 cm, 2.4 cm, 2.3 cm, 2.76 cm = 16.46 cm)
    t8 = doc.add_table(rows=13, cols=5)
    t8.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_table_bw_borders(t8)
    col_w8 = [1.2, 7.8, 2.4, 2.3, 2.76]

    # Header
    set_cell_properties(t8.cell(0, 0), "ที่", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w8[0])
    set_cell_properties(t8.cell(0, 1), "รายการ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w8[1])
    set_cell_properties(t8.cell(0, 2), "จำนวน\n(หน่วย)", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w8[2])
    set_cell_properties(t8.cell(0, 3), "ราคา/\nหน่วย", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w8[3])
    set_cell_properties(t8.cell(0, 4), "งบประมาณ\n(บาท)", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w8[4])
    set_table_header(t8.rows[0])

    # Section 1: ค่าตอบแทนวิทยากร (Merge)
    t8.cell(1, 0).merge(t8.cell(1, 4))
    set_cell_properties(t8.cell(1, 0), "1. ค่าตอบแทนวิทยากร (รวม 64,800 บาท)", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, shading="F2F2F2", width_cm=sum(col_w8))

    # Row 2: ม.1, ม.2, ม.4
    set_cell_properties(t8.cell(2, 0), "1.1", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[0])
    set_cell_properties(t8.cell(2, 1), "- ค่าตอบแทนวิทยากร ม.1, ม.2, ม.4 (ระดับละ 7,200 บ.)", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w8[1])
    set_cell_properties(t8.cell(2, 2), "3 ระดับ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[2])
    set_cell_properties(t8.cell(2, 3), "7,200", align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[3])
    set_cell_properties(t8.cell(2, 4), "21,600", align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[4])

    # Row 3: ม.3, ม.5, ม.6
    set_cell_properties(t8.cell(3, 0), "1.2", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[0])
    set_cell_properties(t8.cell(3, 1), "- ค่าตอบแทนวิทยากร ม.3, ม.5, ม.6 (ระดับละ 14,400 บ.)", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w8[1])
    set_cell_properties(t8.cell(3, 2), "3 ระดับ", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[2])
    set_cell_properties(t8.cell(3, 3), "14,400", align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[3])
    set_cell_properties(t8.cell(3, 4), "43,200", align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[4])

    # Section 2: ค่าอาหารและเครื่องดื่มสำหรับผู้เข้าร่วม (Merge)
    t8.cell(4, 0).merge(t8.cell(4, 4))
    set_cell_properties(t8.cell(4, 0), "2. ค่าอาหารและเครื่องดื่มสำหรับผู้เข้าร่วม (อาหารว่าง 50 บ. + อาหารกลางวัน 60 บ. = 110 บ./คน รวม 289,080 บาท)", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, shading="F2F2F2", width_cm=sum(col_w8))

    # Rows for students M1-M6
    mat_rows = [
        ("2.1", "- นักเรียนระดับชั้นมัธยมศึกษาปีที่ 1", "580 คน", "110", "63,800"),
        ("2.2", "- นักเรียนระดับชั้นมัธยมศึกษาปีที่ 2", "561 คน", "110", "61,710"),
        ("2.3", "- นักเรียนระดับชั้นมัธยมศึกษาปีที่ 3", "514 คน", "110", "56,540"),
        ("2.4", "- นักเรียนระดับชั้นมัธยมศึกษาปีที่ 4", "335 คน", "110", "36,850"),
        ("2.5", "- นักเรียนระดับชั้นมัธยมศึกษาปีที่ 5", "324 คน", "110", "35,640"),
        ("2.6", "- นักเรียนระดับชั้นมัธยมศึกษาปีที่ 6", "314 คน", "110", "34,540"),
    ]
    for idx, (c1, c2, c3, c4, c5) in enumerate(mat_rows, start=5):
        set_cell_properties(t8.cell(idx, 0), c1, align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[0])
        set_cell_properties(t8.cell(idx, 1), c2, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w8[1])
        set_cell_properties(t8.cell(idx, 2), c3, align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[2])
        set_cell_properties(t8.cell(idx, 3), c4, align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[3])
        set_cell_properties(t8.cell(idx, 4), c5, align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[4])

    # Section 3: ค่าวัสดุอุปกรณ์ดำเนินงาน (Merge)
    t8.cell(11, 0).merge(t8.cell(11, 4))
    set_cell_properties(t8.cell(11, 0), "3. ค่าวัสดุอุปกรณ์ดำเนินงาน (รวม 10,000 บาท)", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, shading="F2F2F2", width_cm=sum(col_w8))

    # Row 12: ค่าวัสดุอุปกรณ์
    set_cell_properties(t8.cell(12, 0), "3.1", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[0])
    set_cell_properties(t8.cell(12, 1), "- ค่าวัสดุ อุปกรณ์ และสื่อสำหรับจัดกิจกรรมฐานการเรียนรู้", align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w8[1])
    set_cell_properties(t8.cell(12, 2), "1 ชุด", align=WD_ALIGN_PARAGRAPH.CENTER, width_cm=col_w8[2])
    set_cell_properties(t8.cell(12, 3), "10,000", align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[3])
    set_cell_properties(t8.cell(12, 4), "10,000", align=WD_ALIGN_PARAGRAPH.RIGHT, width_cm=col_w8[4])

    # Total Row: Merge cols 0-3
    row_tot = t8.add_row()
    row_tot.cells[0].merge(row_tot.cells[3])
    set_cell_properties(row_tot.cells[0], "รวมเป็นเงินทั้งสิ้น", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=sum(col_w8[:4]))
    set_cell_properties(row_tot.cells[4], "363,880", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, shading="F2F2F2", width_cm=col_w8[4])

    for row in t8.rows:
        prevent_row_split(row)

    p_note = add_para(doc, left_indent=Cm(0.5), space_before=Pt(0.5), space_after=Pt(1))
    add_styled_run(p_note, "(สามารถถัวเฉลี่ยได้ทุกรายการภายในวงเงินงบประมาณที่กำหนด)", italic=True, size_pt=14)

    # 9. การประเมินผล (Table)
    p_sec9 = add_para(doc, space_before=Pt(1), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_sec9, "9. การประเมินผล", bold=True)

    t9 = doc.add_table(rows=3, cols=3)
    t9.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_table_bw_borders(t9)
    col_w9 = [7.0, 4.7, 4.76]

    # Header
    set_cell_properties(t9.cell(0, 0), "ตัวชี้วัดความสำเร็จ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w9[0])
    set_cell_properties(t9.cell(0, 1), "วิธีประเมิน", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w9[1])
    set_cell_properties(t9.cell(0, 2), "เครื่องมือประเมิน", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, shading="F2F2F2", width_cm=col_w9[2])
    set_table_header(t9.rows[0])

    # Rows
    eval_rows = [
        ("1. นักเรียนร้อยละ 100 เข้าร่วมกิจกรรมตามที่กำหนด", "การตรวจสอบเวลาเข้าร่วมกิจกรรม", "แบบบันทึกการเข้าร่วมกิจกรรม"),
        ("2. นักเรียนมีทักษะชีวิต บุคลิกภาพที่ดี และมีแนวทางในการศึกษาต่อ", "การประเมินความพึงพอใจและประโยชน์ที่ได้รับ", "แบบประเมินความพึงพอใจของนักเรียน")
    ]
    for r_idx, (c1, c2, c3) in enumerate(eval_rows, start=1):
        set_cell_properties(t9.cell(r_idx, 0), c1, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w9[0])
        set_cell_properties(t9.cell(r_idx, 1), c2, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w9[1])
        set_cell_properties(t9.cell(r_idx, 2), c3, align=WD_ALIGN_PARAGRAPH.LEFT, width_cm=col_w9[2])

    for row in t9.rows:
        prevent_row_split(row)

    # 10. Signature Blocks exactly matching planning template (Page 18)
    doc.add_page_break()
    p_sig_top = add_para(doc, space_before=Pt(10), space_after=Pt(0), keep_with_next=True)
    
    def fill_sig_cell(cell, lines, width_cm=8.23, align=WD_ALIGN_PARAGRAPH.CENTER):
        cell.width = Cm(width_cm)
        cell.text = ''
        for i, item in enumerate(lines):
            if i == 0:
                p = cell.paragraphs[0]
            else:
                p = cell.add_paragraph()
            p.alignment = align
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            if isinstance(item, tuple):
                text, bold, italic, underline = item
                add_styled_run(p, text, size_pt=15, bold=bold, italic=italic, underline=underline)
            elif item == "":
                add_styled_run(p, " ", size_pt=8)
            else:
                add_styled_run(p, item, size_pt=15)

    # 1. ผู้เสนอ งาน / โครงการ (Left) & กลุ่มบริหารวิชาการ (Right)
    t_sig1 = doc.add_table(rows=1, cols=2)
    t_sig1.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_invisible_borders(t_sig1)
    fill_sig_cell(t_sig1.cell(0, 0), [
        "(ลงชื่อ)....................................................",
        "(..............................................)",
        "ผู้เสนอ งาน / โครงการ"
    ], width_cm=8.23)
    fill_sig_cell(t_sig1.cell(0, 1), [
        "(ลงชื่อ)....................................................",
        "(..............................................)",
        "กลุ่มบริหารวิชาการ"
    ], width_cm=8.23)
    prevent_row_split(t_sig1.rows[0])

    # 2. รองผู้อำนวยการกลุ่มบริหารวิชาการ (Right Column)
    add_para(doc, space_before=Pt(2), space_after=Pt(0), keep_with_next=True)
    t_sig2 = doc.add_table(rows=1, cols=2)
    t_sig2.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_invisible_borders(t_sig2)
    t_sig2.cell(0, 0).width = Cm(8.23)
    t_sig2.cell(0, 0).text = ''
    fill_sig_cell(t_sig2.cell(0, 1), [
        "(ลงชื่อ)....................................................",
        "(นางสาวภัทรพร   ประมาตร)",
        "รองผู้อำนวยการกลุ่มบริหารวิชาการ"
    ], width_cm=8.23)
    prevent_row_split(t_sig2.rows[0])

    # 3. ความคิดเห็นของหัวหน้างานแผนงาน (Left: Title + Options, Right: Signature)
    add_para(doc, space_before=Pt(2), space_after=Pt(0), keep_with_next=True)
    t_plan = doc.add_table(rows=1, cols=2)
    t_plan.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_invisible_borders(t_plan)
    
    fill_sig_cell(t_plan.cell(0, 0), [
        ("ความคิดเห็นของหัวหน้างานแผนงาน", True, False, True),
        "",
        "[       ]  เห็นควรให้ดำเนินการ",
        "[       ]  ไม่ควรให้ดำเนินการ"
    ], width_cm=8.23, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    fill_sig_cell(t_plan.cell(0, 1), [
        "",
        "(ลงชื่อ)....................................................",
        "(นายพินิจ     จันทร์ดี)",
        "หัวหน้างานแผนงาน"
    ], width_cm=8.23, align=WD_ALIGN_PARAGRAPH.CENTER)
    prevent_row_split(t_plan.rows[0])

    # 4. ผลการพิจารณาของผู้อำนวยการ (Centered Title, Checkboxes Left, Signature Right)
    p_dir_title = add_para(doc, space_before=Pt(2), space_after=Pt(1), align=WD_ALIGN_PARAGRAPH.CENTER, keep_with_next=True)
    add_styled_run(p_dir_title, "ผลการพิจารณาของผู้อำนวยการ", bold=True, underline=True, size_pt=15.5)

    p_dir_chk1 = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_dir_chk1, "[       ]  อนุมัติ", size_pt=15)

    p_dir_chk2 = add_para(doc, left_indent=Cm(1.0), space_after=Pt(0), keep_with_next=True)
    add_styled_run(p_dir_chk2, "[       ]  ไม่อนุมัติ  เนื่องด้วยเหตุผลดังนี้  ............................................................................", size_pt=15)

    p_dir_line = add_para(doc, left_indent=Cm(1.0), space_after=Pt(1), keep_with_next=True)
    add_styled_run(p_dir_line, "            .............................................................................................................................", size_pt=15)

    t_dir = doc.add_table(rows=1, cols=2)
    t_dir.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_invisible_borders(t_dir)
    t_dir.cell(0, 0).width = Cm(8.23)
    t_dir.cell(0, 0).text = ''
    fill_sig_cell(t_dir.cell(0, 1), [
        "(ลงชื่อ)....................................................",
        "(นางสุภาพร   รัตน์น้อย)",
        "ผู้อำนวยการโรงเรียนพูลเจริญวิทยาคม"
    ], width_cm=8.23, align=WD_ALIGN_PARAGRAPH.CENTER)
    prevent_row_split(t_dir.rows[0])

    doc.save("โครงการ 01 formatted.docx")
    print("File created successfully: 'โครงการ 01 formatted.docx'")

if __name__ == "__main__":
    update_main_project_doc()
    create_activity_schedule_doc()
