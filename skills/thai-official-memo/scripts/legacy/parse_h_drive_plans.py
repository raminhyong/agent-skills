import os
import re
import json
import docx

h_dir = r"H:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\แบบขออนุมัติใช้แผนการสอน"
files = sorted(os.listdir(h_dir))

records = []

for f in files:
    if not f.endswith(".docx"):
        continue
    fpath = os.path.join(h_dir, f)
    doc = docx.Document(fpath)
    
    # Extract teacher info
    teacher_name = f.replace("แบบเสนอขออนุมัติโครงการการจัดการเรียนรู้ - ", "").replace(".docx", "").strip()
    position = ""
    academic_standing = ""
    subject_count = ""
    courses = []
    
    target_p = ""
    for p in doc.paragraphs:
        if "ข้าพเจ้า" in p.text:
            target_p = p.text
            break
            
    if target_p:
        # e.g., ข้าพเจ้า นางวรางคณา ศรีม่วง ตำแหน่ง ครู วิทยฐานะ ครูชำนาญการพิเศษ กลุ่มสาระการเรียนรู้ภาษาไทย ได้รับมอบหมายจากโรงเรียนพูลเจริญวิทยาคม ให้จัดการเรียนการสอน จำนวน 1 รายวิชา ประกอบด้วย 1. รหัสวิชา ท23101 ชื่อวิชา ภาษาไทยพื้นฐาน 5  จำนวน 1.5 หน่วยกิต ได้ดำเนินการจัดทำโครงการการจัดการเรียนรู้เสร็จสิ้นแล้วนั้น
        m_name = re.search(r"ข้าพเจ้า\s+([^\n\r]+?)\s+ตำแหน่ง\s+([^\n\r]+?)\s+วิทยฐานะ\s+([^\n\r]+?)\s+กลุ่มสาระ", target_p)
        if m_name:
            teacher_name = m_name.group(1).strip()
            position = m_name.group(2).strip()
            academic_standing = m_name.group(3).strip()
        else:
            m_name2 = re.search(r"ข้าพเจ้า\s+([^\n\r]+?)\s+ตำแหน่ง\s+([^\n\r]+?)\s+กลุ่มสาระ", target_p)
            if m_name2:
                teacher_name = m_name2.group(1).strip()
                position = m_name2.group(2).strip()
        
        m_cnt = re.search(r"จำนวน\s*(\d+)\s*รายวิชา", target_p)
        if m_cnt:
            subject_count = m_cnt.group(1).strip()
            
        # extract course parts
        # Let's find after 'ประกอบด้วย'
        if "ประกอบด้วย" in target_p:
            courses_str = target_p.split("ประกอบด้วย", 1)[1]
            if "ได้ดำเนินการ" in courses_str:
                courses_str = courses_str.split("ได้ดำเนินการ", 1)[0]
                
            # split by number like 1. 2. 3.
            items = re.split(r'\d+\.\s*', courses_str)
            for item in items:
                item = item.strip()
                if not item:
                    continue
                # item like: รหัสวิชา ท23101 ชื่อวิชา ภาษาไทยพื้นฐาน 5  จำนวน 1.5 หน่วยกิต
                m_c = re.search(r"รหัสวิชา\s*([^\s]+)\s+ชื่อวิชา\s*([^\n\r]+?)(?:\s+จำนวน\s*([\d\.]+)\s*หน่วยกิต|$)", item)
                if m_c:
                    c_code = m_c.group(1).strip()
                    c_name = m_c.group(2).strip()
                    c_credit = m_c.group(3).strip() if m_c.group(3) else ""
                    courses.append({"code": c_code, "name": c_name, "credit": c_credit, "raw": item})
                else:
                    courses.append({"raw": item})
                    
    records.append({
        "file": f,
        "teacher": teacher_name,
        "position": position,
        "academic_standing": academic_standing,
        "subject_count": subject_count,
        "courses": courses,
        "raw_p": target_p
    })

with open("d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/scratch/extracted_teachers_courses.json", "w", encoding="utf-8") as out:
    json.dump(records, out, ensure_ascii=False, indent=2)

print(f"Extracted {len(records)} records successfully.")
