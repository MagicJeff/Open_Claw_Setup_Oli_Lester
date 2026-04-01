"""
OpenClaw — Carousel Researcher
OpenAI primary + Gemini fallback researcher for the experiment carousel.
Used exclusively by the experiment carousel (sequential, one at a time).
"""
import asyncio
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

RESEARCHER_TIMEOUT_SECS = 300  # 5 minutes


@dataclass
class ResearcherResult:
    findings: str
    tool_calls_made: int
    timed_out: bool


async def _run_openai_researcher(topic: str, research_type: str, project_name: str) -> ResearcherResult:
    """
    Primary path: OpenAI Responses API synthesis.
      1. Fetch supplemental data in parallel (HN, arXiv, Polymarket, Reddit)
      2. OpenAI synthesises everything into structured findings
    """
    from config import PROJECTS_DIR
    from core.openai_client import openai_generate
    from tools.research import fetch_supplemental

    soul_path = PROJECTS_DIR / project_name / "SOUL.md"
    soul_context = ""
    if soul_path.exists():
        soul_context = f"\n\nProject researcher identity:\n{soul_path.read_text()[:1500]}"

    # Fetch supplemental sources in parallel (~5-10s)
    supplemental = await fetch_supplemental(topic, project_name)
    logger.debug("Supplemental fetch complete for %s (%d chars)", project_name, len(supplemental))

    system_prompt = (
        f"You are a specialist research agent for the {project_name} project.{soul_context}\n\n"
        f"You have been given supplemental data from Hacker News, arXiv, Polymarket, and/or Reddit. "
        f"Synthesise all available sources into actionable findings.\n\n"
        f"Produce structured findings:\n"
        f"## Summary\n## Key Findings\n## Recommendation\n\n"
        f"Be specific, cite sources, and focus on actionable insights for {project_name}."
    )

    user_msg = (
        f"Research task: {topic}\n"
        f"Type: {research_type}\n\n"
        f"--- Supplemental data (pre-fetched) ---\n{supplemental[:6000]}"
    )

    findings = await openai_generate(system_prompt, user_msg, timeout=180)
    if not findings:
        raise RuntimeError("OpenAI returned empty response")

    logger.info("OpenAI researcher done: %d chars", len(findings))
    return ResearcherResult(findings=findings, tool_calls_made=0, timed_out=False)


async def _run_gemini_researcher(topic: str, research_type: str, project_name: str) -> ResearcherResult:
    """
    Fallback path: Gemini + Google Search grounding synthesis.
    Rotates through the shared key pool on 429/503.
    """
    from google import genai
    from google.genai import types
    from config import CAROUSEL_ARBITER_MODEL, PROJECTS_DIR
    from core.key_pool import get_pool
    from tools.research import fetch_supplemental

    soul_path = PROJECTS_DIR / project_name / "SOUL.md"
    soul_context = ""
    if soul_path.exists():
        soul_context = f"\n\nProject researcher identity:\n{soul_path.read_text()[:1500]}"

    pool = get_pool()
    current_key = pool.get_key()

    # Fetch supplemental sources
    supplemental = await fetch_supplemental(topic, project_name)

    system_prompt = (
        f"You are a specialist research agent for the {project_name} project.{soul_context}\n\n"
        f"You have been given supplemental data from Hacker News, arXiv, Polymarket, and/or Reddit "
        f"in addition to your Google Search access. Use ALL available sources.\n\n"
        f"Produce structured findings:\n"
        f"## Summary\n## Key Findings\n## Recommendation\n\n"
        f"Be specific, cite sources, and focus on actionable insights for {project_name}."
    )

    user_msg = (
        f"Research task: {topic}\n"
        f"Type: {research_type}\n\n"
        f"--- Supplemental data (pre-fetched) ---\n{supplemental[:6000]}"
    )

    last_exc: Exception | None = None
    for attempt in range(pool.available_count + 1):
        try:
            client = genai.Client(api_key=current_key)
            response = await client.aio.models.generate_content(
                model=CAROUSEL_ARBITER_MODEL,
                contents=user_msg,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    system_instruction=system_prompt,
                ),
            )
            findings = (response.text or "").strip()

            # Append grounding source URLs
            sources = []
            if response.candidates:
                meta = getattr(response.candidates[0], "grounding_metadata", None)
                if meta:
                    for chunk in getattr(meta, "grounding_chunks", []) or []:
                        web = getattr(chunk, "web", None)
                        if web and getattr(web, "uri", None):
                            title = getattr(web, "title", web.uri)
                            sources.append(f"- [{title}]({web.uri})")
            if sources:
                findings += "\n\n**Sources:**\n" + "\n".join(sources[:10])

            if not findings:
                return ResearcherResult(findings="[Gemini returned empty response]", tool_calls_made=0, timed_out=False)

            logger.info("Gemini researcher fallback done: %d chars, %d google sources", len(findings), len(sources))
            return ResearcherResult(findings=findings, tool_calls_made=1, timed_out=False)

        except Exception as e:
            last_exc = e
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                pool.mark_exhausted(current_key, is_quota=True)
                current_key = pool.get_key()
                logger.warning("Researcher quota hit — rotating to next key (attempt %d)", attempt + 1)
            elif "503" in msg or "UNAVAILABLE" in msg:
                pool.mark_exhausted(current_key, is_quota=False)
                wait = 15 * (attempt + 1)
                logger.warning("Researcher 503 — retrying in %ds", wait)
                await asyncio.sleep(wait)
                current_key = pool.get_key()
            else:
                logger.error("Gemini researcher error for '%s': %r", topic, e)
                return ResearcherResult(findings=f"[Gemini researcher error] {e}", tool_calls_made=0, timed_out=False)

    logger.error("Researcher: all Gemini keys exhausted for '%s': %r", topic, last_exc)
    return ResearcherResult(findings=f"[All researcher backends failed] {last_exc}", tool_calls_made=0, timed_out=False)


async def run_researcher(
    topic: str,
    research_type: str,
    project_name: str,
) -> ResearcherResult:
    """
    Run the carousel researcher.
    Primary: OpenAI Responses API (via openclaw gateway).
    Fallback: Gemini + Google Search grounding (key pool rotation).
    """
    logger.info("Carousel researcher starting: [%s] %s", research_type, topic)
    try:
        return await _run_openai_researcher(topic, research_type, project_name)
    except Exception as e:
        logger.warning("OpenAI researcher failed (%s) — falling back to Gemini", e)
        return await _run_gemini_researcher(topic, research_type, project_name)
