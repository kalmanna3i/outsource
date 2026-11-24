"""SQLite helpers and seed data."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.config import get_settings
from core.mandate import LifeMandate, MandateStatus, default_life_mandate, utc_now
from core.models import Goal, LifeBlueprint, PersonProfile


SCHEMA = """
CREATE TABLE IF NOT EXISTS blueprint (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS workflows (
    workflow_id TEXT PRIMARY KEY,
    data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS people (
    person_id TEXT PRIMARY KEY,
    data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings_kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS radar_opportunities (
    dedup_key TEXT PRIMARY KEY,
    data_json TEXT NOT NULL,
    first_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agent_activity (
    call_id TEXT PRIMARY KEY,
    workflow_id TEXT,
    data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS life_mandate (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS life_mandate_revisions (
    revision INTEGER PRIMARY KEY,
    data_json TEXT NOT NULL,
    saved_at TEXT NOT NULL
);
"""


def db_path() -> Path:
    return get_settings().data_dir / "outsource.db"


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False) -> None:
    path = db_path()
    if reset and path.exists():
        path.unlink()
    with connect() as conn:
        conn.executescript(SCHEMA)
        row = conn.execute("SELECT data_json FROM blueprint WHERE id = 1").fetchone()
        if not row:
            bp = default_blueprint()
            conn.execute(
                "INSERT INTO blueprint (id, data_json) VALUES (1, ?)",
                (bp.model_dump_json(),),
            )
        people_count = conn.execute("SELECT COUNT(*) AS c FROM people").fetchone()["c"]
        if people_count == 0:
            for person in default_people():
                conn.execute(
                    "INSERT INTO people (person_id, data_json) VALUES (?, ?)",
                    (person.person_id, person.model_dump_json()),
                )
        mode = conn.execute(
            "SELECT value FROM settings_kv WHERE key = 'permission_mode'"
        ).fetchone()
        if not mode:
            conn.execute(
                "INSERT INTO settings_kv (key, value) VALUES ('permission_mode', ?)",
                ("MANAGED_AUTONOMY",),
            )
        _seed_mandate(conn)
        conn.commit()


def default_blueprint() -> LifeBlueprint:
    return LifeBlueprint(
        user_name="Kay Al Mannai",
        personal_summary=(
            "Yale SOM MBA candidate building a Personal Strategy & Execution Office "
            "that protects scarce attention for high-leverage human work."
        ),
        career="Post-MBA leadership path with operational excellence and AI-enabled leverage.",
        academic="Complete MGT 409 final and remaining MBA deliverables at high quality.",
        financial="Maintain optionality; avoid impulsive large commitments without analysis.",
        relationships="Show up for important personal milestones (weddings, family).",
        family="Stay present for family obligations without dropping academic/career standards.",
        lifestyle="Protect sleep and focus blocks around hard deadlines.",
        health="No sensitive medical inferences; user-managed only.",
        legacy="Build tools that help managers reclaim judgment time.",
        mission="Build an intentional life: lead an AI-enabled operating business, keep learning, and stay present for the people who matter.",
        guiding_principles=[
            "Protect focus blocks around hard deadlines",
            "Avoid impulsive large financial commitments without analysis",
            "Substance over prestige",
            "Show up for important personal milestones",
        ],
        strategic_objectives=[
            "business ownership: own and operate an AI-enabled business within 5 years",
            "intellectual development: contribute to research on AI and managerial judgment",
            "career advancement: build a network of operators and executives",
            "reputation & contribution: share practitioner insight publicly",
            "meaningful relationships: stay close to friends and family",
        ],
        goals=[
            Goal(
                title="Submit MGT 409 final (app + report + slides)",
                domain="academic",
                target_date="2026-11-23",
                importance=10,
                progress=0.7,
                success_criteria="Repo + report.html + slides.html submitted by 11:59 PM ET",
            ),
            Goal(
                title="Attend close friend's wedding",
                domain="relationships",
                target_date="2026-11-23",
                importance=9,
                progress=0.5,
                success_criteria="Arrive on time, fully present; logistics handled in advance",
            ),
            Goal(
                title="Clear critical work obligation",
                domain="career",
                target_date="2026-11-23",
                importance=8,
                progress=0.4,
                success_criteria="Stakeholder receives required deliverable or confirmed deferral",
            ),
            Goal(
                title="Resolve insurance claim status",
                domain="financial",
                target_date="2026-11-30",
                importance=7,
                progress=0.2,
                success_criteria="Claim status known; next action scheduled or completed",
            ),
        ],
    )


def default_people() -> list[PersonProfile]:
    return [
        PersonProfile(
            name="Alex Rivera",
            relationship="Close friend (wedding)",
            notes="Wedding this weekend — presence matters more than gifts.",
            milestones=["Wedding ceremony"],
        ),
        PersonProfile(
            name="Jordan Lee",
            relationship="Work stakeholder",
            notes="Needs the work package update today.",
        ),
        PersonProfile(
            name="Sam Patel",
            relationship="MBA classmate",
            notes="Peer review swap possible for slides.",
            milestones=["MBA capstone presentation (Dec 11, illustrative)"],
        ),
    ]


def load_blueprint() -> LifeBlueprint:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT data_json FROM blueprint WHERE id = 1").fetchone()
        return LifeBlueprint.model_validate_json(row["data_json"])


def save_blueprint(bp: LifeBlueprint) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            "UPDATE blueprint SET data_json = ? WHERE id = 1",
            (bp.model_dump_json(),),
        )
        conn.commit()


def save_workflow(workflow_json: str, workflow_id: str, updated_at: str) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO workflows (workflow_id, data_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(workflow_id) DO UPDATE SET
              data_json = excluded.data_json,
              updated_at = excluded.updated_at
            """,
            (workflow_id, workflow_json, updated_at),
        )
        conn.commit()


def load_workflow(workflow_id: str) -> dict | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT data_json FROM workflows WHERE workflow_id = ?",
            (workflow_id,),
        ).fetchone()
        if not row:
            return None
        return json.loads(row["data_json"])


def list_workflows() -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT workflow_id, updated_at, data_json FROM workflows ORDER BY updated_at DESC"
        ).fetchall()
        out = []
        for r in rows:
            data = json.loads(r["data_json"])
            out.append(
                {
                    "workflow_id": r["workflow_id"],
                    "updated_at": r["updated_at"],
                    "status": data.get("status"),
                    "user_request": data.get("user_request", "")[:120],
                }
            )
        return out


def list_people() -> list[PersonProfile]:
    init_db()
    with connect() as conn:
        rows = conn.execute("SELECT data_json FROM people").fetchall()
        return [PersonProfile.model_validate_json(r["data_json"]) for r in rows]


def reset_demo_data() -> None:
    init_db(reset=True)


def get_permission_mode() -> str:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT value FROM settings_kv WHERE key = 'permission_mode'"
        ).fetchone()
        return row["value"] if row else "MANAGED_AUTONOMY"


def set_permission_mode(mode: str) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO settings_kv (key, value) VALUES ('permission_mode', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (mode,),
        )
        conn.commit()


def seen_opportunity_keys() -> set[str]:
    init_db()
    with connect() as conn:
        return {r["dedup_key"] for r in conn.execute("SELECT dedup_key FROM radar_opportunities")}


def save_opportunity(dedup_key: str, data_json: str, first_seen: str) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO radar_opportunities (dedup_key, data_json, first_seen)
            VALUES (?, ?, ?)
            ON CONFLICT(dedup_key) DO UPDATE SET data_json = excluded.data_json
            """,
            (dedup_key, data_json, first_seen),
        )
        conn.commit()


def get_setting_json(key: str) -> str | None:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT value FROM settings_kv WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None


def _seed_mandate(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT data_json FROM life_mandate WHERE id = 1").fetchone()
    if row:
        return
    mandate = default_life_mandate()
    payload = mandate.model_dump_json()
    conn.execute("INSERT INTO life_mandate (id, data_json) VALUES (1, ?)", (payload,))
    conn.execute(
        "INSERT INTO life_mandate_revisions (revision, data_json, saved_at) VALUES (1, ?, ?)",
        (payload, utc_now().isoformat()),
    )


def load_mandate() -> LifeMandate:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT data_json FROM life_mandate WHERE id = 1").fetchone()
        return LifeMandate.model_validate_json(row["data_json"])


def list_mandate_revisions() -> list[LifeMandate]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT data_json FROM life_mandate_revisions ORDER BY revision"
        ).fetchall()
        return [LifeMandate.model_validate_json(row["data_json"]) for row in rows]


def load_approved_mandate() -> LifeMandate | None:
    approved = [item for item in list_mandate_revisions() if item.status == MandateStatus.APPROVED]
    return approved[-1] if approved else None


def save_mandate_revision(mandate: LifeMandate) -> LifeMandate:
    """Append a revision. Does not rewrite older rows."""
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT MAX(revision) AS r FROM life_mandate_revisions").fetchone()
        nxt = int(row["r"] or 0) + 1
        mandate.revision = nxt
        payload = mandate.model_dump_json()
        conn.execute(
            "INSERT INTO life_mandate_revisions (revision, data_json, saved_at) VALUES (?, ?, ?)",
            (nxt, payload, utc_now().isoformat()),
        )
        conn.execute(
            """
            INSERT INTO life_mandate (id, data_json) VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET data_json = excluded.data_json
            """,
            (payload,),
        )
        conn.commit()
    return mandate


def save_draft(mandate: LifeMandate) -> LifeMandate:
    mandate.status = MandateStatus.DRAFT
    mandate.approved_at = None
    mandate.approved_by = ""
    mandate.change_note = mandate.change_note or "Draft saved by user"
    return save_mandate_revision(mandate)


def approve_mandate(mandate: LifeMandate, editor: str) -> LifeMandate:
    mandate.status = MandateStatus.APPROVED
    mandate.approved_by = editor or "user"
    mandate.approved_at = utc_now()
    mandate.change_note = mandate.change_note or "Approved by user"
    return save_mandate_revision(mandate)


def update_priorities(priorities: list[str], editor: str) -> LifeMandate:
    """User-approved priority change. Mission text is copied, not rewritten."""
    base = load_approved_mandate()
    if base is None:
        raise ValueError("Approve a mandate before updating priorities.")
    nxt = base.model_copy(deep=True)
    nxt.priorities = [item.strip() for item in priorities if item.strip()]
    nxt.change_note = "User updated priorities"
    nxt.mission = base.mission
    return approve_mandate(nxt, editor)


def save_daily_checkin(day: str, payload: dict, user_id: str = "local") -> None:
    """One row per user and day. Saving again replaces that day. It does not invent other days."""
    set_setting_json(f"daily_checkin:{user_id}:{day}", json.dumps(payload))


def load_daily_checkin(day: str, user_id: str = "local") -> dict | None:
    raw = get_setting_json(f"daily_checkin:{user_id}:{day}")
    if not raw:
        return None
    data = json.loads(raw)
    return data if isinstance(data, dict) else None


def save_assessments(scores: dict[str, int], user_id: str = "local") -> None:
    """Saved 0–10 dimension assessments. Missing keys are not filled in.

    Each save appends one history row. Days between saves are not filled in.
    """
    clean = {str(key): int(value) for key, value in scores.items()}
    set_setting_json(f"assessments:{user_id}", json.dumps(clean))
    history = load_assessment_history(user_id)
    history.append({"recorded_at": utc_now().isoformat(), "scores": clean})
    set_setting_json(f"assessment_history:{user_id}", json.dumps(history))


def load_assessment_history(user_id: str = "local") -> list[dict]:
    raw = get_setting_json(f"assessment_history:{user_id}")
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        return []
    rows = []
    for item in data:
        if not isinstance(item, dict):
            continue
        recorded_at = item.get("recorded_at")
        scores = item.get("scores")
        if not recorded_at or not isinstance(scores, dict):
            continue
        rows.append({"recorded_at": str(recorded_at), "scores": {str(k): int(v) for k, v in scores.items()}})
    return rows


def save_aspirations(scores: dict[str, int], user_id: str = "local") -> None:
    """Desired targets the user saved. Unset dimensions stay unset."""
    clean = {str(key): int(value) for key, value in scores.items()}
    set_setting_json(f"aspirations:{user_id}", json.dumps(clean))


def load_aspirations(user_id: str = "local") -> dict[str, int]:
    raw = get_setting_json(f"aspirations:{user_id}")
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        return {}
    out: dict[str, int] = {}
    for key, value in data.items():
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        out[str(key)] = max(0, min(10, number))
    return out


def load_assessments(user_id: str = "local") -> dict[str, int]:
    raw = get_setting_json(f"assessments:{user_id}")
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        return {}
    out: dict[str, int] = {}
    for key, value in data.items():
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        out[str(key)] = max(0, min(10, number))
    return out


def set_setting_json(key: str, value: str) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO settings_kv (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        conn.commit()
