#!/usr/bin/env python3
"""Compare weights.txt files from two mobilenet example model folders.

Each weights.txt file contains one integer value per line. This script
compares the two files value-by-value and reports:
  - line/value counts for each file
  - whether the files are identical
  - number and percentage of mismatched values (for the overlapping range)
  - the first few mismatches (line number, value in each file)

Usage:
    python compare_weights.py [file_a] [file_b] [--max-diffs N]

Defaults to comparing:
  example_models/mobilenet_v2_1.0_224_INT8/src/mobilenet_v2_1_0_224_INT8_weights.txt
  example_models/mobilenet_v2_new/src/mobilenet_v2_1.0_224_INT8_weights.txt
"""

import argparse
import sys
from pathlib import Path

DEFAULT_FILE_A = (
    "example_models/mobilenet_v2_1.0_224_INT8/src/"
    "mobilenet_v2_1_0_224_INT8_weights.txt"
)
DEFAULT_FILE_B = (
    "example_models/mobilenet_v2_new/src/"
    "mobilenet_v2_1.0_224_INT8_weights.txt"
)


def load_values(path: Path) -> list[str]:
    with path.open("r") as f:
        return [line.strip() for line in f if line.strip() != ""]


def compare_files(path_a: Path, path_b: Path, max_diffs: int) -> int:
    print(f"File A: {path_a}")
    print(f"File B: {path_b}")

    values_a = load_values(path_a)
    values_b = load_values(path_b)

    count_a, count_b = len(values_a), len(values_b)
    print(f"Value count A: {count_a}")
    print(f"Value count B: {count_b}")

    if values_a == values_b:
        print("Result: IDENTICAL")
        return 0

    overlap = min(count_a, count_b)
    mismatches = [
        (i, values_a[i], values_b[i])
        for i in range(overlap)
        if values_a[i] != values_b[i]
    ]

    print(f"Result: DIFFERENT")
    print(f"Compared {overlap} overlapping values")
    print(
        f"Mismatched values: {len(mismatches)} "
        f"({100 * len(mismatches) / overlap:.4f}% of overlap)"
    )
    if count_a != count_b:
        print(
            f"Length mismatch: A has {count_a - overlap if count_a > overlap else 0} "
            f"extra line(s), B has {count_b - overlap if count_b > overlap else 0} "
            f"extra line(s)"
        )

    if mismatches:
        print(f"\nFirst {min(max_diffs, len(mismatches))} mismatches (line: A vs B):")
        for line_no, val_a, val_b in mismatches[:max_diffs]:
            print(f"  line {line_no + 1}: {val_a} != {val_b}")

    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "file_a", nargs="?", default=DEFAULT_FILE_A, help="First weights.txt file"
    )
    parser.add_argument(
        "file_b", nargs="?", default=DEFAULT_FILE_B, help="Second weights.txt file"
    )
    parser.add_argument(
        "--max-diffs",
        type=int,
        default=20,
        help="Max number of mismatches to print (default: 20)",
    )
    args = parser.parse_args()

    path_a = Path(args.file_a)
    path_b = Path(args.file_b)

    for p in (path_a, path_b):
        if not p.is_file():
            print(f"Error: file not found: {p}", file=sys.stderr)
            return 2

    return compare_files(path_a, path_b, args.max_diffs)


if __name__ == "__main__":
    sys.exit(main())
