# OpenClaw Use Cases

This document focuses on practical workflows that are supported by the codebase as it exists in the repo.

## 1. Job Search Discovery And CV Tailoring

### User Problem

Finding relevant roles is noisy, and tailoring a CV for each role is repetitive and easy to do badly under time pressure.

### Agents And Tools Involved

- `NexusOS` orchestrator
- `projects/job_search/project.py`
- job search and scoring helpers in `projects/job_search/`
- CV repository files in `projects/job_search/cv_repository/`
- scheduled daily job search scans in `bot/scheduler.py`

### Output Or Result

The system can search for live roles, score them against the user profile, cache job descriptions, and generate tailored CV drafts saved back into the repository for review.

## 2. Continuous Research Backlog For Active Projects

### User Problem

It is hard to keep multiple long-running ideas moving forward without constantly deciding what to research next.

### Agents And Tools Involved

- experiment carousel in `core/experiment_loop.py`
- backlog files in `projects/*/experiment_backlog.md`
- researcher and arbiter loops
- project playbooks and reflection files in `research/`

### Output Or Result

The system can pick from a project backlog, run a research pass, decide whether the result is worth keeping, and write approved knowledge back into project artefacts.

## 3. Utility Research And Codebase Audit

### User Problem

A growing personal AI system needs regular review for architectural, performance, and reliability issues.

### Agents And Tools Involved

- `projects/utility_researcher/project.py`
- parallel local researcher calls through `core/researcher.py`
- git-backed output written into `research/`

### Output Or Result

The system can audit the codebase across focus areas, summarise findings, and store a structured report that is easy to review later.

## 4. Scheduled Briefings And Daily Prompts

### User Problem

An always-on system is only useful if it surfaces what matters at the right time without manual prompting.

### Agents And Tools Involved

- scheduler in `bot/scheduler.py`
- Telegram bot interface
- orchestrator summaries over plans, reflections, job search state, and research output

### Output Or Result

The system can send scheduled briefings, job search scans, and profile-building prompts to the user at defined times, using the same orchestration layer as interactive chat.

## 5. Trading Research And Paper Portfolio Tracking

### User Problem

Tracking ideas and paper positions across a developing trading thesis is hard to do consistently by hand.

### Agents And Tools Involved

- `projects/trader/project.py`
- paper trading helpers in `projects/trader/paper_trader.py`
- trader watchlist and playbook files in `research/trader/`

### Output Or Result

The system can maintain a watchlist-oriented research workflow and track simulated paper positions, including open positions and trade history.

## 6. Operational Monitoring Through The Portal

### User Problem

When a system runs continuously, you need a quick way to see whether it is healthy and what it is working on.

### Agents And Tools Involved

- portal backend in `portal/server.py`
- static portal frontend in `portal/static/`
- runtime config, service checks, backlog parsing, and research file reads

### Output Or Result

The portal can show whether key services are active, which projects are running, which models are available in Ollama, and what recent research or backlog state looks like.

## Notes On Scope

This list is intentionally conservative. The repo includes signs of additional agent workflows and experimental services, but the workflows above are the clearest capabilities I can support directly from the current codebase.
