# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** BungChay
- **Mã Nhóm / Lớp:** `K4A-L3-DAY10`
- **Tên Repository Nộp Bài:** K4-L3A-Day10-BungChay

---

## # Thành viên

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | Nguyễn Đỗ Chiến Thắng | 2A202602442 | nguyendochienthang711@gmail.com | Trưởng nhóm / Pipeline Lead (`core/`, `phase1.py`, `corruption_flow.py`) | `report/2A202602442_NguyenDoChienThang.md` |
| 2 | Dương Đạt Khang | 2A202602624 | khangnguyhiemlslsls@gmail.com | Data Foundation Owner (`crossref.py`, `cleaning.py`, raw data & idempotent repair) | `report/2A202602624_DuongDatKhang.md` |
| 3 | Đặng Hữu Tâm | 2A202602940 | danghuutam@gmail.com | RAG Specialist (`retrieval/index.py`, `embeddings.py`, ChromaDB 3 collections) | `report/2A202602940_DangHuuTam.md` |
| 4 | Nguyễn Hoàng Việt | 2A202602602 | vietnguyenhoang004@gmail.com | Observability & Evaluation Lead (`quality.py` GX 1.x, `testset.py`, reporting) | `report/2A202602602_NguyenHoangViet.md` |

---

## # Cá nhân

### ## NguyenDoChienThang-2A202602442
- **Vai trò:** Trưởng nhóm & Pipeline Lead (`src/core/`, `src/pipelines/`, `script/`).
- **Công việc chi tiết đã hoàn thành:**
  - Thiết kế cấu trúc hệ thống, kiến trúc luồng dữ liệu 2 pha (Baseline Ingestion và Corruption-Repair Flow).
  - Quản lý cấu hình tập trung trong `src/core/config.py` (Pydantic Settings, đường dẫn artifacts, cấu hình LLM, embedding, ChromaDB collections và Freshness SLA).
  - Cung cấp các tiện ích I/O dữ liệu an toàn trong `src/core/utils.py` (ghi JSON/CSV đảm bảo mã hóa UTF-8, timestamp UTC).
  - Điều phối và lắp ráp pipeline đầu-cuối trong `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py`, tạo entrypoint `script/run_phase1.py` và `script/run_corruption_flow.py` chạy độc lập với exit code 0.
  - Quản trị Git repository, phân nhánh công việc, merge code và theo dõi Contributor tracking trên GitHub đảm bảo 100% thành viên xuất hiện trên nhánh `main`.
  - Khắc phục lỗi bảo mật hệ thống Windows Defender Application Control (AppLocker) chặn DLL của `pyarrow.dataset` thông qua cơ chế fallback an toàn và shim trong `retrieval/embeddings.py`.
- **Điều học được / Đóng góp chính:**
  - Nắm vững kiến trúc Pipeline hướng dữ liệu (Data-Centric Pipeline) có tính Idempotent cao.
  - Hiểu rõ hiện tượng Silent Failure trong các hệ thống AI/RAG: dữ liệu bẩn làm suy thoái mô hình âm thầm nếu không có lớp Observability Gate bảo vệ.

### ## DuongDatKhang-2A202602624
- **Vai trò:** Data Foundation Owner (`src/ingestion/`).
- **Công việc chi tiết đã hoàn thành:**
  - Xây dựng module nạp dữ liệu thô `src/ingestion/crossref.py` hỗ trợ Dual-mode: tải trực tiếp từ Crossref REST API với cơ chế retry/exponential backoff và tự động chuyển sang local snapshot (`data/raw/crossref_records.json`) khi mất kết nối mạng.
  - Thiết kế và triển khai quy trình làm sạch, tiền xử lý trong `src/ingestion/cleaning.py`: bóc tách thẻ JATS XML/HTML, chuẩn hóa khoảng trắng thừa, sinh khóa duy nhất `paper_id`, tính toán độ tuổi dữ liệu `age_days` so với mốc UTC hiện tại, và định dạng chuỗi `text_for_embedding` chuẩn 5 trường thông tin (Title, Authors, Published, Categories, Summary).
  - Triển khai kịch bản làm bẩn dữ liệu `src/ingestion/corruption.py` với đủ 6 dạng lỗi thực tế: drop 20% bản ghi mới nhất, xóa rỗng summary, tiêm nhiễu token rác, cắt ngắn tiêu đề (<8 ký tự), lùi ngày xuất bản 365 ngày (stale data), và nhân bản bản ghi (duplicate rows).
  - Thực thi cơ chế tự phục hồi Idempotent Repair (`repair_from_raw`), bảo toàn nguyên vẹn snapshot gốc và tái lập 100% dữ liệu sạch.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về Data Lineage (truy vết nguồn gốc dữ liệu) và nguyên tắc bất biến của Raw Data Layer.
  - Nắm vững phương pháp thiết kế hàm biến đổi có tính Idempotent để đảm bảo hệ thống có thể phục hồi dữ liệu nhất quán bất kỳ lúc nào.

### ## DangHuuTam-2A202602940
- **Vai trò:** RAG Specialist (`src/retrieval/`).
- **Công việc chi tiết đã hoàn thành:**
  - Khởi tạo và quản lý 3 collection ChromaDB độc lập (`papers-baseline`, `papers-corrupted`, `papers-repaired`) nhằm cô lập hoàn toàn không gian vector, ngăn ngừa rò rỉ dữ liệu giữa các pha thử nghiệm.
  - Tích hợp mô hình sinh vector embedding `sentence-transformers/all-MiniLM-L6-v2` (384 chiều, chuẩn hóa L2 cosine distance) trong `src/retrieval/embeddings.py` và `src/retrieval/index.py`.
  - Viết script kiểm thử độc lập `script/smoke_retrieval.py` đạt 13/13 test cases PASS, kiểm tra toàn diện khả năng index 24 tài liệu, 8 trường metadata và truy vấn QA trên cả 4 dạng câu hỏi.
  - Tinh chỉnh `src/retrieval/llm.py` để hỗ trợ `MockChatModel` với phương thức `bind_tools()`, cho phép pipeline chạy kiểm thử trơn tru offline mà không cần API key.
  - Tối ưu hóa `src/retrieval/agent.py` để trích xuất thuộc tính `.text` chuẩn xác, tránh lỗi nhận signature block từ Gemini 3.
  - Phân tích cơ chế suy giảm truy xuất: khi tiêu đề bị cắt ngắn hoặc bản ghi bị drop, semantic search bị nhầm lẫn giữa các tài liệu gần trùng (Hit Rate sụt từ 100% xuống 70%).
- **Điều học được / Đóng góp chính:**
  - Nắm vững cách xây dựng hệ thống Hybrid Retrieval kết hợp Vector Similarity Search với exact metadata filtering.
  - Hiểu rõ sự phụ thuộc trực tiếp của biểu diễn không gian vector vào chất lượng làm sạch của văn bản đầu vào.

### ## NguyenHoangViet-2A202602602
- **Vai trò:** Observability & Evaluation Lead (`src/observability/`, `src/evaluation/`).
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập Data Quality Gate trong `src/observability/quality.py` theo đúng chuẩn hiện đại **Great Expectations 1.x** (sử dụng `gx.get_context(mode="ephemeral")`, `gx.ExpectationSuite`, `gx.ValidationDefinition`) với 4 expectations cốt lõi: số lượng dòng, tính không null của `paper_id`, tính duy nhất (uniqueness), và độ dài tối thiểu của `summary` (>= 30 ký tự).
  - Triển khai bộ giám sát Freshness SLA Monitoring: kiểm tra tỷ lệ bản ghi có `age_days > 180` ngày so với ngưỡng cho phép tối đa 25%, xuất báo cáo `freshness_report.json`.
  - Xây dựng bộ testset kiểm chuẩn cố định gồm 10 câu hỏi đa dạng trong `src/evaluation/testset.py`, bao quát 4 nhóm nghiệp vụ: `summary`, `authors`, `date`, `categories` kèm cặp `ground_truth_doc_ids` chuẩn xác.
  - Lập trình module đánh giá `src/evaluation/metrics.py` đo lường định lượng: Retrieval Hit Rate, Mean Token F1, LLM Judge Accuracy và Judge Score trên cả 3 trạng thái.
  - Tự động sinh báo cáo đối chiếu định lượng 3 trạng thái tại `data/reports/corruption_report.md` và `data/reports/phase1_report.md`.
  - Xây dựng giao diện trực quan **Interactive Observability Dashboard (Bonus B1: +5 điểm)** bằng Streamlit `dashboard.py` và file HTML độc lập `data/reports/dashboard.html`.
- **Điều học được / Đóng góp chính:**
  - Làm chủ cú pháp mới của Great Expectations 1.x, tránh các lỗi deprecated của GX 0.x.
  - Hiểu cách thiết lập các chốt kiểm soát tự động để phát hiện suy thoái dữ liệu trước khi ảnh hưởng đến người dùng cuối.
