import fitz  # PyMuPDF
import sys
import os
import json
import time
import urllib.request
import urllib.error

# Configuration
PDF_PATH = r"E:\dailm---distributed-ai-labor-market\海南大学平安校园升级改造项目招标文件.pdf"
API_URL = "http://127.0.0.1:8000/api/prebid/full-strike"
OUTPUT_NAME = "HAINAN_UNI_CAMPUS_SECURITY_V1"
STRIKE_DIR = "strike_packages"

def extract_pdf_full_text(path):
    print(f"[*] Extracting full text from: {path}")
    if not os.path.exists(path):
        print(f"[!] Error: File not found at {path}")
        return None
    
    try:
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        print(f"[+] Extraction complete. Original Length: {len(full_text)} characters.")
        
        # Truncate to avoid browser UI freeze / timeout
        if len(full_text) > 10000:
            print("[*] Truncating to 10000 characters for validation pipeline test.")
            full_text = full_text[:10000] + "\n\n(END OF CONTENT - TRUNCATED FOR TEST)"

        return full_text
    except Exception as e:
        print(f"[!] Error during extraction: {e}")
        return None

def trigger_full_strike(content):
    print(f"[*] Triggering full-strike analysis for: {OUTPUT_NAME}")
    payload = {
        "content": content,
        "style": "GOV_BIZ",
        "output_name": OUTPUT_NAME,
        "draft_path": os.path.join(STRIKE_DIR, f"{OUTPUT_NAME}.md")
    }
    
    try:
        start_time = time.time()
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=300) as response:
            duration = time.time() - start_time
            result = json.loads(response.read().decode('utf-8'))
            print(f"[+] API Call Successful. Duration: {duration:.2f}s")
            return result
    except urllib.error.URLError as e:
        print(f"[!] Network Error: {e}")
        return None
    except Exception as e:
        print(f"[!] Unexpected Error: {e}")
        return None

def verify_outputs(result):
    print("[*] Verifying generated assets...")
    if not result or result.get("status") != "SUCCESS":
        print("[!] Validation failed: Invalid result data.")
        return False
    
    # Check paths
    draft_path = result.get("bid_draft_path")
    
    if draft_path and os.path.exists(draft_path):
        print(f"[+] Bid Draft generated: {draft_path}")
    else:
        print(f"[!] Missing Bid Draft at expected path.")
        return False
        
    print("[+] All core assets verified successfully.")
    return True

def main():
    # 1. Extract
    content = extract_pdf_full_text(PDF_PATH)
    if not content:
        sys.exit(1)
        
    # 2. Strike
    result = trigger_full_strike(content)
    if not result:
        sys.exit(1)
        
    # 3. Verify
    if verify_outputs(result):
        print("\n" + "="*40)
        print(" MISSION ACCOMPLISHED: END-TO-END VALIDATION PASSED ")
        print("="*40)
        print(f"Results Summary:")
        print(f" - Blueprint features: {len(result.get('blueprint', {}).get('features', []))}")
        print(f" - Bid Draft: {result.get('bid_draft_path')}")
        print(f" - UI Schema: {json.dumps(result.get('ui_schema', {}), indent=2)[:200]}...")
    else:
        print("\n[!] Validation Failed during verification phase.")
        sys.exit(1)

if __name__ == "__main__":
    main()
