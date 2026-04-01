# Operations

OpenClaw is operated as a long-running service, not treated as a script that runs when needed. The engineering work includes deployment, service management, failure recovery, resource constraints, and keeping the system aligned over time.

## Service Architecture

The system runs as three separate services on Oracle Cloud:

- **Main application** — the NexusOS orchestrator, Telegram bot, scheduler, and experiment carousel, managed by `systemd`
- **Portal** — a read-only status dashboard served separately, also under `systemd`
- **Ollama** — local model infrastructure containerised via Docker Compose

Each service has its own restart policy. The carousel is supervised in `main.py` and restarted automatically after crashes. Ollama and the portal can fail independently without taking down the main application.

## Claude Code As An Operations Layer

Claude Code runs locally and connects to the same Telegram channel as OpenClaw. This makes it part of the operating model, not just a development tool.

In practice:

- The **health checker** agent runs on a cron schedule — 8am daily report to Telegram, evening check. It monitors service status, carousel activity, key pool state, memory, and build queue. Known issues are fixed silently; anything requiring attention is surfaced to Oliver.
- The **builder** agent picks up jobs queued by OpenClaw, implements them, rsyncs to the server, restarts the service, and sends a Telegram confirmation.
- The **research digest** agent runs Sunday evenings, synthesising carousel output across all projects and proposing new research directions.

## Runtime Configuration

Operational parameters live in `data/runtime_config.json` and can be changed without restarting the service:

- `carousel_paused` — pause the experiment loop
- `carousel_active_projects` — which projects the carousel cycles through
- `carousel_slot_cooldown_secs` — time between carousel slots (default 600s, ~100 arbiter calls/day on free tier)
- Model names for researcher and builder workers

## Review Cadence

The system is steered through a regular review rhythm:

- **8am daily** — set direction, review overnight carousel output, approve or discard proposals
- **4pm daily** — review what changed, make small course corrections
- **Sunday weekly** — analyse accumulated research across all projects, identify trends, dead ends, and direction changes

This matters operationally: a continuously running system drifts without regular steering. The cadence keeps it aligned with changing priorities while preserving continuity across sessions.

## Failure Handling

- OpenAI primary, Gemini fallback on all hosted model calls
- Gemini key pool rotates across multiple keys with separate backoff for quota errors (24h reset) and transient outages (60s reset)
- Local Ollama workers are semaphore-limited to prevent OOM on constrained hardware
- The carousel loop is supervised and restarted after crashes
- Telethon startup is optional — if not configured, the rest of the system still runs
- Runtime flags allow pausing the carousel without a code change or restart
