# Agents

OpenClaw uses two types of agent configuration:

**Claude Code agents** — persistent terminal sessions running on the local machine. Each has a `CLAUDE.md` that defines its behaviour on startup. These handle implementation, deployment, health monitoring, and other tasks that require a local development environment or filesystem access.

**SOUL files** — identity and operating mandate files for the carousel's project researchers. Each active project can have a `SOUL.md` that gives the researcher agent a distinct personality, philosophy, and decision-making framework tailored to that domain. The carousel loads these at research time to shape how findings are framed and prioritised.

## Claude Code Agents

| Agent | File | Purpose |
|---|---|---|
| Builder | [builder.md](builder.md) | Picks up build jobs queued by OpenClaw, implements them, deploys to server |
| CV Writer | [cv-writer.md](cv-writer.md) | Event-driven CV generation triggered via Telegram |
| Health Checker | [health-checker.md](health-checker.md) | Scheduled health monitoring and morning briefing |
| Project Onboarder | [project-onboarder.md](project-onboarder.md) | Guided interview to scaffold new carousel projects |
| Research Digest | [research-digest.md](research-digest.md) | Weekly synthesis of carousel output across all projects |

## SOUL Files

| Agent | File | Domain |
|---|---|---|
| Job Recruiter | [souls/job-recruiter.md](souls/job-recruiter.md) | Job search — role discovery, fit analysis, application framing |
| Polymath Trader | [souls/polymath-trader.md](souls/polymath-trader.md) | Trading — macro research, thesis development, paper positions |
| Reddit Marketer | [souls/reddit-marketer.md](souls/reddit-marketer.md) | Community — grassroots engagement strategy for Dice 10k |
| Self Architect | [souls/self-architect.md](souls/self-architect.md) | System improvement — continuous review and critique of OpenClaw itself |
