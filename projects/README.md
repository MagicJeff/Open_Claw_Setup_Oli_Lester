# Projects

Each folder here is a **carousel project** — a long-running autonomous agent with its own identity, implementation, and accumulated knowledge.

## What a project is

A project is three things combined:

- **`soul.md`** — the agent's identity: its mission, operating principles, and how it thinks. This is what makes each agent distinct rather than generic.
- **Code** — the implementation: how it fetches data, scores results, generates outputs.
- **Knowledge** — accumulated over time in `PLAYBOOK.md` and `lessons.md`: what worked, what didn't, what to try next.

The carousel runs these projects perpetually. Each cycle: research a topic → arbiter decides APPROVE / REFINE / DISCARD → on empty backlog, reflect and generate 3 new grounded directions.

## Active Projects

| Project | Agent | Mission |
|---------|-------|---------|
| [job-search/](job-search/) | Job Recruiter | Find and frame CSM/TAM roles that match Oliver's background |
| [trader/](trader/) | Polymath Trader | Paper-trade a macro strategy via AI debate pipeline |
| [reddit/](reddit/) | Reddit Marketer | Build grassroots community for Dice 10k iOS game |
| [utility-researcher/](utility-researcher/) | Self-Architect | Audit and improve the OpenClaw system itself |

## How a new project is added

The [project-onboarder agent](../agents/project-onboarder.md) handles this end-to-end: 5-question interview → scaffolds all files → registers with the carousel → deploys → confirms via Telegram.
