from pypdf import PdfReader
import os
import json

pdf_path = r"E:\dailm---distributed-ai-labor-market\海南大学平安校园升级改造项目招标文件.pdf"
output_path = "RFP_EXTRACTION_FINAL.txt"

def find_compliance(extracted_data, keyword):
    return keyword in extracted_data

def fatal_risk_check(extracted_data):
    red_lines = ["签字盖章", "法人授权", "有效期限", "★"]
    warnings = []
    for line in red_lines:
        if not find_compliance(extracted_data, line):
            warnings.append(f"【废标风险】未检测到强制响应项：{line}")
    return warnings

def audit_rfp():
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    reader = PdfReader(pdf_path)
    findings = []
    
    findings.append(f"--- RFP AUDIT PULSE: {os.path.basename(pdf_path)} ---")
    findings.append(f"TOTAL PAGES: {len(reader.pages)}")
    findings.append(f"INSTRUCTION: Use dual-pane view mapping. Click anchors to jump to PDF page.")

    keywords = ["★", "评分", "技术参数", "技术需求", "商务要求", "中标", "废标", "签字盖章", "法人授权", "有效期限"]
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        if any(key in text for key in keywords):
            findings.append(f"\n[PAGE_ANCHOR: {i+1}]")
            # Extract lines containing keywords
            lines = text.split('\n')
            for line in lines:
                if any(key in line for key in keywords):
                    findings.append(f"    <a href='#pdf-page-{i+1}'>[Link to Page {i+1}]</a> {line.strip()}")

    # 【新增：将提取到的“★”项转化为 GUI 可识别的 Blueprint】
    blueprint = {
        "project_name": "海南大学平安校园升级改造项目",
        "features": [],
        "star_clauses": 0
    }
    
    star_count = 0
    # Search findings for "★" items to populate blueprint
    for item in findings:
        if "★" in item:
            star_count += 1
            # 提取具体的评分点文字 (cleaning up the link and whitespace)
            clean_text = item.split(']</a>')[-1].strip() if ']</a>' in item else item
            blueprint["features"].append({
                "id": f"star_{star_count}",
                "name": clean_text[:50] + "..." if len(clean_text) > 50 else clean_text,
                "status": "pending"
            })
    
    blueprint["star_clauses"] = star_count

    # 保存为 GUI 真正需要的 JSON 文件
    with open("blueprint.json", "w", encoding="utf-8") as f:
        json.dump(blueprint, f, ensure_ascii=False, indent=4)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(findings))
    
    print(f"✅ 审计完成。已产出文本脉冲和 blueprint.json")

if __name__ == "__main__":
    audit_rfp()
