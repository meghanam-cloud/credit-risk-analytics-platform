
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_root_exists():
    """Verify that the project root can be located."""
    assert PROJECT_ROOT.is_dir()


def test_app_file_exists():
    """Verify that the Streamlit dashboard exists."""
    assert (PROJECT_ROOT / "app.py").is_file()


def test_pipeline_files_exist():
    """Verify that the main pipeline scripts exist."""
    assert (PROJECT_ROOT / "src" / "load_to_postgres.py").is_file()
    assert (PROJECT_ROOT / "src" / "run_data_quality_checks.py").is_file()
    assert (PROJECT_ROOT / "src" / "run_pipeline.py").is_file()


def test_analytics_sql_exists():
    """Verify that the analytics refresh SQL file exists."""
    assert (PROJECT_ROOT / "sql" / "06_refresh_analytics.sql").is_file()
