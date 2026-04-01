# Operations Notes

This public repo is a portfolio snapshot, not a deployable production clone. Even so, it is useful to show the operating model of the real system.

## Operating Pattern

The real OpenClaw setup runs as a long-lived service with:

- a main Python application process
- a read-only status portal
- local model infrastructure through Ollama
- scheduled jobs
- a continuous background improvement loop

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

## What A Hiring Manager Should Take From This

The main point is that the system is operated, not merely prompted. The engineering work includes runtime management, failure handling, resource constraints, and visibility into system state.
