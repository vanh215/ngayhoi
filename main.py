import os
import sqlite3
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Cổng Đăng Ký Ngày Hội Việc Làm")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Kết nối CSDL dùng chung (hỗ trợ cả file thật ngayhoi.db lẫn :memory: khi test)
DB_PATH = os.getenv("DB_PATH", "ngayhoi.db")
db = sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dang_ky (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sv TEXT NOT NULL,
            ma_phien TEXT NOT NULL,
            UNIQUE(ma_sv, ma_phien)
        )
    """)
    db.commit()

init_db()

class DangKyRequest(BaseModel):
    ma_sv: str = Field(..., json_schema_extra={"example": "23110151"})
    ma_phien: str = Field(..., json_schema_extra={"example": "P01"})

@app.post("/api/dang-ky", status_code=status.HTTP_201_CREATED)
def dang_ky(data: DangKyRequest):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?)",
            (data.ma_sv.strip(), data.ma_phien.strip())
        )
        db.commit()
        return {"ok": True, "message": "Đăng ký thành công!"}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="DA_DANG_KY"
        )