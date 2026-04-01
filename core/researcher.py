"""
OpenClaw v4 — Researcher worker (DeepSeek R1 8B via Ollama)
Max 2 concurrent researchers (Semaphore(2)).
"""
import asyncio
import logging

import httpx

from config import OLLAMA_URL, RESEARCHER_MODEL

logger = logging.getLogger(__name__)

_semaphore = asyncio.Semaphore(2)

_DEFAULT_SYSTEM = (
    "You are a specialist research agent. Investigate the given topic thoroughly. "
    "Structure your findings with these sections:\n"
    "## Summary\n## Key Findings\n## Risks / Issues\n## Recommendations\n\n"
    "Be specific, cite evidence, and prioritise findings as Critical/High/Medium/Low."
)


async def research(
    topic: str,
    context: str,
    system_prompt: str | None = None,
) -> str:
    """
    Spawn a DeepSeek R1 8B researcher for a specific topic.
    Blocks if 2 researchers are already running (Semaphore).
    Returns structured findings as a string.
    """
    system = system_prompt or _DEFAULT_SYSTEM
    payload = {
        "model": RESEARCHER_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Topic: {topic}\n\nContext:\n{context}"},
        ],
        "stream": False,
        "options": {
            "num_ctx": 16384,  # Override Ollama default (2048) — fits ~12K chars of context
        },
    }

    async with _semaphore:
        logger.info("Researcher starting: %s", topic)
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(OLLAMA_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                findings = data["message"]["content"]
                logger.info("Researcher done: %s (%d chars)", topic, len(findings))
                return findings
        except httpx.ConnectError:
            return f"[Researcher error] Ollama not reachable at {OLLAMA_URL}. Is it running?"
        except httpx.ReadTimeout:
            return f"[Researcher error] Timeout — {RESEARCHER_MODEL} took too long. Try a shorter context."
        except Exception as e:
            logger.error("Researcher error for '%s': %r", topic, e)
            return f"[Researcher error] {type(e).__name__}: {e}"


async def research_parallel(tasks: list[dict]) -> list[str]:
    """
    Run multiple research tasks in parallel (Semaphore caps at 2 concurrent).
    Each task dict: {"topic": str, "context": str, "system_prompt": str | None}
    Returns list of findings in the same order as tasks.
    """
    coros = [research(**task) for task in tasks]
    return list(await asyncio.gather(*coros))
