# Giới hạn chỗ mỗi phiên
Sức chứa: 30 sinh viên / phiên. Đếm riêng từng phiên.

| # | Đang có | Hành động | Kết quả |
|---|---|---|---|
| 1 | P01 trống | SV001 đăng ký P01 | 201 |
| 2 | P01 có 29 | SV mới đăng ký P01 | 201 |
| 3 | P01 có 30 | SV mới đăng ký P01 | 409 HET_CHO |
| 4 | P01 có 30, gồm SV000 | SV000 đăng ký lại P01 | 409 DA_DANG_KY |
| 5 | P01 có 30 | SV031 đăng ký P02 | 201 |
| 6 | P01 trống | 40 SV cùng lúc | 30x201, 10x409 |

Ngoài phạm vi: hủy đăng ký.
