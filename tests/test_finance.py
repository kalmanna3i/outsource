"""Financial projection tests."""

from services.finance import project_cashflow


def test_projection_grows_with_surplus() -> None:
    result = project_cashflow(
        starting_cash=10_000,
        annual_income=100_000,
        annual_expenses=70_000,
        years=5,
        inflation=0.0,
        income_growth=0.0,
    )
    assert len(result.years) == 5
    assert result.years[-1].net_worth == 10_000 + 5 * 30_000
    assert any("Taxes omitted" in s for s in result.simplifications)


def test_inflation_raises_expenses() -> None:
    result = project_cashflow(
        starting_cash=0,
        annual_income=50_000,
        annual_expenses=40_000,
        years=2,
        inflation=0.10,
        income_growth=0.0,
    )
    assert result.years[1].expenses > result.years[0].expenses
