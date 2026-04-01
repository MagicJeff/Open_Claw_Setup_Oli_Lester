import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

_researcher_limit = asyncio.Semaphore(2)
_builder_limit = asyncio.Semaphore(1)


async def run_local_researcher(ollama_url: str, model: str, topic: str, context: str) -> str:
    """Representative local researcher pattern with explicit concurrency limits."""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a specialist research agent. Return structured findings.",
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nContext:\n{context}",
            },
        ],
        "stream": False,
    }

    async with _researcher_limit:
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(ollama_url, json=payload)
                response.raise_for_status()
                return response.json()["message"]["content"]
        except httpx.ConnectError:
            return "[Researcher error] Ollama is not reachable."
        except Exception as exc:
            logger.error("Local researcher failed: %s", exc)
            return f"[Researcher error] {exc}"


async def run_local_builder(ollama_url: str, model: str, task: str, context: str) -> str:
    """Representative local builder pattern with stricter serial execution."""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert Python developer. Return clean implementation code.",
            },
            {
                "role": "user",
                "content": f"Task: {task}\n\nContext:\n{context}",
            },
        ],
        "stream": False,
    }

    async with _builder_limit:
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(ollama_url, json=payload)
                response.raise_for_status()
                return response.json()["message"]["content"]
        except httpx.ConnectError:
            return "[Builder error] Ollama is not reachable."
        except Exception as exc:
            logger.error("Local builder failed: %s", exc)
            return f"[Builder error] {exc}"
