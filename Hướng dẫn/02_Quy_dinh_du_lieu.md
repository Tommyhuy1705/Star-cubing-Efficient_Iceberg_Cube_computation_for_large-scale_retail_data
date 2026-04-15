# Quy định dữ liệu

## 1. Mục tiêu quản trị dữ liệu

- Đảm bảo dữ liệu đầu vào nhất quán để thuật toán Star-cubing hoạt động ổn định.
- Giảm sai lệch kết quả cube do lỗi định dạng, giá trị thiếu hoặc ngoại lệ.

## 2. Quy định thư mục dữ liệu

| Thư mục | Mục đích | Quy định |
|---|---|---|
| data/raw | Dữ liệu gốc | Chỉ thêm mới, không chỉnh sửa trực tiếp file gốc |
| data/processed | Dữ liệu đã chuẩn hóa | Tạo bởi pipeline xử lý, có thể ghi đè theo phiên bản |

## 3. Chuẩn schema cho Fact_Retail_Sales

| Cột | Kiểu dữ liệu | Null | Quy định |
|---|---|---|---|
| transaction_id | VARCHAR(64) | Không | Duy nhất cho mỗi giao dịch |
| sale_timestamp | TIMESTAMP | Không | Theo múi giờ thống nhất |
| customer_id | VARCHAR(64) | Không | Định danh khách hàng |
| store_id | VARCHAR(64) | Không | Định danh cửa hàng |
| product_category | VARCHAR(100) | Không | Danh mục chuẩn hóa |
| product_name | VARCHAR(150) | Không | Tên sản phẩm |
| payment_method | VARCHAR(50) | Không | Ví dụ: Cash, Card, E-Wallet |
| region | VARCHAR(100) | Không | Khu vực bán |
| quantity | INTEGER | Không | > 0 |
| unit_price | DECIMAL(18,2) | Không | >= 0 |
| sales_amount | DECIMAL(18,2) | Không | quantity * unit_price |

## 4. Quy tắc chất lượng dữ liệu

| Nhóm kiểm tra | Điều kiện | Hành động khi vi phạm |
|---|---|---|
| Tính duy nhất | transaction_id không trùng | Loại bản ghi trùng hoặc gắn cờ |
| Giá trị thiếu | Không null ở cột bắt buộc | Loại bản ghi hoặc bổ sung theo rule |
| Miền giá trị | quantity > 0, unit_price >= 0 | Loại bản ghi sai |
| Logic nghiệp vụ | sales_amount = quantity * unit_price | Tính lại hoặc loại bỏ |
| Tính nhất quán danh mục | category/payment/region theo từ điển chuẩn | Chuẩn hóa giá trị |

## 5. Quy tắc đặt tên file dữ liệu

Mẫu khuyến nghị:

```text
retail_pos_YYYYMMDD_v{version}.csv
```

Ví dụ: `retail_pos_20260415_v1.csv`

## 6. Quy định bảo mật dữ liệu

1. Không lưu thông tin nhạy cảm thật (PII thật) vào kho mã nguồn.
2. Mọi thông tin định danh nhạy cảm phải ẩn danh hoặc sinh tổng hợp.
3. Không commit file dữ liệu lớn hoặc file chứa thông tin xác thực.

## 7. Checklist trước khi nạp dữ liệu vào DB

- Đã chạy kiểm tra null/trùng/outlier.
- Đã chuẩn hóa kiểu dữ liệu và timezone.
- Đã xác nhận số lượng bản ghi đầu vào/đầu ra sau tiền xử lý.
- Đã lưu log kiểm tra dữ liệu kèm timestamp.
