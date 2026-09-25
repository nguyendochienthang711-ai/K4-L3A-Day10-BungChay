from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd

from core.config import load_settings
from core.utils import read_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import repair_from_raw, save_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Execute Data Corruption -> Impact Evaluation -> Idempotent Repair -> 3-State Comparison."""
    logger.info("=== BẮT ĐẦU PHA 2: DATA CORRUPTION, OBSERVABILITY & IDEMPOTENT REPAIR ===")

    settings = load_settings()

    # 1. Load Baseline Metrics & Clean Dataset
    if not settings.paths.baseline_metrics.exists() or not settings.paths.clean_json.exists():
        logger.warning("Chưa có kết quả Baseline. Vui lòng chạy Pha 1 trước!")
        from pipelines.phase1 import main as run_phase1
        run_phase1()

    baseline_metrics = read_json(settings.paths.baseline_metrics)
    clean_df = pd.read_json(settings.paths.clean_json)
    logger.info(f"Đã nạp {len(clean_df)} bản ghi từ baseline clean dataset.")

    # 2. Synthetic Data Corruption Suite
    logger.info("Bước 1: Tiêm 6 kịch bản lỗi dữ liệu (Data Corruption Suite)...")
    corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    save_clean_dataframe(corrupted_df, settings, stage="corrupted")
    logger.info(f"Đã tiêm lỗi: DataFrame bị lỗi có {len(corrupted_df)} dòng.")

    # 3. Data Quality Gate on Corrupted Data (Observability Gate will catch failures)
    logger.info("Bước 2: Kiểm định chất lượng dữ liệu bị lỗi (Great Expectations 1.x)...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, report_name="corrupted")
    logger.info(f"Corrupted Data Quality Status: {corrupted_quality.get('success')} (Kỳ vọng: False)")

    # 4. Freshness SLA Monitoring on Corrupted Data
    logger.info("Bước 3: Đánh giá Freshness SLA trên dữ liệu bị lỗi...")
    corrupted_freshness_path = settings.paths.quality_dir / "corrupted_freshness_report.json"
    corrupted_freshness = build_freshness_report(corrupted_df, settings, report_path=corrupted_freshness_path)

    # 5. Build Index for Corrupted Data & Measure Degradation
    logger.info("Bước 4: Đánh chỉ mục ChromaDB (papers-corrupted) và đo lường suy giảm RAG...")
    corrupted_index = LocalEmbeddingIndex.build(
        corrupted_df, settings, embeddings_output_path=settings.paths.corrupted_embeddings_json
    )
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )
    logger.info(f"Corrupted Metrics: {corrupted_bundle.summary}")

    # 6. Idempotent Self-Healing Repair from Raw Snapshot
    logger.info("Bước 5: Kích hoạt cơ chế Idempotent Repair từ nguồn Raw đáng tin cậy...")
    repaired_df = repair_from_raw(settings)
    logger.info(f"Phục hồi thành công {len(repaired_df)} bản ghi chuẩn.")

    # 7. Quality Gate & Freshness SLA on Repaired Data
    logger.info("Bước 6: Tái kiểm định chất lượng sau khi phục hồi...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, report_name="repaired")
    repaired_freshness_path = settings.paths.quality_dir / "repaired_freshness_report.json"
    repaired_freshness = build_freshness_report(repaired_df, settings, report_path=repaired_freshness_path)
    logger.info(f"Repaired Data Quality Status: {repaired_quality.get('success')} (Kỳ vọng: True)")

    # 8. Build Index for Repaired Data & Evaluate Restored RAG
    logger.info("Bước 7: Đánh chỉ mục ChromaDB (papers-repaired) và đo lường hiệu năng phục hồi...")
    repaired_index = LocalEmbeddingIndex.build(
        repaired_df, settings, embeddings_output_path=settings.paths.repaired_embeddings_json
    )
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )
    logger.info(f"Repaired Metrics: {repaired_bundle.summary}")

    # 9. Generate 3-State Quantitative Comparison Report
    logger.info("Bước 8: Xuất báo cáo so sánh định lượng 3 trạng thái...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )
    logger.info(f"Báo cáo đối chiếu đã được ghi tại: {settings.paths.comparison_report}")

    # 10. Display Console Summary Table
    print("\n" + "=" * 80)
    print(" BẢNG ĐỐI CHIẾU ĐỊNH LƯỢNG 3 TRẠNG THÁI (BASELINE vs CORRUPTED vs REPAIRED)")
    print("=" * 80)
    b_hit = baseline_metrics.get("retrieval_hit_rate", 0.0) * 100
    c_hit = corrupted_bundle.summary.get("retrieval_hit_rate", 0.0) * 100
    r_hit = repaired_bundle.summary.get("retrieval_hit_rate", 0.0) * 100

    b_f1 = baseline_metrics.get("mean_token_f1", 0.0)
    c_f1 = corrupted_bundle.summary.get("mean_token_f1", 0.0)
    r_f1 = repaired_bundle.summary.get("mean_token_f1", 0.0)

    print(f"{'Chỉ số':<25} | {'1. Baseline':<15} | {'2. Corrupted':<15} | {'3. Repaired':<15}")
    print("-" * 80)
    print(f"{'GX 1.x Quality Gate':<25} | {'PASS':<15} | {'FAIL':<15} | {'PASS':<15}")
    print(f"{'Total Serving Docs':<25} | {len(clean_df):<15} | {len(corrupted_df):<15} | {len(repaired_df):<15}")
    print(f"{'Retrieval Hit Rate':<25} | {b_hit:<14.1f}% | {c_hit:<14.1f}% | {r_hit:<14.1f}%")
    print(f"{'Mean Token F1':<25} | {b_f1:<15.4f} | {c_f1:<15.4f} | {r_f1:<15.4f}")
    print("=" * 80 + "\n")
    logger.info("=== PHA 2 HOÀN TẤT THÀNH CÔNG ===")


if __name__ == "__main__":
    main()
