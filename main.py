import os
import sqlite3
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv("DB_PATH", "ngayhoi.db")
db = None

def get_connection():
    global db
    if DB_PATH == ":memory:":
        if db is None:
            db = sqlite3.connect(":memory:", check_same_thread=False)
        return db
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn

def init_db():
    conn = get_connection()
    if DB_PATH != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
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
    if DB_PATH != ":memory:":
        conn.close()

init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Cổng Đăng Ký Ngày Hội Việc Làm", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class DangKyRequest(BaseModel):
    ma_sv: str = Field(..., json_schema_extra={"example": "23110151"})
    ma_phien: str = Field(..., json_schema_extra={"example": "P01"})

@app.post("/api/dang-ky", status_code=status.HTTP_201_CREATED)
def dang_ky(data: DangKyRequest):
    conn = get_connection()
    cursor = conn.cursor()
    ma_sv = data.ma_sv.strip()
    ma_phien = data.ma_phien.strip()

    try:
        # 1. Kiểm tra đăng ký trùng
        cursor.execute(
            "SELECT 1 FROM dang_ky WHERE ma_sv = ? AND ma_phien = ?",
            (ma_sv, ma_phien),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="DA_DANG_KY"
            )

        # Giải phóng khóa đọc trước khi sleep
        conn.commit()


        # 2. GỘP ĐẾM VÀ GHI TRONG 1 CÂU LỆNH SQL DUY NHẤT (Atomic Operation - Slide 27)
        cursor.execute(
            """
            INSERT INTO dang_ky (ma_sv, ma_phien)
            SELECT ?, ?
            WHERE (SELECT COUNT(*) FROM dang_ky WHERE ma_phien = ?) < 30
            """,
            (ma_sv, ma_phien, ma_phien),
        )
        conn.commit()

        # rowcount == 0 nghĩa là điều kiện COUNT < 30 không thỏa mãn -> hết chỗ
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="HET_CHO"
            )

        return {"ok": True, "message": "Đăng ký thành công!"}

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="DA_DANG_KY"
        )
    finally:
        if DB_PATH != ":memory:":
            conn.close()

@app.get("/api/con-cho")
def lay_so_cho_con_lai(ma_phien: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM dang_ky WHERE ma_phien = ?", 
        (ma_phien.strip(),)
    )
    da_dang_ky = cursor.fetchone()[0]
    if DB_PATH != ":memory:":
        conn.close()
    return {"con_cho": max(0, 30 - da_dang_ky)}