# Quy trình thực thi Star-cubing

## 1. Mục tiêu quy trình

Mô tả luồng chuẩn từ dữ liệu giao dịch đến bảng Iceberg Cube để đảm bảo tái lập kết quả.

## 2. Luồng xử lý tổng quan

| Bước | Thành phần | Mô tả đầu ra |
|---|---|---|
| 1 | data_generator | Dữ liệu giao dịch bán lẻ dạng bảng |
| 2 | db_manager | Nạp vào Fact_Retail_Sales |
| 3 | star_tree | Cây sao từ các chiều dữ liệu |
| 4 | star_cubing | Tập tổ hợp thỏa ngưỡng MIN_SUP |
| 5 | db_manager | Ghi kết quả vào Iceberg_Sales_Cube |

## 3. Các bước chi tiết

1. Chuẩn bị dữ liệu đầu vào theo đúng quy định ở tài liệu dữ liệu.
2. Sắp xếp thứ tự chiều (dimension ordering) để tối ưu chèn Star-tree.
3. Chèn từng giao dịch vào Star-tree và cập nhật aggregate.
4. Áp dụng pruning theo ngưỡng support `MIN_SUP`.
5. Sinh các tổ hợp cube hợp lệ và tính tổng measure (ví dụ total_sales_amount).
6. Ghi kết quả vào bảng đích để phục vụ truy vấn OLAP/BI.

## 4. Tiêu chí đánh giá kết quả

| Chỉ số | Ý nghĩa | Mục tiêu |
|---|---|---|
| Support_count | Tần suất xuất hiện của tổ hợp chiều | >= MIN_SUP |
| Tổng doanh thu | Tổng sales_amount của tổ hợp | Chính xác theo fact |
| Thời gian chạy | Thời gian hoàn thành pipeline | Theo SLA nhóm đặt ra |
| Tính tái lập | Chạy lại cho cùng input cho kết quả giống nhau | Bắt buộc |

## 5. Mẫu log thí nghiệm

| Experiment_ID | Ngày chạy | Dữ liệu đầu vào | MIN_SUP | Số bản ghi fact | Số dòng cube | Thời gian chạy | Ghi chú |
|---|---|---|---:|---:|---:|---:|---|
| EXP001 | 2026-04-15 | retail_pos_20260415_v1.csv | 100 | 100000 | 8200 | 00:03:25 | Chạy baseline |

## 6. Rủi ro thường gặp

- Chọn thứ tự dimension chưa phù hợp làm cây quá rộng.
- Dữ liệu bẩn gây sai support hoặc sai aggregate.
- Thiếu kiểm soát transaction khi ghi DB dẫn đến dữ liệu không nhất quán.

## 7. Đề xuất mở rộng

1. Thêm benchmark so sánh giữa các mức `MIN_SUP`.
2. Thêm unit test cho từng bước chèn/prune/traverse cây.
3. Bổ sung truy vấn kiểm thử OLAP trong `sql/02_queries.sql`.
