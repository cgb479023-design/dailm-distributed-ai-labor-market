import http.client

def check_root():
    conn = http.client.HTTPConnection("127.0.0.1", 8000)
    print(f"Checking http://127.0.0.1:8000/docs...")
    try:
        conn.request("GET", "/docs")
        response = conn.getresponse()
        print(f"Status: {response.status}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_root()
