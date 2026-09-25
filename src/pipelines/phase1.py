from __future__ import annotations

import logging
import pandas as pd

from core.config import load_settings
from core.utils import now_utc, read_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe, save_clean_dataframe
from ingestion.crossref import fetch_source_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Execute Baseline Pipeline End-to-End (Phase 1)."""
    logger.info("=== BẮT ĐẦU PHA 1: BASELINE DATA PIPELINE & OBSERVABILITY ===")

    # 1. Load settings
    settings = load_settings()
    logger.info(f"Target Project: {settings.paths.project_dir}")

    # 2. Ingestion: fetch or load raw records
    logger.info("Bước 1: Thu thập metadata bài báo từ Crossref...")
    raw_records = fetch_source_records(settings)
    logger.info(f"Đã tải {len(raw_records)} bài báo thô.")

    # 3. Data Cleaning
    logger.info("Bước 2: Tiền xử lý, chuẩn hóa và làm sạch dữ liệu...")
    clean_df = build_clean_dataframe(raw_records, now_utc())
    save_clean_dataframe(clean_df, settings, stage="clean")
    logger.info(f"Làm sạch hoàn tất: {len(clean_df)} bản ghi hợp lệ.")

    # 4. Data Observability Gate (Great Expectations 1.x)
    logger.info("Bước 3: Thực thi Data Quality Gate (Great Expectations 1.x)...")
    quality = run_data_quality_checks(clean_df, settings, report_name="baseline")
    logger.info(f"Quality Check Status: {quality.get('success')}")

    # 5. Freshness SLA Monitoring
    logger.info("Bước 4: Kiểm tra Freshness SLA...")
    freshness = build_freshness_report(clean_df, settings)
    logger.info(f"Freshness Status: {freshness.get('status')} (Stale ratio: {freshness.get('stale_ratio')})")

    # 6. Embedding & Vector Store Indexing (ChromaDB)
    logger.info("Bước 5: Tạo vector embeddings và đánh chỉ mục ChromaDB (papers-baseline)...")
    index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)
    logger.info("Đánh chỉ mục vector hoàn tất.")

    # 7. Benchmark Test Set Generation
    logger.info("Bước 6: Sinh bộ câu hỏi benchmark test set (10 câu qua 4 nhóm)...")
    test_set = build_test_set(clean_df, settings.paths.eval_testset)
    logger.info(f"Đã sinh {len(test_set)} câu hỏi đánh giá chuẩn.")

    # 8. Evaluation & Scoring
    logger.info("Bước 7: Đánh giá RAG Agent trên dữ liệu sạch...")
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )
    logger.info(f"Baseline Metrics: {eval_bundle.summary}")

    # 9. Generate Phase 1 Markdown Report
    logger.info("Bước 8: Xuất báo cáo tổng kết Pha 1...")
    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "raw_records_count": len(raw_records),
        "clean_rows": len(clean_df),
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=eval_bundle.summary,
        quality=quality,
        freshness=freshness,
    )
    logger.info(f"Báo cáo Pha 1 đã được tạo tại: {settings.paths.baseline_report}")
    logger.info("=== PHA 1 HOÀN TẤT THÀNH CÔNG ===")


if __name__ == "__main__":
    main()
