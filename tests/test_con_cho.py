import os
os.environ["DB_PATH"] = ":memory:"

from fastapi.testclient import TestClient
from main import app, init_db

client = TestClient(app)

def test_con_cho_ban_dau_la_30():
    init_db()
    res = client.get("/api/con-cho?ma_phien=P01")
    assert res.status_code == 200
    assert res.json() == {"con_cho": 30}