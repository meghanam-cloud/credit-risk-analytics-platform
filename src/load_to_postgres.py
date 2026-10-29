
from pathlib import Path
import getpass
import sys
import os

import psycopg
from psycopg import sql

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

FILES = [
    {
        "path": RAW_DIR / "sample_orig_2020.txt",
        "table": "origination_raw",
        "expected_fields": 31,
        "expected_rows": 50_000,
    },
    {
        "path": RAW_DIR / "sample_perf_2020.txt",
        "table": "performance_raw",
        "expected_fields": 35,
        "expected_rows": 2_517_857,
    },
]


def main():
    password = os.getenv("PGPASSWORD")

    if not password:
        password = getpass.getpass("PostgreSQL password: ")
    with psycopg.connect(
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5432")),
    dbname=os.getenv("PGDATABASE", "credit_risk_db"),
    user=os.getenv("PGUSER", "postgres"),
    password=password,
    ) as conn:
        with conn.cursor() as cur:
            for item in FILES:
                path = item["path"]
                table = item["table"]

                if not path.exists():
                    raise FileNotFoundError(f"File not found: {path}")

                print(f"\nChecking {path.name}...")
                source_rows = 0

                # Validate each line before loading.
                with path.open("r", encoding="utf-8") as source:
                    for line_number, line in enumerate(source, start=1):
                        if len(line.rstrip("\r\n").split("|")) != item["expected_fields"]:
                            raise ValueError(
                                f"{path.name}, line {line_number}: "
                                f"expected {item['expected_fields']} fields"
                            )
                        source_rows += 1

                if source_rows != item["expected_rows"]:
                    raise ValueError(
                        f"{path.name}: expected {item['expected_rows']} rows, "
                        f"found {source_rows}"
                    )

                # Avoid accidentally appending duplicate data on reruns.
                cur.execute(
                    sql.SQL("TRUNCATE TABLE staging.{}").format(
                        sql.Identifier(table)
                    )
                )

                print(f"Loading {source_rows:,} rows into staging.{table}...")

                copy_statement = sql.SQL(
                    "COPY staging.{} FROM STDIN WITH "
                    "(FORMAT csv, DELIMITER '|', QUOTE '\"', "
                    "ESCAPE '\"', NULL '')"
                ).format(sql.Identifier(table))

                with cur.copy(copy_statement) as copy:
                    with path.open("r", encoding="utf-8", newline="") as source:
                        for line in source:
                            copy.write(line)

                cur.execute(
                    sql.SQL("SELECT COUNT(*) FROM staging.{}").format(
                        sql.Identifier(table)
                    )
                )
                loaded_rows = cur.fetchone()[0]

                if loaded_rows != source_rows:
                    raise RuntimeError(
                        f"Row count mismatch for {table}: "
                        f"source={source_rows}, loaded={loaded_rows}"
                    )

                print(f"PASS: {table}: {loaded_rows:,} rows loaded.")

    print("\nAll files loaded and row counts verified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
