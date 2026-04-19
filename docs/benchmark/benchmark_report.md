# Benchmark Report - POS CSV

## 1. Mục tiêu

So sánh hiệu năng và không gian lưu trữ của 4 thuật toán trên dữ liệu bán lẻ:

- Star-cubing baseline (trước tăng cường)
- Star-cubing enhanced (sau tăng cường)
- BUC
- Bottom-up

## 2. Cấu hình benchmark

- Input: `data/pos_data.csv`
- Algorithm set: `full`
- Raw limit: `5000000` dòng CSV thô
- Cleaned rows sau ETL: `4962783`
- Dataset sizes benchmark: `full` (`4962783` rows)
- Repeat: `1`
- Iceberg threshold: `min_sup = 18000000`
- Shuffle seed: `20260418`
- Metrics: runtime, CPU time, peak tracemalloc, cube rows, output storage

## 3. Kết quả tổng hợp

Nguồn: `docs/benchmark/logs/summary_by_algorithm.csv`

| Algorithm | Mean Runtime (s) | Mean CPU (s) | Mean Peak RAM (MB) | Mean Output (KB) | Mean Cube Rows |
| :-- | --: | --: | --: | --: | --: |
| Star-cubing enhanced | 221.4151 | 209.1719 | 46.6270 | 1912.9900 | 57252.00 |
| BUC | 980.5245 | 964.8750 | 100.3440 | 1925.4870 | 57637.00 |
| Bottom-up | 3540.8799 | 3475.4844 | 87.7170 | 1925.4870 | 57637.00 |
| Star-cubing baseline | 7353.2844 | 6812.8750 | 85.2870 | 1925.4870 | 57637.00 |

### Nhận xét chính

- Star-cubing enhanced có runtime trung bình thấp nhất trong 4 thuật toán.
- BUC có peak tracemalloc cao nhất trong profile full-size này.
- Star-cubing baseline có runtime cao nhất ở stress profile.
- Star-cubing enhanced tạo output nhỏ hơn nhóm còn lại (1912.990 KB vs 1925.487 KB).

## 4. Biểu đồ bằng chứng

Các file được sinh tại:

- `docs/benchmark/charts/runtime_line.png`
- `docs/benchmark/charts/memory_bar.png`
- `docs/benchmark/charts/storage_line.png`

Diễn giải nhanh:

- `runtime_line.png`: do profile `sizes=full` chỉ có 1 mốc dữ liệu nên hiển thị theo dạng điểm cho mỗi thuật toán.
- `memory_bar.png`: thể hiện peak memory trung bình theo thuật toán trên full-size.
- `storage_line.png`: cũng là dạng điểm vì chỉ có 1 mốc `dataset_rows`.

## 5. Artifact phục vụ báo cáo

- Log chi tiết: `docs/benchmark/logs/performance_log.csv`
- Log JSON: `docs/benchmark/logs/performance_log.json`
- Bảng tổng hợp: `docs/benchmark/logs/summary_by_algorithm.csv`
- Tài liệu kỹ thuật: `docs/benchmark/benchmark_algorithm_spec.md`

## 6. Kết luận

Benchmark mode `full` đã hoàn tất trên dữ liệu lớn và sinh đủ log/charts cho 4 thuật toán. Ở stress profile này, Star-cubing enhanced có thời gian chạy thấp nhất và output nhỏ nhất, trong khi baseline là phương án chậm nhất.
