import sqlite3
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Cổng Đăng Ký Ngày Hội Việc Làm")

# Cấu hình CORS chuẩn cho phép toàn diện các nguồn cục bộ và phương thức OPTIONS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép các cổng cục bộ kết nối không bị chặn Preflight
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

DB_NAME = "ngayhoi.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dang_ky (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sv TEXT NOT NULL,
            ma_phien TEXT NOT NULL,
            UNIQUE(ma_sv, ma_phien)
        )
    """)
    conn.commit()
    conn.close()

init_db()

class DangKyRequest(BaseModel):
    ma_sv: str = Field(..., example="23110151")
    ma_phien: str = Field(..., example="P01")

@app.post("/api/dang-ky", status_code=status.HTTP_201_CREATED)
def dang_ky(data: DangKyRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?)",
            (data.ma_sv.strip(), data.ma_phien.strip())
        )
        conn.commit()
        return {"ok": True, "message": "Đăng ký thành công!"}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="DA_DANG_KY"
        )
    finally:
        conn.close()