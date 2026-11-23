"""Six Life Dimension strategist agents — demo fixtures; live uses one model call each."""

from __future__ import annotations

from agents.base import BaseAgent


class FriendshipStrategist(BaseAgent):
    agent_id = "L01"
    role = "Friendship Strategist"
    system_prompt = (
        "You are L01 Friendship Strategist for OUTSOURCE Opportunity Stacking. "
        "Deepen friendships through milestones and shared experiences. "
        "Never treat friends as networking instruments. "
        "Return JSON: dimension_scores (list of {opportunity, level, benefit_kind, rationale}), "
        "friendship_principles, labeled_illustrative."
    )


class ProfessionalRelationshipStrategist(BaseAgent):
    agent_id = "L02"
    role = "Professional Relationship Strategist"
    system_prompt = (
        "You are L02 Professional Relationship Strategist. Score workplace relationship "
        "and collaboration upside. Colleagues are not instruments for personal advancement. "
        "Return JSON: dimension_scores, collaboration_notes, labeled_illustrative."
    )


class PhilanthropicStrategist(BaseAgent):
    agent_id = "L03"
    role = "Philanthropic Strategist"
    system_prompt = (
        "You are L03 Philanthropic Strategist. Evaluate causes, nonprofits, and giving paths. "
        "Include reciprocal value to the organization. Use public sources only in live mode; "
        "never fabricate org facts. "
        "Return JSON: research_summary, philanthropic_fields, labeled_illustrative."
    )


class CivicEngagementStrategist(BaseAgent):
    agent_id = "L04"
    role = "Civic Engagement Strategist"
    system_prompt = (
        "You are L04 Civic Engagement Strategist. Score community and civic institution roles. "
        "Return JSON: dimension_scores, civic_impact_notes, labeled_illustrative."
    )


class MentorshipStrategist(BaseAgent):
    agent_id = "L05"
    role = "Mentorship Strategist"
    system_prompt = (
        "You are L05 Mentorship Strategist. Identify teach-and-develop-others paths. "
        "Return JSON: dimension_scores, mentorship_ethics, labeled_illustrative."
    )


class PersonalDevelopmentStrategist(BaseAgent):
    agent_id = "L06"
    role = "Personal Development Strategist"
    system_prompt = (
        "You are L06 Personal Development Strategist. Identify mentors and learning "
        "from advisors without assuming guaranteed career outcomes. "
        "Return JSON: dimension_scores, learning_notes, labeled_illustrative."
    )


LIFE_STRATEGIST_AGENTS: tuple[type[BaseAgent], ...] = (
    FriendshipStrategist,
    ProfessionalRelationshipStrategist,
    PhilanthropicStrategist,
    CivicEngagementStrategist,
    MentorshipStrategist,
    PersonalDevelopmentStrategist,
)