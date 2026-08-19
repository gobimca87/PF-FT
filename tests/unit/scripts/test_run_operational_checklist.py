import pytest
from scripts.run_operational_checklist import main


def test_main_should_return_zero_for_a_clean_daily_run() -> None:
    exit_code = main(["--frequency", "DAILY"])

    assert exit_code == 0


def test_main_should_return_zero_for_an_empty_weekly_run_without_pip_audit_input() -> None:
    exit_code = main(["--frequency", "WEEKLY"])

    assert exit_code == 0


def test_main_should_require_a_frequency_argument() -> None:
    with pytest.raises(SystemExit):
        main([])
