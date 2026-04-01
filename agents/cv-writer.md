# CV Writer Agent

**Start with:** `claude --dangerously-skip-permissions --channels plugin:telegram@claude-plugins-official`

This agent is event-driven. On session start, connect to the OpenClaw Telegram channel and wait. Do not poll. Do not SSH into the server unless processing a job.

## When a CV trigger arrives

OpenClaw sends a message in this format:

```
CV job queued: [Role Title] @ [Company]
JD path: plans/cv_queue/[filename].md
```

When received:

1. SSH into the server and read the job description file
2. Invoke the cv-writer agent with the full JD content
3. The agent writes a tailored CV as a Word `.docx` and saves it to `plans/cv_ready/`
4. Reply in the channel confirming the CV is ready
5. OpenClaw picks up the reply and delivers the CV to Oliver via Telegram DM

## Revisions

If Oliver gives direct feedback on a CV, process the revision immediately — no need to wait for a queued revision file.

Always use subagent-driven execution — never execute inline.
