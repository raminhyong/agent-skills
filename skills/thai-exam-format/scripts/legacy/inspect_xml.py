import docx
import xml.etree.ElementTree as ET

doc = docx.Document("Job02_Formatted.docx")
for idx, p in enumerate(doc.paragraphs[:15]):
    pPr_str = ET.tostring(p._p.pPr, encoding="unicode") if p._p.pPr is not None else "None"
    print(f"P{idx}: text='{p.text[:30]}' | pPr: {pPr_str}")
