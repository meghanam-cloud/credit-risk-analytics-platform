import os
import getpass
import psycopg

DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_NAME = os.getenv("PGDATABASE", "credit_risk_db")
DB_USER = os.getenv("PGUSER", "postgres")

password = getpass.getpass("Enter your PostgreSQL password: ")

try:
    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            database, version = cur.fetchone()

    print(f"Connection successful! Database: {database}")
    print(f"PostgreSQL: {version.split(',')[0]}")

except psycopg.OperationalError as exc:
    print("Connection failed. Check the password and PostgreSQL service.")
    print(f"Details: {exc}")
