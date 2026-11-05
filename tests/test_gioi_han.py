import os
os.environ["DB_PATH"] = ":memory:"  # CSDL tạm, không đụng dữ liệu thật

import pytest
from fastapi.testclient import TestClient
import main

# Khởi tạo lại bảng trên CSDL tạm :memory:
main.db = main.sqlite3.connect(":memory:", check_same_thread=False)
main.init_db()

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def so_trong():
    main.db.execute("DELETE FROM dang_ky")
    main.db.commit()

def lap_day(ma_phien: str, n: int):
    for i in range(n):
        client.post("/api/dang-ky", json={"ma_sv": f"SV{i:03d}", "ma_phien": ma_phien})

# 1. Phiên P01 trống -> SV001 đăng ký thành công (201)
def test_1_phien_trong_dang_ky_thanh_cong():
    r = client.post("/api/dang-ky", json={"ma_sv": "SV001", "ma_phien": "P01"})
    assert r.status_code == 201

# 2. Phiên P01 đang có 29 người -> Người thứ 30 đăng ký thành công (201)
def test_2_cho_thu_30_thanh_cong():
    lap_day("P01", 29)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV_MOI", "ma_phien": "P01"})
    assert r.status_code == 201

# 3. Phiên P01 đã có 30 người -> Người thứ 31 đăng ký BỊ TỪ CHỐI (409 HET_CHO)
def test_3_nguoi_thu_31_bi_tu_choi():
    lap_day("P01", 30)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV_MOI", "ma_phien": "P01"})
    assert r.status_code == 409
    assert r.json().get("detail") == "HET_CHO"

# 4. Phiên P01 có 30 người (gồm SV000) -> SV000 đăng ký lại bị báo lỗi DA_DANG_KY
def test_4_dang_ky_trung_bi_tu_choi():
    lap_day("P01", 30)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV000", "ma_phien": "P01"})
    assert r.status_code == 409
    assert r.json().get("detail") == "DA_DANG_KY"

# 5. Phiên P01 đã đủ 30 chỗ -> Nhưng đăng ký sang phiên P02 vẫn thành công (201)
def test_5_phien_khac_van_con_cho():
    lap_day("P01", 30)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV031", "ma_phien": "P02"})
    assert r.status_code == 201