"""SIMULATED_FIXTURE data for Strategic Radar demo mode.

Every person, organization and event here is illustrative unless it carries a
source URL, a retrieval date and VERIFIED_SOURCE. Nothing below is a real
research result.
"""

from __future__ import annotations

from typing import Any

ILLUSTRATIVE = "[Illustrative]"
SIMULATED = "SIMULATED_FIXTURE"

VERIFIED_RETRIEVED = "2026-11-23"
YALE_SOM_ABOUT = "https://som.yale.edu/about"


def _opp(**kw: Any) -> dict[str, Any]:
    kw.setdefault("verification_status", SIMULATED)
    kw.setdefault("illustrative", True)
    kw.setdefault("source_urls", [])
    return kw


CAPITAL_PARTNER = _opp(
    title=f"{ILLUSTRATIVE} Potential capital partner for an operator-led acquisition",
    opportunity_type="introduction",
    category="Potential capital partner",
    mission_area="business ownership",
    relevant_people=[f"{ILLUSTRATIVE} Search-fund investor 'Investor A'"],
    relevant_organizations=[f"{ILLUSTRATIVE} Search-fund investor group"],
    description="A search-fund style investor that backs MBA operators acquiring small service businesses.",
    event_date_or_deadline="2026-12-15",
    location="Video call",
    who=f"{ILLUSTRATIVE} Investor A (search-fund investor persona)",
    what="Exploratory conversation about acquisition criteria and operator support",
    when="Before the investor's Q1 2027 fund deployment window (illustrative deadline Dec 15)",
    where="30-minute video call",
    why="Directly advances the business ownership objective: own and operate an AI-enabled business",
    how="Warm introduction via a Yale SOM alumni contact (HYPOTHETICAL path — not verified)",
    cost="~3 h prep + call; $0; competes with end-of-term deliverables",
    estimated_financial_cost=0.0,
    estimated_time_hours=3.0,
    estimated_time_commitment="3 hours (prep, call, follow-up)",
    nonfinancial_considerations=["Early-stage; no commitment expected", "Signals seriousness about acquisition path"],
    recommended_next_action="Ask an alumni contact whether a warm introduction is appropriate",
    contact_or_registration_info="Via alumni introduction (no direct contact on file)",
    conversation_topics=[
        "Investor's acquisition criteria (industry, size, geography)",
        "How AI-enabled operations change small-business valuations",
        "What support new operators receive in year one",
    ],
    preparation_requirements=[
        "One-page operator thesis",
        "Two example target industries with rationale",
        "Clear ask: advice, not capital, at this stage",
    ],
)

ACADEMIC_COLLAB = _opp(
    title=f"{ILLUSTRATIVE} Academic collaboration on AI and managerial judgment",
    opportunity_type="collaboration",
    category="Academic collaboration",
    mission_area="intellectual development",
    relevant_people=[f"{ILLUSTRATIVE} Faculty researcher 'Professor B'"],
    relevant_organizations=["Yale School of Management"],
    description="A faculty research project seeking MBA practitioners for a case study on AI-assisted managerial judgment.",
    event_date_or_deadline="2026-12-04",
    location="New Haven, CT",
    who=f"{ILLUSTRATIVE} Professor B (faculty researcher persona)",
    what="Contribute OUTSOURCE as a practitioner case on delegating work between AI and humans",
    when="Illustrative participant deadline Dec 4",
    where="Yale SOM, 165 Whitney Avenue, New Haven (address verified)",
    why="Advances intellectual development: contribute to research on AI and managerial judgment",
    how="Short email with a two-paragraph summary of the OUTSOURCE build and its evidence ledger",
    cost="~4 h over two weeks; $0; competes with job search time",
    estimated_financial_cost=0.0,
    estimated_time_hours=4.0,
    estimated_time_commitment="4 hours over two weeks",
    nonfinancial_considerations=["Builds research credibility", "Requires sharing anonymized build notes"],
    recommended_next_action="Send a short expression-of-interest email (draft prepared, not sent)",
    contact_or_registration_info="Faculty office email (look up on the official Yale SOM directory before sending)",
    conversation_topics=[
        "How OUTSOURCE separates AI work from human-only work",
        "Evidence ledger and honesty labels as a research instrument",
        "Measured token costs from the live run",
    ],
    preparation_requirements=[
        "Two-paragraph project summary",
        "Link to repo and BUILD_STATUS.md",
        "List of what data can and cannot be shared",
    ],
)

EXEC_EVENT = _opp(
    title=f"{ILLUSTRATIVE} Operators & AI executive roundtable",
    opportunity_type="event",
    category="Executive networking event",
    mission_area="career advancement",
    relevant_people=[],
    relevant_organizations=[f"{ILLUSTRATIVE} Operators & AI roundtable organizers"],
    description="An invitation-only evening roundtable where operating executives discuss deploying AI agents in mid-size companies.",
    event_date_or_deadline="2026-12-09",
    location="New York, NY",
    who=f"{ILLUSTRATIVE} ~30 operating executives (COO/CFO level)",
    what="Evening roundtable with structured small-group discussions",
    when="Illustrative date Dec 9; RSVP closes Dec 2",
    where="Midtown Manhattan (illustrative venue)",
    why="Advances career advancement: build a network of operators and executives",
    how="Request an invitation through the organizer form with a two-line bio",
    cost="~6 h incl. travel; ~$60 train fare; one evening",
    estimated_financial_cost=60.0,
    estimated_time_hours=6.0,
    estimated_time_commitment="6 hours including New Haven–NYC travel",
    nonfinancial_considerations=["Late return to New Haven", "High density of relevant operators"],
    recommended_next_action="Submit invitation request before Dec 2",
    contact_or_registration_info="Organizer registration form (illustrative)",
    conversation_topics=["Where AI agents fail in real operations", "Human-in-the-loop handoffs"],
    preparation_requirements=["Two-line bio", "Three questions for operators"],
)

EXEC_EVENT_DUP = {
    **EXEC_EVENT,
    "title": f"{ILLUSTRATIVE} Operators and AI Executive Roundtable",
    "description": "Executive roundtable (NYC) on deploying AI agents in mid-size companies — surfaced from a contact's public post.",
}

SPEAKING = _opp(
    title=f"{ILLUSTRATIVE} Speaking slot: student AI conference panel",
    opportunity_type="speaking",
    category="Professional speaking opportunity",
    mission_area="reputation & contribution",
    relevant_people=[f"{ILLUSTRATIVE} Panel organizer 'Organizer C'"],
    relevant_organizations=[f"{ILLUSTRATIVE} Student-run AI conference"],
    description="A call for practitioner speakers on a panel about personal AI agents and the future of managerial work.",
    event_date_or_deadline="2027-02-20",
    location="New Haven, CT",
    who=f"{ILLUSTRATIVE} Organizer C (student conference organizer persona)",
    what="15-minute panel contribution on building OUTSOURCE",
    when="Illustrative proposal deadline Jan 15, 2027; event Feb 20",
    where="On campus (illustrative)",
    why="Advances reputation & contribution: share practitioner insight publicly",
    how="Submit a 150-word abstract via the call-for-speakers form",
    cost="~8 h prep; $0; competes with spring recruiting",
    estimated_financial_cost=0.0,
    estimated_time_hours=8.0,
    estimated_time_commitment="8 hours (abstract, slides, rehearsal)",
    nonfinancial_considerations=["Public visibility", "Reuses MGT 409 final materials"],
    recommended_next_action="Draft a 150-word abstract from the MGT 409 report",
    contact_or_registration_info="Call-for-speakers form (illustrative)",
    conversation_topics=["Honest status labels for AI products", "Delegation boundaries"],
    preparation_requirements=["150-word abstract", "Speaker bio", "Three-slide outline"],
)

FRIEND_MILESTONE = _opp(
    title=f"{ILLUSTRATIVE} Friend's milestone: Sam Patel's capstone presentation",
    opportunity_type="milestone",
    category="Friend's upcoming milestone",
    mission_area="meaningful relationships",
    relevant_people=["Sam Patel (simulated People CRM contact)"],
    relevant_organizations=[],
    description="Sam Patel (MBA classmate in the simulated People CRM) has a capstone presentation on Dec 11.",
    event_date_or_deadline="2026-12-11",
    location="New Haven, CT",
    who="Sam Patel — MBA classmate (simulated CRM record)",
    what="Attend or send encouragement before the capstone presentation",
    when="Dec 11 (from simulated CRM milestone)",
    where="Campus (illustrative)",
    why="Advances meaningful relationships; honors the principle 'Show up for important personal milestones'",
    how="Short encouraging message the day before; attend if the calendar allows",
    cost="~1.5 h; $0",
    estimated_financial_cost=0.0,
    estimated_time_hours=1.5,
    estimated_time_commitment="1.5 hours",
    nonfinancial_considerations=["Reciprocates Sam's slide peer review"],
    recommended_next_action="Draft a short good-luck note and hold a calendar slot",
    contact_or_registration_info="From People CRM (simulated)",
    conversation_topics=["Sam's capstone topic", "Post-MBA plans"],
    preparation_requirements=["Check capstone time and room"],
)

DISTRACTION_PRESTIGE = _opp(
    title=f"{ILLUSTRATIVE} Paid '40 Under 40' listing offer",
    opportunity_type="award",
    category="Recognition offer",
    mission_area="personal branding",
    relevant_people=[],
    relevant_organizations=[f"{ILLUSTRATIVE} Pay-to-play awards publisher"],
    description="An unsolicited offer to be featured in a paid '40 Under 40' list for a $3,000 placement fee.",
    event_date_or_deadline="2026-12-31",
    location="Online",
    who=f"{ILLUSTRATIVE} Awards publisher sales team",
    what="Paid placement in a recognition list",
    when="Offer expires Dec 31 (illustrative)",
    where="Online",
    why="Claims visibility; no clear link to stated objectives",
    how="Pay the placement fee",
    cost="$3,000; ~2 h",
    estimated_financial_cost=3000.0,
    estimated_time_hours=2.0,
    estimated_time_commitment="2 hours",
    nonfinancial_considerations=["Pay-to-play recognition carries reputational risk"],
    recommended_next_action="Decline",
    risk_flags=["prestige_only"],
)

DISTRACTION_TONIGHT = _opp(
    title=f"{ILLUSTRATIVE} Token presale webinar tonight",
    opportunity_type="event",
    category="Investment webinar",
    mission_area="speculative trading",
    relevant_people=[],
    relevant_organizations=[f"{ILLUSTRATIVE} Token presale promoter"],
    description="A promotional webinar for a crypto token presale, streaming tonight at 9 PM ET.",
    event_date_or_deadline="2026-11-23",
    location="Online",
    who=f"{ILLUSTRATIVE} Presale promoters",
    what="Promotional webinar",
    when="Tonight 9 PM ET",
    where="Online",
    why="No link to stated objectives",
    how="Register",
    cost="2 h tonight; presale minimum $1,000",
    estimated_financial_cost=1000.0,
    estimated_time_hours=2.0,
    estimated_time_commitment="2 hours tonight",
    nonfinancial_considerations=["Speculative"],
    recommended_next_action="Ignore",
    risk_flags=["speculative"],
)


def intelligence_fixtures() -> dict[str, dict[str, Any]]:
    """Per-agent demo payloads. Includes deliberate duplicates and distractions."""
    return {
        "R01": {"opportunities": [CAPITAL_PARTNER, EXEC_EVENT]},
        "R02": {"opportunities": [EXEC_EVENT_DUP]},
        "R03": {"opportunities": [EXEC_EVENT, DISTRACTION_TONIGHT]},
        "R04": {"opportunities": [SPEAKING, DISTRACTION_PRESTIGE]},
        "R05": {"opportunities": [CAPITAL_PARTNER]},
        "R06": {"opportunities": [ACADEMIC_COLLAB]},
        "R07": {"opportunities": [FRIEND_MILESTONE]},
    }


def network_fixture() -> dict[str, list[dict[str, Any]]]:
    nodes = [
        {"node_id": "user", "label": "Kay Al Mannai", "node_type": "user"},
        {"node_id": "yale_som", "label": "Yale School of Management", "node_type": "university"},
        {"node_id": "new_haven", "label": "165 Whitney Ave, New Haven", "node_type": "association"},
        {"node_id": "sam", "label": "Sam Patel (simulated CRM)", "node_type": "person", "illustrative": True},
        {"node_id": "alex", "label": "Alex Rivera (simulated CRM)", "node_type": "person", "illustrative": True},
        {"node_id": "alumni", "label": f"{ILLUSTRATIVE} SOM alumni contact", "node_type": "person", "illustrative": True},
        {"node_id": "investor_a", "label": f"{ILLUSTRATIVE} Investor A", "node_type": "person", "illustrative": True},
        {"node_id": "prof_b", "label": f"{ILLUSTRATIVE} Professor B", "node_type": "person", "illustrative": True},
        {"node_id": "organizer_c", "label": f"{ILLUSTRATIVE} Organizer C", "node_type": "person", "illustrative": True},
        {"node_id": "roundtable", "label": f"{ILLUSTRATIVE} Operators & AI roundtable", "node_type": "event", "illustrative": True},
        {"node_id": "ai_ops", "label": "AI-enabled operations", "node_type": "industry"},
        {"node_id": "g_business", "label": "Goal: business ownership", "node_type": "goal"},
        {"node_id": "g_intellect", "label": "Goal: intellectual development", "node_type": "goal"},
        {"node_id": "g_career", "label": "Goal: career advancement", "node_type": "goal"},
        {"node_id": "g_reputation", "label": "Goal: reputation & contribution", "node_type": "goal"},
        {"node_id": "g_relationships", "label": "Goal: meaningful relationships", "node_type": "goal"},
    ]
    edges = [
        {
            "source": "yale_som", "target": "new_haven", "relation": "located at", "status": "VERIFIED",
            "source_url": YALE_SOM_ABOUT, "retrieved_at": VERIFIED_RETRIEVED,
            "note": "Address listed on the Yale SOM About page",
        },
        {"source": "user", "target": "yale_som", "relation": "MBA candidate", "status": "USER_PROVIDED"},
        {"source": "user", "target": "sam", "relation": "classmate (CRM)", "status": "USER_PROVIDED"},
        {"source": "user", "target": "alex", "relation": "close friend (CRM)", "status": "USER_PROVIDED"},
        {"source": "user", "target": "alumni", "relation": "possible intro path", "status": "HYPOTHETICAL",
         "note": "Not verified; would need user confirmation"},
        {"source": "alumni", "target": "investor_a", "relation": "possible intro path", "status": "HYPOTHETICAL"},
        {"source": "yale_som", "target": "prof_b", "relation": "illustrative affiliation", "status": "HYPOTHETICAL",
         "note": "Persona is illustrative; affiliation not verified"},
        {"source": "user", "target": "organizer_c", "relation": "cold outreach path", "status": "HYPOTHETICAL"},
        {"source": "user", "target": "roundtable", "relation": "invitation request path", "status": "HYPOTHETICAL"},
        {"source": "investor_a", "target": "ai_ops", "relation": "illustrative thesis", "status": "HYPOTHETICAL"},
        {"source": "investor_a", "target": "g_business", "relation": "serves", "status": "MISSION_LINK"},
        {"source": "prof_b", "target": "g_intellect", "relation": "serves", "status": "MISSION_LINK"},
        {"source": "roundtable", "target": "g_career", "relation": "serves", "status": "MISSION_LINK"},
        {"source": "organizer_c", "target": "g_reputation", "relation": "serves", "status": "MISSION_LINK"},
        {"source": "sam", "target": "g_relationships", "relation": "serves", "status": "MISSION_LINK"},
        {"source": "alex", "target": "g_relationships", "relation": "serves", "status": "MISSION_LINK"},
    ]
    return {"nodes": nodes, "edges": edges}
