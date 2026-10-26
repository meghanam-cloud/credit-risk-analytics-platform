
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

ORIG_FILE = RAW_DIR / "sample_orig_2020.txt"
PERF_FILE = RAW_DIR / "sample_perf_2020.txt"


def profile_origination():
    total_rows = 0
    unique_loans = set()
    blank_loan_ids = 0

    print("\n=== ORIGINATION DATA ===")

    with ORIG_FILE.open("r", encoding="utf-8-sig") as file:
        for line in file:
            columns = line.rstrip("\r\n").split("|")
            total_rows += 1

            # Field 20 is the Loan Identifier (1-based).
            loan_id = columns[19].strip()

            if loan_id:
                unique_loans.add(loan_id)
            else:
                blank_loan_ids += 1

    print(f"Total rows: {total_rows:,}")
    print(f"Unique loan IDs: {len(unique_loans):,}")
    print(f"Blank loan IDs: {blank_loan_ids:,}")

    return unique_loans


def profile_performance(origination_loans):
    total_rows = 0
    unique_loans = set()
    blank_loan_ids = 0
    unmatched_rows = 0
    sample_periods = set()

    print("\n=== MONTHLY PERFORMANCE DATA ===")

    with PERF_FILE.open("r", encoding="utf-8-sig") as file:
        for line in file:
            columns = line.rstrip("\r\n").split("|")
            total_rows += 1

            loan_id = columns[0].strip()
            period = columns[1].strip()

            if loan_id:
                unique_loans.add(loan_id)

                if loan_id not in origination_loans:
                    unmatched_rows += 1
            else:
                blank_loan_ids += 1

            if period and len(sample_periods) < 12:
                sample_periods.add(period)

    print(f"Total monthly records: {total_rows:,}")
    print(f"Unique loan IDs: {len(unique_loans):,}")
    print(f"Blank loan IDs: {blank_loan_ids:,}")
    print(f"Rows with loan IDs absent from origination: {unmatched_rows:,}")
    print(f"Sample reporting periods: {sorted(sample_periods)}")


def main():
    if not ORIG_FILE.exists() or not PERF_FILE.exists():
        print("ERROR: One or both source files are missing from data/raw.")
        return

    origination_loans = profile_origination()
    profile_performance(origination_loans)

    print("\nProfiling complete.")


if __name__ == "__main__":
    main()
