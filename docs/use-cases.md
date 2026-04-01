# OpenClaw Use Cases

Practical workflows the system supports in production.

## 1. Job Search — Discovery, Scoring, And CV Generation

**Problem:** Finding relevant roles is noisy. Tailoring a CV for each one is repetitive and easy to do badly under time pressure.

**How it works:**

- Daily scheduled scan searches for live roles matching a target profile
- Each result is scored 0–100 using weighted signal matching across role type, AI/tool keywords, seniority markers, and location — filtered below 45
- High-scoring roles are surfaced to Oliver via Telegram
- Oliver can trigger `queue_cv_build` with a job description; the CV Writer Claude Code agent writes a tailored CV as a Word document and sends it back via Telegram

**What this replaces:** Manual job board browsing, copy-paste CV editing under time pressure.

## 2. Continuous Research Via The Experiment Carousel

**Problem:** Keeping multiple long-running projects moving forward without constantly deciding what to research next.

**How it works:**

- The carousel runs perpetually, cycling through active project backlogs
- Each cycle: researcher fetches supplemental data (HN, arXiv, Polymarket, Reddit) and synthesises findings; arbiter decides APPROVE / REFINE / DISCARD
- Approved findings are appended to the project playbook — additive, compounding knowledge
- When the backlog empties, a reflection pass reads accumulated knowledge and generates 3 new grounded topics
- The carousel self-directs: REFINE re-queues sharper versions, dead ends stay in the decision log and aren't re-researched

**What this replaces:** Ad hoc research sessions that lose continuity between conversations.

## 3. AI-Assisted Build Pipeline

**Problem:** OpenClaw can identify improvements but can't safely implement multi-file code changes on itself.

**How it works:**

- When Oliver approves a proposed change, OpenClaw calls `queue_build_job` with a description
- The Claude Code builder agent picks up the job, implements it locally, rsyncs to the server, restarts the service, and sends a Telegram confirmation
- The entire cycle — proposal, approval, implementation, deployment — happens without Oliver touching a terminal

**What this replaces:** Manual implementation of every system improvement, context-switching between planning and building.

## 4. Trading Research And Thesis Tracking

**Problem:** Developing a paper trading thesis requires consistent research and a way to track conviction over time.

**How it works:**

- The trader carousel module researches topics from a watchlist-oriented backlog
- Approved findings are written as structured thesis documents with conviction levels (LOW / MEDIUM / HIGH)
- HIGH conviction findings trigger an alert
- A running watchlist tracks all active theses, dates, and status

**What this replaces:** Scattered notes and inconsistent follow-through on investment ideas.

## 5. Operational Monitoring

**Problem:** When a system runs continuously, you need a quick way to see whether it is healthy and what it is doing.

**How it works:**

- The health checker Claude Code agent runs at 8am and 7pm daily
- Checks: service status, carousel activity, key pool availability, memory usage, build queue
- Auto-fixes known issues silently; sends a Telegram summary with anything that needs attention
- A read-only portal also shows live service state, active projects, and recent carousel output

**What this replaces:** SSHing into the server to check logs manually.
