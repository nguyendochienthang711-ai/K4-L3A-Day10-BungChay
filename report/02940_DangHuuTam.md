# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                           |
| ------------------ | ------------------------------------------------------------------- |
| Họ và tên       | Đặng Hữu Tâm                                                      |
| MSSV               | 02940                                                               |
| Khóa/Lớp         | K4                                                                  |
| Tên nhóm         | BungChay                                                            |
| Vai trò chính    | RAG & Vector Index Specialist                                       |
| Repository         | https://github.com/nguyendochienthang711-ai/K4-L3A-Day10-BungChay |
| Ngày hoàn thành | 2026-09-25                                                          |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | ------------ |
| Embedding + vector index | `src/retrieval/embeddings.py`, `src/retrieval/index.py` (`LocalEmbeddingIndex.build/load/search/lookup`) | Clean dataframe (9 cột, `text_for_embedding`) | 3 collection ChromaDB `papers-baseline` / `papers-corrupted` / `papers-repaired` + manifest trong `data/embeddings/` | Hoàn thành |
| QA trả lời câu hỏi | `src/retrieval/qa.py` (`answer_question`) | Câu hỏi test set + index | `AnswerResult` (answer, retrieved_doc_ids, contexts) cho `evaluation/metrics.py` | Hoàn thành (dùng nguyên logic starter, đã kiểm chứng) |
| Multi-provider LLM + agent | `src/retrieval/llm.py` (`build_llm`), `src/retrieval/agent.py` (`build_agent`, `run_agent_question`) | `LLM_PROVIDER`, `LLM_MODEL` trong `.env` | Agent LangChain 2 tool chạy được với `mock` và Gemini | Hoàn thành (đã sửa 2 lỗi) |
| Smoke test retrieval | `script/smoke_retrieval.py` | `data/raw/crossref_records.json` | 13 check tự động cho index + QA + semantic search | Hoàn thành |

Phần của tôi nằm giữa pipeline: nhận dataframe sạch từ `cleaning.py` (thành viên ingestion/cleaning), cung cấp index và `answer_question` cho `evaluation/metrics.py`, được `phase1.py` và `corruption_flow.py` gọi để build 3 collection.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ------------------------------ | -------- |
| Kiểm tra contract dữ liệu giữa `cleaning.py` và `index.py` | Ingestion/cleaning | Xác nhận đủ 9 cột, `published` là chuỗi, không có NaN → index 24 docs + QA đúng |
| Kiểm tra test set khớp mẫu câu hỏi của `qa.py` | Evaluation (`testset.py`) | Cả 10 câu dùng đúng mẫu, title trong dấu nháy đơn |
| Chạy lại 2 pipeline để xác minh số liệu nhóm | Integration | Tái hiện đúng 100% `data/results/*.json` |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Viết smoke test độc lập cho retrieval (ChromaDB ở thư mục tạm, không đụng `data/chroma`) | `script/smoke_retrieval.py` | 13/13 check chính PASS | `python script/smoke_retrieval.py` |
| Sửa agent không chạy được với provider `mock` | `src/retrieval/llm.py` | Agent chạy không cần API key | Hỏi agent với `LLM_PROVIDER=mock` → trả lời mock, không crash |
| Sửa output agent với Gemini 3 bị lẫn content block/signature | `src/retrieval/agent.py` | Trả về chuỗi câu trả lời sạch | Hỏi agent với `gemini-3.8-flash` → "authored by Bao Do and Linh Ngo" (đúng raw data) |
| Kiểm chứng 3 collection sau khi nhóm hoàn thiện pipeline | `data/chroma/` | `papers-baseline` 24, `papers-corrupted` 22, `papers-repaired` 24 | `chromadb.PersistentClient('data/chroma').list_collections()` |

Output cụ thể phần việc của tôi giúp xác minh: 3 collection tách biệt trong `data/chroma/` và kết quả retrieval (`retrieved_doc_ids`) trong `data/results/{baseline,corrupted,repaired}_answers.json` — đây là nguồn để tính `retrieval_hit_rate` 100% → 70% → 100%.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Biến bảng dữ liệu sạch thành một kho tìm kiếm ngữ nghĩa để trả lời câu hỏi về bài báo, và giữ được 3 trạng thái dữ liệu (sạch / lỗi / phục hồi) tách biệt để so sánh công bằng trên cùng một test set.

### Cách triển khai

- **Embedding:** `sentence-transformers/all-MiniLM-L6-v2`, vector 384 chiều, chuẩn hóa (`normalize_embeddings=True`); model được cache bằng `lru_cache` để không tải lại.
- **Index:** ChromaDB `PersistentClient`, không gian `cosine`, điểm = `1 - distance`. `build()` luôn `delete_collection` rồi tạo lại → chạy lại nhiều lần cho kết quả như nhau (idempotent), không còn vector cũ sót lại. ID bản ghi = `paper_id::index` để vẫn nạp được các dòng trùng khi tiêm lỗi duplicate.
- **3 collection:** tên collection suy ra từ đường dẫn manifest (`embeddings_json` / `corrupted_embeddings_json` / `repaired_embeddings_json`), nên pipeline chỉ cần truyền đúng path.
- **QA:** không gọi LLM để đánh giá tái lập được. (1) Nếu câu hỏi có title trong `'...'` thì tra đúng bài theo title/DOI; (2) ghép với top-4 semantic search; (3) lấy câu trả lời từ metadata theo từ khóa (authors / published / categories / câu đầu summary).
- **Agent:** LangChain `create_agent` với 2 tool `semantic_search_papers` và `lookup_paper`; đổi provider chỉ bằng `.env`.

### Input, output và contract

| Thành phần | Mô tả |
| ------------------------------ | ------------------------------------------- |
| Input | DataFrame có `paper_id, title, summary, published, authors_joined, categories_joined, text_for_embedding, abs_url, pdf_url`; `published` phải là chuỗi `YYYY-MM-DD`; không NaN |
| Output | Collection ChromaDB + manifest JSON; `AnswerResult(answer, retrieved_doc_ids, retrieved_contexts, retrieved_titles)` |
| Module phụ thuộc | `ingestion/cleaning.py`, `core/config.py` |
| Module sử dụng output | `evaluation/metrics.py`, `pipelines/phase1.py`, `pipelines/corruption_flow.py` |
| Điều kiện lỗi cần xử lý | `published` kiểu Timestamp → Chroma báo `ValueError` (đã thử); title chứa dấu `'` → regex cắt sai (không xuất hiện trong 24 bài); không có API key → phải dùng `mock` |

### Cách xác minh

```bash
python script/smoke_retrieval.py
python script/run_phase1.py
python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** index đủ docs, QA đúng 4 loại câu hỏi, 3 collection tồn tại, số liệu tái hiện được.
- **Kết quả thực tế:** smoke test 13/13 PASS; 2 pipeline exit code 0; 3 collection 24/22/24 docs; `data/results/*.json` sinh ra giống hệt bản nhóm đã commit.
- **Artifact/log:** `data/chroma/`, `data/embeddings/`, `data/results/`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Smoke test cho thấy nếu chỉ dùng semantic search thì hit@1 = 13/24 vì dữ liệu có 12 cặp bài gần trùng ("X" và "Advanced Perspectives on X"). Có thể "sửa" `qa.py` cho search thông minh hơn.
- **Các phương án đã cân nhắc:** (A) Cải tiến retrieval (thêm rerank/lọc theo title gần đúng); (B) giữ nguyên logic exact lookup + semantic search của starter.
- **Phương án đã chọn:** (B) giữ nguyên.
- **Lý do:** Mục tiêu bài lab là đo tác động của dữ liệu lỗi lên RAG. Exact lookup theo title là lớp bảo vệ khi dữ liệu sạch; khi title bị hỏng hoặc bài bị xóa, hệ thống rơi về semantic search và lộ ra silent failure. Làm retrieval "khôn" hơn sẽ che mất tác động của corruption, đồng thời thay đổi logic chung mà evaluation của cả nhóm đang dựa vào.
- **Bằng chứng quyết định phù hợp:** Corrupted hit rate giảm rõ 100% → 70% và phục hồi 100% sau repair; các câu MISS đúng là những bài bị xóa (xem mục 8).

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Chạy agent với `LLM_PROVIDER=mock` → `NotImplementedError` tại bước `bind_tools`. Với Gemini thì `run_agent_question` trả về `[{'type': 'text', 'text': '...', 'extras': {'signature': '...'}}]` thay vì chuỗi.
- **Lệnh hoặc bước tái hiện:** `build_agent(settings, index)` rồi `run_agent_question(agent, "Who authored '<title>'?")` với từng provider.
- **Nguyên nhân gốc:** `FakeListChatModel` của LangChain không cài đặt `bind_tools()` mà `create_agent` bắt buộc gọi; Gemini 3 trả `content` dạng danh sách block, còn code cũ lấy thẳng `.content`.
- **Cách xử lý:** Trong `llm.py` tạo lớp con `_MockChatModel` có `bind_tools()` trả về chính nó. Trong `agent.py` dùng thuộc tính `.text` của message (chỉ lấy phần chữ), fallback về `str(content)`.
- **Cách xác minh sau khi sửa:** `mock` → trả lời "This is a mock response..." không crash; Gemini → "The paper ... was authored by Bao Do and Linh Ngo." (khớp `crossref_records.json`); smoke test vẫn 13/13.
- **Điều học được:** Không có API key thì pipeline phải vẫn chạy được (giám khảo có thể chạy lại trên máy khác), nên chế độ `mock` phải đi được hết các đường code, kể cả agent.

Blocker phụ đã gặp: `gemini-2.5-flash` trả 404 "no longer available to new users" → chuyển `LLM_MODEL=gemini-3.8-flash`. Gemini free tier giới hạn 20 request/ngày (429) → khi chạy toàn pipeline dùng `LLM_PROVIDER=mock`.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Crossref → vector index:** `crossref.py` lấy dữ liệu (hoặc đọc snapshot offline) và lưu 2 file raw; `cleaning.py` chuẩn hóa, bỏ trùng theo `paper_id`, tính `age_days`, ghép `text_for_embedding` 5 phần (Title/Authors/Published/Categories/Summary); `index.py` nhúng bằng MiniLM và nạp vào collection ChromaDB kèm metadata.
2. **Evaluation set:** mỗi câu hỏi có `ground_truth` và `ground_truth_doc_ids` (DOI). Retrieval hit = DOI đúng có trong top-4 kết quả; Token F1 so câu trả lời với ground truth; judge chấm mức đúng của câu trả lời.
3. **Quality checks vs freshness:** quality checks (GX 1.x) kiểm tra *cấu trúc/nội dung* dữ liệu — số dòng, không null, `paper_id` duy nhất, summary ≥ 30 ký tự. Freshness đo *độ cũ* — tỷ lệ bài có `age_days > 180` không được vượt 25%. Dữ liệu có thể đúng cấu trúc nhưng đã cũ, và ngược lại.
4. **Cùng test set:** nếu đổi câu hỏi thì không biết điểm thay đổi do dữ liệu hay do đề. Giữ nguyên test set thì dữ liệu là biến số duy nhất giữa baseline, corrupted, repaired.
5. **Repair thành công dựa trên:** `repaired_metrics.json` quay về bằng baseline (hit rate 100%, F1 1.0), `repaired_quality_report.json` PASS, freshness PASS, và collection `papers-repaired` có lại đủ 24 docs.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | 1.00 | 0.70 | 1.00 | 3 câu MISS đúng là 3 bài test bị xóa (drop latest) |
| `mean_token_f1` | 1.00 | 0.90 | 1.00 | Chỉ giảm 0.10 vì 2/3 câu MISS vẫn "trả lời đúng" nhờ bài song sinh |
| `judge_accuracy` | 1.00 | 0.90 | 1.00 | Judge là heuristic dựa trên Token F1 (LLM không được gọi), nên đi theo F1 |
| `mean_judge_score` | 5.0 | 4.6 | 5.0 | Như trên |
| Quality checks | PASS | FAIL | PASS | GX bắt được blank summary và duplicate `paper_id` |
| Freshness status | Fresh (1/24 stale) | Stale (11/22) | Fresh (1/24) | Stale date đẩy tỷ lệ bài cũ lên 50% > ngưỡng 25% |
| Số docs trong collection | 24 | 22 | 24 | 24 − 4 bài bị xóa + 2 dòng trùng = 22 |

Nguồn: `data/results/*_metrics.json`, `data/results/corrupted_answers.json`, `data/quality/`, ChromaDB `data/chroma/`. Đã chạy lại 2 pipeline và tái hiện đúng các số này.

### Kết luận từ số liệu

1. **Drop latest records** (xóa 4 bài, trong đó 3 bài thuộc test set: `...1804`, `...1807`, `...1808`) → collection còn 22 docs nhưng check row count (5–5000) vẫn PASS, tức GX **không** bắt được lỗi mất bài; quality gate FAIL là do các lỗi khác (`paper_id` trùng, summary quá ngắn) → retrieval hit rate 100% → 70% (eval_004, eval_007, eval_008 MISS). Đây là lỗ hổng của quality gate: cần thêm check so số dòng với lần chạy trước.
2. **Repair từ `crossref_records.json`** → quality PASS, freshness Fresh, collection `papers-repaired` đủ 24 docs → hit rate, F1, judge về lại bằng baseline.

**Corruption nào ảnh hưởng rõ nhất và vì sao?**

Drop latest records ảnh hưởng rõ nhất đến retrieval vì bài đúng không còn trong index, không thể hit. Nhưng điểm đáng chú ý là hậu quả của nó ở tầng câu trả lời: khi bài đúng biến mất, semantic search lấy bài "song sinh" đứng đầu:

| Câu | Bài đúng | Top-1 thực tế | Câu trả lời | Đánh giá |
| --- | --- | --- | --- | --- |
| eval_004 (categories) | `...1804` (bị xóa) | `...1816` Advanced Perspectives on Freshness SLAs... | Data Management, Artificial Intelligence | Đúng đáp án, **sai tài liệu** |
| eval_008 (categories) | `...1808` (bị xóa) | `...1820` Advanced Perspectives on Multi-Agent Consensus... | Multi-Agent Systems, Artificial Intelligence | Đúng đáp án, **sai tài liệu** |
| eval_007 (date) | `...1807` (bị xóa) | `...1819` (bị lùi ngày) | 2025-06-07 (đúng là 2026-06-25) | Sai, trả lời tự tin |

Đây chính là silent failure: không có lỗi runtime, agent vẫn trả lời trôi chảy, và 2/3 trường hợp còn trông như đúng.

**Kết quả nào khác với kỳ vọng ban đầu?**

- Truncate title, blank summary và noise **gần như không làm đổi metric**. Kiểm tra log cho thấy: blank summary rơi vào `...1802`, nhưng câu hỏi về bài này là loại *authors* nên không cần summary; noise rơi vào 2 bài không có trong test set; truncate title rơi vào `...1810` (title còn `'Autom'`).
- Với `...1810` (eval_010), exact lookup theo title thất bại, top-1 là bài song sinh `...1822`, nhưng câu trả lời vẫn đúng (2 bài có cùng tác giả) và **metric vẫn tính là hit** vì `...1810` nằm ở vị trí thứ 2 trong top-4. Tức là `retrieval_hit_rate` (bất kỳ trong top-k) không phát hiện được việc câu trả lời lấy từ sai tài liệu.
- Giả thuyết đã kiểm tra: smoke test trên dữ liệu sạch cho hit@1 = 13/24 nhưng hit@4 = 24/24 khi chỉ dùng semantic search — khớp với hiện tượng trên.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về data pipeline:** Index phải idempotent (xóa rồi tạo lại collection) và tách riêng theo trạng thái dữ liệu; nếu không thì không so sánh hay rollback được.
2. **Về data quality/observability:** Metric RAG tổng hợp có thể che lỗi dữ liệu — F1 chỉ giảm 0.10 dù 3/10 câu lấy sai tài liệu. Quality gate và freshness ở tầng dữ liệu mới bắt được lỗi sớm và rõ ràng.
3. **Về ảnh hưởng của data đến RAG agent:** Khi dữ liệu có các bản gần trùng, semantic search sẽ lặng lẽ thay bài đúng bằng bài giống nó; agent vẫn trả lời tự tin, nên câu trả lời "đúng" chưa chắc đã có nguồn đúng.

### Nếu có thêm thời gian

Thêm metric **source-grounded accuracy / hit@1**: chỉ tính đúng khi câu trả lời lấy từ đúng `ground_truth_doc_ids` ở vị trí đầu. Đo bằng cách so `retrieved_doc_ids[0]` với ground truth trên cùng test set; kỳ vọng corrupted sẽ giảm từ 1.0 xuống ~0.6 (eval_004, 007, 008, 010), phản ánh đúng mức hỏng thay vì 0.9 như Token F1.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

Ghi chú: Tôi có sử dụng trợ lý AI (Claude) để hỗ trợ đọc code, viết smoke test và gỡ lỗi agent, theo chính sách AI tại `docs/RULES.md`; toàn bộ thay đổi đã được chạy kiểm chứng và tôi hiểu logic của từng phần.

**Họ và tên:** Đặng Hữu Tâm
**Ngày xác nhận:** 2026-09-25
