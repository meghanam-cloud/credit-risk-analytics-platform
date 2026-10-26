
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

FILES = {
    "sample_orig_2020.txt": 31,
    "sample_perf_2020.txt": 35,
}


def validate_file(filename, expected_columns):
    file_path = RAW_DIR / filename
    total_rows = 0
    invalid_rows = 0

    print(f"\nValidating: {filename}")

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False

    with file_path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            total_rows += 1
            columns = line.rstrip("\r\n").split("|")

            if len(columns) != expected_columns:
                invalid_rows += 1

                if invalid_rows <= 10:
                    print(
                        f"Invalid row {line_number}: "
                        f"expected {expected_columns} fields, "
                        f"found {len(columns)}"
                    )

    print(f"Total rows: {total_rows:,}")
    print(f"Invalid rows: {invalid_rows:,}")

    if invalid_rows == 0:
        print("RESULT: PASS")
        return True

    print("RESULT: CHECK REQUIRED")
    return False


def main():
    results = []

    for filename, expected_columns in FILES.items():
        results.append(validate_file(filename, expected_columns))

    print("\n--- FINAL SUMMARY ---")

    if all(results):
        print("Both files passed field-count validation.")
    else:
        print("At least one file needs further inspection.")


if __name__ == "__main__":
    main()
