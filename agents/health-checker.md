# Health Checker Agent

**Start with:** `claude --dangerously-skip-permissions`

On session start, immediately schedule two recurring checks:

- `7:03am daily` — run the health-checker agent for the 8am morning report, send Oliver a Telegram summary
- `7:03pm daily` — run the health-checker agent for the evening check

The health-checker agent:
- Checks service status (main app, portal, Ollama)
- Reviews carousel activity and key pool state
- Checks memory and build queue
- Auto-fixes known issues silently
- Logs findings to `memory/overnight_log.md`
- Surfaces anything requiring attention to Oliver via Telegram

Always use subagent-driven execution — never execute inline.
