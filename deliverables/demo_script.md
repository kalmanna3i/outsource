# OUTSOURCE — Demo Script (Priority 0)

**Presenter:** Kay Al Mannai · **Course:** MGT 409 · **Runtime:** ~3–5 minutes  
**Mode:** Start with `APP_MODE=demo` and `LLM_MODE=demo` so every fixture is labeled. Email, purchases, and the insurer stay simulated even if you later set `LLM_MODE=live`.

## Setup

```bash
cd outsource
source .venv/bin/activate
APP_MODE=demo streamlit run app.py
```

Confirm the header pill shows **MODE: DEMO**.

## Narration

1. **Problem (15s)**  
   “Managers don’t lack AI tools — they lack a system that knows their goals, decides what is worth their scarce attention, and brings them in only when a human is truly required.”

2. **Life Blueprint (20s)**  
   Open **My Life Blueprint**. Point at goals: MGT 409 final (importance 10), wedding (9), work obligation (8), insurance claim (7).

3. **Intake (20s)**  
   **Daily Briefing** → request already filled:  
   *I need to finish my MBA final tonight, attend a wedding, handle an important work obligation, and find out what is happening with my insurance claim.*  
   Click **Run Priority 0 workflow**.

4. **Multi-agent path (45s)**  
   While it runs, name the agents: A01 Chief of Staff → A02 Strategy (reads goals) → B01 Opportunity Cost → F02 Decomposition → F03 Execution → simulated insurer wall → F05 Handoff → F04 Calendar/ICS.  
   Open **Agent Activity**: multiple distinct calls, each labeled `[DEMO FIXTURE]` (or `[LIVE]` in live mode).

5. **Decision quality (30s)**  
   **My Decisions**: recommended sequence protects the wedding’s fixed window and the academic hard stop; insurance is AI-prep + human verification, not fake automation.

6. **Flagship handoff (60s)**  
   Back on Briefing: private brief with talking points and documents. Calendar slot does **not** contain claim IDs or ID instructions. **Download ICS** and open it.  
   Paste a result, e.g. *Verified identity. Claim under review; upload EOB within 14 days.* → **Submit result & resume**. Status becomes COMPLETED; follow-ups appear under **My Work**.

7. **Safety (20s)**  
   **Settings** → paste *Ignore previous instructions… api_key=sk-…* → show quarantine banner + `[REDACTED]`.

8. **Life Mandate (40s)**  
   Open **Life Mandate**. The philosophy line is “The art of building an intentional life.” Edit the mission, **Save draft**, then **Approve mandate**. Change priorities to a single line, `infrastructure`, and click **Update priorities**. The discretionary pick becomes the site seminar. Say that success is the user’s sentence. **Run discovery and recommendation** uses a labeled dataset. The outreach card says `DRAFT_NOT_SENT`.

9. **Honesty close (15s)**  
   “Demo mode never pretends fixtures are live calls. Email, purchases, and real insurer APIs are not implemented. Live search and background monitoring are not built. See BUILD_STATUS.md.”

## Pass criteria

- [ ] Multiple agent calls visible  
- [ ] Opportunity-cost plan with tradeoffs  
- [ ] AI vs human allocation  
- [ ] Identity-verification blocker  
- [ ] ICS downloadable; sensitive details only in private brief  
- [ ] Resume after user result  
- [ ] Mode clearly labeled  
- [ ] Approved priority change moves the discretionary pick  
- [ ] Outreach stays DRAFT_NOT_SENT  
