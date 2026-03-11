import fitz
import sys
import os

pdf_path = r"E:\dailm---distributed-ai-labor-market\海南大学平安校园升级改造项目招标文件.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: File not found at {pdf_path}")
    sys.exit(1)

try:
    doc = fitz.open(pdf_path)
    text = ""
    # Extract first 5 pages to avoid massive payload for initial validation
    for i in range(min(5, len(doc))):
        text += doc[i].get_text()
    
    print("--- PDF CONTENT PREVIEW ---")
    print(text[:1000])
    print("--- END PREVIEW ---")
    doc.close()
except Exception as e:
    print(f"Error parsing PDF: {e}")
    sys.exit(1)
