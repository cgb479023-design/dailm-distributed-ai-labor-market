from pypdf import PdfReader
import os

pdf_path = r"E:\dailm---distributed-ai-labor-market\海南大学平安校园升级改造项目招标文件.pdf"
output_path = "RFP_EXTRACTION_FINAL.txt"

def audit_rfp():
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    reader = PdfReader(pdf_path)
    findings = []
    
    findings.append(f"--- RFP AUDIT PULSE: {os.path.basename(pdf_path)} ---")
    findings.append(f"TOTAL PAGES: {len(reader.pages)}")

    keywords = ["★", "评分", "技术参数", "技术需求", "商务要求", "中标", "废标"]
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if any(key in text for key in keywords):
            findings.append(f"\n[PAGE {i+1}]")
            # Extract lines containing keywords
            lines = text.split('\n')
            for line in lines:
                if any(key in line for key in keywords):
                    findings.append(line.strip())

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(findings))
    
    print(f"Audit Complete. Findings saved to {output_path}")

if __name__ == "__main__":
    audit_rfp()
