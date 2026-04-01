"""
OpenClaw — Carousel Arbiter
OpenAI primary + Gemini fallback judge for researcher findings. Three outcomes:
  APPROVE  — pass to builder with specific build instructions
  REFINE   — topic has promise; re-queue with a more focused version
  DISCARD  — not worth pursuing
"""
import asyncio
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_APPROVE_RE       = re.compile(r"decision:\s*approve", re.IGNORECASE)
_REFINE_RE        = re.compile(r"decision:\s*refine", re.IGNORECASE)
_DISCARD_RE       = re.compile(r"decision:\s*discard", re.IGNORECASE)
_BUILD_RE         = re.compile(r"build instructions?:\s*(.+?)(?=\n\s*(?:reason|refined topic|decision):|$)", re.IGNORECASE | re.DOTALL)
_REFINED_TOPIC_RE = re.compile(r"refined topic:\s*(.+)", re.IGNORECASE)
_REASON_RE        = re.compile(r"reason:\s*(.+)", re.IGNORECASE)

_PROJECT_OBJECTIVES = {
    "utility_researcher": "Identify friction in Oliver's daily life and find practical ways to remove it.",
    "job_search":     "Secure a CSM/TAM role at a tech/AI company in the UK for Oliver Lester.",
    "trader":         "Develop a profitable paper trading strategy via AI debate pipeline.",
    "reddit":         "Build community for Dice 10k iOS game on Reddit.",
}

_ARBITER_SYSTEM = (
    "You are the arbiter for the {project} project. "
    "Project objective: {objective}\n\n"
    "Evaluate the researcher's findings and choose one of three decisions.\n\n"
    "Respond in EXACTLY one of these formats:\n\n"
    "DECISION: APPROVE\n"
    "BUILD INSTRUCTIONS: <specific, actionable instructions for the builder>\n\n"
    "or:\n\n"
    "DECISION: REFINE\n"
    "REFINED TOPIC: <a more specific, targeted version of the research topic>\n\n"
    "or:\n\n"
    "DECISION: DISCARD\n"
    "REASON: <one sentence explaining why>\n\n"
    "Rules:\n"
    "- APPROVE if findings contain a concrete, actionable improvement that is safe and clearly beneficial.\n"
    "- REFINE if the topic has real promise but the findings were too shallow, incomplete, or off-target "
    "— re-queue a sharper version of the question.\n"
    "- DISCARD if vague beyond recovery, risky, already implemented, or not worth pursuing.\n\n"
    "For trader project topics only: when your decision is APPROVE, include a CONVICTION line:\n"
    "CONVICTION: LOW | MEDIUM | HIGH\n\n"
    "HIGH conviction means: the research shows a structural advantage that appears genuinely "
    "underpriced and time-sensitive. Use sparingly. LOW is the default for interesting-but-uncertain findings."
)


@dataclass
class ArbiterDecision:
    approved: bool
    refined_topic: str = ""
    build_instructions: str = ""
    reason: str = ""


def parse_arbiter_response(text: str) -> ArbiterDecision:
    """Parse APPROVE / REFINE / DISCARD from arbiter response text."""
    if _APPROVE_RE.search(text):
        m = _BUILD_RE.search(text)
        return ArbiterDecision(approved=True, build_instructions=m.group(1).strip() if m else "")

    if _REFINE_RE.search(text):
        m = _REFINED_TOPIC_RE.search(text)
        refined = m.group(1).strip().splitlines()[0] if m else ""
        return ArbiterDecision(approved=False, refined_topic=refined)

    if _DISCARD_RE.search(text):
        m = _REASON_RE.search(text)
        reason = m.group(1).strip().splitlines()[0] if m else ""
        return ArbiterDecision(approved=False, reason=reason)

    logger.warning("Arbiter returned malformed response, defaulting to DISCARD")
    return ArbiterDecision(approved=False, reason="Arbiter response was malformed.")


async def _run_openai_arbiter(system: str, user_msg: str) -> ArbiterDecision:
    """Primary: OpenAI Responses API via openclaw gateway."""
    from core.openai_client import openai_generate

    raw = await openai_generate(system, user_msg, timeout=60)
    if not raw:
        raise RuntimeError("OpenAI arbiter returned empty response")
    logger.info("OpenAI arbiter response: %s", raw[:200])
    return parse_arbiter_response(raw)


async def _run_gemini_arbiter(system: str, user_msg: str) -> ArbiterDecision:
    """Fallback: Gemini with key pool rotation."""
    from google import genai
    from core.key_pool import get_pool
    from config import CAROUSEL_ARBITER_MODEL

    pool = get_pool()
    current_key = pool.get_key()

    last_exc: Exception | None = None
    for attempt in range(pool.available_count + 1):
        try:
            client = genai.Client(api_key=current_key)
            response = await client.aio.models.generate_content(
                model=CAROUSEL_ARBITER_MODEL,
                contents=user_msg,
                config={"system_instruction": system},
            )
            raw = response.text or ""
            logger.info("Gemini arbiter fallback response: %s", raw[:200])
            return parse_arbiter_response(raw)
        except Exception as e:
            last_exc = e
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                pool.mark_exhausted(current_key, is_quota=True)
                current_key = pool.get_key()
                logger.warning("Arbiter quota hit — rotating key (attempt %d)", attempt + 1)
            elif "503" in msg or "UNAVAILABLE" in msg:
                pool.mark_exhausted(current_key, is_quota=False)
                wait = 15 * (attempt + 1)
                logger.warning("Arbiter 503 — retrying in %ds", wait)
                await asyncio.sleep(wait)
                current_key = pool.get_key()
            else:
                logger.error("Gemini arbiter error: %r", e)
                return ArbiterDecision(approved=False, reason=f"Arbiter error: {e}")

    logger.error("Arbiter all Gemini keys exhausted: %r", last_exc)
    return ArbiterDecision(approved=False, reason=f"Arbiter error: {last_exc}")


async def run_arbiter(
    project_name: str,
    topic: str,
    findings: str,
) -> ArbiterDecision:
    """
    Call the arbiter to decide on research findings.
    Primary: OpenAI Responses API. Fallback: Gemini key pool.
    """
    objective = _PROJECT_OBJECTIVES.get(project_name, "Improve the OpenClaw system.")
    system = _ARBITER_SYSTEM.format(project=project_name, objective=objective)
    user_msg = f"Research topic: {topic}\n\nFindings:\n{findings[:8000]}"

    try:
        return await _run_openai_arbiter(system, user_msg)
    except Exception as e:
        logger.warning("OpenAI arbiter failed (%s) — falling back to Gemini", e)
        return await _run_gemini_arbiter(system, user_msg)
