# Builder Agent

**Start with:** `claude --dangerously-skip-permissions`

On session start, immediately start a loop that checks the server's `plans/build_queue/` every hour. If jobs are queued, invoke the builder agent to implement them. Otherwise do nothing.

The builder agent:
1. Reads the job spec from `plans/build_queue/`
2. Implements the change locally
3. Rsyncs to the server and restarts the service
4. Moves the job file to `plans/build_done/`
5. Sends Oliver a Telegram summary

Always use subagent-driven execution — never execute inline.
