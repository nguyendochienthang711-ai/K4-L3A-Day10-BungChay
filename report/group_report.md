# Group Report — Day 10: Data Pipeline & Data Observability

> Dùng mẫu này cho báo cáo chung của nhóm 3–5 thành viên. Thay toàn bộ nội dung trong dấu `[ ]` bằng thông tin và kết quả thực tế. Xóa các dòng hướng dẫn không còn cần thiết trước khi nộp.

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                                                                  |
| ------------------ | -------------------------------------------------------------------------- |
| Khóa/Lớp         | [K3 hoặc K4]                                                              |
| Tên nhóm         | [Tên hoặc mã nhóm]                                                     |
| Repository         | [Đường dẫn repository]                                                 |
| Ngày hoàn thành | [YYYY-MM-DD]                                                               |
| Thông tin         | Nội dung                                                                  |
| ------------------ | -------------------------------------------------------------------------- |
| Khóa/Lớp         | K4A-L3-DAY10                                                               |
| Tên nhóm         | BungChay (Group 19)                                                        |
| Repository         | https://github.com/nguyendochienthang711-ai/K4-L3A-Day10-BungChay          |
| Ngày hoàn thành | 2026-09-25                                                                 |

### Thành viên và phân công

| STT | Họ và tên                  | MSSV                  | Vai trò chính                      | Module/deliverable sở hữu                                                                  |
| --: | ----------------------------- | --------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------- |
|   1 | [Họ tên]                    | [MSSV]                | [Vai trò]                           | [File, hàm hoặc artifact]                                                                  |
|   2 | [Họ tên]                    | [MSSV]                | [Vai trò]                           | [File, hàm hoặc artifact]                                                                  |
|   3 | [Họ tên]                    | [MSSV]                | [Vai trò]                           | [File, hàm hoặc artifact]                                                                  |
|   4 | [Nếu có]                    | [MSSV]                | [Vai trò]                           | [File, hàm hoặc artifact]                                                                  |
|   5 | [Nếu có]                    | [MSSV]                | [Vai trò]                           | [File, hàm hoặc artifact]                                                                  |
|   1 | Nguyễn Đỗ Chiến Thắng    | [MSSV]                | Trưởng nhóm / Pipeline Integrator | `src/core/`, `script/run_phase1.py`, `script/run_corruption_flow.py`                   |
|   2 | **Dương Quang Khang** | **2A202602624** | **Data Foundation Owner**      | `src/ingestion/crossref.py`, `src/ingestion/cleaning.py`, `data/raw/`, `data/clean/` |
|   3 | Đặng Hữu Tâm              | 02940                 | RAG & Vector Index Specialist        | `src/retrieval/index.py`, `src/retrieval/embeddings.py`, ChromaDB collections            |
|   4 | [Thành viên 4]              | [MSSV]                | Observability & Evaluation Lead      | `src/observability/quality.py` (GX 1.x), `src/evaluation/testset.py`, reporting          |

---

## 2. Tóm tắt kết quả

Viết từ 150–250 từ, trả lời ngắn gọn:
Nhóm **BungChay** đã hoàn thành trọn vẹn toàn bộ chu trình kỹ thuật của bài lab **Day 10 — Data Pipeline & Data Observability for RAG**:

1. **Khối Data Foundation:** Xây dựng module thu thập Crossref API với cơ chế Cứu hộ Offline (Dual-Mode), làm sạch chuẩn hóa dữ liệu học thuật (loại bỏ thẻ HTML/JATS XML rác, khử trùng lặp mã DOI `paper_id`, tính `age_days` chuẩn UTC và ghép trường nhúng ngữ cảnh `text_for_embedding` 5 phần), bàn giao 24 bản ghi sạch vào `data/clean/papers_clean.csv` và `papers_clean.json`.
2. **Khối Data Observability:** Thiết lập trạm kiểm soát chất lượng dữ liệu (**Data Quality Gate**) sử dụng chuẩn mới **Great Expectations 1.x** (ephemeral context) với 4 Expectations thiết yếu và cơ chế giám sát **Freshness SLA** (ngưỡng 180 ngày).
3. **Khối RAG & Evaluation:** Khởi tạo ChromaDB index 24 tài liệu với mô hình `all-MiniLM-L6-v2`, xây dựng bộ test chuẩn gồm 10 câu hỏi qua 4 nhóm nghiệp vụ.
4. **Hiện tượng Silent Failure:** Tiêm 6 kịch bản lỗi thực tế (xóa tóm tắt, cắt ngắn tiêu đề, chèn ký tự rác, lùi ngày...) khiến điểm Retrieval Hit Rate sụt giảm nghiêm trọng từ **100% xuống 70%** mà Agent không hề báo lỗi crash.
5. **Cơ chế Idempotent Repair:** Triển khai hàm tự phục hồi an toàn trực tiếp từ nguồn lưu trữ thô ban đầu `data/raw/crossref_records.json`, khôi phục thành công 100% hiệu năng của RAG Agent (Hit Rate đạt lại 100%, Token F1 đạt 1.0) và đưa Quality Gate trở lại trạng thái **PASS**.

- Nhóm đã hoàn thành những phần nào?
- Baseline pipeline đã tạo ra các artifact nào?
- Corruption nào ảnh hưởng rõ nhất đến data quality hoặc agent?
- Repair đã phục hồi được chỉ số nào?
- Blocker hoặc giới hạn quan trọng nhất còn lại là gì?

---

**Tóm tắt của nhóm:**

[Viết phần tóm tắt tại đây.]

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

Điều chỉnh sơ đồ dưới đây nếu cách triển khai thực tế của nhóm khác starter:

```text
Crossref API
    -> raw response/raw records
    -> cleaning và data modeling
    -> embedding + ChromaDB index
    -> evaluation baseline
    -> quality/freshness reports
    -> corruption
    -> re-index và re-evaluate
    -> repair từ dữ liệu nguồn
    -> comparison report
Nguồn Crossref REST API (hoặc Snapshot Offline data/raw/crossref_response.json)
    ├── 1. Kéo dữ liệu & Bảo tồn bản gốc (Raw Preservation) -> data/raw/crossref_records.json
    ├── 2. Làm sạch & Chuẩn hóa (Transformation)            -> data/clean/papers_clean.csv
    ├── 3. Trạm kiểm soát chất lượng (Quality Gate)         -> Great Expectations 1.x & Freshness SLA
    ├── 4. Nhúng ngữ nghĩa & Lưu Vector (Index)             -> MiniLM + ChromaDB (papers-baseline)
    ├── 5. Đánh giá chất lượng RAG (Benchmark)              -> Hit Rate, Token F1, LLM Judge Score
    ├── 6. Thử thách tiêm độc tố dữ liệu (Corruption)       -> Giả lập 6 lỗi dữ liệu thực tế
    └── 7. Phục hồi an toàn & Đối chiếu (Repair)            -> Tái tạo từ Raw & Báo cáo 3 trạng thái
```

### Trách nhiệm của từng khối

| Khối                       | Input                                            | Xử lý chính                                                                                               | Output/artifact                                                                   | Owner                                       |
| --------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | ------------------------------------------- |
| Ingestion                   | [Nguồn/input]                                   | [Fetch, retry, parse...]                                                                                     | [Đường dẫn artifact]                                                          | [Thành viên]                              |
| Cleaning                    | [Input]                                          | [Các quy tắc chính]                                                                                       | [Đường dẫn artifact]                                                          | [Thành viên]                              |
| Embedding/index             | [Input]                                          | [Model/index config]                                                                                         | [Đường dẫn artifact]                                                          | [Thành viên]                              |
| Evaluation                  | [Input]                                          | [Test set và metrics]                                                                                       | [Đường dẫn artifact]                                                          | [Thành viên]                              |
| Observability               | [Input]                                          | [Quality/freshness checks]                                                                                   | [Đường dẫn artifact]                                                          | [Thành viên]                              |
| Corruption/repair           | [Input]                                          | [Corruption và repair]                                                                                      | [Đường dẫn artifact]                                                          | [Thành viên]                              |
| Orchestration               | [Input]                                          | [Thứ tự chạy]                                                                                             | [Reports/metrics]                                                                 | [Thành viên]                              |
| Khối                       | Input                                            | Xử lý chính                                                                                               | Output/artifact                                                                   | Owner                                       |
| :---                        | :---                                             | :---                                                                                                         | :---                                                                              | :---                                        |
| **Ingestion**         | Crossref REST API / Snapshot raw JSON            | Fetch có retry/timeout 15s, parse payload, làm sạch thẻ XML rác, hỗ trợ Dual-Mode offline fallback    | `data/raw/crossref_response.json`, `data/raw/crossref_records.json`           | **Dương Quang Khang**               |
| **Cleaning**          | Danh sách`PaperRecord`, tham số `run_date` | Khử trùng lặp theo`paper_id`, tính `age_days`, tạo cột hỗ trợ, cấu trúc `text_for_embedding` | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json`                 | **Dương Quang Khang**               |
| **Embedding/index**   | Clean DataFrame (24 dòng sạch)                 | Tạo vector nhúng 384 chiều (`all-MiniLM-L6-v2`), index vào ChromaDB collection                         | `data/chroma/` (`papers-baseline`, `papers-corrupted`, `papers-repaired`) | Đặng Hữu Tâm                            |
| **Evaluation**        | Clean DataFrame, Chroma index                    | Sinh 10 câu hỏi test (4 nhóm nghiệp vụ), đo Hit Rate, Token F1, Judge Score                            | `data/eval/test_set.json`, `data/results/*_metrics.json`                      | Observability & Evaluation Lead             |
| **Observability**     | DataFrame (sạch / lỗi / phục hồi)            | Ephemeral Context GX 1.x (4 Expectations), giám sát Freshness SLA                                          | `data/quality/*_quality_report.json`, `freshness_report.json`                 | Observability & Evaluation Lead             |
| **Corruption/repair** | Clean DataFrame, Raw records                     | Tiêm 6 lỗi dữ liệu; hàm`repair_from_raw()` tự động tái tạo dữ liệu từ snapshot thô           | `data/results/corruption_log.json`, `data/clean/papers_clean_repaired.csv`    | **Dương Quang Khang** & Integration |
| **Orchestration**     | Cấu hình`Settings`, các pipeline scripts    | Điều phối liên kết toàn luồng Phase 1 và Phase 2 end-to-end                                          | `data/reports/phase1_report.md`, `data/reports/corruption_report.md`          | Trưởng nhóm                              |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng                        |
| ---------------------------- | ------------------------------------------ |
| `LLM_PROVIDER`             | [Giá trị]                                |
| `LLM_MODEL`                | [Giá trị]                                |
| Embedding model              | [Giá trị]                                |
| Số lượng Crossref records | [Giá trị]                                |
| Retrieval`top_k`           | [Giá trị]                                |
| Freshness threshold          | [Giá trị]                                |
| Random seed, nếu có        | [Giá trị]                                |
| Biến/cấu hình             | Giá trị sử dụng                        |
| :---                         | :---                                       |
| `LLM_PROVIDER`             | `gemini` (hỗ trợ fallback `mock`)    |
| `LLM_MODEL`                | `gemini-2.5-flash`                       |
| Embedding model              | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 bài báo                               |
| Retrieval`top_k`           | 4                                          |
| Freshness threshold          | 180 ngày                                  |
| Random seed                  | Cố định cho bộ test                    |

Không dán nội dung API key hoặc file `.env` vào báo cáo.

### Lệnh cài đặt

Chỉ giữ lại cách nhóm đã dùng.

```bash
uv sync
```

Hoặc:

```bash
```powershell
python -m pip install -e .
```

### Lệnh chạy

Baseline:

```bash
uv run python script/run_phase1.py
1. **Kiểm tra nhanh khối Ingestion & Cleaning:**
```powershell
python verify_cp1.py
```

Hoặc với môi trường `pip` đã kích hoạt:

```bash
2. **Chạy Baseline Pipeline (Phase 1):**
```powershell
python script/run_phase1.py
```

Corruption flow:

```bash
uv run python script/run_corruption_flow.py
```

Hoặc với môi trường `pip` đã kích hoạt:

```bash
3. **Chạy Corruption, Repair & Comparison Flow (Phase 2):**
```powershell
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                                                                                                      |
| ----------------- | ----------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Baseline pipeline | [Thành công/Thất bại một phần/Thất bại] | [Thời gian]                  | [Artifact hoặc log đã che secret]                                                                              |
| Corruption flow   | [Thành công/Thất bại một phần/Thất bại] | [Thời gian]                  | [Artifact hoặc log đã che secret]                                                                              |
| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                                                                                                      |
| :---              | :---                                            | :---                          | :---                                                                                                              |
| `verify_cp1.py` | Thành công 100%                               | 2026-09-25 14:58              | In ra 4 chỉ số đạt chuẩn: nạp 24 bài, clean 24 dòng, GX status True, is_fresh True                        |
| Baseline pipeline | Thành công 100%                               | 2026-09-25 16:47              | Sinh đủ`baseline_metrics.json` và `phase1_report.md`                                                       |
| Corruption flow   | Thành công 100%                               | 2026-09-25 16:47              | Sinh đủ`corruption_log.json`, `corrupted_metrics.json`, `repaired_metrics.json`, `corruption_report.md` |

---

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                                                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Source                      | [Crossref endpoint/dataset thực tế]                                                                                      |
| Query/filter                | [Query hoặc filter]                                                                                                       |
| Thời điểm lấy dữ liệu | [Timestamp]                                                                                                                |
| Số record nhận được    | [Số lượng]                                                                                                              |
| Cơ chế retry/backoff      | [Mô tả ngắn]                                                                                                            |
| Thuộc tính                | Giá trị                                                                                                                  |
| :---                        | :---                                                                                                                       |
| Source                      | Crossref REST API (`https://api.crossref.org/works`)                                                                     |
| Query/filter                | `query=agentic retrieval augmented generation large language model`, `has-abstract:true`                               |
| Thời điểm lấy dữ liệu | 2026-09-25                                                                                                                 |
| Số record nhận được    | 24 bài báo khoa học                                                                                                     |
| Cơ chế retry/backoff      | Timeout 15s; tự động fallback đọc snapshot`data/raw/crossref_response.json` khi dính mã lỗi 429 hoặc rớt mạng |

### Raw và clean schema

| Trường               | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa                                              | Xử lý khi thiếu/sai                                                     |
| ---------------------- | --------------- | ------------ | ------------------------------------------------------ | -------------------------------------------------------------------------- |
| [Tên trường]        | [Kiểu]         | [Có/Không] | [Ý nghĩa]                                            | [Cách xử lý]                                                            |
| [Tên trường]        | [Kiểu]         | [Có/Không] | [Ý nghĩa]                                            | [Cách xử lý]                                                            |
| Trường               | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa                                              | Xử lý khi thiếu/sai                                                     |
| :---                   | :---            | :---:        | :---                                                   | :---                                                                       |
| `paper_id`           | `str`         | Có          | Mã định danh duy nhất (DOI)                        | Bỏ qua bản ghi nếu thiếu DOI                                           |
| `title`              | `str`         | Có          | Tiêu đề bài báo khoa học                         | Cắt khoảng trắng thừa; bỏ bản ghi nếu rỗng                         |
| `summary`            | `str`         | Có          | Tóm tắt nội dung nghiên cứu                       | Loại bỏ thẻ`<jats:p>`, `</jats:p>`, chuẩn hóa khoảng trắng      |
| `authors`            | `list[str]`   | Có          | Danh sách tác giả nghiên cứu                      | Ghép`"Given Family"`, fallback thành tên chuỗi                       |
| `categories`         | `list[str]`   | Có          | Lĩnh vực / chuyên ngành phân loại                | Lấy từ`subject`, fallback `"Computer Science"`                       |
| `published`          | `str` (ISO)   | Có          | Ngày xuất bản (`YYYY-MM-DD`)                      | Parse từ mảng`date-parts`, chuẩn hóa ISO 8601                        |
| `age_days`           | `int`         | Có          | Số ngày tính từ ngày xuất bản đến ngày chạy | Tính theo chuẩn UTC:`(run_date - published).days`                      |
| `text_for_embedding` | `str`         | Có          | Chuỗi ngữ cảnh tổng hợp nhúng vector             | Ghép 5 phần tiêu chuẩn: Title, Authors, Published, Categories, Summary |

### Quy tắc cleaning

| Quy tắc                                           | Quality dimension liên quan | Số record bị tác động | Cách xác minh                                                                  |
| -------------------------------------------------- | ---------------------------- | -------------------------: | -------------------------------------------------------------------------------- |
| [Ví dụ: loại record không có title]           | [Completeness/Validity/...]  |              [Số lượng] | [Artifact/kiểm tra]                                                             |
| [Quy tắc thực tế]                               | [Dimension]                  |              [Số lượng] | [Artifact/kiểm tra]                                                             |
| Quy tắc                                           | Quality dimension            |     Số record tác động | Cách xác minh                                                                  |
| :---                                               | :---                         |                      :---: | :---                                                                             |
| Xóa thẻ HTML/XML rác (`<jats:p>`, v.v.)       | Validity & Accuracy          |                    24 / 24 | Hàm`_clean_str()`, kiểm tra không còn ký tự `<>` trong text            |
| Khử trùng lặp theo khóa duy nhất`paper_id`  | Uniqueness                   |             Toàn bộ tập | `df.drop_duplicates(subset=['paper_id'])`, GX `ExpectColumnValuesToBeUnique` |
| Chuẩn hóa ngày xuất bản và tính`age_days` | Consistency & Timeliness     |                    24 / 24 | Chuyển đổi qua`pd.to_datetime(..., utc=True)`, kiểm tra `age_days >= 0`  |
| Tạo trường nhúng`text_for_embedding` 5 phần | Completeness                 |                    24 / 24 | Kiểm tra độ dài chuỗi và GX`ExpectColumnValuesToNotBeNull`               |

Giải thích cách nhóm tạo `text_for_embedding`, document ID và `age_days`:
-------------------------------------------------

[Mô tả tại đây.]

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế                                                                   |
| ---------------------------------------- | -------------------------------------------------------------------------------------- |
| Số câu hỏi                            | [Số lượng]                                                                          |
| Các`question_type`                    | [Danh sách]                                                                           |
| Ground-truth document ID                 | [Cách tạo/đối chiếu]                                                              |
| Embedding model                          | [Tên model]                                                                           |
| Vector store/collection                  | [Tên/config]                                                                          |
| Retrieval`top_k`                       | [Giá trị]                                                                            |
| LLM provider/model                       | [Giá trị]                                                                            |
| Test set dùng chung cho ba trạng thái | [Đường dẫn hoặc ID/hash]                                                          |
| Thành phần                             | Cấu hình thực tế                                                                   |
| :---                                     | :---                                                                                   |
| Số câu hỏi                            | 10 câu hỏi chuẩn hóa                                                               |
| Các`question_type`                    | `summary` (4 câu), `authors` (2 câu), `date` (2 câu), `categories` (2 câu) |
| Ground-truth document ID                 | Ánh xạ mã DOI chính xác của bài báo tương ứng trong tập clean              |
| Embedding model                          | `sentence-transformers/all-MiniLM-L6-v2`                                             |
| Vector store / collection                | ChromaDB local (`papers-baseline`, `papers-corrupted`, `papers-repaired`)        |
| Retrieval`top_k`                       | 4                                                                                      |
| LLM provider/model                       | `gemini` / `gemini-2.5-flash`                                                      |
| Test set dùng chung                     | `data/eval/test_set.json` (cố định cho cả 3 trạng thái)                        |

Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:

> **Tại sao test set được giữ nguyên cho cả ba trạng thái?**
> Trong phương pháp luận thực nghiệm (Controlled Experiment), test set cố định đóng vai trò là "thước đo đối chứng chuẩn". Nếu thay đổi đề thi giữa các trạng thái, chúng ta không thể xác định được sự sụt giảm hiệu năng là do dữ liệu bị lỗi hay do câu hỏi mới khó hơn.

[Giải thích tại đây.]
--------------------------

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái  | Ghi chú                                                           |
| ------------------------ | -------------------------------------- | ------------- | ------------------------------------------------------------------ |
| Raw response/records     | `data/raw/`                          | [Có/Thiếu]  | [Ghi chú]                                                         |
| Cleaned dataset          | `data/clean/`                        | [Có/Thiếu]  | [Ghi chú]                                                         |
| Embedding manifest/index | `data/embeddings/`                   | [Có/Thiếu]  | [Ghi chú]                                                         |
| Evaluation set           | `data/eval/`                         | [Có/Thiếu]  | [Ghi chú]                                                         |
| Baseline metrics         | `data/results/baseline_metrics.json` | [Có/Thiếu]  | [Ghi chú]                                                         |
| Quality/freshness        | `data/quality/`                      | [Có/Thiếu]  | [Ghi chú]                                                         |
| Baseline report          | `data/reports/phase1_report.md`      | [Có/Thiếu]  | [Ghi chú]                                                         |
| Artifact                 | Đường dẫn thực tế                | Trạng thái  | Ghi chú                                                           |
| :---                     | :---                                   | :---:         | :---                                                               |
| Raw response/records     | `data/raw/`                          | **Có** | `crossref_response.json` và `crossref_records.json` (24 bài) |
| Cleaned dataset          | `data/clean/`                        | **Có** | `papers_clean.csv` và `papers_clean.json` (24 dòng sạch)    |
| Chroma Vector DB         | `data/chroma/`                       | **Có** | Chứa 3 collections tách biệt                                    |
| Evaluation set           | `data/eval/`                         | **Có** | `test_set.json` (10 câu hỏi chuẩn)                            |
| Baseline metrics         | `data/results/baseline_metrics.json` | **Có** | Ghi nhận Hit Rate = 1.0, Token F1 = 1.0                           |
| Quality/freshness        | `data/quality/`                      | **Có** | `baseline_quality_report.json`, `freshness_report.json`        |
| Baseline report          | `data/reports/phase1_report.md`      | **Có** | Báo cáo chi tiết Phase 1                                        |

### Baseline metrics

| Metric                 |               Giá trị | Diễn giải                                                                                           |
| ---------------------- | ----------------------: | ----------------------------------------------------------------------------------------------------- |
| `retrieval_hit_rate` |             [Giá trị] | [Ý nghĩa trong kết quả của nhóm]                                                                |
| `mean_token_f1`      |             [Giá trị] | [Diễn giải]                                                                                         |
| `judge_accuracy`     |             [Giá trị] | [Diễn giải]                                                                                         |
| `mean_judge_score`   |             [Giá trị] | [Diễn giải]                                                                                         |
| Ragas, nếu có        |         [Giá trị/N/A] | [Diễn giải hoặc lý do không chạy]                                                               |
| Metric                 |               Giá trị | Diễn giải                                                                                           |
| :---                   |                   :---: | :---                                                                                                  |
| `retrieval_hit_rate` | **1.0000 (100%)** | 10/10 câu hỏi đều truy vấn trúng tài liệu chứa đáp án trong Top-4                         |
| `mean_token_f1`      |        **1.0000** | Độ tương đồng từ vựng giữa câu trả lời sinh ra và Ground Truth đạt điểm tuyệt đối |
| `judge_accuracy`     | **1.0000 (100%)** | 100% câu trả lời được LLM Judge chấm đạt yêu cầu nghiệp vụ                               |
| `mean_judge_score`   |    **5.00 / 5.0** | Điểm số đánh giá chất lượng câu trả lời đạt mức tối đa                               |

---

## 8. Data quality và freshness

### Quality checks

### Quality checks (Great Expectations 1.x)

| Check                                   | Quality dimension | Ngưỡng/kỳ vọng                                            | Kết quả baseline               | Bằng chứng                     |
| --------------------------------------- | ----------------- | ------------------------------------------------------------- | -------------------------------- | -------------------------------- |
| [Tên check]                            | [Dimension]       | [Ngưỡng]                                                    | [Pass/Fail + giá trị]          | [Artifact]                       |
| [Tên check]                            | [Dimension]       | [Ngưỡng]                                                    | [Pass/Fail + giá trị]          | [Artifact]                       |
| Check                                   | Quality dimension | Ngưỡng/kỳ vọng                                            | Kết quả baseline               | Bằng chứng                     |
| :---                                    | :---              | :---                                                          | :---:                            | :---                             |
| `ExpectTableRowCountToBeBetween`      | Completeness      | 5 đến 5000 dòng                                            | **PASS** (24 dòng)        | `baseline_quality_report.json` |
| `ExpectColumnValuesToNotBeNull`       | Completeness      | Không null ở`paper_id`, `title`, `text_for_embedding` | **PASS** (0 null)          | `baseline_quality_report.json` |
| `ExpectColumnValuesToBeUnique`        | Uniqueness        | `paper_id` là khóa duy nhất                              | **PASS** (0 trùng lặp)   | `baseline_quality_report.json` |
| `ExpectColumnValueLengthsToBeBetween` | Validity          | `summary` có độ dài $\ge 30$ ký tự                  | **PASS** (đủ ngữ cảnh) | `baseline_quality_report.json` |

### Freshness

### Freshness SLA

| Thuộc tính               | Giá trị                                                                                       |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| Freshness được đo tại | [Dataset/index/artifact]                                                                        |
| Timestamp mới nhất       | [Giá trị]                                                                                     |
| Ngưỡng freshness         | [Giá trị]                                                                                     |
| Trạng thái baseline      | [Fresh/Stale/Unknown]                                                                           |
| Lý do                     | [Giải thích dựa trên số liệu]                                                             |
| Thuộc tính               | Giá trị                                                                                       |
| :---                       | :---                                                                                            |
| Vị trí đo freshness     | Trường`age_days` tính từ ngày `published` trên tập cleaned dataset                   |
| Timestamp mới nhất       | `2026-05-20`                                                                                  |
| Ngưỡng freshness SLA     | 180 ngày (tối đa 25% bài báo được phép quá hạn)                                      |
| Trạng thái baseline      | **Fresh (is_fresh = True)**                                                               |
| Lý do                     | Chỉ có 1/24 bài báo có`age_days > 180` (tỷ lệ 4.2% $\le$ 25% ngưỡng SLA cho phép) |

---

## 9. Corruption scenarios và repair

| Corruption                    | Cách tạo                                  | Record bị tác động | Quality signal kỳ vọng                                         | Tác động thực tế                   | Cách repair                             |
| ----------------------------- | ------------------------------------------- | ---------------------: | ---------------------------------------------------------------- | --------------------------------------- | ---------------------------------------- |
| [Loại corruption]            | [Mô tả]                                   |          [Số lượng] | [Kỳ vọng]                                                      | [Artifact/metric]                       | [Cách repair]                           |
| [Loại corruption]            | [Mô tả]                                   |          [Số lượng] | [Kỳ vọng]                                                      | [Artifact/metric]                       | [Cách repair]                           |
| Corruption                    | Cách tạo                                  | Record bị tác động | Quality signal kỳ vọng                                         | Tác động thực tế                   | Cách repair                             |
| :---                          | :---                                        |                  :---: | :---                                                             | :---                                    | :---                                     |
| **Drop latest records** | Xóa 20% bản ghi mới nhất                |             5 bản ghi | `ExpectTableRowCountToBeBetween` cảnh báo nếu thiếu nhiều | Mất tài liệu mới, giảm Hit Rate    | Đọc lại từ bản lưu raw             |
| **Blank summary**       | Xóa rỗng trường tóm tắt               |             3 bản ghi | `ExpectColumnValueLengthsToBeBetween` báo **FAIL**      | Mất ngữ cảnh, Agent bị ảo giác    | Khôi phục từ`crossref_records.json` |
| **Inject noise**        | Chèn ký tự rác vô nghĩa               |             3 bản ghi | Vector embedding bị sai lệch nghiêm trọng                    | Top-k retrieval lấy nhầm tài liệu   | Làm sạch lại từ raw data             |
| **Truncate title**      | Cắt tiêu đề dưới 8 ký tự            |             3 bản ghi | Tiêu đề không đủ nghĩa                                    | Tra cứu theo tiêu đề bị thất bại | Tái tạo lại tiêu đề gốc           |
| **Stale date**          | Lùi ngày xuất bản về 365 ngày trước |             4 bản ghi | Freshness SLA cảnh báo**STALE_WARNING**                  | Vi phạm SLA dữ liệu tươi           | Tính toán lại`age_days` từ raw     |
| **Duplicate rows**      | Nhân đôi một số bản ghi               |             2 bản ghi | `ExpectColumnValuesToBeUnique` báo **FAIL**             | Làm loãng Vector Search               | `drop_duplicates` theo `paper_id`    |

Corruption log:

> **Cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy:**
> Hệ thống **không sửa thủ công cục bộ** trên file lỗi mà áp dụng cơ chế **Idempotent Repair**: hàm `repair_from_raw()` triệu hồi dữ liệu gốc nguyên sơ từ `data/raw/crossref_records.json`, chạy lại toàn bộ quy trình tiền xử lý chuẩn hóa và tái tạo ra tập dữ liệu sạch `data/clean/papers_clean_repaired.csv`.

- Đường dẫn: `data/results/corruption_log.json`
- Trạng thái: [Có/Thiếu]
- Nhận xét: [Log có đủ loại corruption, record bị tác động và tham số hay không?]

---

Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy thay vì chỉ che kết quả lỗi:

[Giải thích tại đây.]

## 10. So sánh baseline, corrupted và repaired

| Metric/signal                         |             Baseline |                     Corrupted |                     Repaired |             Thay đổi do corruption |                                       Mức phục hồi | Nhận xét   |
| ------------------------------------- | -------------------: | ----------------------------: | ---------------------------: | -----------------------------------: | ----------------------------------------------------: | ------------ |
| `retrieval_hit_rate`                |                  [ ] |                           [ ] |                          [ ] |                                  [ ] |                                                   [ ] | [Nhận xét] |
| `mean_token_f1`                     |                  [ ] |                           [ ] |                          [ ] |                                  [ ] |                                                   [ ] | [Nhận xét] |
| `judge_accuracy`                    |                  [ ] |                           [ ] |                          [ ] |                                  [ ] |                                                   [ ] | [Nhận xét] |
| `mean_judge_score`                  |                  [ ] |                           [ ] |                          [ ] |                                  [ ] |                                                   [ ] | [Nhận xét] |
| Quality checks pass/fail              |                  [ ] |                           [ ] |                          [ ] |                                  [ ] |                                                   [ ] | [Nhận xét] |
| Freshness status                      |                  [ ] |                           [ ] |                          [ ] |                                  [ ] |                                                   [ ] | [Nhận xét] |
| Metric/signal                         |  🟢 Baseline (Sạch) | 🔴 Corrupted (Bị tiêm lỗi) | 🔵 Repaired (Sau phục hồi) | Biến thiên (Corrupt$\to$ Repair) |                                            Nhận xét |              |
| :---                                  |                :---: |                         :---: |                        :---: |                                :---: |                                                  :--- |              |
| **Data Quality Gate (GX 1.x)**  |       **PASS** |        **FAIL (ALARM)** |               **PASS** |             Phát hiện & Phục hồi |            Bắt trúng lỗi schema và độ dài text |              |
| **Freshness SLA (> 180 ngày)** |       **PASS** |        **FAIL (STALE)** |               **PASS** |               Phục hồi độ tươi |               Cảnh báo khi dữ liệu bị lùi ngày |              |
| **`retrieval_hit_rate`**      |    **100.00%** |              **70.00%** |            **100.00%** |       $\uparrow$ **+30.00%** |        Dữ liệu lỗi làm mất tài liệu liên quan |              |
| **`mean_token_f1`**           |     **1.0000** |              **0.9000** |             **1.0000** |       $\uparrow$ **+0.1000** | Câu trả lời AI chính xác tuyệt đối sau repair |              |
| **`judge_accuracy`**          |    **100.00%** |              **90.00%** |            **100.00%** |       $\uparrow$ **+10.00%** |             Điểm đánh giá phục hồi toàn diện |              |
| **`mean_judge_score`**        | **5.00 / 5.0** |          **4.60 / 5.0** |         **5.00 / 5.0** |         $\uparrow$ **+0.40** |                        Lấy lại phong độ cao nhất |              |

Nêu ít nhất hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:

### Hai kết luận nhân quả được minh chứng bằng artifacts:

1. **Chuỗi ô nhiễm (Data Corruption $\to$ Quality Alarm $\to$ Silent Failure):**Khi dữ liệu bị tiêm lỗi xóa trắng tóm tắt (`blank_summary`) và cắt ngắn tiêu đề $\rightarrow$ Great Expectations 1.x lập tức báo động đỏ `ExpectColumnValueLengthsToBeBetween FAIL` $\rightarrow$ Vector Store không tìm thấy ngữ cảnh khiến `retrieval_hit_rate` sụp đổ từ 100% xuống 70% (Agent trả lời trôi chảy nhưng thiếu căn cứ, minh chứng cho hiện tượng **Silent Failure**).
2. **Chuỗi phục hồi (Idempotent Repair $\to$ Quality Recovery $\to$ Agent Recovery):**Hàm `repair_from_raw()` kích hoạt tái tạo lại dữ liệu sạch từ bản lưu thô $\rightarrow$ Great Expectations 1.x chuyển sang trạng thái `PASS` $\rightarrow$ ChromaDB nạp lại các vector chuẩn giúp `retrieval_hit_rate` và `mean_token_f1` hồi phục về mức tuyệt đối 100%.
3. [Corruption/data change] → [quality/freshness signal] → [retrieval/answer metric].
4. [Repair action] → [quality/freshness recovery] → [agent metric recovery hoặc lý do chưa recovery].

---

Không kết luận corruption “có tác động” nếu số liệu không cho thấy thay đổi. Nếu kết quả khác kỳ vọng, mô tả giả thuyết và cách nhóm đã kiểm tra.

## 11. Vấn đề tích hợp quan trọng

Mô tả một vấn đề phát sinh khi ghép các module trong pipeline và cách nhóm xử lý:

* **Triệu chứng:** Khi chạy các câu lệnh kiểm tra inline trên Windows PowerShell (ví dụ lệnh test quality gate chứa tham số `res[\"success\"]`), terminal báo lỗi cú pháp: `SyntaxError: unterminated string literal (detected at line 1)` và lỗi font `UnicodeEncodeError: 'charmap' codec can't encode character '\u1ec7'`.
* **Nguyên nhân:** Windows PowerShell xử lý dấu nháy kép escape `\"` không tương thích với chuẩn Bash, đồng thời mã hóa output mặc định trên Windows là `cp1252` làm crash các chuỗi tiếng Việt có dấu.
* **Cách xử lý:**
  1. Xây dựng script chuyên dụng [`verify_cp1.py`](file:///C:/Users/khang/Downloads/gitlabVin/K4-L3A-Day10-Group19-BungChay/verify_cp1.py) để chạy trực tiếp không qua shell inline string.
  2. Bổ sung cấu hình `$env:PYTHONIOENCODING="utf-8"` trong hướng dẫn chạy terminal.
* **Cách xác minh:** Chạy `python verify_cp1.py`, toàn bộ 4 chỉ số của Checkpoint 1 được in ra trơn tru không có lỗi.

- **Triệu chứng:** [Lỗi hoặc kết quả sai.]
- **Nguyên nhân:** [Root cause.]
- **Cách xử lý:** [Thay đổi đã thực hiện.]
- **Cách xác minh:** [Lệnh và artifact.]

---

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại                            | Ảnh hưởng                                             | Hướng cải thiện có thể kiểm chứng                                                                                                                |
| ------------------------------------------------ | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Giới hạn]                                     | [Ảnh hưởng]                                           | [Đề xuất]                                                                                                                                             |
| [Giới hạn]                                     | [Ảnh hưởng]                                           | [Đề xuất]                                                                                                                                             |
| Giới hạn hiện tại                            | Ảnh hưởng                                             | Hướng cải thiện có thể kiểm chứng                                                                                                                |
| :---                                             | :---                                                     | :---                                                                                                                                                     |
| **Kích hoạt Repair còn thủ công**     | Phải chạy lệnh script để phục hồi khi có sự cố | Xây dựng cơ chế**Automated Self-Healing**: Khi GX 1.x báo `FAIL`, pipeline tự động trigger `repair_from_raw()` và re-index Vector DB. |
| **Giám sát trực quan chưa có web UI** | Chỉ xem được kết quả qua log JSON và Markdown     | Tích hợp Streamlit Dashboard hiển thị phân bố độ tuổi bài báo và cảnh báo Data Drift theo thời gian thực (đạt điểm Bonus B1).        |

---

## 13. Checklist trước khi nộp

- [ ] Thông tin nhóm và repository chính xác.
- [ ] Phân công khớp với module, artifact và kết quả thực tế.
- [ ] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [ ] Baseline, corrupted và repaired dùng cùng evaluation set.
- [ ] Bảng metrics khớp với các file trong `data/results/`.
- [ ] Quality/freshness conclusions khớp với `data/quality/`.
- [ ] Các đường dẫn báo cáo và artifact truy cập được.
- [ ] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [ ] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
- [X] Thông tin nhóm `BungChay` và repository chính xác.
- [X] Phân công vai trò từng thành viên khớp với code và deliverable thực tế.
- [X] Các lệnh tái hiện đã được kiểm tra chạy thành công 100%.
- [X] Cả ba trạng thái Baseline, Corrupted và Repaired đều dùng chung một bộ test set `test_set.json`.
- [X] Bảng số liệu trong báo cáo khớp 100% với các file JSON trong `data/results/`.
- [X] Kết luận Data Quality và Freshness khớp với `data/quality/`.
- [X] Mỗi thành viên đã có báo cáo vai trò riêng trong `report/`.
- [X] Tuyệt đối không commit file `.env`, API key hoặc Secret lên repository.
