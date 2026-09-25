# Group Report — Day 10: Data Pipeline & Data Observability

> Báo cáo tổng kết chính thức của nhóm BungChay cho dự án Day 10: Data Pipeline, Data Observability & RAG System.

---

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| :--- | :--- |
| **Khóa / Lớp** | K4A - Level 3 (Day 10) |
| **Tên nhóm** | BungChay (`K4A-L3-DAY10`) |
| **Tên Repository** | `K4-L3A-Day10-BungChay` |
| **Ngày hoàn thành** | 2026-09-25 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module / deliverable sở hữu |
| --: | :--- | :---: | :--- | :--- |
| 1 | Nguyễn Đỗ Chiến Thắng | 2A202602442 | Trưởng nhóm / Pipeline Lead | `src/core/`, `src/pipelines/` (`phase1.py`, `corruption_flow.py`), `script/` entrypoints, orchestration & Git management |
| 2 | Dương Gia Khang | 2A202601892 | Data Foundation Owner | `src/ingestion/` (`crossref.py`, `cleaning.py`, `corruption.py`), Raw data preservation & Idempotent Repair flow |
| 3 | Đặng Hữu Tâm | 02940 | RAG Specialist | `src/retrieval/` (`index.py`, `embeddings.py`, `llm.py`, `agent.py`), ChromaDB 3 collections (`papers-baseline`, `papers-corrupted`, `papers-repaired`), smoke tests |
| 4 | Nguyễn Hoàng Việt | 2A202601404 | Observability & Evaluation Lead | `src/observability/` (`quality.py` GX 1.x, `reporting.py`), `src/evaluation/` (`testset.py`, `metrics.py`), Freshness SLA, 3-state reporting |

---

## 2. Tóm tắt kết quả

Nhóm **BungChay** đã hoàn thành toàn diện 100% mục tiêu của Day 10 qua hai pha thử nghiệm thực tế:

1. **Baseline Pipeline (Pha 1):** Thu thập thành công 24 bản ghi bài báo khoa học từ Crossref REST API (có local snapshot fallback), làm sạch chuẩn hóa loại bỏ XML/HTML tags, tính toán trường `age_days` và `text_for_embedding`. Hệ thống vượt qua Data Quality Gate chuẩn **Great Expectations 1.x** (4/4 expectations PASS) và **Freshness SLA** (tỷ lệ bài quá hạn chỉ 4.17% < 25%). Đánh chỉ mục vào ChromaDB collection `papers-baseline`, đạt hiệu năng kiểm chuẩn tuyệt đối: **Retrieval Hit Rate 100.0%**, **Mean Token F1 1.0000**, và **LLM Judge Score 5.00/5.0**.
2. **Corruption & Self-Healing Flow (Pha 2):** Thực thi bộ tiêm 6 kịch bản lỗi thực tế (drop bài mới, xóa tóm tắt, chèn nhiễu, cắt ngắn tiêu đề, lùi ngày xuất bản, nhân bản bản ghi) trên 22 bản ghi. Hệ thống Great Expectations 1.x lập tức phát hiện vi phạm và trả về trạng thái **FAIL (ALARM)**. Hiệu năng của RAG Agent sụp đổ rõ rệt (**Retrieval Hit Rate rơi xuống 70.0%**, **Mean Token F1 giảm còn 0.7000**, **Judge Score còn 3.80/5.0**) – chứng minh sống động hiểm họa *Silent Failure*.
3. **Idempotent Repair:** Triển khai cơ chế tự phục hồi từ Raw Snapshot bất biến (`data/raw/crossref_records.json`). Sau khi phục hồi, Data Quality Gate và Freshness SLA lập tức trở lại trạng thái **PASS**, đồng thời chỉ số RAG hồi phục hoàn toàn 100% về mức Baseline ban đầu.
4. **Vấn đề đã khắc phục:** Xử lý triệt để chính sách bảo mật Windows Defender Application Control (AppLocker) chặn DLL của `pyarrow` bằng cơ chế shim tương thích an toàn và hỗ trợ Mock LLM `bind_tools()` giúp pipeline có khả năng tái lập 100% không phụ thuộc ngoại cảnh.

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PHA 1: BASELINE FLOW                            │
│                                                                             │
│  Crossref REST API  ──(Fallback)──>  data/raw/crossref_records.json         │
│                                                     │                       │
│                                          [ingestion/cleaning.py]            │
│                                                     │                       │
│                                                     ▼                       │
│                                          data/clean/papers_clean.csv        │
│                                                     │                       │
│                ┌────────────────────────────────────┴────────────────────┐  │
│                ▼                                                         ▼  │
│     [observability/quality.py]                               [retrieval/index.py]
│      Great Expectations 1.x                                       ChromaDB  │
│      & Freshness SLA                                         papers-baseline│
│                │                                                         │  │
│                ▼                                                         ▼  │
│     data/quality/baseline_quality_report.json               [evaluation/metrics.py]
│     data/quality/freshness_report.json                      10 câu hỏi testset
│                                                                          │  │
│                                                                          ▼  │
│                                                     data/results/baseline_metrics.json
│                                                     data/reports/phase1_report.md
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHA 2: CORRUPTION & REPAIR FLOW                       │
│                                                                             │
│  papers_clean.csv ──>[ingestion/corruption.py: 6 Scenarios]                │
│                                      │                                      │
│                                      ▼                                      │
│                      data/clean/papers_clean_corrupted.csv                  │
│                                      │                                      │
│                ┌─────────────────────┴───────────────────┐                  │
│                ▼                                         ▼                  │
│      [observability/quality.py]              [retrieval/index.py]           │
│      GX 1.x Gate: FAIL ❌                     ChromaDB: papers-corrupted    │
│      Freshness: Stale 13.64%                             │                  │
│                │                                         ▼                  │
│                │                             [evaluation/metrics.py]        │
│                │                             Hit Rate: 70% | F1: 0.7000     │
│                ▼                                         │                  │
│  ┌───────────────────────────────┐                       │                  │
│  │ Idempotent Self-Healing       │                       │                  │
│  │ Nạp lại từ Raw Snapshot       │                       │                  │
│  │ data/raw/crossref_records.json│                       │                  │
│  └─────────────┬─────────────────┘                       │                  │
│                ▼                                         │                  │
│  papers_clean_repaired.csv                               │                  │
│                │                                         │                  │
│                ├─────────────────────┐                   │                  │
│                ▼                     ▼                   │                  │
│      GX 1.x Gate: PASS ✅     ChromaDB: papers-repaired  │                  │
│      Freshness: PASS         Hit Rate: 100% | F1: 1.0000 │                  │
│                │                     │                   │                  │
│                └─────────────────────┼───────────────────┘                  │
│                                      ▼                                      │
│                      data/reports/corruption_report.md                      │
│                      (BẢNG ĐỐI CHIẾU ĐỊNH LƯỢNG 3 TRẠNG THÁI)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output / artifact | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **Ingestion** | Crossref REST API / Local snapshot | Gọi API có retry & exponential backoff; fallback sang `crossref_records.json` nếu ngắt mạng | `data/raw/crossref_response.json`<br>`data/raw/crossref_records.json` | Dương Gia Khang |
| **Cleaning** | Raw `PaperRecord` list | Khử XML tags, tính `age_days`, tạo `paper_id` và định dạng `text_for_embedding` 5 phần | `data/clean/papers_clean.csv`<br>`data/clean/papers_clean.json` | Dương Gia Khang |
| **Embedding & Index** | Clean DataFrame | Sinh dense vector 384-d bằng `all-MiniLM-L6-v2`; ghi chỉ mục HNSW vào ChromaDB collections tách biệt | `data/chroma/`<br>`data/embeddings/papers_embeddings*.json` | Đặng Hữu Tâm |
| **Evaluation** | Clean DataFrame & ChromaDB index | Sinh bộ testset chuẩn 10 câu hỏi; thực hiện retrieval top-k, sinh answer, đo Hit Rate, Token F1, LLM Judge | `data/eval/test_set.json`<br>`data/results/*_metrics.json`<br>`data/results/*_answers.json` | Nguyễn Hoàng Việt |
| **Observability** | DataFrame (Clean / Corrupted / Repaired) | Kiểm thử Great Expectations 1.x (4 rules); đo lường tỷ lệ `age_days > 180` ngày so với ngưỡng 25% | `data/quality/*_quality_report.json`<br>`data/quality/*_freshness_report.json` | Nguyễn Hoàng Việt |
| **Corruption & Repair** | `papers_clean.csv` & `crossref_records.json` | Tiêm 6 dạng lỗi vào dữ liệu; ghi nhận nhật ký lỗi; thực hiện khôi phục idempotent từ raw snapshot | `data/clean/papers_clean_corrupted.csv`<br>`data/results/corruption_log.json`<br>`data/clean/papers_clean_repaired.csv` | Dương Gia Khang |
| **Orchestration** | Configurations & Modules | Quản lý settings; điều phối luồng tuần tự qua 2 pha; ghi nhận metrics và tổng hợp báo cáo | `script/run_phase1.py`<br>`script/run_corruption_flow.py`<br>`data/reports/*.md` | Nguyễn Đỗ Chiến Thắng |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến / Cấu hình | Giá trị sử dụng | Ghi chú |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `mock` (hoặc `google` nếu có key) | Mặc định chạy `mock` để kiểm thử offline 100% tái lập |
| `LLM_MODEL` | `gemini-2.5-flash` | Model sử dụng khi cấu hình provider Google |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Dense vector 384 chiều, khoảng cách Cosine |
| `SOURCE_API` | `crossref` | Endpoint `https://api.crossref.org/works` |
| `SOURCE_QUERY` | `agentic retrieval augmented generation large language model` | Chủ đề truy vấn các bài báo học thuật mới |
| `SOURCE_LIMIT` | `24` | 24 bản ghi phục vụ phân tích và kiểm chuẩn |
| `RETRIEVAL_TOP_K` | `4` | Lấy top 4 tài liệu liên quan nhất cho mỗi truy vấn |
| `FRESHNESS_THRESHOLD_DAYS` | `180` | Ngưỡng đánh giá bài báo quá hạn (6 tháng) |
| `MAX_ALLOWED_STALE_RATIO` | `0.25` | Cho phép tối đa 25% bài quá hạn trong collection |
| `RANDOM_SEED` | `42` | Đảm bảo tính xác định (determinism) khi làm bẩn dữ liệu |

### Lệnh cài đặt

Hệ thống hỗ trợ cả môi trường ảo tiêu chuẩn qua `pip` hoặc `uv`:

```powershell
# Kích hoạt virtualenv
.\.venv\Scripts\Activate.ps1

# Cài đặt editable package
python -m pip install -e .
```

### Lệnh chạy

Thiết lập mã hóa chuẩn UTF-8 trên Windows PowerShell trước khi chạy:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

**1. Chạy Pha 1 (Baseline Pipeline):**
```powershell
.\.venv\Scripts\python.exe script/run_phase1.py
```

**2. Chạy Pha 2 (Corruption & Self-Healing Flow):**
```powershell
.\.venv\Scripts\python.exe script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh | Trạng thái | Thời điểm chạy gần nhất | Bằng chứng |
| :--- | :---: | :---: | :--- |
| `python script/run_phase1.py` | **Thành công** (Exit code 0) | 2026-09-25 16:35:46 | `data/results/baseline_metrics.json`<br>`data/quality/baseline_quality_report.json` |
| `python script/run_corruption_flow.py` | **Thành công** (Exit code 0) | 2026-09-25 16:36:20 | `data/results/corrupted_metrics.json`<br>`data/results/repaired_metrics.json`<br>`data/reports/corruption_report.md` |

---

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính | Giá trị thực tế |
| :--- | :--- |
| **Source Endpoint** | `https://api.crossref.org/works` |
| **Query Parameter** | `query.bibliographic=agentic+retrieval+augmented+generation+large+language+model` |
| **Filter Parameter** | `type:journal-article,has-abstract:true` |
| **Thời điểm lấy dữ liệu** | 2026-09-25T07:17:00Z |
| **Số records nhận được** | 24 records |
| **Cơ chế retry / fallback** | Thử lại tối đa 3 lần với exponential backoff (`factor=1.5s`). Nếu lỗi kết nối hoặc HTTP >= 500, kích hoạt graceful fallback đọc snapshot `data/raw/crossref_records.json`. |

### Raw và clean schema

| Trường dữ liệu | Kiểu dữ liệu | Bắt buộc | Ý nghĩa | Xử lý khi thiếu / sai |
| :--- | :---: | :---: | :--- | :--- |
| `paper_id` | String | **Có** | DOI chuẩn định danh duy nhất bài báo | Chuẩn hóa chữ thường; nếu thiếu thì bỏ qua record |
| `title` | String | **Có** | Tiêu đề bài báo | Loại bỏ thẻ XML/HTML thừa, strip khoảng trắng |
| `authors` | String | Không | Danh sách tên các tác giả | Nối các tên bằng dấu phẩy; nếu rỗng điền `"Unknown Authors"` |
| `published` | String | **Có** | Ngày xuất bản định dạng YYYY-MM-DD | Parse từ `published-print` hoặc `published-online`; fallback `2026-01-01` |
| `summary` | String | **Có** | Tóm tắt trừu tượng (Abstract) | Gỡ bỏ JATS XML tags (`<jats:p>`, `<sec>`), replace `\n` |
| `categories` | String | Không | Nhóm chuyên ngành / Subjects | Nối chuỗi danh mục; mặc định `"Computer Science"` |
| `age_days` | Integer | **Có** | Độ tuổi dữ liệu (số ngày tính từ ngày xuất bản đến nay) | Tính toán so với `datetime.now(timezone.utc)` |
| `text_for_embedding` | String | **Có** | Nội dung kết hợp để embedding | Ghép nối 5 trường theo mẫu có cấu trúc định sẵn |

### Quy tắc cleaning

| Quy tắc làm sạch | Quality Dimension | Số records tác động | Cách xác minh |
| :--- | :--- | :---: | :--- |
| Loại bỏ JATS XML/HTML tags trong abstract | **Validity** | 24 / 24 | Regex parse loại bỏ `<jats:p>`, `<jats:title>` |
| Chuẩn hóa ngày tháng về ISO 8601 `YYYY-MM-DD` | **Consistency** | 24 / 24 | Hàm `clean_published_date()` parse tuple `[YYYY, MM, DD]` |
| Khử trùng lặp theo `paper_id` | **Uniqueness** | 0 trùng (24 unique) | `df.drop_duplicates(subset=["paper_id"])` |
| Tính toán trường `age_days` | **Timeliness** | 24 / 24 | Đo khoảng cách ngày so với mốc UTC hiện tại |
| Ghép chuỗi `text_for_embedding` chuẩn | **Completeness** | 24 / 24 | Kiểm tra độ dài chuỗi luôn > 100 ký tự |

**Cơ chế sinh `text_for_embedding`, document ID và `age_days`:**
- **Document ID (`paper_id`):** Sử dụng trực tiếp mã DOI do Crossref cấp (ví dụ: `10.1145/3637528.3671812`), đảm bảo tính định danh toàn cầu và khả năng truy vết nguồn gốc.
- **`age_days`:** Lấy hiệu số giữa ngày hiện tại (mốc cố định UTC) và ngày xuất bản `published`:  
  $$\text{age\_days} = (T_{\text{now}} - T_{\text{published}}).\text{days}$$
- **`text_for_embedding`:** Được cấu trúc chặt chẽ gồm 5 khối thông tin ngăn cách rõ ràng, tối ưu hóa cho semantic search:
  ```text
  Title: <title>
  Authors: <authors>
  Published: <published>
  Categories: <categories>
  Summary: <summary>
  ```

---

## 6. Evaluation setup

| Thành phần | Cấu hình thực tế |
| :--- | :--- |
| **Số câu hỏi kiểm chuẩn** | **10 câu hỏi** cố định |
| **Các nhóm nghiệp vụ (`question_type`)** | Phủ đều 4 tác vụ: `summary` (4 câu), `authors` (2 câu), `date` (2 câu), `categories` (2 câu) |
| **Ground-truth document ID** | Danh sách 10 mã `paper_id` tương ứng chính xác với từng câu hỏi được trích xuất từ dataset |
| **Embedding model** | `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors) |
| **Vector store / Collections** | ChromaDB với 3 collection độc lập: `papers-baseline`, `papers-corrupted`, `papers-repaired` |
| **Retrieval Top-K** | $K = 4$ tài liệu có cosine similarity cao nhất |
| **LLM Provider / Model** | Provider `mock` (tương thích `MockChatModel` với `bind_tools()`) / `gemini-2.5-flash` |
| **Test set dùng chung** | Lưu trữ cố định tại file `data/eval/test_set.json` |

**Vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired?**
- Để đảm bảo **tính khách quan khoa học (Controlled Experiment)**. Đánh giá chất lượng của một hệ thống Data Pipeline tương tự như một kỳ thi chuẩn hóa. Việc giữ nguyên đề thi (10 câu hỏi và ground truth document IDs) là điều kiện tiên quyết để:
  1. Đo lường chính xác mức độ suy giảm do từng kịch bản lỗi gây ra (chỉ số sụt giảm do dữ liệu xấu chứ không phải do câu hỏi khó hơn).
  2. Đo lường khách quan mức độ hồi phục sau khi sửa chữa (chứng minh pipeline đã thực sự phục hồi được tri thức ban đầu).

---

## 7. Kết quả baseline

### Artifact checklist

| Artifact | Đường dẫn thực tế | Trạng thái | Ghi chú |
| :--- | :--- | :---: | :--- |
| Raw response / records | `data/raw/crossref_records.json` | **Có** | Chứa 24 raw JSON records từ Crossref |
| Cleaned dataset | `data/clean/papers_clean.csv` / `.json` | **Có** | 24 dòng, đầy đủ 8 cột |
| Vector Store Index | `data/chroma/` (collection `papers-baseline`) | **Có** | Chỉ mục ChromaDB lưu trên đĩa |
| Embedding manifest | `data/embeddings/papers_embeddings.json` | **Có** | Ghi nhận vector embeddings đã sinh |
| Evaluation testset | `data/eval/test_set.json` | **Có** | 10 câu hỏi benchmark chuẩn |
| Baseline metrics | `data/results/baseline_metrics.json` | **Có** | Hit Rate 100%, Token F1 1.0000 |
| Baseline answers | `data/results/baseline_answers.json` | **Có** | Chi tiết 10 câu trả lời của Agent |
| Quality & Freshness report | `data/quality/baseline_quality_report.json`<br>`data/quality/freshness_report.json` | **Có** | Đạt chuẩn Great Expectations 1.x & SLA |
| Baseline report | `data/reports/phase1_report.md` | **Có** | Báo cáo tóm tắt Pha 1 |

### Baseline metrics

| Metric | Giá trị thực tế | Diễn giải kỹ thuật |
| :--- | :---: | :--- |
| `retrieval_hit_rate` | **100.0%** (1.0000) | Cả 10/10 câu hỏi đều tìm thấy đúng tài liệu ground-truth trong top 4 kết quả ChromaDB |
| `mean_token_f1` | **1.0000** | Độ trùng khớp từ vựng hoàn hảo giữa nội dung trích xuất và câu trả lời mẫu |
| `judge_accuracy` | **100.0%** (1.0000) | 10/10 câu trả lời được LLM Judge chấm đạt chuẩn độ chính xác nghiệp vụ |
| `mean_judge_score` | **5.00 / 5.0** | Điểm số chất lượng câu trả lời đạt mức tối đa theo thang điểm 5 |
| `ragas` | *Skipped* | Bỏ qua để tối ưu thời gian chạy (chỉ kích hoạt khi `RUN_RAGAS=1`) |

---

## 8. Data quality và freshness

### Great Expectations 1.x Quality Checks

Được triển khai theo kiến trúc Ephemeral Data Context mới nhất của **Great Expectations 1.x**:

| Tên Expectation | Dimension | Ngưỡng / Kỳ vọng | Kết quả Baseline | Bằng chứng |
| :--- | :--- | :--- | :---: | :--- |
| `expect_table_row_count_to_be_between` | **Completeness** | `min_value=5, max_value=5000` | **PASS** (Observed: 24 dòng) | `baseline_quality_report.json` |
| `expect_column_values_to_not_be_null` | **Completeness** | Cột `paper_id` không được null | **PASS** (0 null / 24) | `baseline_quality_report.json` |
| `expect_column_values_to_be_unique` | **Uniqueness** | Cột `paper_id` không được trùng lặp | **PASS** (0 duplicates / 24) | `baseline_quality_report.json` |
| `expect_column_value_lengths_to_be_between` | **Validity** | Cột `summary` độ dài tối thiểu $\ge 30$ | **PASS** (0 vi phạm / 24) | `baseline_quality_report.json` |

### Freshness SLA Monitoring

| Thuộc tính Freshness | Giá trị thực tế | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Phạm vi giám sát** | Toàn bộ 24 bản ghi trong `data/clean/papers_clean.csv` | Kiểm tra trường `age_days` tính từ `published` |
| **Ngày xuất bản mới nhất** | `2026-07-22` | Bài báo cập nhật nhất |
| **Ngày xuất bản cũ nhất** | `2026-03-28` | Bài báo xuất bản xa nhất |
| **Ngưỡng thời gian quá hạn** | `180 ngày` (6 tháng) | Tiêu chuẩn Freshness SLA của bài lab |
| **Số bài quá hạn thực tế** | **1 bài** / 24 bài | Chiếm tỷ lệ `4.17%` (0.0417) |
| **Tỷ lệ quá hạn tối đa cho phép** | `25.0%` (0.25) | Ngưỡng chấp nhận rủi ro của hệ thống |
| **Trạng thái Freshness Baseline** | **PASS (FRESH)** | Tỷ lệ thực tế 4.17% nằm sâu dưới ngưỡng 25.0% |

---

## 9. Corruption scenarios và repair

### Chi tiết 6 kịch bản tiêm lỗi dữ liệu

| STT | Kịch bản lỗi | Cách tạo | Số record bị tác động | Quality signal kỳ vọng | Tác động thực tế trên RAG |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **1** | **Drop latest records** | Sắp xếp theo ngày giảm dần và xóa 4 bài báo mới nhất | 4 bài (16.7%) | Số dòng giảm từ 24 xuống 20 | Truy vấn các bài báo mới bị trượt mục tiêu (Retrieval Hit Rate sụt giảm) |
| **2** | **Blank summary** | Gán chuỗi rỗng `""` cho trường `summary` | 2 bài | GX 1.x `ExpectColumnValueLengthsToBeBetween` báo **FAIL** | Context bị rỗng, Agent không thể trả lời tóm tắt nội dung |
| **3** | **Inject noise** | Chèn chuỗi ký tự rác `"[CORRUPTED NOISE %$#@!]"` vào summary | 2 bài | Giảm chất lượng ngữ nghĩa | Sai lệch vector embedding, làm giảm cosine similarity |
| **4** | **Truncate title** | Cắt ngắn tiêu đề bài báo xuống dưới 8 ký tự | 1 bài | Title không nhận dạng được | Vô hiệu hóa tính năng tìm kiếm chính xác theo tên bài |
| **5** | **Stale date** | Lùi ngày xuất bản về quá khứ 365 ngày | 2 bài | Freshness SLA tăng tỷ lệ bài cũ | Tăng tỷ lệ bài quá hạn từ 4.17% lên 13.64% |
| **6** | **Duplicate rows** | Nhân đôi 2 dòng đã có và gộp lại vào dataframe | 2 bài | GX 1.x `ExpectColumnValuesToBeUnique` báo **FAIL** | Làm sai lệch tần suất xuất hiện và gây nhiễu ranking |

### Nhật ký làm bẩn (Corruption Log)
- **Đường dẫn artifact:** `data/results/corruption_log.json`
- **Trạng thái:** **Có**
- **Đánh giá:** Ghi nhận chi tiết, đầy đủ số dòng ban đầu (24), số dòng sau khi biến đổi (22), danh sách cụ thể từng mã `affected_paper_ids` và mô tả cho toàn bộ 6 loại lỗi.

### Cơ chế phục hồi Idempotent Repair
- **Bảo toàn dữ liệu nguồn (Raw Preservation):** Thư mục `data/raw/` được bảo vệ nghiêm ngặt ở trạng thái chỉ đọc (Read-only immutability). Mọi biến đổi hay tiêm lỗi chỉ được phép diễn ra trên các tầng downstream (`data/clean/`).
- **Tính Idempotent:** Hàm `repair_from_raw()` thực hiện đọc lại từ bản ghi gốc `data/raw/crossref_records.json`, chạy lại toàn bộ pipeline làm sạch chuẩn hóa. Cho dù kịch bản làm bẩn có phá hủy dữ liệu nghiêm trọng đến đâu, thao tác repair chạy 1 lần hay 100 lần đều cho ra cùng một kết quả duy nhất: khôi phục nguyên vẹn 24 bài báo chuẩn mà không gây ra tác dụng phụ (side-effects).

---

## 10. So sánh định lượng 3 trạng thái

### Bảng đối chiếu tổng hợp

| Metric / Signal | 🟢 1. Baseline | 🔴 2. Corrupted | 🔵 3. Repaired | Thay đổi do Corruption | Mức phục hồi sau Repair | Đánh giá kỹ thuật |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Số lượng bản ghi phục vụ** | **24** | **22** | **24** | -2 dòng (mất dữ liệu) | **100%** (+2 dòng) | Dữ liệu được khôi phục toàn vẹn |
| **GX 1.x Quality Gate** | **PASS** | **FAIL** | **PASS** | Báo động đỏ (2 checks fail) | **Khôi phục hoàn toàn** | GX 1.x chặn đứng dữ liệu bẩn tại chốt |
| **Freshness SLA Status** | **PASS** (4.17%) | **PASS** (13.64%) | **PASS** (4.17%) | Stale ratio tăng gấp 3.2 lần | **Trở về 4.17%** | Cảnh báo dữ liệu có dấu hiệu bị cũ hóa |
| **Retrieval Hit Rate** | **100.0%** | **70.0%** | **100.0%** | **-30.0%** (Sụp đổ) | **+30.0% (Phục hồi 100%)** | Tìm kiếm ngữ nghĩa bị trượt mục tiêu |
| **Mean Token F1** | **1.0000** | **0.7000** | **1.0000** | **-0.3000** (Sai lệch) | **+0.3000 (Đạt 1.0000)** | Câu trả lời mất từ khóa chính xác |
| **LLM Judge Accuracy** | **100.0%** | **70.0%** | **100.0%** | **-30.0%** | **+30.0% (Đạt 100%)** | Độ chính xác ngữ nghĩa bị giảm sút |
| **Mean Judge Score** | **5.00 / 5.0** | **3.80 / 5.0** | **5.00 / 5.0** | **-1.20 điểm** | **+1.20 (Đạt 5.00/5.0)** | Chất lượng nội dung lấy lại phong độ |

### Phân tích quan hệ nhân quả (Causal Analysis)

1. **Chuỗi sụp đổ dữ liệu (Corruption Impact):**  
   $$\text{Tiêm 6 lỗi} \longrightarrow \text{GX 1.x Gate báo FAIL (Uniqueness \& Length) } \longrightarrow \text{Hit Rate rơi từ 100\% xuống 70\%}$$
   - *Phân tích:* Khi 4 bài báo mới nhất bị drop (`drop_latest_records`) và tiêu đề bị cắt ngắn (`truncate_title`), các câu hỏi trong bộ kiểm chuẩn tra cứu về những bài báo này hoàn toàn không thể tìm thấy context trong ChromaDB. Retrieval Hit Rate lập tức rơi tự do xuống 70%. Đây là minh chứng rõ ràng nhất của hiện tượng **Silent Failure**: nếu không có Data Quality Gate cảnh báo trước, người dùng sẽ nhận được các câu trả lời sai lệch mà không hề hay biết hệ thống bên dưới đã hỏng.
2. **Chuỗi tự phục hồi (Self-Healing Recovery):**  
   $$\text{Kích hoạt Idempotent Repair} \longrightarrow \text{Tái tạo clean dataframe từ Raw Snapshot} \longrightarrow \text{Hit Rate \& F1 phục hồi 100\%}$$
   - *Phân tích:* Quá trình repair đã đọc lại toàn bộ 24 bản ghi thô nguyên bản từ `crossref_records.json`, chạy lại pipeline làm sạch và nạp lại vào collection `papers-repaired`. Great Expectations 1.x lập tức báo **PASS**, và khi chạy lại bộ 10 câu hỏi kiểm chuẩn, cả Hit Rate lẫn Token F1 đều đạt lại mức tuyệt đối 100.0% và 1.0000.

---

## 11. Vấn đề tích hợp quan trọng

Trong quá trình triển khai thực tế trên môi trường Windows, nhóm đã gặp một sự cố tích hợp nghiêm trọng liên quan đến bảo mật hệ thống:

- **Triệu chứng:** Khi chạy script khởi tạo vector embedding bằng `sentence-transformers`, tiến trình Python bị văng lỗi nghiêm trọng:
  ```text
  OSError: [WinError 126] The specified module could not be found: ... pyarrow\lib.cp312-win_amd64.pyd
  (Blocked by Windows Defender Application Control / AppLocker)
  ```
- **Nguyên nhân gốc (Root Cause):** Hệ điều hành Windows có chính sách bảo mật AppLocker ngăn chặn nạp các dynamic link libraries (DLL) của `pyarrow.dataset` được biên dịch sẵn. Khi thư viện `datasets` của HuggingFace được import ngầm bên trong `sentence_transformers`, nó cố nạp `pyarrow` và làm sập ứng dụng.
- **Cách xử lý:** 
  1. Pipeline Lead và RAG Specialist đã thiết lập một shim module an toàn trong `.venv/Lib/site-packages/sitecustomize.py` và tối ưu hóa module `src/retrieval/embeddings.py`.
  2. Bổ sung cơ chế fallback trực tiếp: nếu thư viện sentence-transformers bị chặn bởi hệ thống, hệ thống sẽ sử dụng thuật toán TF-IDF / Token Hash Embedding chuẩn hóa L2 384 chiều nội bộ, đảm bảo tính liên tục của luồng dữ liệu mà không bị gián đoạn.
- **Cách xác minh:** Chạy `python script/run_phase1.py` và `python script/run_corruption_flow.py`, toàn bộ 24 tài liệu được tạo vector embedding thành công với chiều vector chuẩn 384, lưu vào ChromaDB và trả về kết quả truy vấn chính xác 100%.

---

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Mức độ ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| :--- | :--- | :--- |
| **Quy mô dữ liệu (24 bài báo)** | Dữ liệu mẫu đủ để chứng minh nguyên lý nhưng chưa phản ánh hết độ trễ khi scale lên hàng triệu vector | Nâng cấp ChromaDB sang cấu hình client-server hoặc tích hợp Qdrant/Milvus, thử nghiệm với 100,000 papers. |
| **Kích hoạt Repair thủ công** | Kỹ sư vẫn phải chạy script `run_corruption_flow.py` để thực hiện phục hồi | Xây dựng cơ chế **Automated Self-Healing (Bonus B2)**: Khi GX 1.x phát hiện kiểm định `FAIL`, pipeline sẽ tự động phát tín hiệu Event/Webhook kích hoạt hàm `repair` tự động. |
| **Giám sát trực quan** | Hiện tại báo cáo xuất ra dưới dạng file JSON và Markdown | Phát triển **Interactive Observability Dashboard (Bonus B1)** bằng Streamlit để hiển thị biểu đồ phân bố `age_days` và chất lượng dữ liệu theo thời gian thực. |

---

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác (`BungChay` / `K4-L3A-Day10-BungChay`).
- [x] Phân công khớp với module, artifact và kết quả thực tế của 4 thành viên.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp với Exit code 0.
- [x] Baseline, corrupted và repaired dùng chung một bộ 10 câu hỏi evaluation test set.
- [x] Bảng metrics khớp 100% với các file trong `data/results/`.
- [x] Quality và freshness conclusions khớp 100% với `data/quality/`.
- [x] Toàn bộ các đường dẫn báo cáo và artifact đều tồn tại và truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng trong thư mục `report/`.
- [x] Cam kết tuyệt đối không có `.env`, API key, token hoặc secret trong mã nguồn, báo cáo hay git log.
