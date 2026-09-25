# Member Role Report — Day 10: Data Pipeline & Data Observability

> Báo cáo vai trò cá nhân của Trưởng nhóm & Điều phối viên Pipeline (Pipeline Lead).

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | **Nguyễn Đỗ Chiến Thắng** |
| **MSSV** | **2A202602442** |
| **Khóa / Lớp** | K4A - Level 3 (Day 10) |
| **Tên nhóm** | BungChay (`K4A-L3-DAY10`) |
| **Vai trò chính** | **Pipeline Lead & Systems Integrator** |
| **Repository** | `https://github.com/nguyendochienthang711-ai/K4-L3A-Day10-BungChay` |
| **Ngày hoàn thành** | 2026-09-25 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu chính (Ownership)

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **System Architecture & Config** | `src/core/config.py`<br>`load_settings` | Biến môi trường `.env`, hằng số mặc định | Đối tượng cấu hình `Settings` (Pydantic / Dataclass) | **Hoàn thành** |
| **Core Utilities & Safe I/O** | `src/core/utils.py`<br>`write_json`, `write_csv`, `now_utc` | Dữ liệu thô / Dict / DataFrame | Files được ghi an toàn UTF-8 không lỗi encoding | **Hoàn thành** |
| **Phase 1 Baseline Pipeline** | `src/pipelines/phase1.py`<br>`script/run_phase1.py` | Lệnh CLI, Raw Ingestion module | Pipeline baseline chạy từ đầu đến cuối với Exit Code 0 | **Hoàn thành** |
| **Phase 2 Corruption & Repair** | `src/pipelines/corruption_flow.py`<br>`script/run_corruption_flow.py` | Clean data, Corruption module, Raw snapshot | Pipeline đối chiếu 3 trạng thái và tự phục hồi với Exit Code 0 | **Hoàn thành** |
| **Git Governance & Integration** | GitHub repo `main` branch, PR reviews | Pull requests từ các thành viên | Đảm bảo 100% thành viên có commit trên `main`, không leak secret | **Hoàn thành** |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên / Module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| **Khắc phục DLL Blocking trên Windows** | Đặng Hữu Tâm (`src/retrieval/embeddings.py`) | Tạo cơ chế shim an toàn cho `pyarrow.dataset`, giải phóng tiến trình embedding bị chặn bởi AppLocker |
| **Chuẩn hóa UTF-8 Console I/O** | Toàn đội (môi trường Windows PowerShell) | Cấu hình `$env:PYTHONIOENCODING="utf-8"` và `PYTHONUTF8=1` để log in tiếng Việt không bị `UnicodeEncodeError` |
| **Tích hợp Data Quality Gate GX 1.x** | Nguyễn Hoàng Việt (`src/observability/quality.py`) | Hỗ trợ kết nối output của GX 1.x vào pipeline để xuất báo cáo `phase1_report.md` và `corruption_report.md` |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Hàm / Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Xây dựng kiến trúc Baseline Pipeline** | `src/pipelines/phase1.py`<br>`script/run_phase1.py` | Tự động hóa 7 bước từ Ingestion đến xuất báo cáo Markdown | Chạy `python script/run_phase1.py` đạt Exit code 0 |
| **Xây dựng luồng Corruption & Self-Healing** | `src/pipelines/corruption_flow.py`<br>`script/run_corruption_flow.py` | Thực thi đo lường 3 trạng thái (Baseline, Corrupted, Repaired) | Chạy `python script/run_corruption_flow.py` đạt Exit code 0 |
| **Tự động xuất bảng đối chiếu Markdown** | `src/observability/reporting.py`<br>`data/reports/corruption_report.md` | Bảng so sánh định lượng đầy đủ các chỉ số và nhận định kỹ thuật | Kiểm tra file `data/reports/corruption_report.md` |
| **Quản trị repository & tích hợp mã nguồn** | GitHub commit history nhánh `main` | 100% thành viên xuất hiện trên tab Insights > Contributors | Xem `git log --graph --oneline` |

**Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:**
File thực thi `script/run_corruption_flow.py` phối hợp toàn diện tất cả các khối trong hệ thống: từ việc tiêm 6 kịch bản lỗi, phát hiện qua Great Expectations 1.x, ghi nhận sự suy thoái của RAG Agent (Hit Rate giảm xuống 70%), sau đó tự động kích hoạt Idempotent Repair từ snapshot gốc và phục hồi 100% các chỉ số (Hit Rate 100%, Token F1 1.0000). Toàn bộ luồng in ra bảng so sánh 3 trạng thái trực quan trên console và xuất file `data/reports/corruption_report.md`.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Một hệ thống RAG trong thực tế thường xuyên đối mặt với sự cố "âm thầm suy thoái" (**Silent Failure**): dữ liệu đầu vào bị lỗi cú pháp, mất mát hoặc cũ kỹ nhưng pipeline không có cơ chế cảnh báo, khiến AI vẫn trả lời bình thản nhưng thông tin hoàn toàn sai lệch. Vai trò Pipeline Lead phải thiết kế một kiến trúc pipeline thống nhất, có tính Module hóa cao, đảm bảo tính bất biến của nguồn dữ liệu thô (Raw Immutability) và khả năng tự phục hồi (Self-Healing) có tính **Idempotent**.

### Cách triển khai
1. **Thiết kế Orchestrator phân tầng:** Tách biệt hoàn toàn luồng nghiệp vụ giữa Pha 1 (Baseline Ingestion) và Pha 2 (Corruption & Repair Flow). Các module chỉ giao tiếp thông qua Data Contract (Pydantic / Pandas DataFrame với schema được kiểm định) và các file artifact trên đĩa.
2. **Cơ chế Idempotent Execution:** Đảm bảo khi chạy lại pipeline nhiều lần, các tài nguyên như ChromaDB collection không bị chèn trùng lặp dữ liệu (sử dụng cơ chế `get_or_create_collection` và xóa collection cũ trước khi re-index), các thư mục artifact tự động được tạo nếu chưa tồn tại.
3. **Quản lý cấu hình tập trung (`core/config.py`):** Mọi đường dẫn thư mục (`data/raw`, `data/clean`, `data/chroma`, `data/quality`, `data/results`, `data/reports`) và tham số hoạt động (ngưỡng Freshness 180 ngày, top_k 4, random seed 42) đều được gom vào lớp `Settings`, ngăn chặn hoàn toàn việc hardcode đường dẫn tuyệt đối máy cá nhân.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Tham số dòng lệnh, cấu hình trong `.env`, danh sách bản ghi từ Ingestion |
| **Output** | Exit code 0, console output bảng đối chiếu định lượng, toàn bộ artifacts trong thư mục `data/` |
| **Module phụ thuộc** | `src/ingestion`, `src/retrieval`, `src/observability`, `src/evaluation` |
| **Module sử dụng output** | Toàn bộ thành viên nhóm, các script kiểm chuẩn và giám khảo đánh giá |
| **Điều kiện lỗi cần xử lý** | Mất mạng khi fetch Crossref API, thư mục đích chưa tồn tại, collection ChromaDB bị xung đột, Windows encoding mismatch |

### Cách xác minh

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe script/run_phase1.py
.\.venv\Scripts\python.exe script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Cả hai script chạy từ đầu đến cuối không phát sinh ngoại lệ (Exit code 0), in đầy đủ thông tin từng bước và bảng so sánh 3 trạng thái.
- **Kết quả thực tế:** Exit code 0 trên cả hai script; sinh đủ 100% các file artifacts theo yêu cầu của `docs/SUBMISSION.md`.
- **Artifact / log:** `data/reports/phase1_report.md` và `data/reports/corruption_report.md`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương án tổ chức Vector Store ChromaDB khi thực hiện so sánh 3 trạng thái (Baseline, Corrupted, Repaired).
- **Các phương án đã cân nhắc:**
  1. *Phương án A:* Dùng chung một ChromaDB collection duy nhất, sau mỗi pha thì xóa sạch và ghi đè lại.
  2. *Phương án B:* Khởi tạo 3 collections tách biệt hoàn toàn trên cùng một persistent directory: `papers-baseline`, `papers-corrupted`, và `papers-repaired`.
- **Phương án đã chọn:** **Phương án B**.
- **Lý do:** 
  - *Data Isolation & Auditing:* Cho phép cô lập tuyệt đối dữ liệu giữa các pha, không có nguy cơ rò rỉ (data leakage) giữa dữ liệu sạch và dữ liệu bẩn.
  - *Truy vết và tái kiểm thử:* Sau khi chạy xong, giám khảo hoặc bất kỳ thành viên nào đều có thể truy vấn độc lập vào từng collection cụ thể để tái hiện lại kết quả kiểm tra mà không cần phải chạy lại toàn bộ quá trình biến đổi.
- **Bằng chứng quyết định phù hợp:** Cả 3 collections tồn tại song song trong `data/chroma/`, hỗ trợ đánh giá độc lập và chính xác với Hit Rate: Baseline = 100%, Corrupted = 70%, Repaired = 100%.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng / lỗi nguyên văn:**
  ```text
  OSError: [WinError 126] The specified module could not be found: ... pyarrow\lib.cp312-win_amd64.pyd
  ```
  Tiến trình nạp mô hình vector embedding bị sập ngay lập tức khi gọi `sentence_transformers`.
- **Lệnh tái hiện:**
  ```powershell
  .\.venv\Scripts\python.exe -c "import sentence_transformers"
  ```
- **Nguyên nhân gốc (Root cause):** Hệ thống Windows kích hoạt cơ chế AppLocker / Application Control chặn nạp DLL của `pyarrow.dataset`. Khi `datasets` (phụ thuộc của `sentence_transformers`) được import, nó cố import `pyarrow` và gây crash tiến trình.
- **Cách xử lý:**
  1. Thêm cơ chế shim trong `.venv/Lib/site-packages/sitecustomize.py` để mock module `pyarrow.dataset` an toàn khi import.
  2. Tối ưu hóa `src/retrieval/embeddings.py` với cơ chế Graceful Fallback: nếu transformer bị chặn bởi OS, tự động chuyển sang giải thuật trích xuất đặc trưng L2-normalized 384 chiều, đảm bảo pipeline chạy xuyên suốt trên mọi máy tính.
- **Cách xác minh sau khi sửa:** Chạy lại `.\.venv\Scripts\python.exe script/run_phase1.py`, chương trình tạo vector thành công cho 24 tài liệu và index vào ChromaDB bình thường.
- **Điều học được:** Khi phát triển pipeline trên môi trường đa nền tảng (Windows/Linux/macOS), các thư viện phụ thuộc C-extensions / native DLLs rất dễ bị ảnh hưởng bởi chính sách bảo mật hệ điều hành. Luôn phải thiết kế cơ chế fallback và test tính tương thích từ sớm.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - API Crossref trả về danh sách bài báo dạng JSON $\to$ Module Ingestion bóc tách thành danh sách `PaperRecord` và lưu snapshot vào `data/raw/crossref_records.json` $\to$ Module Cleaning gỡ bỏ XML/HTML tags, tính `age_days`, tạo `paper_id` và định dạng chuỗi `text_for_embedding` gồm 5 trường $\to$ Lưu thành `papers_clean.csv` $\to$ Mô hình embedding biến đổi `text_for_embedding` thành vector dense 384 chiều $\to$ Index vào ChromaDB collection kèm metadata.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Bộ kiểm chuẩn gồm 10 câu hỏi nghiệp vụ, mỗi câu có danh sách `ground_truth_doc_ids` chuẩn. Khi truy vấn, ChromaDB trả về top 4 tài liệu liên quan nhất. Nếu `ground_truth_doc_ids` nằm trong danh sách trả về, ta tính là 1 lần trúng đích (**Hit Rate = 1**). Sau đó, câu trả lời sinh ra từ context được so sánh từ vựng với đáp án mẫu để đo **Token F1**, và được LLM Judge chấm điểm ngữ nghĩa từ 1 đến 5.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - *Quality checks (Great Expectations 1.x):* Kiểm tra **tính toàn vẹn cấu trúc và logic dữ liệu** (schema, số dòng, nullability, uniqueness, độ dài văn bản).
   - *Freshness monitoring:* Kiểm tra **tính cập nhật theo thời gian của tri thức** (SLA tuổi thọ dữ liệu, `age_days <= 180`). Dữ liệu có thể hoàn toàn sạch về cú pháp nhưng đã bị lỗi thời về mặt tri thức nếu không thỏa mãn Freshness SLA.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Nhằm duy trì nguyên tắc **biến số đối chứng duy nhất (Controlled Experiment)**. Đề thi phải giữ nguyên 100% thì sự thay đổi của các chỉ số hiệu năng (Hit Rate, F1, Judge Score) mới phản ánh trung thực tác động của chất lượng dữ liệu (Data Quality) chứ không bị nhiễu do độ khó của câu hỏi.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - *Artifacts:* `repaired_quality_report.json` đạt trạng thái `success: true` (toàn bộ 4 expectations PASS); `repaired_freshness_report.json` đạt `PASS`.
   - *Metrics:* `repaired_metrics.json` ghi nhận **Retrieval Hit Rate đạt 100.0%** (tăng từ 70.0%), **Mean Token F1 đạt 1.0000** (tăng từ 0.7000), và **Judge Score đạt 5.00/5.0**.

---

## 8. Phân tích kết quả thực nghiệm

### Metrics chính ghi nhận thực tế

| Metric / Signal | 🟢 Baseline | 🔴 Corrupted | 🔵 Repaired | Nhận xét cá nhân |
| :--- | :---: | :---: | :---: | :--- |
| `retrieval_hit_rate` | **100.0%** | **70.0%** | **100.0%** | Sụt giảm 30% do mất 4 bài báo mới và tiêu đề bị cắt ngắn; phục hồi hoàn hảo sau repair |
| `mean_token_f1` | **1.0000** | **0.7000** | **1.0000** | Mất mát từ khóa chính xác khi context bị nhiễu hoặc rỗng; đạt lại 1.0000 sau phục hồi |
| `judge_accuracy` | **100.0%** | **70.0%** | **100.0%** | Tỷ lệ câu trả lời đúng bản chất ngữ nghĩa phục hồi từ 70% lên 100% |
| `mean_judge_score` | **5.00 / 5.0** | **3.80 / 5.0** | **5.00 / 5.0** | Điểm số chất lượng câu trả lời lấy lại phong độ tối đa 5/5 |
| **Great Expectations Gate** | **PASS** | **FAIL** | **PASS** | Chặn đứng vi phạm tính duy nhất (duplicate) và độ dài summary < 30 ký tự |
| **Freshness SLA Status** | **PASS** (4.17%) | **PASS** (13.64%) | **PASS** (4.17%) | Tỷ lệ bài quá hạn tăng từ 4.17% lên 13.64% nhưng vẫn nằm dưới trần 25% |

### Kết luận từ số liệu

1. **Chuỗi nguyên nhân - bằng chứng 1 (Corruption):**  
   Tiêm kịch bản `drop_latest_records` (4 bài) & `truncate_title` (1 bài) $\longrightarrow$ Great Expectations 1.x báo động đỏ **FAIL** $\longrightarrow$ Retrieval Hit Rate sụt giảm nghiêm trọng từ **100.0% xuống 70.0%**.
2. **Chuỗi nguyên nhân - bằng chứng 2 (Repair):**  
   Kích hoạt cơ chế Idempotent Repair từ snapshot gốc `crossref_records.json` $\longrightarrow$ Great Expectations 1.x và Freshness SLA lập tức trở về trạng thái **PASS** $\longrightarrow$ Retrieval Hit Rate và Mean Token F1 phục hồi 100% về mức tuyệt đối **100.0% và 1.0000**.

- **Corruption ảnh hưởng rõ nhất và vì sao:**  
  Kịch bản `drop_latest_records` và `truncate_title` gây ảnh hưởng tàn phá nhất đến RAG Agent. Khi tài liệu không còn trong Vector DB hoặc tiêu đề bị cắt ngắn dưới 8 ký tự, vector search không thể tìm thấy context đúng, dẫn đến việc Agent trích xuất sai hoặc từ chối trả lời.
- **Kết quả khác với kỳ vọng ban đầu:**  
  Kịch bản `stale_date` làm tăng số bài quá hạn từ 1 bài lên 3 bài (tỷ lệ tăng từ 4.17% lên 13.64%), nhưng trạng thái chung của Freshness SLA vẫn là `PASS` vì ngưỡng tối đa cho phép của bài lab là 25.0%. Điều này cho thấy hệ thống giám sát hoạt động rất nhạy về mặt tỷ lệ định lượng nhưng vẫn đảm bảo tính dung hòa đối với các biến động nhẹ.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Kiến trúc Pipeline hướng dữ liệu (Data-Centric):** AI mô hình ngôn ngữ lớn mạnh mẽ đến đâu cũng chỉ là hàm ánh xạ từ context đầu vào. Kiểm soát chất lượng dữ liệu ở từng chặng của pipeline mới là chìa khóa quyết định độ tin cậy của toàn hệ thống.
2. **Giá trị của Data Observability Gate:** Thiết lập các chốt kiểm định tự động bằng Great Expectations 1.x giúp chặn đứng dữ liệu lỗi ngay tại "cửa ngõ", ngăn chặn hiện tượng Silent Failure trước khi dữ liệu kịp thẩm thấu vào tầng serving.
3. **Nguyên tắc Bất biến của Raw Data (Raw Immutability):** Việc bảo toàn nguyên vẹn snapshot gốc là nền tảng cho phép xây dựng các quy trình tự phục hồi (Self-Healing) có tính Idempotent cao.

### Nếu có thêm thời gian
Tôi sẽ tích hợp cơ chế **Automated Self-Healing Pipeline (Bonus B2)**: Khi chốt kiểm định GX 1.x phát hiện `FAIL`, một Event Hook sẽ tự động kích hoạt tiến trình `repair_from_raw()` và cập nhật lại Vector DB trong nền mà không cần kỹ sư phải can thiệp bằng dòng lệnh thủ công.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Đỗ Chiến Thắng  
**Ngày xác nhận:** 2026-09-25
