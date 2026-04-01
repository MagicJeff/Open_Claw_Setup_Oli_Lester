"""
Score a job against Oliver's profile using keyword + title heuristics.
Phase 1: simple weighted keyword scoring. Phase 2: replace with LLM scoring.

Oliver's profile:
- Strong: comms, interpersonal, stakeholder management, AI building, vibe coding
- Weak: hard technical skills (no CS degree, <2 years formal experience)
- Target: tech-adjacent roles bridging business and tech, junior/trainee/associate
- Differentiator: AI tools, multi-agent integrations, prompt engineering, vibe coding
- Location: London hybrid or remote UK
"""
from typing import Any

# Heavy weight — these are the bullseye roles
_ROLE_SIGNALS_HIGH = [
    # Tech-adjacent / bridge roles
    "implementation consultant", "solutions consultant", "technical consultant",
    "ai consultant", "ai specialist", "ai engineer", "automation consultant",
    "digital transformation", "technical customer success", "customer success manager",
    "technical account manager", "client solutions", "solutions engineer",
    "pre-sales consultant", "pre-sales engineer", "sales engineer",
    "product consultant", "platform consultant", "integration consultant",
    "ai product manager", "technical product manager",
    # Junior engineering roles — low bar, hire on potential
    "junior platform engineer", "associate platform engineer",
    "junior devops", "associate devops", "graduate devops",
    "junior cloud engineer", "associate cloud engineer", "graduate cloud",
    "junior site reliability", "associate site reliability",
    "junior software engineer", "associate software engineer", "graduate engineer",
    "junior infrastructure", "associate infrastructure",
    "junior backend", "associate backend",
]

# Medium weight — broader tech-adjacent roles worth considering
_ROLE_SIGNALS_MED = [
    "customer success", "client success", "account manager", "account executive",
    "business analyst", "systems analyst", "process consultant",
    "relationship manager", "partnership manager", "technical support",
    "product manager", "product specialist", "solutions architect",
    "junior architect", "associate consultant", "associate engineer",
    "onboarding specialist", "implementation specialist",
    # General platform/devops/cloud (without junior qualifier — scored lower)
    "platform engineer", "devops engineer", "cloud engineer",
    "site reliability engineer", "sre", "infrastructure engineer",
    "software engineer",
]

# AI/vibe-coding skill signals — Oliver's biggest differentiator, high weight
_AI_SIGNALS = [
    "ai", "artificial intelligence", "llm", "gpt", "claude", "gemini",
    "prompt engineering", "vibe coding", "agentic", "multi-agent",
    "automation", "no-code", "low-code", "ai tools", "generative ai",
    "chatgpt", "copilot", "cursor", "workflow automation",
    "n8n", "zapier", "make.com", "langchain",
]

# General skill signals
_SKILL_SIGNALS = [
    "communication", "stakeholder", "relationship", "interpersonal",
    "presentation", "client-facing", "customer-facing", "technical writing",
    "project management", "cross-functional", "product knowledge",
    "saas", "api", "integration", "onboarding", "training",
    "python", "startup", "scale-up",
    # Platform/cloud/devops skills — positive in junior context
    "aws", "cloud", "devops", "observability", "reliability",
    "kubernetes", "docker", "terraform", "ci/cd", "infrastructure",
    "monitoring", "deployment", "cloud-native",
]

# Junior/trainee/potential signals — good for Oliver
_JUNIOR_SIGNALS = [
    "junior", "associate", "graduate", "trainee", "entry level", "entry-level",
    "0-1 year", "0-2 year", "1-2 year", "no experience required",
    "potential", "attitude", "willingness to learn", "eager", "growth mindset",
    "we'll train", "training provided", "fast learner",
]

# Hard disqualifiers — Oliver genuinely can't compete here
_NEGATIVE_SIGNALS_HARD = [
    "java developer", "backend engineer", "data engineer", "devops engineer",
    "infrastructure engineer", "network engineer", "security engineer",
    "c++ engineer", "embedded engineer", "firmware engineer",
    "10+ years", "10 years experience", "15 years", "12 years",
    "director level", "vp of", "vice president", "c-level", "chief ",
    "united states only", "us only", "must be us", "canada only",
]

# Soft negatives — reduce score but don't kill it
_NEGATIVE_SIGNALS_SOFT = [
    "5+ years", "7+ years", "8+ years",
    "computer science degree required", "cs degree required",
    "must have degree", "engineering degree required",
    "aws certified", "gcp certified", "azure certified",
    "no remote", "on-site only", "fully on-site",
]

_UK_SIGNALS = [
    "uk", "united kingdom", "london", "manchester", "edinburgh",
    "birmingham", "bristol", "leeds", "remote uk", "hybrid uk",
    "hybrid", "remote",
]


def score_job(job: dict[str, Any], profile: str) -> dict[str, Any]:
    """
    Score a job 0–100 against Oliver's profile.
    Returns {"score": int, "reasoning": str, "match_signals": list, "red_flags": list}
    """
    text = (
        (job.get("title", "") + " " + job.get("description", "") + " " + job.get("location", ""))
        .lower()
    )

    match_signals: list[str] = []
    red_flags: list[str] = []
    score = 20  # low baseline — must earn the score

    # High-value role signals (+12 each)
    for signal in _ROLE_SIGNALS_HIGH:
        if signal in text:
            match_signals.append(f"target role: {signal}")
            score += 12

    # Medium role signals (+6 each)
    for signal in _ROLE_SIGNALS_MED:
        if signal in text:
            match_signals.append(f"adjacent role: {signal}")
            score += 6

    # AI/vibe-coding signals (+8 each, capped at +32) — Oliver's biggest edge
    ai_hits = 0
    for signal in _AI_SIGNALS:
        if signal in text:
            if ai_hits < 4:
                match_signals.append(f"AI signal: {signal}")
                score += 8
            ai_hits += 1

    # General skill signals (+3 each)
    for signal in _SKILL_SIGNALS:
        if signal in text:
            match_signals.append(f"skill: {signal}")
            score += 3

    # Junior/potential signals (+5 each) — Oliver needs these doors
    for signal in _JUNIOR_SIGNALS:
        if signal in text:
            match_signals.append(f"junior/potential: {signal}")
            score += 5

    # UK/remote location (+8, once)
    for signal in _UK_SIGNALS:
        if signal in text:
            match_signals.append("UK/remote location confirmed")
            score += 8
            break

    # Hard negatives (-25 each)
    for neg in _NEGATIVE_SIGNALS_HARD:
        if neg in text:
            red_flags.append(f"hard disqualifier: {neg}")
            score -= 25

    # Soft negatives (-10 each)
    for neg in _NEGATIVE_SIGNALS_SOFT:
        if neg in text:
            red_flags.append(f"soft negative: {neg}")
            score -= 10

    score = max(0, min(100, score))

    return {
        "score": score,
        "reasoning": f"{len(match_signals)} positive signals, {len(red_flags)} red flags",
        "match_signals": match_signals[:6],
        "red_flags": red_flags,
    }


def rank_jobs(jobs: list[dict], profile: str) -> list[dict]:
    """Score and sort jobs, highest score first. Filters out score < 45."""
    scored = []
    for job in jobs:
        result = score_job(job, profile)
        scored.append({**job, **result})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [j for j in scored if j["score"] >= 45]
