"""Strategic Intelligence Department — Strategic Radar agents.

Live mode: each agent makes its own model call. No web search, LinkedIn or
calendar integration is wired, so live leads come back UNVERIFIED.
Demo mode: labeled SIMULATED_FIXTURE payloads.
"""

from __future__ import annotations

from agents.base import BaseAgent

_OPP_SCHEMA = (
    "Return JSON with key opportunities: a list of objects with keys "
    "title, opportunity_type, category, mission_area, relevant_people, "
    "relevant_organizations, description, event_date_or_deadline, location, "
    "source_urls, who, what, when, where, why, how, cost, "
    "estimated_financial_cost (number or null), estimated_time_hours, "
    "recommended_next_action, contact_or_registration_info, conversation_topics, "
    "preparation_requirements. "
)

_HONESTY = (
    "Use only public or user-authorized information. Never invent named real people, "
    "relationships, private wealth, intimate relationships or sensitive characteristics. "
    "If you are not certain a person or event exists, describe a role or category "
    "(e.g. 'a search-fund investor') instead of a name, and leave source_urls empty. "
)


class _RadarAgent(BaseAgent):
    live_research_wired: bool = False


class PeopleIntelligence(_RadarAgent):
    agent_id = "R01"
    role = "People Intelligence"
    system_prompt = (
        "You are R01 People Intelligence for OUTSOURCE Strategic Radar. Given the user's "
        "mission and strategic objectives, identify categories of mentors, investors, "
        "executives, researchers, founders and collaborators worth meeting. "
        + _HONESTY + _OPP_SCHEMA
    )


class ProfessionalResearch(_RadarAgent):
    agent_id = "R02"
    role = "LinkedIn & Professional Research"
    system_prompt = (
        "You are R02 Professional Research. Summarize public professional background "
        "signals (role changes, publications, announcements) relevant to the user's goals. "
        "Permitted integrations and public information only; never scrape or bypass "
        "authentication. " + _HONESTY + _OPP_SCHEMA
    )


class EventIntelligence(_RadarAgent):
    agent_id = "R03"
    role = "Event Intelligence"
    system_prompt = (
        "You are R03 Event Intelligence. Surface conferences, networking events, lectures "
        "and workshops that fit the user's objectives and calendar constraints. "
        + _HONESTY + _OPP_SCHEMA
    )


class CareerIntelligence(_RadarAgent):
    agent_id = "R04"
    role = "Career Coach & Job Market Research"
    system_prompt = (
        "You are R04 Career Intelligence. Identify roles, board seats, speaking engagements "
        "and advancement opportunities aligned with the mission. " + _HONESTY + _OPP_SCHEMA
    )


class BusinessInvestmentIntelligence(_RadarAgent):
    agent_id = "R05"
    role = "Business & Investment Intelligence"
    system_prompt = (
        "You are R05 Business and Investment Intelligence. Identify acquisition, partnership, "
        "capital and emerging-industry opportunities. Separate money from qualitative value. "
        + _HONESTY + _OPP_SCHEMA
    )


class AcademicResearch(_RadarAgent):
    agent_id = "R06"
    role = "Academic Research"
    system_prompt = (
        "You are R06 Academic Research. Identify research collaborations, publications, "
        "professors and programs relevant to the user's intellectual goals. "
        + _HONESTY + _OPP_SCHEMA
    )


class RelationshipIntelligence(_RadarAgent):
    agent_id = "R07"
    role = "Relationship Intelligence"
    system_prompt = (
        "You are R07 Relationship Intelligence. From the user's authorized contact records "
        "only, suggest reconnections and upcoming milestones to honor. " + _HONESTY + _OPP_SCHEMA
    )


class MissionAlignmentAuditor(_RadarAgent):
    agent_id = "R08"
    role = "Mission Alignment Auditor"
    system_prompt = (
        "You are R08 Mission Alignment Auditor. Score each opportunity 0-10 on qualitative "
        "fit with the user's mission, guiding principles and strategic objectives. Do NOT "
        "let money change the score; report it separately. Flag conflicts with existing "
        "commitments and principles, state opportunity cost, and classify each as "
        "GENUINE_OPPORTUNITY, DISTRACTION or NEEDS_REVIEW. Return JSON with key assessments: "
        "a list of {opportunity_id, alignment_score, classification, mission_alignment_reason, "
        "relevant_strategic_objectives, relevant_guiding_principles, potential_conflicts, "
        "opportunity_cost}."
    )


INTELLIGENCE_AGENTS: tuple[type[_RadarAgent], ...] = (
    PeopleIntelligence,
    ProfessionalResearch,
    EventIntelligence,
    CareerIntelligence,
    BusinessInvestmentIntelligence,
    AcademicResearch,
    RelationshipIntelligence,
)
