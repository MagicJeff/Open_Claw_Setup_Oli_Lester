# Research Digest Agent

**Start with:** `claude --dangerously-skip-permissions`

Runs Sunday evenings. On session start:

- If it is Sunday evening: immediately invoke the research-digest agent
- Otherwise: confirm readiness and state when the next Sunday is

The research-digest agent:
1. Reads carousel playbooks and reflections across all active projects
2. Synthesises findings — what worked, what didn't, what is emerging
3. Identifies patterns across projects (cross-domain insights)
4. Proposes new research directions and seeds backlogs
5. Sends Oliver a Telegram summary

Always use subagent-driven execution — never execute inline.
