"""Utility script to fetch a slice of the Anthropic HH-RLHF dataset.

Usage:
    python download_hh_rlhf_samples.py --count 100 --out backend/data/hh_rlhf_samples.jsonl

Requires the `datasets` package. Install via `pip install datasets`.
"""

import argparse
import json
from pathlib import Path

from datasets import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100, help="Number of samples to export")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("backend/data/hh_rlhf_samples.jsonl"),
        help="Destination JSONL file",
    )
    args = parser.parse_args()

    print(f"Loading Anthropic/hh-rlhf dataset (first {args.count} rows)…")
    dataset = load_dataset("Anthropic/hh-rlhf", split=f"train[:{args.count}]")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with args.out.open("w", encoding="utf-8") as f:
        for idx, item in enumerate(dataset):
            record = {"id": idx, "chosen": item["chosen"], "rejected": item["rejected"]}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(dataset)} rows to {args.out}")


if __name__ == "__main__":
    main()
