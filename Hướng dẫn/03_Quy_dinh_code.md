# Quy định code Python và SQL

## 1. Mục tiêu

Đảm bảo code dễ bảo trì, dễ review và đồng nhất giữa các thành viên.

## 2. Quy ước chung

| Hạng mục | Quy định |
|---|---|
| Naming Python | snake_case cho biến/hàm, PascalCase cho class |
| Typing | Ưu tiên type hints cho hàm public |
| Docstring | Bắt buộc cho class/hàm chính |
| Import | Chia nhóm: chuẩn, thư viện ngoài, nội bộ |
| Độ dài hàm | Khuyến nghị <= 60 dòng (trừ trường hợp đặc biệt) |
| Side effects | Tách logic xử lý và I/O |

## 3. Quy định theo module

| Module | Trách nhiệm chính | Không nên làm |
|---|---|---|
| src/config.py | Đọc biến môi trường, cấu hình hệ thống | Chứa logic nghiệp vụ |
| src/data_generator.py | Sinh dữ liệu POS mẫu | Truy vấn DB trực tiếp |
| src/db_manager.py | Kết nối DB, insert/select dữ liệu | Chứa thuật toán khai phá |
| src/algorithm/* | Cài đặt StarNode/StarTree/StarCubing | Đọc trực tiếp file .env |
| main.py | Điều phối pipeline chạy tổng thể | Nhồi toàn bộ logic vào 1 file |

## 4. Chuẩn viết hàm khung

- Dùng docstring mô tả đầu vào, đầu ra, mục đích.
- Với chức năng chưa cài đặt, giữ `pass` kèm TODO rõ ràng.

Ví dụ:

```python
def generate_iceberg_cube(self):
    """Sinh các tổ hợp cube thỏa ngưỡng support tối thiểu."""
    # TODO: Duyệt Star-tree và kết xuất DataFrame kết quả.
    pass
```

## 5. Quy định SQL

| Hạng mục | Quy định |
|---|---|
| Tên bảng/cột | Dùng chữ cái, dấu gạch dưới, nhất quán tiếng Anh |
| Định dạng câu lệnh | Viết hoa từ khóa SQL (SELECT, FROM, WHERE...) |
| Script schema | Mỗi đối tượng có chú thích ngắn gọn |
| Truy vấn test | Lưu trong file riêng (02_queries.sql) |

## 6. Checklist code review

1. Có docstring cho các hàm/class chính.
2. Không hard-code thông tin nhạy cảm.
3. Có xử lý lỗi kết nối DB cơ bản.
4. Không vi phạm tách lớp trách nhiệm module.
5. Đảm bảo code chạy được ở mức scaffold (không vỡ import/cấu trúc).
