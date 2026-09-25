# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** BungChay
- **Mã Nhóm / Lớp:** `K4A-L3-DAY10`
- **Tên Repository Nộp Bài:** K4-L3A-Day10-BungChay

---

## # Thành viên

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | | | | Trưởng nhóm / Pipeline Integrator (`core/`, `phase1.py`, `corruption_flow.py`) | `report/<MSSV1>_HoTen.md` |
| 2 | | | | Data Foundation & Recovery (`crossref.py`, `cleaning.py`, raw data) | `report/<MSSV2>_HoTen.md` |
| 3 | Đặng Hữu Tâm | 2A202602940 | | RAG & Vector Index (`retrieval/index.py`, `embeddings.py`, ChromaDB) | `report/02940_DangHuuTam.md` |
| 4 | Nguyễn Hoàng Việt | 2A202602602 | vietnguyenhoang004@gmail.com | Observability & Evaluation (`quality.py` GX 1.x, `testset.py`, reporting) | `report/2A202602602_NguyenHoangViet.md` |

*(Nếu nhóm có 3 hoặc 5-6 thành viên, xem bảng phân công chi tiết theo vai trò trong file `CHECKPOINTS.md`)*.

---

## # Cá nhân

### ## HoVaTen1-MSSV1
- **Vai trò:** Trưởng nhóm & Điều phối Pipeline.
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập cấu hình hệ thống `core/config.py` và đường dẫn artifacts `core/utils.py`.
  - Kết nối luồng thực thi trong `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py`.
  - Kiểm tra tính nhất quán của các artifacts và theo dõi Contributor tracking trên GitHub nhánh `main`.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về thiết kế Idempotent Pipeline và quản lý trạng thái luồng dữ liệu đa tầng.

### ## HoVaTen2-MSSV2
- **Vai trò:** Phụ trách Ingestion, Làm sạch & Phục hồi dữ liệu.
- **Công việc chi tiết đã hoàn thành:**
  - Xây dựng module thu thập Crossref API với cơ chế Fallback offline trong `src/ingestion/crossref.py`.
  - Chuẩn hóa schema, tính toán trường `age_days` và `text_for_embedding` trong `src/ingestion/cleaning.py`.
  - Thực thi cơ chế Idempotent Repair phục hồi dữ liệu từ raw snapshot.
- **Điều học được / Đóng góp chính:**
  - Kỹ thuật truy vết nguồn gốc dữ liệu (Data Lineage) và bảo toàn raw snapshot trước khi biến đổi.

### ## DangHuuTam-02940
- **Vai trò:** Phụ trách RAG, Vector Database & Embedding (`src/retrieval/`).
- **Công việc chi tiết đã hoàn thành:**
  - Kiểm chứng embedding `sentence-transformers/all-MiniLM-L6-v2` + ChromaDB bằng `script/smoke_retrieval.py`: index đủ 24 docs, vector 384 chiều, 8 trường metadata, QA đúng cả 4 loại câu hỏi (13/13 check PASS).
  - Đo retrieval thuần semantic: hit@4 = 24/24 nhưng hit@1 chỉ 13/24 do 12 cặp bài gần trùng → giải thích vì sao corruption làm hỏng title lookup sẽ kéo retrieval xuống.
  - Sửa `retrieval/llm.py`: provider `mock` hỗ trợ `bind_tools()` để agent chạy được không cần API key.
  - Sửa `retrieval/agent.py`: lấy `.text` để câu trả lời Gemini 3 không lẫn content block/signature.
  - Kiểm tra tích hợp với `cleaning.py` của nhóm: đủ cột, `published` dạng chuỗi, index + QA chạy đúng.
  - Đang chờ: chạy tích hợp 3 collection (`papers-baseline`, `papers-corrupted`, `papers-repaired`) khi `phase1.py` và `corruption_flow.py` hoàn thành.
- **Điều học được / Đóng góp chính:**
  - Cách cô lập các không gian vector để so sánh khách quan giữa dữ liệu sạch và dữ liệu bị lỗi; semantic search đơn thuần dễ nhầm giữa các tài liệu gần trùng, nên exact lookup theo ID/title là lớp bảo vệ quan trọng.

### ## NguyenHoangViet-2A202602602
- **Vai trò:** Phụ trách Data Observability & Benchmark Evaluation (`src/observability/`, `src/evaluation/`).
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập Data Quality Gate chuẩn hóa theo **Great Expectations 1.x** (`mode="ephemeral"`) với 4 Expectations cốt lõi trong `src/observability/quality.py`, kiểm định dữ liệu sạch đạt `PASS`, bắt lỗi chính xác khi tiêm dữ liệu hỏng (`FAIL`).
  - Triển khai cơ chế giám sát độ tươi tri thức **Freshness SLA** (`age_days > 180`), ghi nhận tỷ lệ bài báo cũ 4.2% $\le$ 25% (PASS), xuất `data/quality/freshness_report.json`.
  - Xây dựng bộ đề thi đánh giá RAG chuẩn hóa gồm 10 câu hỏi bao phủ 4 nhóm nghiệp vụ (`summary`, `authors`, `date`, `categories`) trong `src/evaluation/testset.py`, xuất `data/eval/test_set.json`.
  - Tự động hóa xuất báo cáo Markdown Pha 1 (`phase1_report.md`) và Pha 2 (`corruption_report.md`) đối chiếu 3 trạng thái rõ ràng (Baseline vs Corrupted vs Repaired) trong `src/observability/reporting.py`.
  - Đo lường và chứng minh hiện tượng **Silent Failure**: Retrieval Hit Rate sụt giảm từ 100% xuống 70% khi dữ liệu bị tiêm lỗi, và phục hồi lại 100% sau Idempotent Repair.
  - Xây dựng giao diện trực quan **Interactive Observability Dashboard (Bonus B1: +5 điểm)** qua cả 2 hình thức: ứng dụng Streamlit `dashboard.py` (5 tabs phân tích) và trang Web HTML độc lập `data/reports/dashboard.html`.
  - Khắc phục triệt để lỗi xung đột môi trường (PyTorch 2.2.2 / NumPy 1.26.4 / Transformers 4.44.2) trên macOS và lỗi fallback judge trong `metrics.py`.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc cách thức Data Quality Gate ngăn chặn dữ liệu bẩn thẩm thấu vào Vector DB; làm chủ kiến trúc Ephemeral Context của GX 1.x và quy trình thiết lập chuẩn Ground Truth để đo lường định lượng chất lượng RAG Agent.
