# Major Technical Decisions

## Multiple Model Providers

OpenClaw uses more than one provider because the system needs resilience and optionality. Orchestration, research, judgement, and implementation work have different cost, latency, and reliability profiles. A mixed setup is more complex, but more realistic for an always-on agent system.

## Local Models Through Ollama

Local models are included because they reduce marginal cost for repeated worker tasks and provide more control over execution. The trade-off is infrastructure overhead and stricter resource management, which is why the real system limits worker concurrency.

## Persistent Orchestrator

The system uses a long-running orchestrator rather than short-lived task scripts because the workflows are ongoing. Scheduled jobs, context retention, and background improvement loops are much easier to manage in that model.

## Project Module Boundaries

The system is broken into project domains because one generic agent quickly becomes hard to reason about. Project boundaries make the tool surface clearer and reduce prompt sprawl.

## File-Backed State

Markdown and JSON state are used heavily because they are transparent, reviewable, and easy to version. For a single-user operated system, that trade-off is often better than introducing a database too early.

## Constrained Tool Access

The system favours narrow tool exposure over aspirational autonomy. This is a practical safety choice. A smaller, well-understood tool surface is easier to operate reliably.

## Lightweight Observability

The repo uses logs, service units, and a simple status portal rather than a full observability stack. That is enough to operate the system and explain its state without introducing unnecessary infrastructure.
