# Báo Cáo Pha 1: Baseline Data Pipeline & Observability

## 1. Tổng Quan Hệ Thống (Executive Summary)
- **Nguồn dữ liệu:** Crossref REST API
- **Chủ đề tìm kiếm:** `agentic retrieval augmented generation large language model`
- **Số bản ghi thô (Raw Records):** 24
- **Số bản ghi sạch (Cleaned Records):** 24
- **Trạng thái Data Quality Gate (GX 1.x):** **PASS**
- **Trạng thái Freshness SLA:** **PASS** (Stale ratio: 4.2%)

---

## 2. Kiểm Soát Chất Lượng Dữ Liệu (Data Observability)

### 2.1. Great Expectations 1.x Quality Gate
- **Chế độ thực thi:** Ephemeral Context (in-memory)
- **Kết quả nghiệm thu:** `success = True`
- **Bộ Expectations:**
  1. `ExpectTableRowCountToBeBetween`: Số dòng từ 5 đến 5000 (Thực tế: 24).
  2. `ExpectColumnValuesToNotBeNull`: `paper_id`, `title`, `text_for_embedding` không bị rỗng.
  3. `ExpectColumnValuesToBeUnique`: `paper_id` là duy nhất, không trùng lặp.
  4. `ExpectColumnValueLengthsToBeBetween`: `summary` có độ dài tối thiểu >= 30 ký tự.

### 2.2. Freshness SLA Monitoring
- **Ngưỡng quy định:** 180 ngày (6 tháng).
- **Tỉ lệ bản ghi quá hạn cho phép:** <= 25.0%.
- **Bản ghi quá hạn thực tế:** 1 / 24 (4.17%).
- **Kết luận:** `PASS`.

---

## 3. Đánh Giá Hiệu Năng RAG Agent (Baseline Benchmarks)

Đánh giá được thực hiện trên bộ benchmark chuẩn 10 câu hỏi qua 4 nhóm: `summary`, `authors`, `date`, `categories`.

| Chỉ Số (Metric) | Kết Quả Đạt Được | Ý Nghĩa Kỹ Thuật |
| :--- | :---: | :--- |
| **Số câu hỏi benchmark** | `10` | Phủ đều 4 tác vụ thông tin chính |
| **Retrieval Hit Rate** | **100.0%** | Tỉ lệ bài báo đúng được tìm thấy trong Top-K |
| **Mean Token F1** | **1.0000** | Độ trùng khớp từ vựng giữa câu trả lời và Ground Truth |
| **Judge Accuracy** | **100.0%** | Tỉ lệ câu trả lời được LLM Judge chấm đúng bản chất |
| **Mean Judge Score** | **5.00 / 5.0** | Điểm trung bình chất lượng câu trả lời |

---

## 4. Kết Luận Pha 1
Dữ liệu sạch đã vượt qua Data Quality Gate và Freshness SLA, vector embeddings được khởi tạo chính xác trên ChromaDB (`papers-baseline`). RAG Agent hoạt động ổn định và đạt kết quả kiểm chuẩn nền tảng (Baseline) tin cậy.
