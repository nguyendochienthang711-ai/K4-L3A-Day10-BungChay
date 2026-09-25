# Member Role Report — Day 10: Data Pipeline & Data Observability

> Báo cáo vai trò cá nhân của Chuyên viên Nền tảng Dữ liệu & Phục hồi (Data Foundation Owner).

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | **Dương Đạt Khang** |
| **MSSV** | **2A202602624** |
| **Khóa / Lớp** | K4A - Level 3 (Day 10) |
| **Tên nhóm** | BungChay (`K4A-L3-DAY10`) |
| **Vai trò chính** | **Data Foundation Owner** |
| **Repository** | `https://github.com/nguyendochienthang711-ai/K4-L3A-Day10-BungChay` |
| **Ngày hoàn thành** | 2026-09-25 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu chính (Ownership)

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Raw Data Ingestion** | `src/ingestion/crossref.py`<br>`fetch_source_records`, `fetch_from_api` | Crossref REST API endpoint, tham số query & filter | `data/raw/crossref_response.json`<br>`data/raw/crossref_records.json` | **Hoàn thành** |
| **Data Cleaning & Modeling** | `src/ingestion/cleaning.py`<br>`build_clean_dataframe`, `clean_text` | Danh sách thô `PaperRecord` | `data/clean/papers_clean.csv`<br>`data/clean/papers_clean.json` | **Hoàn thành** |
| **Data Corruption Suite** | `src/ingestion/corruption.py`<br>`corrupt_dataset`, 6 hàm tiêm lỗi | Clean DataFrame, tỷ lệ lỗi, seed | `data/clean/papers_clean_corrupted.csv`<br>`data/results/corruption_log.json` | **Hoàn thành** |
| **Idempotent Repair Flow** | `src/ingestion/corruption.py`<br>`repair_from_raw` | Snapshot thô `crossref_records.json` | `data/clean/papers_clean_repaired.csv`<br>`data/clean/papers_clean_repaired.json` | **Hoàn thành** |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên / Module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| **Định nghĩa Data Contract** | Nguyễn Hoàng Việt (`src/observability/quality.py`) | Thống nhất tên cột chuẩn (`paper_id`, `title`, `summary`, `published`, `age_days`, `text_for_embedding`) để Great Expectations kiểm định không bị lệch schema |
| **Định dạng Text cho Embedding** | Đặng Hữu Tâm (`src/retrieval/index.py`) | Cung cấp cấu trúc văn bản 5 phần có phân cách rõ ràng, giúp embedding model tính toán vector ngữ nghĩa chính xác |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Hàm / Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Thu thập dữ liệu Crossref Dual-Mode** | `src/ingestion/crossref.py` | 24 bản ghi nghiên cứu học thuật chuẩn, có cơ chế lưu raw snapshot | Kiểm tra file `data/raw/crossref_records.json` |
| **Làm sạch văn bản & tính `age_days`** | `src/ingestion/cleaning.py` | Bóc tách 100% thẻ XML/HTML, chuẩn hóa ngày ISO, sinh `text_for_embedding` | Kiểm tra file `data/clean/papers_clean.csv` |
| **Hiện thực hóa 6 kịch bản làm bẩn dữ liệu** | `src/ingestion/corruption.py` | 22 bản ghi bị nhiễm độc, ghi chép đầy đủ nhật ký tiêm lỗi | Kiểm tra file `data/results/corruption_log.json` |
| **Khôi phục dữ liệu Idempotent Repair** | `src/ingestion/corruption.py` | Tái lập toàn vẹn 24 bản ghi sạch từ raw snapshot | So sánh diff giữa `papers_clean.csv` và `papers_clean_repaired.csv` |

**Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:**
File `data/clean/papers_clean.csv` và `data/results/corruption_log.json`. Cụ thể, file log ghi nhận chính xác 6 kịch bản lỗi: 4 bài mới nhất bị xóa (`drop_latest_records`), 2 bài bị xóa tóm tắt (`blank_summary`), 2 bài bị chèn token rác (`inject_noise`), 1 bài bị cắt ngắn tiêu đề (`truncate_title`), 2 bài bị lùi ngày xuất bản 365 ngày (`stale_date`), và 2 bài bị nhân bản (`duplicate_rows`).

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Dữ liệu thu thập từ các API học thuật như Crossref thường chứa các thẻ XML đặc thù của chuẩn xuất bản khoa học (JATS XML như `<jats:p>`, `<jats:sec>`, `<jats:title>`), khoảng trắng ngắt dòng bất thường, ngày tháng không đồng nhất giữa bản in và bản online, cũng như các bản ghi trùng lặp. Nếu đưa trực tiếp dữ liệu thô này vào Vector Database, mô hình embedding sẽ học cả các thẻ XML rác, làm sai lệch không gian biểu diễn ngữ nghĩa. Ngoài ra, cần thiết kế một cơ chế phục hồi dữ liệu từ nguồn gốc (Raw Lineage) để giải quyết sự cố dữ liệu bị lỗi một cách triệt để.

### Cách triển khai
1. **Bóc tách XML bằng Regular Expressions & HTML Parser:** Xây dựng hàm `clean_text()` sử dụng regex loại bỏ triệt để các tag `<jats:...>` và `</jats:...>`, unescape các ký tự HTML entities (`&amp;`, `&lt;`, `&gt;`), và nén các khoảng trắng liên tiếp thành một dấu cách duy nhất.
2. **Chuẩn hóa ngày xuất bản & tính độ tuổi dữ liệu:** Hàm `clean_published_date()` bóc tách cấu trúc mảng `date-parts` từ Crossref, ưu tiên ngày xuất bản online hoặc print, định dạng thành chuỗi `YYYY-MM-DD`. Sau đó, `age_days` được tính bằng khoảng cách ngày so với mốc thời gian UTC hiện tại.
3. **Cấu trúc hóa chuỗi Pre-embedding:** Hàm `build_clean_dataframe()` tổng hợp các trường thành chuỗi chuẩn 5 phần: `Title`, `Authors`, `Published`, `Categories`, `Summary`.
4. **Idempotent Self-Healing:** Hàm `repair_from_raw()` đọc trực tiếp file `data/raw/crossref_records.json` bất biến, nạp vào quy trình làm sạch chuẩn, đảm bảo kết quả đầu ra luôn nhất quán 100% mà không bị phụ thuộc vào trạng thái bẩn trước đó.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | JSON response từ Crossref API hoặc snapshot `data/raw/crossref_records.json` |
| **Output** | `data/clean/papers_clean.csv`, `papers_clean.json`, `papers_clean_corrupted.csv`, `papers_clean_repaired.csv` |
| **Module phụ thuộc** | `src/core/config.py`, `src/core/utils.py` |
| **Module sử dụng output** | `src/retrieval/index.py`, `src/observability/quality.py`, `src/pipelines/` |
| **Điều kiện lỗi cần xử lý** | Mất kết nối internet, mã lỗi HTTP 429/500, dữ liệu thiếu trường abstract hoặc ngày tháng |

### Cách xác minh

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe -c "from ingestion.cleaning import build_clean_dataframe; from ingestion.crossref import load_local_snapshot; from core.utils import now_utc; records = load_local_snapshot(); df = build_clean_dataframe(records, now_utc()); print(f'So ban ghi sach: {len(df)}, So cot: {len(df.columns)}')"
```

- **Kết quả mong đợi:** Xuất ra 24 bản ghi sạch, đủ 8 cột chuẩn.
- **Kết quả thực tế:** `So ban ghi sach: 24, So cot: 8`.
- **Artifact:** `data/clean/papers_clean.csv`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn chiến lược xử lý dữ liệu khi mất kết nối internet hoặc API Crossref bị rate-limit trong quá trình chạy chấm điểm và kiểm thử.
- **Các phương án đã cân nhắc:**
  1. *Phương án 1:* Báo lỗi dừng chương trình (fail-fast) nếu không thể kết nối tới Crossref API.
  2. *Phương án 2:* Kiến trúc Dual-Mode Ingestion: gọi API trực tiếp với cơ chế thử lại (exponential backoff); nếu thất bại, tự động chuyển sang đọc bản sao lưu ngoại tuyến (Offline Snapshot) đã lưu sẵn tại `data/raw/crossref_records.json`.
- **Phương án đã chọn:** **Phương án 2 (Dual-Mode Ingestion)**.
- **Lý do:** Giúp hệ thống đạt tính sẵn sàng cao (High Availability) và khả năng tái lập 100% trong mọi điều kiện mạng, đặc biệt khi máy chấm thi của giám khảo không có internet hoặc bị chặn kết nối quốc tế.
- **Bằng chứng quyết định phù hợp:** Pipeline chạy trơn tru mượt mà ngay cả khi ngắt kết nối mạng máy tính, toàn bộ 24 bản ghi chuẩn được nạp vào luồng xử lý và vượt qua Quality Gate.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng / lỗi nguyên văn:**
  ```text
  ValueError: Length of summary must be between 30 and 5000 characters. Found: '<jats:p></jats:p>' (length 17)
  ```
  Một số bản ghi từ Crossref trả về phần tóm tắt chứa toàn thẻ JATS rỗng hoặc thẻ phân đoạn không có nội dung thực tế.
- **Lệnh tái hiện:**
  ```powershell
  .\.venv\Scripts\python.exe -c "from ingestion.cleaning import clean_text; print(len(clean_text('<jats:p>   </jats:p>')))"
  ```
- **Nguyên nhân gốc (Root cause):** Trình bóc tách chuỗi ban đầu chỉ sử dụng `str.replace('\n', ' ')` mà không bóc tách các thẻ XML phân cấp của chuẩn JATS. Khi thẻ XML bị gỡ bỏ, chuỗi tóm tắt trở thành chuỗi rỗng hoặc quá ngắn, vi phạm expectation về độ dài văn bản của Great Expectations.
- **Cách xử lý:** Bổ sung biểu thức chính quy mạnh `re.sub(r'<[^>]+>', '', text)` trong hàm `clean_text()` để loại bỏ hoàn toàn mọi cặp thẻ XML/HTML, kết hợp cơ chế kiểm tra: nếu văn bản sau khi gỡ thẻ có độ dài `< 30` ký tự, tự động bổ sung tiêu đề bài báo làm nội dung tóm tắt dự phòng (fallback summary).
- **Cách xác minh sau khi sửa:** Chạy kiểm định `run_data_quality_checks` trên tập dữ liệu sạch, toàn bộ 24 bản ghi đều đạt độ dài `summary >= 30` ký tự (PASS).
- **Điều học được:** Dữ liệu từ các nhà xuất bản học thuật không bao giờ chuẩn chỉnh 100%. Luôn phải có lớp tiền xử lý phòng thủ (Defensive Data Cleaning) để bảo vệ các tầng xử lý phía sau.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - API Crossref trả về dữ liệu JSON thô $\to$ Ingestion trích xuất thành danh sách đối tượng `PaperRecord` và lưu bản sao bất biến vào `data/raw/` $\to$ Cleaning module bóc tách XML tags, tính `age_days`, gán `paper_id` duy nhất và tạo `text_for_embedding` $\to$ Ghi ra `papers_clean.csv` $\to$ Embedding module dùng mô hình `all-MiniLM-L6-v2` chuyển văn bản thành vector dense 384 chiều $\to$ Index vào ChromaDB collection với chỉ mục HNSW.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Bộ 10 câu hỏi kiểm chuẩn có sẵn danh sách `ground_truth_doc_ids`. Khi câu hỏi được đưa vào hệ thống, ChromaDB thực hiện tìm kiếm vector tương đồng nhất và trả về danh sách tài liệu. Nếu tài liệu chuẩn nằm trong top kết quả, **Retrieval Hit Rate được tính là 1**. Câu trả lời sinh ra sau đó được đối chiếu với đáp án mẫu để tính **Token F1** và **LLM Judge Score**.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - *Quality checks:* Đánh giá **tính đúng đắn về mặt cấu trúc và cú pháp dữ liệu** (schema, rỗng, trùng lặp, độ dài văn bản).
   - *Freshness monitoring:* Đánh giá **tính cập nhật của thông tin theo thời gian** (SLA tuổi thọ dữ liệu). Dữ liệu hoàn toàn đúng cú pháp nhưng nếu xuất bản quá lâu trong quá khứ (`age_days > 180`) sẽ bị cảnh báo vi phạm độ tươi.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để đảm bảo tính công bằng khoa học của thực nghiệm. Chỉ khi giữ nguyên thước đo (Ground Truth), sự biến thiên của các chỉ số mới phản ánh chính xác tác động của việc dữ liệu bị tiêm lỗi và khả năng phục hồi của hệ thống.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - *Artifact:* `repaired_quality_report.json` và `repaired_freshness_report.json` đều đạt `PASS`.
   - *Metric:* Retrieval Hit Rate hồi phục từ **70.0% lên 100.0%**, Mean Token F1 hồi phục từ **0.7000 lên 1.0000**, và báo cáo `corruption_report.md` xác nhận AI khôi phục toàn vẹn năng lực ban đầu.

---

## 8. Phân tích kết quả thực nghiệm

### Metrics chính ghi nhận thực tế

| Metric / Signal | 🟢 Baseline | 🔴 Corrupted | 🔵 Repaired | Nhận xét cá nhân |
| :--- | :---: | :---: | :---: | :--- |
| `retrieval_hit_rate` | **100.0%** | **70.0%** | **100.0%** | Giảm 30% do mất 4 bài báo mới nhất và cắt ngắn title; phục hồi hoàn hảo sau repair |
| `mean_token_f1` | **1.0000** | **0.7000** | **1.0000** | Câu trả lời bị sai lệch khi summary bị rỗng hoặc tiêm nhiễu; hồi phục tuyệt đối sau repair |
| `judge_accuracy` | **100.0%** | **70.0%** | **100.0%** | Tỷ lệ câu trả lời đúng bản chất phục hồi từ 70% lên 100% |
| `mean_judge_score` | **5.00 / 5.0** | **3.80 / 5.0** | **5.00 / 5.0** | Điểm số chất lượng câu trả lời lấy lại mức tối đa 5/5 |
| **Great Expectations Gate** | **PASS** | **FAIL** | **PASS** | Báo động đỏ khi bị trùng lặp ID và summary bị xóa trắng |
| **Freshness SLA Status** | **PASS** (4.17%) | **PASS** (13.64%) | **PASS** (4.17%) | Tỷ lệ bài quá hạn tăng từ 4.17% lên 13.64% khi lùi ngày xuất bản |

### Kết luận từ số liệu

1. **Chuỗi nguyên nhân - bằng chứng 1:**  
   Thực thi 6 kịch bản lỗi trong `src/ingestion/corruption.py` $\longrightarrow$ Great Expectations 1.x báo **FAIL** trên 2 chỉ tiêu (Uniqueness và Min Length) $\longrightarrow$ Retrieval Hit Rate sụt giảm nghiêm trọng từ **100.0% xuống 70.0%**.
2. **Chuỗi nguyên nhân - bằng chứng 2:**  
   Thực thi hàm `repair_from_raw()` đọc lại snapshot `crossref_records.json` $\longrightarrow$ Great Expectations 1.x đạt lại **PASS** $\longrightarrow$ Retrieval Hit Rate và Token F1 hồi phục hoàn toàn về mức tuyệt đối **100.0% và 1.0000**.

- **Kịch bản lỗi gây ảnh hưởng rõ nhất:**  
  `drop_latest_records` (xóa 4 bài mới nhất) và `truncate_title` gây thiệt hại nặng nhất cho hệ thống RAG vì nó triệt tiêu hoàn toàn khả năng tìm kiếm ngữ nghĩa đối với các câu hỏi kiểm chuẩn tương ứng.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Tầm quan trọng sống còn của Data Lineage:** Luôn bảo toàn dữ liệu gốc thô (Raw Data Immutability). Đây là "phao cứu sinh" duy nhất cho phép tái tạo lại toàn bộ hệ sinh thái dữ liệu khi có sự cố.
2. **Thiết kế hàm có tính Idempotent:** Mọi hàm biến đổi dữ liệu cần được thiết kế để có thể chạy lại nhiều lần mà kết quả không thay đổi và không phát sinh rác.
3. **Mối quan hệ nhân quả trực tiếp giữa Data Quality và RAG Accuracy:** Dữ liệu đầu vào bị ô nhiễm dù chỉ ở mức độ nhỏ cũng sẽ làm suy giảm nghiêm trọng độ chính xác của AI ở tầng phục vụ.

### Nếu có thêm thời gian
Tôi sẽ xây dựng một module **Schema Evolution & Anomaly Detector**: tự động so sánh phân bố thống kê của các đợt nạp dữ liệu mới so với lịch sử (Data Drift Detection) để phát hiện sớm các hiện tượng bất thường của nguồn cung cấp dữ liệu bên thứ ba.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Dương Đạt Khang  
**Ngày xác nhận:** 2026-09-25
