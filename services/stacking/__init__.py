"""Multidimensional opportunity stacking engine."""

from services.stacking.chief_of_staff import recommend_bundle
from services.stacking.fixtures import ILLUSTRATIVE_OPPORTUNITIES, SAMPLE_LIFE_MANDATE
from services.stacking.hours import compare_hours
from services.stacking.scoring import compute_stacking_score

__all__ = [
    "ILLUSTRATIVE_OPPORTUNITIES",
    "SAMPLE_LIFE_MANDATE",
    "compare_hours",
    "compute_stacking_score",
    "recommend_bundle",
]