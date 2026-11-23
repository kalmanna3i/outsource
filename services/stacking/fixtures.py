"""SIMULATED_FIXTURE / Illustrative opportunity data — not researched organizations."""

from __future__ import annotations

from core.models import (
    BenefitKind,
    ContributionLevel,
    DimensionContribution,
    EvidenceType,
    LifeDimension,
    MatrixCell,
    MatrixColumn,
    PhilanthropicResearchRecord,
    StackedOpportunity,
    LifeMandateSample,
)


def _cells(
    giving: ContributionLevel,
    career: ContributionLevel,
    learning: ContributionLevel,
    business: ContributionLevel,
    network: ContributionLevel,
    kinds: tuple[BenefitKind, ...] | None = None,
) -> list[MatrixCell]:
    default_kinds = kinds or (BenefitKind.DIRECT,) * 5
    cols = [
        MatrixColumn.GIVING_BACK,
        MatrixColumn.CAREER,
        MatrixColumn.LEARNING,
        MatrixColumn.BUSINESS,
        MatrixColumn.NETWORK,
    ]
    levels = [giving, career, learning, business, network]
    return [
        MatrixCell(
            column=col,
            level=lev,
            benefit_kind=default_kinds[i] if i < len(default_kinds) else BenefitKind.DIRECT,
            note="Illustrative — SIMULATED_FIXTURE",
        )
        for i, (col, lev) in enumerate(zip(cols, levels, strict=True))
    ]


ILLUSTRATIVE_OPPORTUNITIES: list[StackedOpportunity] = [
    StackedOpportunity(
        label="Illustrative — Community foundation investment committee",
        monthly_hours=6.0,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.PHILANTHROPIST,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
                rationale="Structured giving with governance exposure.",
            ),
            DimensionContribution(
                dimension=LifeDimension.MENTEE,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.COMPLEMENTARY,
                rationale="Learn allocator and fiduciary judgment.",
            ),
            DimensionContribution(
                dimension=LifeDimension.COLLEAGUE,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.INDIRECT,
                rationale="Professional credibility via civic leadership (not guaranteed promotion).",
            ),
        ],
        matrix=_cells(
            ContributionLevel.STRONG,
            ContributionLevel.MODERATE,
            ContributionLevel.STRONG,
            ContributionLevel.MODERATE,
            ContributionLevel.MODERATE,
        ),
        philanthropy=PhilanthropicResearchRecord(
            opportunity_label="Illustrative — Community foundation investment committee",
            mission="Illustrative regional grantmaking and endowment stewardship.",
            community_impact="Illustrative — deploys capital to local nonprofits.",
            governance="Illustrative — investment policy overseen by volunteer committee.",
            time_commitment_hours_month=6.0,
            financial_contribution="Illustrative — no personal donation required; time primary.",
            skills_given=["capital allocation review", "committee deliberation"],
            skills_gained=["nonprofit finance", "fiduciary process"],
            application_path="Illustrative — nomination via network introduction.",
            conflicts_of_interest=["Illustrative — disclose employer and board affiliations."],
            reciprocal_value_note=(
                "User would contribute disciplined investment review; not extract deal flow."
            ),
            evidence_type=EvidenceType.SIMULATED_FIXTURE,
        ),
        reciprocal_value="Disciplined investment analysis and meeting preparation for the committee.",
    ),
    StackedOpportunity(
        label="Illustrative — Entrepreneurship nonprofit mentor program",
        monthly_hours=5.0,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.MENTOR,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
            ),
            DimensionContribution(
                dimension=LifeDimension.FRIEND,
                level=ContributionLevel.LIMITED,
                benefit_kind=BenefitKind.OVERLAPPING,
                rationale="Shared cohort events may deepen friendships — counted once under mentor.",
            ),
            DimensionContribution(
                dimension=LifeDimension.MENTEE,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.COMPLEMENTARY,
                rationale="Exposure to founder problems sharpens own business judgment.",
            ),
        ],
        matrix=_cells(
            ContributionLevel.MODERATE,
            ContributionLevel.LIMITED,
            ContributionLevel.MODERATE,
            ContributionLevel.STRONG,
            ContributionLevel.STRONG,
        ),
        reciprocal_value="Office hours and candid feedback for early-stage founders.",
    ),
    StackedOpportunity(
        label="Illustrative — Infrastructure nonprofit board",
        monthly_hours=8.0,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.PHILANTHROPIST,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
            ),
            DimensionContribution(
                dimension=LifeDimension.COMMUNITY_MEMBER,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
            ),
            DimensionContribution(
                dimension=LifeDimension.COLLEAGUE,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.VERIFIED,
                rationale="Board listed on biography — not a guaranteed advancement channel.",
            ),
        ],
        matrix=_cells(
            ContributionLevel.STRONG,
            ContributionLevel.MODERATE,
            ContributionLevel.LIMITED,
            ContributionLevel.LIMITED,
            ContributionLevel.MODERATE,
            kinds=(
                BenefitKind.DIRECT,
                BenefitKind.SPECULATIVE,
                BenefitKind.INDIRECT,
                BenefitKind.INDIRECT,
                BenefitKind.INDIRECT,
            ),
        ),
        reciprocal_value="Governance oversight and strategic introductions for the mission.",
    ),
    StackedOpportunity(
        label="Illustrative — General volunteer program",
        monthly_hours=4.0,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.COMMUNITY_MEMBER,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.DIRECT,
            ),
        ],
        matrix=_cells(
            ContributionLevel.MODERATE,
            ContributionLevel.LIMITED,
            ContributionLevel.LIMITED,
            ContributionLevel.LIMITED,
            ContributionLevel.LIMITED,
        ),
        reciprocal_value="Reliable volunteer shifts and warmth toward staff and clients.",
    ),
    StackedOpportunity(
        label="Illustrative — University advisory council",
        monthly_hours=4.0,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.MENTOR,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.DIRECT,
            ),
            DimensionContribution(
                dimension=LifeDimension.MENTEE,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.COMPLEMENTARY,
            ),
            DimensionContribution(
                dimension=LifeDimension.COLLEAGUE,
                level=ContributionLevel.LIMITED,
                benefit_kind=BenefitKind.INDIRECT,
            ),
        ],
        matrix=_cells(
            ContributionLevel.MODERATE,
            ContributionLevel.MODERATE,
            ContributionLevel.STRONG,
            ContributionLevel.LIMITED,
            ContributionLevel.STRONG,
        ),
        reciprocal_value="Industry perspective for curriculum and student programming.",
    ),
    StackedOpportunity(
        label="Illustrative — Small business mentorship (accelerator)",
        monthly_hours=5.0,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.MENTOR,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
            ),
            DimensionContribution(
                dimension=LifeDimension.COLLEAGUE,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.INDIRECT,
                rationale="Workplace skills applied — colleagues are not instruments.",
            ),
        ],
        matrix=_cells(
            ContributionLevel.LIMITED,
            ContributionLevel.MODERATE,
            ContributionLevel.MODERATE,
            ContributionLevel.STRONG,
            ContributionLevel.MODERATE,
        ),
        reciprocal_value="Operator-level troubleshooting for small business owners.",
    ),
]

SAMPLE_LIFE_MANDATE = LifeMandateSample(
    title="Illustrative Life Mandate — Kay (SIMULATED_FIXTURE)",
    priorities=[
        "Give back with governance rigor, not performative volunteering",
        "Grow investor judgment without treating friendships as networking tools",
        "Cap civic commitments at 12 hours/month while in MBA final week",
        "Mentor founders where reciprocal learning is genuine",
    ],
    max_monthly_hours=12.0,
)