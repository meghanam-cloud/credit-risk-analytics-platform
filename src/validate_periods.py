
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent.parent
PERF_FILE = PROJECT_DIR / "data" / "raw" / "sample_perf_2020.txt"


def main():
    total_rows = 0
    invalid_periods = 0
    earliest_period = None
    latest_period = None
    invalid_examples = []

    print("Validating monthly reporting periods...")

    if not PERF_FILE.exists():
        print(f"ERROR: File not found: {PERF_FILE}")
        return

    with PERF_FILE.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            columns = line.rstrip("\r\n").split("|")
            total_rows += 1

            if len(columns) < 2:
                invalid_periods += 1
                if len(invalid_examples) < 10:
                    invalid_examples.append((line_number, "Missing Period field"))
                continue

            period = columns[1].strip()

            try:
                if len(period) != 6:
                    raise ValueError("Expected YYYYMM")

                parsed_period = datetime.strptime(period, "%Y%m")

                if parsed_period.strftime("%Y%m") != period:
                    raise ValueError("Invalid reporting period")

                if earliest_period is None or period < earliest_period:
                    earliest_period = period

                if latest_period is None or period > latest_period:
                    latest_period = period

            except ValueError:
                invalid_periods += 1
                if len(invalid_examples) < 10:
                    invalid_examples.append((line_number, period))

    print(f"\nTotal rows checked: {total_rows:,}")
    print(f"Invalid periods: {invalid_periods:,}")

    if earliest_period:
        print(f"Earliest valid period: {earliest_period}")
    if latest_period:
        print(f"Latest valid period: {latest_period}")

    if invalid_examples:
        print("\nFirst invalid examples:")
        for line_number, period in invalid_examples:
            print(f"Line {line_number}: {period}")

    if invalid_periods == 0:
        print("\nRESULT: PASS — all reporting periods are valid.")
    else:
        print("\nRESULT: CHECK REQUIRED — inspect invalid periods.")


if __name__ == "__main__":
    main()
