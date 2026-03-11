import http.client
import json
import time

def test_api():
    conn = http.client.HTTPConnection("127.0.0.1", 8000)
    payload = json.dumps({"task": "creative", "prompt": "Autonomous Verification Pulse."})
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing http://127.0.0.1:8000/api/task...")
    try:
        conn.request("POST", "/api/task", body=payload, headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        print(f"Status: {response.status}")
        print(f"Response Body: {data}")
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_api()
