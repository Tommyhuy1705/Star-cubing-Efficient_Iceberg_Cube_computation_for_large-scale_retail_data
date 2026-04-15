# Hướng dẫn thiết lập và chạy dự án

## 1. Mục tiêu

Thiết lập nhanh môi trường phát triển cho dự án tính Iceberg Cube bằng Star-cubing, đảm bảo chạy được pipeline cơ bản.

## 2. Yêu cầu hệ thống

| Thành phần | Phiên bản khuyến nghị | Ghi chú |
|---|---|---|
| Python | 3.10+ | Khuyến nghị 3.11 |
| pip | Mới nhất | Dùng để cài dependency |
| PostgreSQL hoặc SQL Server | Bất kỳ bản ổn định | Dùng lưu Fact và Cube |
| OS | Windows/Linux/macOS | Dự án độc lập nền tảng |

## 3. Cài đặt môi trường

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Cấu hình biến môi trường

Sửa file `.env` tại thư mục gốc dự án:

| Biến | Bắt buộc | Ví dụ | Ý nghĩa |
|---|---|---|---|
| DB_PROVIDER | Có | postgresql | Loại CSDL: postgresql hoặc sqlserver |
| DB_HOST | Có | localhost | Địa chỉ máy chủ DB |
| DB_PORT | Có | 5432 | Cổng kết nối DB |
| DB_NAME | Có | starcubing | Tên cơ sở dữ liệu |
| DB_USER | Có | postgres | Tài khoản DB |
| DB_PASSWORD | Có | 123456 | Mật khẩu DB |
| DB_DRIVER | Với SQL Server | ODBC Driver 17 for SQL Server | Driver pyodbc |
| MIN_SUP | Có | 100 | Ngưỡng support tối thiểu |

## 5. Khởi tạo schema CSDL

- Chạy script tạo bảng trong thư mục `sql/01_schema.sql`.
- Có thể chạy thủ công bằng công cụ DB (DBeaver/SSMS/psql) hoặc CLI tùy hệ quản trị.

## 6. Chạy ứng dụng

```bash
python main.py
```

## 7. Kiểm tra nhanh sau khi chạy

1. Không có lỗi import dependency.
2. Kết nối DB thành công.
3. Đọc đúng biến `MIN_SUP` từ môi trường.
4. Cấu trúc thư mục `data/raw` và `data/processed` vẫn được giữ nguyên.

## 8. Lỗi thường gặp

| Lỗi | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| ModuleNotFoundError | Chưa cài requirements | Chạy lại `pip install -r requirements.txt` |
| Không kết nối DB | Sai host/user/password | Kiểm tra file `.env` |
| Lỗi driver SQL Server | Thiếu ODBC driver | Cài đúng bản ODBC phù hợp |
