# Iteration History

This repo is more useful if it shows the path, not just the current shape. OpenClaw was built through repeated changes to architecture, workflows, and operating assumptions rather than one clean initial design.

## Initial Approach

The early shape of the system appears to have been closer to a single central AI operator with a growing set of responsibilities. The project history and refactor notes show a gradual move away from one large, monolithic control layer towards clearer project modules, a more explicit runtime lifecycle, and a stronger split between orchestration, research, and background improvement.

## What Failed

### One model path was not enough

Relying too heavily on a single provider created fragility around quota, availability, and control. The current codebase reflects a response to that, with OpenAI-primary and Gemini-fallback behaviour plus local workers through Ollama.

### Background work needed stronger boundaries

Long-running research and improvement loops can become noisy, drift off-topic, or fail in ways that are hard to notice if they share the same surface as user interaction. That is one reason the carousel exists as a separate loop with its own backlog, arbiter, and runtime flags.

### The codebase accumulated monolithic files

The hardest-won lessons here were structural:

- large orchestrator files become hard to reason about
- fallback paths need verification, not just good intentions
- old runtime paths and dead code create confusion fast

### Not every automation path should be fully autonomous

The repo repeatedly chooses supervised workflows over full end-to-end autonomy, especially around external actions. That suggests a lesson learned from operating the system in practice: approval gates are not a limitation, they are part of making the system usable.

## What I Changed

### Shifted to a clearer orchestrator model

The runtime now centres on `NexusOS` as the main orchestrator, with projects registering domain tools through a common interface.

### Added explicit project domains

Instead of keeping all behaviour in one generic assistant, OpenClaw now has dedicated modules for:

- utility research
- job search
- Reddit research
- trading research

That made it easier to add domain logic without rewriting the whole system.

### Added a continuous experiment carousel

The carousel is one of the clearest iteration steps in the repo. Rather than wait for ad hoc prompts, the system can now cycle through active projects, research queued topics, judge the output, and update project knowledge continuously.

### Added local workers and concurrency limits

The local researcher and builder workers are explicitly concurrency-limited. That suggests a move from pure experimentation towards operating discipline on a constrained host.

### Added operational visibility

The portal, service files, and tests show a move from “can this work?” to “can I operate and trust this over time?”

## What Improved

### The repo now shows real systems thinking

The current structure makes it clear that OpenClaw is not just a prompt wrapper. It has lifecycle management, workflow boundaries, project separation, runtime config, and recovery behaviour.

### Workflows became more practical

The strongest example is the job search project. It is not just a chat assistant; it includes live search, scoring, CV generation, and supporting repository state.

### Reliability improved through layered fallbacks

Provider fallback, key rotation, crash supervision, optional subsystem startup, and runtime pause controls all point to the same improvement: the system is better prepared for the way real dependencies fail.

### Iteration became visible

Because plans, playbooks, reflections, decision logs, and backlog files live in the repo, the system’s learning process is inspectable. That is a major improvement over opaque agent behaviour.

## What Remains Rough

### Some core files are still too large

`core/nexus.py` and `core/experiment_loop.py` still carry a lot of responsibility. The architecture is clearer than before, but there is more refactoring to do.

### There is still evidence of migration debt

The repo contains refactor notes, duplicated concepts, and some older artefacts. I would treat that as normal for a live system, but it is still work to finish.

### Coverage is selective, not comprehensive

There are targeted tests around carousel and project behaviour, which is good. There is not yet a full end-to-end test harness for the entire runtime.

### Some capabilities are clearly more mature than others

Job search is already concrete. Other domains, especially research-heavy ones, still look more exploratory.

## Evidence Of Iteration In The Repo

- `docs/decisions.md` documents the reasoning behind major technical choices, including where the original approach was wrong.
- `docs/architecture.md` describes the current system structure and the trade-offs that shaped it.
- Per-project `PLAYBOOK.md`, `DECISION_LOG.md`, and `reflection.md` files accumulate on the server as the carousel runs — they're the live record of what the system learned, not documented retrospectively.

## Bottom Line

The important thing this history shows is not that every idea worked. It shows that I kept turning vague agent ideas into more concrete, more testable, and more operable system behaviour. That is the engineering story behind OpenClaw.
