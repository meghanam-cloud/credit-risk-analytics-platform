
from pathlib import Path
from collections import defaultdict

PROJECT_DIR = Path(__file__).resolve().parent.parent
PERF_FILE = PROJECT_DIR / "data" / "raw" / "sample_perf_2020.txt"


def main():
    if not PERF_FILE.exists():
        print(f"ERROR: File not found: {PERF_FILE}")
        return

    seen = set()
    duplicate_count = 0
    duplicate_examples = []
    total_rows = 0

    print("Checking loan ID + reporting period duplicates...")

    with PERF_FILE.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            columns = line.rstrip("\r\n").split("|")
            total_rows += 1

            loan_id = columns[0].strip()
            period = columns[1].strip()
            key = (loan_id, period)

            if key in seen:
                duplicate_count += 1

                if len(duplicate_examples) < 10:
                    duplicate_examples.append(
                        (line_number, loan_id, period)
                    )
            else:
                seen.add(key)

    print(f"\nTotal performance rows: {total_rows:,}")
    print(f"Unique loan-period combinations: {len(seen):,}")
    print(f"Duplicate rows: {duplicate_count:,}")

    if duplicate_examples:
        print("\nFirst duplicate examples:")
        for line_number, loan_id, period in duplicate_examples:
            print(
                f"Line {line_number}: "
                f"Loan ID={loan_id}, Period={period}"
            )

    if duplicate_count == 0:
        print("\nRESULT: PASS — no duplicate loan-period records found.")
    else:
        print("\nRESULT: CHECK REQUIRED — investigate duplicate records.")


if __name__ == "__main__":
    main()
