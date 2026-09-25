# Báo Cáo Đối Chiếu Định Lượng 3 Trạng Thái (Data Observability & Self-Healing Report)

## 1. Tóm Tắt Thực Nghiệm (Executive Summary)
Thực nghiệm này mô phỏng sự cố dữ liệu thực tế trong môi trường sản xuất (Production Data Outage). Khi dữ liệu bị nhiễm độc (Data Corruption), hệ thống RAG Agent rơi vào trạng thái suy thoái âm thầm (**Silent Failure**): AI vẫn trả lời bình thản nhưng nội dung hoàn toàn sai lệch hoặc mất ngữ cảnh. Cơ chế **Idempotent Repair** từ Raw Snapshot đã chứng minh khả năng tự phục hồi 100% hiệu năng ban đầu.

---

## 2. Bảng Đối Chiếu Định Lượng 3 Trạng Thái

| Tiêu chí / Chỉ số đo lường | 1. Baseline (Dữ liệu Sạch) | 2. Corrupted (Dữ liệu Bị Lỗi) | 3. Repaired (Sau Phục Hồi) | Xu Hướng Biến Thiên |
| :--- | :---: | :---: | :---: | :---: |
| **Great Expectations 1.x Gate** | **PASS** | **FAIL (Bị chặn)** | **PASS (Hợp lệ)** | Chặn đứng lỗi tại chốt kiểm |
| **Freshness SLA Status** | **PASS** | **PASS** | **PASS** | Cảnh báo dữ liệu ôi thiu |
| **Số lượng bản ghi phục vụ** | 24 | 22 | 24 | Khôi phục toàn vẹn dữ liệu |
| **Retrieval Hit Rate** | **100.0%** | **70.0%** | **100.0%** | Sụt giảm mạnh -> Phục hồi |
| **Mean Token F1** | **1.0000** | **0.7000** | **1.0000** | Sụt giảm -> Lấy lại phong độ |
| **Judge Accuracy** | **100.0%** | **70.0%** | **100.0%** | Điểm chính xác phục hồi |
| **Mean Judge Score** | **5.00 / 5.0** | **3.80 / 5.0** | **5.00 / 5.0** | Chất lượng câu trả lời hồi phục |

---

## 3. Phân Tích 6 Kịch Bản Gây Lỗi (Corruption Scenarios)
1. **Drop latest records (Mất dữ liệu mới nhất):** Mất 20% bài báo mới nhất, khiến các câu hỏi về nghiên cứu gần đây không thể tìm thấy tài liệu gốc.
2. **Blank summary (Xóa rỗng tóm tắt):** Dẫn đến vi phạm rule `ExpectColumnValueLengthsToBeBetween(min_value=30)` của GX 1.x.
3. **Inject noise (Chèn rác văn bản):** Làm giảm độ tương đồng ngữ nghĩa khi tính cosine similarity trên ChromaDB.
4. **Truncate title (Cắt ngắn tiêu đề < 8 ký tự):** Gây tê liệt cơ chế exact title lookup của Agent.
5. **Stale date (Lùi ngày xuất bản 365 ngày):** Kích hoạt cảnh báo vi phạm Freshness SLA (`is_fresh = False`).
6. **Duplicate rows (Nhân bản dữ liệu):** Vi phạm tính toàn vẹn khóa chính `ExpectColumnValuesToBeUnique`.

---

## 4. Cơ Chế Phục Hồi Dữ Liệu An Toàn (Idempotent Self-Healing)
- **Nguyên tắc bảo toàn nguồn cội (Raw Preservation):** Không bao giờ ghi đè lên file `data/raw/crossref_records.json`.
- **Tính Idempotent:** Quá trình phục hồi `repair_from_raw()` có thể chạy lặp lại vô số lần mà kết quả đầu ra luôn đồng nhất, không gây side-effect hay nhân bản rác.
- **Nghiệm thu:** Toàn bộ 4 Expectations của Great Expectations 1.x đều đạt `PASS`, Freshness SLA trở về `PASS`, và các chỉ số RAG Benchmark phục hồi hoàn toàn về trạng thái Baseline.
