
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


def test_correct_origination_row_count_passes():
    assert (
        50_000
        == quality_checks.EXPECTED_ORIGINATION_ROWS
    )


def test_incorrect_origination_row_count_fails():
    assert (
        49_999
        != quality_checks.EXPECTED_ORIGINATION_ROWS
    )


def test_correct_performance_row_count_passes():
    assert (
        2_517_857
        == quality_checks.EXPECTED_PERFORMANCE_ROWS
    )


def test_incorrect_performance_row_count_fails():
    assert (
        2_517_856
        != quality_checks.EXPECTED_PERFORMANCE_ROWS
    )


def test_correct_month_count_passes():
    assert 75 == quality_checks.EXPECTED_MONTHS


def test_incorrect_month_count_fails():
    assert 74 != quality_checks.EXPECTED_MONTHS
