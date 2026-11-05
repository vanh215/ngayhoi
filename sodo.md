# SƠ ĐỒ KIẾN TRÚC HỆ THỐNG CỔNG ĐĂNG KÝ NGÀY HỘI VIỆC LÀM (LAB 3)
**Sinh viên thực hiện:** Trịnh Việt Anh  
**Mã sinh viên:** 23110151  
**Môn học:** CSE3051 – Các công cụ AI  

---

## 1. Kiến trúc phân tầng và Ranh giới giao tiếp

[Trình duyệt Web - Frontend]
(Giao diện HTML/Tailwind/JS)
         │
         │  1. HTTP POST /api/dang-ky (Payload: ma_sv, ma_phien)
         │  (Preflight OPTIONS kiểm tra CORS)
         ▼
[Máy chủ FastAPI - Backend] (Cổng 8000)
         │
         │  2. Truy vấn INSERT INTO dang_ky
         ▼
[Cơ sở dữ liệu SQLite: ngayhoi.db]
(Ràng buộc toàn vẹn: UNIQUE(ma_sv, ma_phien))

---

## 2. Luồng xử lý dữ liệu và Xử lý ngoại lệ (Conflict Handling)

Yêu cầu gửi đến
      │
      ▼
Kiểm tra Pydantic Schema (ma_sv, ma_phien)
      │
      ├── (Sai kiểu/Thiếu trường) ──────► Trả về HTTP 422 Unprocessable Entity
      │
      ▼
Thực thi lệnh INSERT vào bảng `dang_ky`
      │
      ├── Thành công ──────────────────► Trả về HTTP 201 Created {"ok": true}
      │
      └── Vi phạm UNIQUE (Đăng ký lại) ─► Trả về HTTP 409 Conflict {"detail": "DA_DANG_KY"}

---

## 3. Cấu hình CORS & Minh chứng kết quả
* CORS Middleware: Cấu hình mở phương thức GET, POST, OPTIONS để hỗ trợ Preflight Request từ giao diện web cục bộ.
* Minh chứng Swagger UI (/docs): Đăng ký lần đầu trả mã 201, đăng ký trùng lần hai lập tức trả mã 409 (ghi nhận tại anh_docs_409.png).
* Minh chứng Frontend: Giao diện phản hồi trực quan theo 3 trạng thái: Đang xử lý, Thông báo xanh (201), và Thông báo đỏ chặn trùng (409) (ghi nhận tại anh_giaodien_3trangthai.png).
