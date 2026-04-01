# Operations Notes

This public repo is a portfolio snapshot, not a deployable production clone. Even so, it is useful to show the operating model of the real system.

## Operating Pattern

The real OpenClaw setup runs as a long-lived service with:

- a main Python application process
- a read-only status portal
- local model infrastructure through Ollama
- scheduled jobs
- a continuous background improvement loop
- a file-backed memory and handover layer for fresh-context agent sessions

## Memory And Handover Model

OpenClaw uses a local memory file system rather than relying on ephemeral chat context alone.

Representative patterns from the working system:

- important decisions are appended to a running build log
- plans, objectives, and research notes are kept as readable Markdown
- fresh-context agents are expected to use those files as handover material before acting

This means a new agent session can recover recent reasoning, major choices, and current direction without pretending it has perfect memory.

## Review Rhythm

The system is also operated on a regular review cadence:

- Sunday weekly review to analyse accumulated research and uncover broader trends or pivots
- `8am` daily check-in to set the day’s direction
- `4pm` daily check-in to review outcomes and make small course corrections

That cadence matters operationally because it keeps the system aligned with changing priorities while still preserving continuity across agent sessions.

## Deployment Style

Representative deployment choices from the working system:

- `systemd` for long-running services
- `docker-compose` for local model infrastructure
- localhost binding for the internal dashboard
- restart policies for long-lived components

## Safety And Reliability

Representative operational controls:

- hosted-provider fallback
- retry and key rotation logic
- allowlisted shell access
- concurrency limits on local worker execution
- pause flags for background loops
- written handovers so new sessions can resume safely

## What A Hiring Manager Should Take From This

The main point is that the system is operated, not merely prompted. The engineering work includes runtime management, failure handling, resource constraints, and visibility into system state.
