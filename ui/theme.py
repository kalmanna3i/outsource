"""Dark workspace: ink on cards, sage and champagne as the only accents."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap');

:root {
  --bg: #0B0E14;
  --card: #11161F;
  --secondary: #151C27;
  --text: #E9EDF2;
  --muted: #8D98A8;
  --sage: #80B5A4;
  --champagne: #B5A083;
  --line: rgba(255,255,255,.07);
}

.stApp {
  background: var(--bg);
  color: var(--text);
  color-scheme: dark;
  font-family: Inter, system-ui, sans-serif;
  font-size: 14px;
  font-weight: 400;
}

[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stWidgetLabel"] * {
  color: var(--text) !important;
  font-family: Inter, system-ui, sans-serif;
  font-weight: 400;
}
[data-testid="stMain"] [data-testid="stTextAreaRootElement"],
[data-testid="stMain"] [data-testid="stTextInputRootElement"],
[data-testid="stMain"] [data-testid="stNumberInputContainer"] {
  background-color: var(--card) !important;
  color: var(--text) !important;
}
[data-testid="stMain"] textarea,
[data-testid="stMain"] input:not([type="checkbox"]):not([type="radio"]) {
  background-color: transparent;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  caret-color: var(--text);
}
[data-testid="stMain"] textarea::placeholder,
[data-testid="stMain"] input::placeholder {
  color: var(--muted) !important;
  -webkit-text-fill-color: var(--muted) !important;
}

h1, h2, h3, [data-testid="stHeading"], [data-testid="stHeading"] * {
  font-family: Inter, system-ui, sans-serif !important;
  font-weight: 500 !important;
  color: var(--text);
  letter-spacing: 0;
}

[data-testid="stHeading"] h1 { font-size: 1.35rem !important; }
[data-testid="stHeading"] h2 { font-size: 1.05rem !important; }
[data-testid="stHeading"] h3, [data-testid="stHeading"] h4 { font-size: 0.95rem !important; }

.life-headline {
  font-family: Inter, system-ui, sans-serif;
  font-weight: 500;
  font-size: 30px;
  color: var(--text);
  margin: 0;
  line-height: 1.2;
}
.life-meta {
  font-size: 13px;
  color: var(--muted);
  margin: 0.2rem 0 0;
}
.life-mission {
  font-family: Inter, system-ui, sans-serif;
  font-weight: 400;
  font-size: 14px;
  color: var(--text);
  margin: 0.45rem 0 0.55rem;
  max-width: none;
  line-height: 1.45;
  overflow: visible;
  white-space: normal;
}
.section-label {
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 0.35rem;
}
.metric-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.35rem;
  margin: 0 0 0.4rem;
  position: relative;
  z-index: 2;
}
.metric-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 0.18rem 0.45rem 0.14rem;
  min-width: 0;
  flex: 1 1 0;
}
.metric-card .k {
  font-size: 0.58rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted);
  line-height: 1.2;
}
.metric-card .v {
  font-size: 28px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.1;
}
.spark { width: 100%; height: 22px; display: block; margin-top: 0.2rem; }
.spark polyline, .spark circle { fill: none; stroke: #80B5A4; stroke-width: 1; }
.metric-card .s {
  font-size: 0.62rem;
  color: var(--muted);
  line-height: 1.2;
}
[data-testid="stMain"] iframe {
  width: 100% !important;
  border: 0;
}
.network-legend {
  font-family: Inter, system-ui, sans-serif;
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--muted);
  margin: 0.15rem 0 0.5rem;
}

.panel {
  background: var(--card);
  border: 1px solid var(--line);
  color: var(--text);
  padding: 1rem 1.1rem;
  margin-bottom: 0.8rem;
}
.panel h3 { color: var(--text); margin-top: 0; }
.kpi {
  font-size: 1.25rem;
  color: var(--text);
  font-family: Inter, system-ui, sans-serif;
  font-weight: 500;
}
.muted { color: var(--muted); font-size: 0.92rem; }
.status-op { color: var(--sage); font-weight: 500; }
.status-sim { color: var(--champagne); font-weight: 500; }
.status-plan { color: var(--muted); font-weight: 500; }
.stButton>button {
  background: var(--card);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 2px;
  font-family: Inter, system-ui, sans-serif;
  font-weight: 400;
}
.stButton>button:hover {
  border-color: var(--sage);
  color: var(--text);
}
section[data-testid="stSidebar"] {
  background: var(--bg);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] {
  font-family: Inter, system-ui, sans-serif;
}
section[data-testid="stSidebar"] * {
  color: var(--text) !important;
}
section[data-testid="stSidebar"] [data-testid="stIconMaterial"] {
  font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
  font-weight: 400 !important;
}
section[data-testid="stSidebar"] .north-star-kicker {
  color: var(--champagne) !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.75rem;
  font-weight: 500;
  margin: 0.2rem 0 0.25rem;
}
section[data-testid="stSidebar"] .north-star {
  color: var(--text) !important;
  font-family: Inter, system-ui, sans-serif;
  font-weight: 400;
  font-size: 0.95rem;
  line-height: 1.4;
  margin: 0 0 0.8rem;
}
section[data-testid="stSidebar"] .mode-line {
  color: var(--muted) !important;
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  margin-top: 0.6rem;
}
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] button[data-testid^="stBaseButton"] {
  background: transparent;
  color: var(--text);
  border: none;
  border-left: 1px solid transparent;
  border-radius: 2px;
  text-align: left !important;
  justify-content: flex-start !important;
  font-weight: 400 !important;
  font-size: 13px !important;
  min-height: 1.4rem;
  padding-top: 0.05rem;
  padding-bottom: 0.05rem;
  padding-left: 0.55rem;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] details summary {
  font-size: 0.78rem;
  padding-top: 0.28rem;
  padding-bottom: 0.28rem;
}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] * {
  color: var(--sage) !important;
  background: rgba(128, 181, 164, 0.08);
  border-left-color: var(--sage);
  font-weight: 500 !important;
}
div[data-testid="stSidebarNav"] { display: none; }
.opp-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-left: 4px solid var(--sage);
  color: var(--text);
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.9rem;
}
.opp-card.distraction { border-left-color: var(--champagne); }
.opp-card.review { border-left-color: var(--muted); }
.opp-cat {
  font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--sage);
}
.opp-title {
  font-family: Inter, system-ui, sans-serif;
  font-weight: 500;
  font-size: 1.15rem;
  color: var(--text);
}
.opp-grid { display: grid; grid-template-columns: 5.5rem 1fr; gap: 0.15rem 0.6rem; font-size: 0.9rem; margin-top: 0.4rem; }
.opp-grid b { color: var(--text); font-weight: 500; }
.badge {
  display: inline-block; padding: 0.1rem 0.5rem; margin-right: 0.35rem; font-size: 0.72rem;
  letter-spacing: 0.05em; border: 1px solid; border-radius: 2px;
}
.badge-sim { color: var(--champagne); border-color: var(--champagne); }
.badge-ver { color: var(--sage); border-color: var(--sage); }
.badge-unv { color: var(--muted); border-color: var(--muted); }
.badge-genuine { color: #090F18; background: var(--sage); border-color: var(--sage); }
.badge-distraction { color: #090F18; background: var(--champagne); border-color: var(--champagne); }
.badge-review { color: var(--text); background: transparent; border-color: var(--muted); }
.next-action { margin-top: 0.5rem; color: var(--text); font-weight: 500; }
</style>
"""


MODULE_STATUS = {
    "Daily Briefing": ("Operational", "status-op"),
    "Life Mandate": (
        "Operational mandate · discovery dataset Simulated · scores Operational",
        "status-op",
    ),
    "My Life Blueprint": ("Operational", "status-op"),
    "My Decisions": ("Operational", "status-op"),
    "My Work": ("Operational", "status-op"),
    "My Attention": ("Operational", "status-op"),
    "My Calendar": ("Operational", "status-op"),
    "My People": ("Simulated integration", "status-sim"),
    "Strategic Radar": (
        "Simulated discovery (illustrative fixtures) · research-to-action Operational",
        "status-sim",
    ),
    "My Network": ("Simulated — illustrative graph; 1 verified public fact", "status-sim"),
    "My Career": ("Planned / not implemented", "status-plan"),
    "My Financial Future": ("Simulated integration", "status-sim"),
    "Agent Activity": ("Operational", "status-op"),
    "Contextual Opportunities": ("Simulated integration", "status-sim"),
    "Opportunity Stacking": ("Simulated integration", "status-sim"),
    "Settings": ("Operational", "status-op"),
}
