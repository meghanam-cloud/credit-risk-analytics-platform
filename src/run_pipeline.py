
from pathlib import Path
import getpass
import os
import subprocess
import sys

import psycopg


PROJECT_DIR = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_DIR / "sql" / "06_refresh_analytics.sql"
LOADER_SCRIPT = PROJECT_DIR / "src" / "load_to_postgres.py"
QUALITY_SCRIPT = PROJECT_DIR / "src" / "run_data_quality_checks.py"


def run_script(script_path: Path, env: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"Running: {script_path.name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_DIR,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_path.name} failed with exit code {result.returncode}"
        )


def refresh_analytics(password: str) -> None:
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")

    print(f"\n{'=' * 60}")
    print("Refreshing analytics tables")
    print("=" * 60)

    # psycopg executes the SQL in a transaction.
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="credit_risk_db",
        user="postgres",
        password=password,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(SQL_FILE.read_text(encoding="utf-8"))

    print("Analytics tables refreshed successfully.")


def main() -> int:
    password = os.getenv("PGPASSWORD")

    if not password:
        password = getpass.getpass("PostgreSQL password: ")

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    try:
        # 1. Load validated source data into staging.
        run_script(LOADER_SCRIPT, env)

        # 2. Rebuild analytics tables from staging.
        refresh_analytics(password)

        # 3. Run all data-quality checks.
        run_script(QUALITY_SCRIPT, env)

    except Exception as exc:
        print(f"\nPIPELINE FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"\n{'=' * 60}")
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
