
import os
import getpass
import psycopg


DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "credit_risk_db"
DB_USER = "postgres"

EXPECTED_ORIGINATION_ROWS = 50_000
EXPECTED_PERFORMANCE_ROWS = 2_517_857
EXPECTED_MONTHS = 75


def main():
    password = os.getenv("PGPASSWORD")

    if not password:
        password = getpass.getpass("PostgreSQL password: ")

    checks = []

    try:
        with psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=password,
            connect_timeout=10,
        ) as conn:
            with conn.cursor() as cur:

                cur.execute(
                    "SELECT COUNT(*) FROM staging.origination_raw"
                )
                origination_rows = cur.fetchone()[0]
                checks.append((
                    "Origination row count",
                    origination_rows == EXPECTED_ORIGINATION_ROWS,
                    f"Found {origination_rows:,} rows",
                ))

                cur.execute(
                    "SELECT COUNT(*) FROM staging.performance_raw"
                )
                performance_rows = cur.fetchone()[0]
                checks.append((
                    "Performance row count",
                    performance_rows == EXPECTED_PERFORMANCE_ROWS,
                    f"Found {performance_rows:,} rows",
                ))

                cur.execute("""
                    SELECT COUNT(DISTINCT loan_identifier)
                    FROM analytics.loan_origination
                """)
                unique_loans = cur.fetchone()[0]
                checks.append((
                    "Unique origination loans",
                    unique_loans == EXPECTED_ORIGINATION_ROWS,
                    f"Found {unique_loans:,} unique loans",
                ))

                cur.execute("""
                    SELECT COUNT(*)
                    FROM staging.origination_raw o
                    LEFT JOIN staging.performance_raw p
                      ON BTRIM(o.loan_identifier) =
                         BTRIM(p.loan_identifier)
                    WHERE p.loan_identifier IS NULL
                """)
                missing_performance = cur.fetchone()[0]
                checks.append((
                    "Origination loans missing performance",
                    missing_performance == 0,
                    f"Found {missing_performance:,} unmatched origination rows",
                ))

                cur.execute("""
                    SELECT COUNT(*)
                    FROM staging.performance_raw p
                    LEFT JOIN staging.origination_raw o
                      ON BTRIM(p.loan_identifier) =
                         BTRIM(o.loan_identifier)
                    WHERE o.loan_identifier IS NULL
                """)
                missing_origination = cur.fetchone()[0]
                checks.append((
                    "Performance loans missing origination",
                    missing_origination == 0,
                    f"Found {missing_origination:,} unmatched performance rows",
                ))

                cur.execute("""
                    SELECT
                        COUNT(*),
                        MIN(reporting_month),
                        MAX(reporting_month),
                        COALESCE(SUM(total_records), 0)
                    FROM analytics.monthly_delinquency_summary
                """)
                months, first_month, last_month, summary_rows = cur.fetchone()

                checks.append((
                    "Monthly summary periods",
                    months == EXPECTED_MONTHS,
                    f"Found {months} periods ({first_month} to {last_month})",
                ))

                checks.append((
                    "Monthly summary record total",
                    summary_rows == EXPECTED_PERFORMANCE_ROWS,
                    f"Summary covers {summary_rows:,} records",
                ))

    except Exception as exc:
        print(f"\nERROR: {exc}")
        print("Check PostgreSQL is running and the database credentials are correct.")
        raise SystemExit(1)

    print("\nDATA QUALITY REPORT")
    print("=" * 55)

    for name, passed, details in checks:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {details}")

    passed_count = sum(1 for _, passed, _ in checks if passed)
    print("=" * 55)
    print(f"Result: {passed_count}/{len(checks)} checks passed")

    if passed_count != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
