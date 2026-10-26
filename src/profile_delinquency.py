
from pathlib import Path
from collections import Counter

PROJECT_DIR = Path(__file__).resolve().parent.parent
PERF_FILE = PROJECT_DIR / "data" / "raw" / "sample_perf_2020.txt"


def main():
    status_counts = Counter()
    total_rows = 0

    print("Profiling current loan delinquency status...")

    if not PERF_FILE.exists():
        print(f"ERROR: File not found: {PERF_FILE}")
        return

    with PERF_FILE.open("r", encoding="utf-8-sig") as file:
        for line in file:
            columns = line.rstrip("\r\n").split("|")
            total_rows += 1

            # Field 4 is Current Loan Delinquency Status (1-based).
            status = columns[3].strip()
            status_counts[status if status else "(blank)"] += 1

    print(f"\nTotal records: {total_rows:,}")
    print("\nDelinquency status distribution:")

    for status, count in status_counts.most_common():
        percentage = count / total_rows * 100
        print(f"{status:>10}: {count:>12,} ({percentage:6.2f}%)")

    print("\nProfiling complete.")


if __name__ == "__main__":
    main()
