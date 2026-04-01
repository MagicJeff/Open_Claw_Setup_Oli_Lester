# Agents

These are **Claude Code agents** — persistent terminal sessions running on the local machine. Each has a startup config that defines its behaviour when the session opens.

They handle tasks that require a local development environment: implementing build jobs, deploying to the server, health monitoring, CV generation. OpenClaw communicates with them via Telegram — it queues a job or sends a message, the agent picks it up and acts.

This is distinct from the carousel's **project agents** (see [`projects/`](../projects/)), which run on the server inside OpenClaw and have their own soul, code, and accumulated knowledge.

## Claude Code Agents

| Agent | File | Purpose |
|---|---|---|
| Builder | [builder.md](builder.md) | Picks up build jobs queued by OpenClaw, implements them, deploys to server |
| CV Writer | [cv-writer.md](cv-writer.md) | Event-driven CV generation triggered via Telegram |
| Health Checker | [health-checker.md](health-checker.md) | Scheduled health monitoring and morning briefing |
| Project Onboarder | [project-onboarder.md](project-onboarder.md) | Guided interview to scaffold new carousel projects |
| Research Digest | [research-digest.md](research-digest.md) | Weekly synthesis of carousel output across all projects |
