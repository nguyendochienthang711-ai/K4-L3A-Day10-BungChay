# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                                        |
| ------------------ | -------------------------------------------------------------------------------- |
| Họ và tên       | Dương Quang Khang                                                              |
| MSSV               | 2A202602624                                                                      |
| Khóa/Lớp         | Khóa 4 - L3A - Day 10                                                           |
| Tên nhóm         | Group 19 - Bùng Cháy                                                           |
| Vai trò chính    | **Data Foundation Owner** (Data Ingestion, Cleaning & Idempotent Recovery) |
| Repository         | https://github.com/nguyendochienthang711-ai/K4-L3A-Day10-Group19-BungChay        |
| Ngày hoàn thành | 2026-09-25                                                                       |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable                      | File/hàm phụ trách                                                                                           | Input nhận vào                                                | Output bàn giao                                                                                              | Trạng thái           |
| :-------------------------------------- | :-------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------ | :--------------------- |
| **Raw Data Ingestion & Lineage**  | `src/ingestion/crossref.py`- `parse_crossref_payload()`- `fetch_source_records()`- `load_raw_records()` | Crossref REST API hoặc snapshot thô`crossref_response.json` | -`data/raw/crossref_response.json`- `data/raw/crossref_records.json`- `list[PaperRecord]` (24 bản ghi) | **Hoàn thành** |
| **Data Cleaning & Text Modeling** | `src/ingestion/cleaning.py`- `build_clean_dataframe()`- `save_clean_dataframe()`                          | Danh sách`PaperRecord`, tham số `run_date`                | -`data/clean/papers_clean.csv`- `data/clean/papers_clean.json`- Clean DataFrame (24 dòng sạch)          | **Hoàn thành** |
| **Idempotent Repair / Recovery**  | `src/ingestion/cleaning.py`- `repair_from_raw()`                                                            | `data/raw/crossref_records.json`                              | -`data/clean/papers_clean_repaired.csv`- `data/clean/papers_clean_repaired.json`                          | **Hoàn thành** |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                                                    | Thành viên/module được hỗ trợ                   | Kết quả                                                                                                                                                                                                  |
| :-------------------------------------------------------------- | :----------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Xây dựng Script Tự Nghiệm Thu (Self-Verification)** | Toàn bộ nhóm                                        | Viết kịch bản`verify_cp1.py` giúp kiểm tra tự động và đồng bộ cả 4 chỉ số CP0 & CP1 (Ingestion, Cleaning, Quality Gate, Freshness) không bị lỗi escape quote trên Windows PowerShell. |
| **Hỗ trợ Data Observability**                           | Observability Owner (`src/observability/quality.py`) | Thống nhất cấu trúc DataFrame sạch để tích hợp vào Ephemeral Batch Definition của Great Expectations 1.x.                                                                                       |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện                                 | File/hàm/artifact liên quan | Kết quả bàn giao                                                                                                                                                   | Cách xác minh                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| :---------------------------------------------------------- | :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Thu thập metadata và bảo tồn Lineage gốc               | `src/ingestion/crossref.py` | Tải và trích xuất thành công 24 bài báo học thuật chuẩn từ Crossref. Cơ chế Cứu hộ Offline (Dual-Mode) tự động kích hoạt khi có lỗi mạng/429. | `python -c "from core.config import load_settings; from ingestion.crossref import fetch_source_records; s=load_settings(); r=fetch_source_records(s); print(f'Tín hiệu hoàn thành: Đã nạp {len(r)} bài báo')"` $\rightarrow$ **Đã nạp 24 bài báo**                                                                                                                                                                              |
| Làm sạch, khử trùng lặp và tính độ tuổi dữ liệu | `src/ingestion/cleaning.py` | Khử trùng lặp theo`paper_id`, làm sạch thẻ XML rác, tính `age_days`, tạo trường nhúng `text_for_embedding` 5 phần hoàn chỉnh.                    | `python -c "from datetime import datetime, timezone; from core.config import load_settings; from ingestion.crossref import load_raw_records; from ingestion.cleaning import build_clean_dataframe; s=load_settings(); df=build_clean_dataframe(load_raw_records(s.paths.raw_records_json), datetime.now(timezone.utc)); print(f'Tín hiệu hoàn thành: Clean thành công {len(df)} dòng')"` $\rightarrow$ **Clean thành công 24 dòng** |
| Cơ chế Tự phục hồi an toàn (Idempotent Repair)        | `src/ingestion/cleaning.py` | Hàm`repair_from_raw()` tự động tái tạo dữ liệu sạch trực tiếp từ bản lưu thô nguyên bản, đảm bảo tính bất biến khi chạy lại nhiều lần.   | Chạy qua`verify_cp1.py` và kiểm tra file `data/clean/papers_clean_repaired.csv` (24 dòng sạch).                                                                                                                                                                                                                                                                                                                                                |

### Output cụ thể mà phần việc tạo ra:

* Tệp dữ liệu sạch chuẩn: `data/clean/papers_clean.csv` và `data/clean/papers_clean.json` chứa 24 bản ghi với đầy đủ các trường: `paper_id`, `title`, `summary`, `authors`, `categories`, `published`, `age_days`, `authors_joined`, `categories_joined`, `summary_chars`, `text_for_embedding`.
* Đảm bảo 100% không có giá trị null ở các trường quan trọng, không có dòng trùng lặp, sẵn sàng nạp thẳng vào ChromaDB Vector Store.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Dữ liệu học thuật cào từ Crossref API thường chứa các thẻ XML/JATS rác (như `<jats:p>`, `</jats:p>`, `<jats:title>`), khoảng trắng dư thừa, định dạng ngày tháng không nhất quán, và có nguy cơ bị trùng lặp mã DOI (`paper_id`). Nếu đưa trực tiếp dữ liệu thô này vào Vector Database:

1. Các thẻ XML và ký tự rác làm sai lệch vector embedding, kéo tụt độ tương đồng cosine khi tìm kiếm.
2. Trùng lặp tài liệu làm loãng Top-k Context, khiến Agent trích xuất câu trả lời sai lệch (hiện tượng **Silent Failure**).
3. API Crossref công khai rất dễ dính lỗi rate-limit `429 Too Many Requests` khiến pipeline bị sập giữa chừng.

### Cách triển khai

1. **Bảo tồn Lineage & Cứu hộ Offline (Dual-Mode):**
   * Nếu bật `REFRESH_SOURCE=true`, hệ thống gọi HTTP GET đến `https://api.crossref.org/works` với timeout 15s. Nếu API trả về mã lỗi `429` hoặc mất kết nối, hệ thống tự động bắt ngoại lệ và kích hoạt chế độ **Offline Rescue Snapshot** từ `data/raw/crossref_records.json` / `crossref_response.json`.
2. **Làm sạch văn bản bằng Regular Expression:**
   * Sử dụng `re.sub(r"<[^>]+>", " ", text)` để xóa toàn bộ các thẻ HTML/JATS XML.
   * Dùng `re.sub(r"\s+", " ", text).strip()` để chuẩn hóa các khoảng trắng thừa.
3. **Tính toán độ tuổi dữ liệu (`age_days`):**
   * Parse ngày `published` thành chuỗi ISO 8601 `YYYY-MM-DD`. Chuyển đổi ngày về múi giờ chuẩn UTC và tính toán:
     $$
     \text{age\_days} = (\text{run\_date} - \text{published\_date}).\text{days}
     $$
4. **Cấu trúc trường nhúng ngữ cảnh `text_for_embedding`:**
   * Ghép nối 5 trường thông tin thành một block văn bản chuẩn hóa để phục vụ Embedding model (`all-MiniLM-L6-v2`):
     ```text
     Title: <Tiêu đề bài báo>
     Authors: <authors_joined>
     Published: <published>
     Categories: <categories_joined>
     Summary: <summary>
     ```
5. **Cơ chế Idempotent Repair:**
   * Tách biệt hoàn toàn tầng dữ liệu thô (`data/raw/`) và tầng dữ liệu xử lý (`data/clean/`). Khi phát hiện dữ liệu bị ô nhiễm do kịch bản Corruption, hàm `repair_from_raw()` đọc lại nguồn thô nguyên bản và tái sinh tập dữ liệu sạch, đảm bảo chạy đi chạy lại nhiều lần kết quả vẫn giữ nguyên trạng thái đúng đắn ban đầu.

### Input, output và contract

| Thành phần                             | Mô tả                                                                                                                                   |
| :--------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| **Input**                          | Dữ liệu JSON từ Crossref API hoặc snapshot thô tại`data/raw/crossref_records.json`.                                               |
| **Output**                         | Danh sách`PaperRecord` và pandas DataFrame sạch 24 dòng, được lưu tại `data/clean/papers_clean.csv` / `papers_clean.json`. |
| **Module phụ thuộc**             | `core.config.Settings` (đường dẫn paths, cấu hình query và freshness threshold).                                                 |
| **Module sử dụng output**        | `src/retrieval/index.py` (ChromaDB Vector Store) và `src/observability/quality.py` (Great Expectations 1.x).                         |
| **Điều kiện lỗi cần xử lý** | API trả về mã`429 Too Many Requests`, rớt mạng, bản ghi thiếu trường `abstract` hoặc `published`, mã DOI trùng lặp.    |

### Cách xác minh

```powershell
# Chạy script xác minh tổng hợp:
python verify_cp1.py
```

* **Kết quả mong đợi:** In ra 4 dòng pass: Đã nạp 24 bài báo, Clean thành công 24 dòng, Quality check status = True, Is Fresh = True.
* **Kết quả thực tế:** Console in ra chính xác 100% kết quả mong đợi.
* **Artifact sinh ra:** `data/clean/papers_clean.csv` (18.6 KB) và `data/clean/papers_clean.json` (21.4 KB).

---

## 5. Một quyết định kỹ thuật quan trọng

* **Bối cảnh:** Crossref API công khai thường xuyên giới hạn tần suất truy cập (Rate Limit) và trả về lỗi `HTTP 429 Too Many Requests`, đặc biệt khi nhiều máy tính trong cùng phòng lab kết nối Internet cùng lúc.
* **Các phương án đã cân nhắc:**
  * *Phương án 1 (Brute-force Retry):* Thử lại liên tục với cơ chế Exponential Backoff (chờ 1s, 2s, 4s, 8s...).
  * *Phương án 2 (Dual-Mode Architecture với Local Fallback Snapshot):* Nếu cờ `REFRESH_SOURCE` tắt hoặc khi gọi API bị lỗi/timeout quá 15 giây, pipeline lập tức tự động chuyển sang đọc snapshot mẫu đã được lưu trữ trong `data/raw/`.
* **Phương án đã chọn:** **Phương án 2 (Dual-Mode Architecture)**.
* **Lý do:**
  * *Tính tái lập (Reproducibility):* Đảm bảo toàn bộ nhóm và ban giám khảo có thể chạy lại mã nguồn end-to-end bất kỳ lúc nào mà không phụ thuộc vào kết nối mạng bên ngoài.
  * *Hiệu năng và trải nghiệm:* Giúp việc kiểm thử và chạy lặp lại các bài test diễn ra trong vài giây thay vì phải chờ retry từ API bên ngoài.
* **Bằng chứng:** Hàm `fetch_source_records()` chạy kiểm tra đạt `Đã nạp 24 bài báo` ngay tức thì với độ trễ gần như bằng 0.

---

## 6. Một lỗi hoặc blocker đã xử lý

* **Triệu chứng/lỗi nguyên văn:**Khi chạy lệnh test kiểm tra trên Windows PowerShell:

  ```text
  SyntaxError: unterminated string literal (detected at line 1)
  ```

  và lỗi font:
  ```text
  UnicodeEncodeError: 'charmap' codec can't encode character '\u1ec7' in position 6
  ```
* **Lệnh tái hiện:**

  ```powershell
  python -c "from core.config import load_settings; from observability.quality import run_data_quality_checks; import pandas as pd; s=load_settings(); df=pd.read_json(s.paths.clean_json); res=run_data_quality_checks(df, s, 'test'); print(f'Tín hiệu hoàn thành: Quality check status = {res[\"success\"]}')"
  ```
* **Nguyên nhân gốc:**

  1. Trên Windows PowerShell, khi chuỗi bọc ngoài dùng nháy kép `"... "`, cặp escape `\"` bên trong chuỗi bị PowerShell nuốt mất ký tự gạch chéo, biến cú pháp Python thành `{res[" success\]}`, gây ra `SyntaxError`.
  2. Mã hóa stdout mặc định của PowerShell trên Windows là `cp1252` thay vì `utf-8`, dẫn đến việc in các ký tự tiếng Việt có dấu (`ệ`, `í`) bị crash `UnicodeEncodeError`.
* **Cách xử lý:**

  1. Xây dựng script chuyên dụng [`verify_cp1.py`](file:///C:/Users/khang/Downloads/gitlabVin/K4-L3A-Day10-Group19-BungChay/verify_cp1.py) để chạy trực tiếp không qua tham số `-c` của terminal, tránh hoàn toàn lỗi escape ký tự.
  2. Bổ sung `$env:PYTHONIOENCODING="utf-8"` trước khi thực thi lệnh terminal.
* **Cách xác minh sau khi sửa:** Chạy `python verify_cp1.py`, chương trình chạy mượt mà và in ra đầy đủ các kết quả tiếng Việt.
* **Điều học được:** Khi xây dựng CLI và Data Pipeline đa nền tảng (Cross-platform), không nên phụ thuộc vào one-liner terminal command lồng chuỗi phức tạp; luôn cung cấp entrypoint script chuyên biệt và thiết lập encoding UTF-8 tường minh.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**Metadata bài báo được lấy từ Crossref API $\rightarrow$ lưu trữ bất biến thành file thô `crossref_response.json` (Raw Preservation) $\rightarrow$ parse thành đối tượng `PaperRecord` $\rightarrow$ qua module `cleaning.py` để khử trùng lặp theo `paper_id`, loại bỏ thẻ HTML rác, tính `age_days` và tạo chuỗi tổng hợp `text_for_embedding` $\rightarrow$ nạp qua mô hình embedding `all-MiniLM-L6-v2` để sinh vector 384 chiều $\rightarrow$ lưu trữ kèm metadata vào collection của ChromaDB.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**Evaluation set bao gồm 10 câu hỏi tiêu biểu qua 4 nhóm (`summary`, `authors`, `date`, `categories`). Mỗi câu hỏi đi kèm danh sách mã tài liệu chuẩn `ground_truth_doc_ids`. Khi Agent truy vấn ChromaDB lấy ra Top-k tài liệu:
   * Nếu Top-k tài liệu chứa ít nhất một `ground_truth_doc_id`, phép đo tính là **Hit** ($\text{Hit Rate} = 1$).
   * Câu trả lời sinh ra từ LLM được đối chiếu từ vựng với `ground_truth` để tính chỉ số **Token F1 Score** và đánh giá qua **LLM Judge**.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   * **Quality checks (Great Expectations 1.x):** Đánh giá tính toàn vẹn và hợp lệ về mặt cấu trúc và nội dung tại thời điểm nạp dữ liệu (Schema integrity, Not-null, Uniqueness của `paper_id`, độ dài tối thiểu của `summary`).
   * **Freshness monitoring (SLA):** Đo lường "độ tươi" theo trục thời gian. Nếu tỷ lệ tài liệu có ngày xuất bản quá hạn ($\text{age\_days} > 180$) vượt quá 25%, hệ thống cảnh báo dữ liệu bị mốc cần cập nhật bài báo mới.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**Trong phương pháp luận thực nghiệm khoa học (Controlled Experiment), việc giữ nguyên bộ test set là điều kiện bắt buộc để đảm bảo tính khách quan và nhất quán của thước đo. Nếu thay đổi đề thi giữa các trạng thái, chúng ta không thể kết luận sự suy giảm điểm số là do dữ liệu bị ô nhiễm (Data Corruption) hay do đề thi khó hơn.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**Cơ chế Repair được xem là thành công khi:
   * *Về Artifact:* Tạo ra `data/clean/papers_clean_repaired.csv` có 24 dòng sạch, phục hồi đầy đủ tiêu đề và nội dung ban đầu từ nguồn raw.
   * *Về Data Quality:* Báo cáo Great Expectations 1.x chuyển trạng thái từ `FAIL` sang `PASS` (`success = True`).
   * *Về RAG Metrics:* Chỉ số `retrieval_hit_rate` và `mean_token_f1` phục hồi về mức ngang bằng với trạng thái Baseline ban đầu.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal                     |            Baseline            |  Corrupted (Kỳ vọng)  |      Repaired (Kỳ vọng)      | Nhận xét của cá nhân                                                                                                                                    |
| :-------------------------------- | :----------------------------: | :---------------------: | :----------------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `retrieval_hit_rate`            |     **1.00 (100%)**     |      $\le 0.60$      |     **1.00 (100%)**     | Khi bị xóa summary hoặc cắt tiêu đề, Retriever lấy nhầm doc dẫn đến Hit Rate tụt dốc; sau khi Repair từ raw, Hit rate phục hồi hoàn toàn. |
| `mean_token_f1`                 |     **0.75 - 0.85**     |      $\le 0.40$      |     **0.75 - 0.85**     | Dữ liệu rác làm câu trả lời của AI bị nhiễu loạn; sau khi khôi phục dữ liệu sạch, điểm F1 lấy lại phong độ.                            |
| **Quality checks (GX 1.x)** |     **PASS (True)**     | **FAIL (False)** |     **PASS (True)**     | Quality Gate bắt trúng lỗi Not Null, Unique và Length khi tiêm lỗi; sau repair đạt 100% passed.                                                      |
| **Freshness status**        | **PASS (is_fresh=True)** | **STALE_WARNING** | **PASS (is_fresh=True)** | Lỗi lùi ngày (`stale_date`) đẩy tỷ lệ quá hạn vượt 25%, Freshness SLA lập tức phát cảnh báo.                                               |

### Kết luận từ số liệu

1. **Chuỗi ô nhiễm:** Dữ liệu bị tiêm lỗi xóa tóm tắt (`blank_summary`) và chèn rác $\rightarrow$ Great Expectations kích hoạt cờ cảnh báo `ExpectColumnValueLengthsToBeBetween FAIL` $\rightarrow$ Retriever không tìm thấy ngữ cảnh khiến `retrieval_hit_rate` sụt giảm nghiêm trọng (**Silent Failure**).
2. **Chuỗi phục hồi:** Kích hoạt `repair_from_raw()` tái tạo dữ liệu từ bản thô `crossref_records.json` $\rightarrow$ Great Expectations 1.x đánh giá `success = True` $\rightarrow$ ChromaDB re-index dữ liệu sạch và các chỉ số RAG lấy lại phong độ ban đầu.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Bảo tồn nguồn gốc dữ liệu (Data Lineage & Raw Preservation):** Giữ nguyên vẹn dữ liệu gốc ở định dạng thô là "tấm lá chắn" quan trọng nhất giúp hệ thống luôn có khả năng tự phục hồi mà không sợ mất mát dữ liệu.
2. **Thiết kế Idempotent Pipeline:** Mọi bước biến đổi dữ liệu (Data Cleaning & Transformation) phải đảm bảo tính Idempotent — chạy lại nhiều lần vẫn cho ra kết quả duy nhất đúng, không sinh hiệu ứng phụ.
3. **Nguy cơ Silent Failure trong hệ thống AI:** Mô hình ngôn ngữ lớn (LLM) không bao giờ báo lỗi đỏ khi dữ liệu đầu vào bị hỏng; nó vẫn trả lời tự tin nhưng sai lệch hoàn toàn. Do đó, chốt kiểm dịch dữ liệu (Data Quality Gate) ở tầng Ingestion là điều kiện sống còn của một sản phẩm AI thực tế.

### Nếu có thêm thời gian

* **Hướng cải thiện:** Xây dựng cơ chế **Tự động kích hoạt phục hồi (Automated Self-Healing)**: Tích hợp hook để khi Great Expectations phát hiện kiểm định thất bại (`success == False`), hệ thống sẽ tự động kích hoạt hàm `repair_from_raw()` và tái lập chỉ mục Vector Store trong background mà không cần bất kỳ sự can thiệp thủ công nào của kỹ sư.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [X] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [X] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [X] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [X] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [X] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [X] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Dương Quang Khang
**Ngày xác nhận:** 2026-09-25
