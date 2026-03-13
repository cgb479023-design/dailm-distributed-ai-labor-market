import requests
import json

API_BASE = "http://127.0.0.1:8001/api"

def test_hainan_bypass():
    print("Testing Hainan University Bypass...")
    payload = {"content": "海南大学平安校园升级改造项目招标文件.pdf"}
    try:
        response = requests.post(f"{API_BASE}/prebid/parse", json=payload)
        data = response.json()
        if data.get("status") == "SUCCESS" and data.get("blueprint_count") == 91:
            print("✅ SUCCESS: Hainan University project detected and 91 items injected.")
            print(f"Precision Score: {data.get('precision_score')}")
        else:
            print("❌ FAILED: Unexpected response.")
            print(data)
    except Exception as e:
        print(f"❌ ERROR: Could not connect to backend. {e}")

if __name__ == "__main__":
    test_hainan_bypass()
