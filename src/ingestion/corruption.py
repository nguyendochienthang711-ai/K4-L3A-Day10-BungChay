from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import pandas as pd


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: str | Path) -> pd.DataFrame:
    """Simulate 6 synthetic data corruption scenarios:
    1. Drop latest records (drop ~20% newest papers).
    2. Blank summary (clear abstract in some rows).
    3. Inject noise (insert garbage characters into summary).
    4. Truncate title (shorten title to < 8 chars).
    5. Stale date (shift published date back 365 days).
    6. Duplicate rows (re-append existing rows).
    7. Recompute `text_for_embedding`.
    8. Write detailed corruption log into output_log_path.
    """
    corrupted = df.copy()
    n_rows = len(corrupted)
    log_entries: list[dict[str, Any]] = []

    # 1. Drop latest records: sort by published desc, drop 20% newest records
    drop_count = max(1, int(n_rows * 0.20))
    if "published" in corrupted.columns:
        corrupted = corrupted.sort_values(by="published", ascending=False)
        dropped_ids = corrupted.head(drop_count)["paper_id"].tolist()
        corrupted = corrupted.iloc[drop_count:].copy()
        log_entries.append(
            {
                "corruption_type": "drop_latest_records",
                "count": drop_count,
                "affected_paper_ids": dropped_ids,
                "description": f"Dropped {drop_count} most recent papers.",
            }
        )

    corrupted = corrupted.reset_index(drop=True)
    m = len(corrupted)

    # 2. Blank summary: set empty string for ~2 rows
    blank_indices = [0, min(1, m - 1)] if m > 1 else [0]
    blank_ids = []
    for idx in blank_indices:
        corrupted.at[idx, "summary"] = ""
        corrupted.at[idx, "summary_chars"] = 0
        blank_ids.append(corrupted.at[idx, "paper_id"])
    log_entries.append(
        {
            "corruption_type": "blank_summary",
            "count": len(blank_indices),
            "affected_paper_ids": blank_ids,
            "description": "Erased summary text to simulate crawler extract failure.",
        }
    )

    # 3. Inject noise: add gibberish string to summary in some rows
    noise_indices = [min(2, m - 1), min(3, m - 1)]
    noise_ids = []
    for idx in noise_indices:
        original = corrupted.at[idx, "summary"]
        noisy = f"###NOISE_INJECTION_CORRUPTED_GARBAGE### {original}"
        corrupted.at[idx, "summary"] = noisy
        corrupted.at[idx, "summary_chars"] = len(noisy)
        noise_ids.append(corrupted.at[idx, "paper_id"])
    log_entries.append(
        {
            "corruption_type": "inject_noise",
            "count": len(noise_indices),
            "affected_paper_ids": noise_ids,
            "description": "Injected synthetic noise and random tokens into summary.",
        }
    )

    # 4. Truncate title: cut down to < 8 chars
    trunc_indices = [min(4, m - 1)]
    trunc_ids = []
    for idx in trunc_indices:
        corrupted.at[idx, "title"] = "Corrupt"
        trunc_ids.append(corrupted.at[idx, "paper_id"])
    log_entries.append(
        {
            "corruption_type": "truncate_title",
            "count": len(trunc_indices),
            "affected_paper_ids": trunc_ids,
            "description": "Truncated paper title to '< 8 characters'.",
        }
    )

    # 5. Stale date: shift published date by -365 days and increase age_days
    stale_indices = [min(5, m - 1), min(6, m - 1)]
    stale_ids = []
    for idx in stale_indices:
        pub = pd.to_datetime(corrupted.at[idx, "published"], errors="coerce")
        if pd.notna(pub):
            shifted = pub - pd.Timedelta(days=365)
            corrupted.at[idx, "published"] = shifted.strftime("%Y-%m-%d")
            corrupted.at[idx, "age_days"] = int(corrupted.at[idx, "age_days"]) + 365
            stale_ids.append(corrupted.at[idx, "paper_id"])
    log_entries.append(
        {
            "corruption_type": "stale_date",
            "count": len(stale_indices),
            "affected_paper_ids": stale_ids,
            "description": "Shifted publication date back 365 days to violate Freshness SLA.",
        }
    )

    # 6. Duplicate rows: duplicate 2 rows
    dup_rows = corrupted.iloc[[0, min(1, m - 1)]].copy()
    corrupted = pd.concat([corrupted, dup_rows], ignore_index=True)
    log_entries.append(
        {
            "corruption_type": "duplicate_rows",
            "count": len(dup_rows),
            "affected_paper_ids": dup_rows["paper_id"].tolist(),
            "description": "Duplicated records to violate uniqueness constraint.",
        }
    )

    # 7. Recompute text_for_embedding
    corrupted["text_for_embedding"] = corrupted.apply(
        lambda row: (
            f"Title: {row['title']}\n"
            f"Authors: {row['authors_joined']}\n"
            f"Published: {row['published']}\n"
            f"Categories: {row['categories_joined']}\n"
            f"Summary: {row['summary']}"
        ),
        axis=1,
    )

    # 8. Write corruption log
    out = Path(output_log_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_original_rows": n_rows,
                "total_corrupted_rows": len(corrupted),
                "corruptions": log_entries,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return corrupted
