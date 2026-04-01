"""
Score a job posting against a candidate profile using keyword + title heuristics.
Phase 1: weighted keyword scoring. Phase 2: replace with LLM scoring.

Candidate profile is loaded from private config at runtime — role signals,
skill weights, location preferences, and disqualifiers are all configurable
per user without hardcoding personal details here.
"""
from typing import Any


def score_job(job: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """
    Score a job 0–100 against the candidate profile.
    Returns {"score": int, "reasoning": str, "match_signals": list, "red_flags": list}

    Profile keys expected:
        role_signals_high   — bullseye role titles (+12 each)
        role_signals_med    — adjacent roles worth considering (+6 each)
        skill_signals       — relevant skills and keywords (+3 each)
        ai_signals          — differentiator signals, capped contribution (+8, max 4)
        junior_signals      — openness to potential over experience (+5 each)
        location_signals    — acceptable locations/work modes (+8, once)
        hard_negatives      — disqualifiers (-25 each)
        soft_negatives      — score reducers, not killers (-10 each)
    """
    text = (
        (job.get("title", "") + " " + job.get("description", "") + " " + job.get("location", ""))
        .lower()
    )

    match_signals: list[str] = []
    red_flags: list[str] = []
    score = 20  # low baseline — must earn the score

    for signal in profile.get("role_signals_high", []):
        if signal in text:
            match_signals.append(f"target role: {signal}")
            score += 12

    for signal in profile.get("role_signals_med", []):
        if signal in text:
            match_signals.append(f"adjacent role: {signal}")
            score += 6

    ai_hits = 0
    for signal in profile.get("ai_signals", []):
        if signal in text:
            if ai_hits < 4:
                match_signals.append(f"differentiator: {signal}")
                score += 8
            ai_hits += 1

    for signal in profile.get("skill_signals", []):
        if signal in text:
            match_signals.append(f"skill: {signal}")
            score += 3

    for signal in profile.get("junior_signals", []):
        if signal in text:
            match_signals.append(f"open to potential: {signal}")
            score += 5

    for signal in profile.get("location_signals", []):
        if signal in text:
            match_signals.append("location confirmed")
            score += 8
            break

    for neg in profile.get("hard_negatives", []):
        if neg in text:
            red_flags.append(f"hard disqualifier: {neg}")
            score -= 25

    for neg in profile.get("soft_negatives", []):
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


def rank_jobs(jobs: list[dict], profile: dict[str, Any], min_score: int = 45) -> list[dict]:
    """Score and sort jobs, highest first. Filters below min_score."""
    scored = [
        {**job, **score_job(job, profile)}
        for job in jobs
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [j for j in scored if j["score"] >= min_score]
