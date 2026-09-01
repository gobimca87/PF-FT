import pytest

from pff_fa_ai.integration.tools.policy import ToolRiskClass, requires_hil


@pytest.mark.parametrize(
    "risk_class,expected",
    [
        (ToolRiskClass.READ, False),
        (ToolRiskClass.LOW_RISK_WRITE, False),
        (ToolRiskClass.HIGH_RISK_WRITE, True),
        (ToolRiskClass.TRANSACTIONAL, True),
    ],
)
def test_should_require_hil_only_for_high_risk_operations(
    risk_class: ToolRiskClass, expected: bool
) -> None:
    assert requires_hil(risk_class) is expected
