import os
import fitz # PyMuPDF
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "scripts", "job02_new_parsed.json"), "r", encoding="utf-8") as f:
    questions = json.load(f)

# Let's use PyMuPDF font to measure text width
font = fitz.Font("figo") # standard or measure via docx rendering

# Let's write a script that tests 2-column layout in docx and checks if any choice wraps in Word
print("Measuring choices...")
