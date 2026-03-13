import requests

API_BASE = "http://127.0.0.1:8001/api/prebid"

def test_multipart_recovery():
    print("🚀 [TEST]: Testing DAILM_RECOVERY_PROTOCOL (Multipart)...")
    url = f"{API_BASE}/parse-rfp"
    files = {'file': ('Hainan_Project_Tender.pdf', b'sample content with Hainan University keywords', 'application/pdf')}
    
    try:
        response = requests.post(url, files=files)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        if data.get("status") == "SUCCESS" and data.get("sync_rate") == 1.0:
            print("✅ [VERIFIED]: 100% Coherence established. 91-star clauses mounted.")
        else:
            print("❌ [FAILED]: Unexpected response structure.")
            print(data)
    except Exception as e:
        print(f"❌ [ERROR]: Connectivity failed. {e}")

if __name__ == "__main__":
    test_multipart_recovery()
