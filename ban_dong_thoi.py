import sys
import httpx
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:8000/api/dang-ky"
PHIEN = sys.argv[1]

# Cấu hình timeout 30s để các request cuối hàng không bị đứt kết nối giữa chừng
client_timeout = httpx.Timeout(30.0, connect=10.0)

def gui(i):
    r = httpx.post(
        URL, 
        json={"ma_sv": f"TN{i:03d}", "ma_phien": PHIEN}, 
        timeout=client_timeout
    )
    return r.status_code

with ThreadPoolExecutor(max_workers=40) as ex:
    ma = list(ex.map(gui, range(40)))

print(f"{PHIEN} 201: {ma.count(201)}   409: {ma.count(409)}")