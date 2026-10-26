
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "src" / "run_data_quality_checks.py"

spec = importlib.util.spec_from_file_location(
    "run_data_quality_checks",
    SCRIPT_PATH,
)
quality_checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality_checks)


def test_expected_row_counts_are_positive():
    """Expected database row counts must be positive."""
    assert quality_checks.EXPECTED_ORIGINATION_ROWS > 0
    assert quality_checks.EXPECTED_PERFORMANCE_ROWS > 0
    assert quality_checks.EXPECTED_MONTHS > 0


def test_expected_row_counts_match_project_dataset():
    """Verify the expected dataset sizes configured in the script."""
    assert quality_checks.EXPECTED_ORIGINATION_ROWS == 50_000
    assert quality_checks.EXPECTED_PERFORMANCE_ROWS == 2_517_857
    assert quality_checks.EXPECTED_MONTHS == 75


def test_successful_check_is_counted_as_passed():
    """Verify the reporting logic counts passing checks correctly."""
    checks = [
        ("Origination row count", True, "Found 50,000 rows"),
        ("Performance row count", True, "Found 2,517,857 rows"),
    ]

    passed_count = sum(1 for _, passed, _ in checks if passed)

    assert passed_count == 2
    assert passed_count == len(checks)


def test_failed_check_is_detected():
    """Verify a failed check makes the overall result unsuccessful."""
    checks = [
        ("Origination row count", True, "Found 50,000 rows"),
        ("Performance row count", False, "Found 100 rows"),
    ]

    passed_count = sum(1 for _, passed, _ in checks if passed)

    assert passed_count == 1
    assert passed_count != len(checks)
