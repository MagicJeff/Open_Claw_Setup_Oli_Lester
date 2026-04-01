# Project Onboarder Agent

**Start with:** `claude --dangerously-skip-permissions`

On session start, immediately invoke the project-onboarder agent. It will run a 5-question interview with Oliver to gather everything needed to scaffold a new carousel project.

The agent:
1. Asks 5 questions to define the project's objective, domain, research focus, and output format
2. Scaffolds all required files: `project.py`, `experiment_backlog.md`, `SOUL.md`, `PLAYBOOK.md`
3. Registers the project with the carousel in `data/runtime_config.json`
4. Deploys the changes to the server
5. Confirms via Telegram that the project is live

Always use subagent-driven execution — never execute inline.
