"""Deterministic Parallel Life financial helpers (tested; simplifications labeled)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectionYear(BaseModel):
    year: int
    cash: float
    expenses: float
    net_worth: float


class ProjectionResult(BaseModel):
    years: list[ProjectionYear]
    assumptions: list[str] = Field(default_factory=list)
    simplifications: list[str] = Field(default_factory=list)


def project_cashflow(
    *,
    starting_cash: float,
    annual_income: float,
    annual_expenses: float,
    years: int = 10,
    inflation: float = 0.025,
    income_growth: float = 0.03,
) -> ProjectionResult:
    """Simple deterministic projection. Not tax or retirement advice."""
    cash = starting_cash
    income = annual_income
    expenses = annual_expenses
    out: list[ProjectionYear] = []
    for y in range(1, years + 1):
        cash = cash + income - expenses
        out.append(
            ProjectionYear(year=y, cash=round(cash, 2), expenses=round(expenses, 2), net_worth=round(cash, 2))
        )
        income *= 1 + income_growth
        expenses *= 1 + inflation
    return ProjectionResult(
        years=out,
        assumptions=[
            f"Income growth {income_growth:.1%} / yr",
            f"Expense inflation {inflation:.1%} / yr",
            "No investment returns modeled in this simple path",
        ],
        simplifications=[
            "Taxes omitted (simplification)",
            "Retirement account rules omitted (simplification)",
            "No stochastic shocks",
        ],
    )
