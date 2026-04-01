# Major Technical Decisions

This document summarises the main technical choices visible in the repository and the trade-offs behind them.

## 1. Use Multiple Model Providers

### Decision

Use a mixed provider setup rather than commit the whole system to one model vendor.

### Why

- Different tasks have different needs: orchestration, judgement, research, and coding are not the same workload.
- A single-provider design is brittle when quotas, outages, latency spikes, or pricing change.
- The repo already reflects this split: OpenAI is used through the local gateway, Gemini is used as a fallback path, and Ollama handles local worker workloads.

### Trade-Off

This increases code and operational complexity. There are more failure modes, more configuration, and more behaviour to understand. I accepted that complexity because resilience and control matter more here than keeping the architecture theoretically neat.

## 2. Include Local Models Through Ollama

### Decision

Run local open-source models alongside hosted APIs.

### Why

- Local models are useful for repeatable worker tasks where marginal cost matters.
- They provide a controllable fallback when I do not want every task to depend on an external API.
- They make it easier to experiment with specialised worker roles such as local research and coding helpers.

### Trade-Off

Local models are slower, heavier to operate, and more constrained than top hosted models. They also require explicit concurrency control, which is why the local researcher and builder workers use semaphores.

## 3. Keep The Core Runtime Always On

### Decision

Deploy the runtime and portal as long-running services rather than run them manually ad hoc.

### Why

- The whole point of OpenClaw is persistent operation.
- Background schedules, job scans, and the experiment carousel only make sense if the system stays up.
- The systemd service files make the repo clearly legible as an operated system rather than a toy local script.

### Trade-Off

An always-on system is harder to maintain. Logging, restart behaviour, health checks, and configuration hygiene matter much more once the code is actually running continuously.

## 4. Use A Project Module Architecture

### Decision

Represent each domain as a project module implementing a common base interface.

### Why

- It keeps the orchestrator general while allowing domain-specific tools and prompts.
- It makes the repo easier to navigate: job search logic lives under `projects/job_search/`, trading logic under `projects/trader/`, and so on.
- It is a good compromise between one giant agent and a fully distributed microservice setup.

### Trade-Off

The boundary is good, but not perfect. Some core files are still doing too much, especially `core/nexus.py` and `core/experiment_loop.py`. The repo shows both the value of modularity and the next refactor that is still needed.

## 5. Store Operational State In Markdown And Small JSON Files

### Decision

Persist plans, memory, backlog, research output, and runtime flags in repo-visible files.

### Why

- Easy to inspect and debug.
- Easy to version and reason about.
- Easy to present in a portfolio because the system’s state is legible in plain text.
- Good enough for a single-user, supervised system.

### Trade-Off

This is less structured than a database. It would not be my first choice for a larger multi-user product, but for this stage it improves transparency and lowers operational burden.

## 6. Constrain Tool Access Instead Of Chasing Full Autonomy

### Decision

Keep a narrow tool layer and explicit approval boundaries.

### Why

- Real automation is useful only if it behaves predictably.
- The allowlisted shell tool and project-specific workflows reduce the chance of the orchestrator doing unsafe or low-value things.
- The repo consistently treats outward-facing actions as supervised.

### Trade-Off

This makes the system less magical, but much more believable. I would rather show engineering judgement and clear boundaries than claim autonomy the repo does not safely support.

## 7. Separate Background Improvement From User Interaction

### Decision

Run the experiment carousel as its own continuous loop rather than merge it directly into the chat path.

### Why

- User requests should stay responsive.
- Research and iteration are open-ended and can fail, stall, or become noisy.
- The carousel can be paused, tuned, and observed independently through runtime config and portal state.

### Trade-Off

This adds another moving part, but it is a cleaner design than blocking user interaction on long-running research loops.

## 8. Prefer Lightweight Observability Over Heavy Infrastructure

### Decision

Use logging, service status, and a small read-only portal instead of building a full monitoring stack.

### Why

- This system needed enough visibility to operate, not an enterprise observability platform.
- The portal answers the immediate questions: what is up, what is active, and what has the system been producing?

### Trade-Off

The current setup is intentionally lightweight. It is enough for a serious personal system, but it is not the end state for a larger production product.

## Summary Of The Core Trade-Off

OpenClaw is built around four tensions:

- speed versus reliability
- cost versus capability
- autonomy versus control
- simplicity versus operational realism

The repository is strongest when it shows how those tensions were handled in practice. That is the main design story I would want a hiring manager to see.
