import asyncio
import re

_ALLOWLIST = [
    r"^docker ps( -a)?$",
    r"^(sudo )?systemctl (restart|start|stop|status) openclaw(\.service)?$",
    r"^(sudo )?journalctl -u openclaw( -n \d+)?( --no-pager)?$",
    r"^df -h$",
    r"^free -h$",
]

_COMPILED = [re.compile(pattern) for pattern in _ALLOWLIST]


def is_allowed(command: str) -> bool:
    return any(pattern.match(command.strip()) for pattern in _COMPILED)


async def run_guarded(command: str, timeout: int = 60) -> str:
    """Representative shell execution guard used to keep ops commands narrow."""
    if not is_allowed(command):
        return f"Blocked command: {command}"

    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    return stdout.decode().strip() or "(no output)"
