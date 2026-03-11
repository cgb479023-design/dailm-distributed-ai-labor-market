import json
import urllib.request

def run_test():
    print("[TEST] Hitting /api/prebid/full-strike...")
    payload = {
        "content": "129海口市城市大脑二期项目招标文件.doc",
        "style": "GOV_BIZ",
        "output_name": "HAINAN_FINAL_STRIKE",
        "score_mapping": []
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8000/api/prebid/full-strike", data=data, headers={'Content-Type': 'application/json'})
    
    try:
        response = urllib.request.urlopen(req, timeout=120)
        print(f"Status: {response.status}")
        if response.status == 200:
            resp_body = response.read().decode('utf-8')
            print("Success: ", str(resp_body)[:500] + "...\n")
        else:
            print("Failed: ", response.read().decode('utf-8'))
    except Exception as e:
        print("Exception: ", str(e))

if __name__ == "__main__":
    run_test()
