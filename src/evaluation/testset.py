from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import first_sentence


def build_test_set(df: pd.DataFrame, output_path: str | Path) -> list[dict[str, Any]]:
    """Build a benchmark evaluation set of 10 questions covering 4 task types:
    summary, authors, date, categories.
    """
    if len(df) < 5:
        raise ValueError(f"DataFrame has only {len(df)} records; need at least 5 for test set.")

    # Select representative papers deterministically
    records = df.to_dict(orient="records")
    test_set: list[dict[str, Any]] = []

    # Distribution of 10 questions:
    # 0, 1, 2: summary (3 questions)
    # 3, 4, 5: authors (3 questions)
    # 6, 7: date (2 questions)
    # 8, 9: categories (2 questions)
    types_config = [
        ("summary", 0),
        ("summary", 1),
        ("summary", 2),
        ("authors", 3),
        ("authors", 4),
        ("authors", 5),
        ("date", 6),
        ("date", 7),
        ("categories", 8),
        ("categories", 9),
    ]

    for idx, (q_type, paper_idx) in enumerate(types_config):
        row = records[paper_idx % len(records)]
        title = row["title"]
        paper_id = row["paper_id"]

        if q_type == "summary":
            question = f"What is the summary of the paper '{title}'?"
            ground_truth = first_sentence(str(row["summary"]))
        elif q_type == "authors":
            question = f"Who authored the paper '{title}'?"
            ground_truth = str(row["authors_joined"])
        elif q_type == "date":
            question = f"When was the paper '{title}' published?"
            ground_truth = str(row["published"])
        elif q_type == "categories":
            question = f"What categories are associated with the paper '{title}'?"
            ground_truth = str(row["categories_joined"])
        else:
            question = f"Describe the paper '{title}'."
            ground_truth = first_sentence(str(row["summary"]))

        test_set.append(
            {
                "id": f"eval_{idx + 1:03d}",
                "question_type": q_type,
                "question": question,
                "ground_truth": ground_truth,
                "ground_truth_doc_ids": [paper_id],
            }
        )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(test_set, f, indent=2, ensure_ascii=False)

    return test_set
