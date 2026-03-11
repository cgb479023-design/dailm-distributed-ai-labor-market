import http.client
import json

def purge_system():
    conn = http.client.HTTPConnection("127.0.0.1", 8000)
    print(f"Triggering http://127.0.0.1:8000/api/system/purge...")
    try:
        conn.request("POST", "/api/system/purge")
        response = conn.getresponse()
        data = response.read().decode()
        print(f"Status: {response.status}")
        print(f"Response Body: {data}")
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    purge_system()
