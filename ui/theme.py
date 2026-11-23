"""Executive visual theme: deep navy, warm ivory, muted teal."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Source+Sans+3:wght@400;500;600&display=swap');

:root {
  --navy: #0B1F33;
  --navy-2: #14304A;
  --ivory: #F7F3EC;
  --teal: #3F6F7A;
  --teal-soft: #D7E4E7;
  --ink: #1A2430;
  --muted: #5C6B7A;
  --line: #D9D2C5;
  --warn: #8A5A2B;
}

.stApp {
  background: #F7F3EC;
  color: var(--ink);
  font-family: 'Source Sans 3', sans-serif;
}

h1, h2, h3, .brand-title {
  font-family: 'Cormorant Garamond', Georgia, serif !important;
  letter-spacing: 0.01em;
}

.brand-wrap {
  padding: 1.4rem 1.6rem 1.2rem 1.6rem;
  margin-bottom: 1.2rem;
  border-radius: 6px;
  background:
    radial-gradient(1200px 500px at 10% -10%, #1A3A55 0%, transparent 55%),
    radial-gradient(900px 400px at 100% 0%, #2C5560 0%, transparent 45%),
    linear-gradient(180deg, #0B1F33 0%, #10263A 100%);
}
.brand-title {
  font-size: 2.6rem;
  color: #F7F3EC;
  margin: 0;
  font-weight: 600;
}
.brand-tag {
  color: #D7E4E7;
  font-size: 1.05rem;
  margin-top: 0.2rem;
}
.mode-pill {
  display: inline-block;
  margin-top: 0.75rem;
  padding: 0.25rem 0.7rem;
  border: 1px solid #D7E4E7;
  color: #F7F3EC;
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.panel {
  background: rgba(247, 243, 236, 0.96);
  border: 1px solid var(--line);
  padding: 1rem 1.1rem;
  margin-bottom: 0.8rem;
}
.panel h3 {
  color: var(--navy);
  margin-top: 0;
}
.kpi {
  font-size: 1.6rem;
  color: var(--navy);
  font-family: 'Cormorant Garamond', Georgia, serif;
}
.muted { color: var(--muted); font-size: 0.92rem; }
.status-op { color: #1F5C45; font-weight: 600; }
.status-sim { color: var(--warn); font-weight: 600; }
.status-plan { color: var(--muted); font-weight: 600; }
.stButton>button {
  background: var(--navy);
  color: #F7F3EC;
  border: none;
  border-radius: 2px;
}
.stButton>button:hover {
  background: var(--teal);
  color: white;
}
section[data-testid="stSidebar"] {
  background: #0B1F33;
}
section[data-testid="stSidebar"] * {
  color: #F7F3EC !important;
}
div[data-testid="stSidebarNav"] { display: none; }
</style>
"""


MODULE_STATUS = {
    "Daily Briefing": ("Operational", "status-op"),
    "My Life Blueprint": ("Operational", "status-op"),
    "My Decisions": ("Operational", "status-op"),
    "My Work": ("Operational", "status-op"),
    "My Attention": ("Operational", "status-op"),
    "My Calendar": ("Operational", "status-op"),
    "My People": ("Simulated integration", "status-sim"),
    "My Network": ("Planned / not implemented", "status-plan"),
    "My Career": ("Planned / not implemented", "status-plan"),
    "My Financial Future": ("Simulated integration", "status-sim"),
    "Agent Activity": ("Operational", "status-op"),
    "Settings": ("Operational", "status-op"),
}
