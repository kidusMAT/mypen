import urllib.request
try:
    req = urllib.request.Request("http://127.0.0.1:8000/books/?page=2&ajax=1")
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Failed with status:", e.code)
    print(e.read().decode('utf-8'))
