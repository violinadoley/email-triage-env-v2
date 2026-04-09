"""
Deterministic graders for all three email triage tasks.

All graders return (reward: float, score: float, feedback: str).
Scores are always in [0.0, 1.0].
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


# ─── Shared ───────────────────────────────────────────────────────────────────

VALID_CATEGORIES = {"spam", "work", "personal", "newsletter"}


def _clamp(score: float) -> float:
    """Clamp score to strictly open interval (0, 1) as required by the validator."""
    return max(0.01, min(0.99, score))


# ─── Task 1: classify_email (easy) ────────────────────────────────────────────

def grade_classify(content: str, ground_truth: str) -> Tuple[float, float, str]:
    """
    Score 1.0 for correct label, 0.0 otherwise.
    Accepts labels embedded in longer text (e.g. "This email is spam").
    """
    predicted = content.strip().lower()
    if predicted not in VALID_CATEGORIES:
        for cat in VALID_CATEGORIES:
            if cat in predicted:
                predicted = cat
                break
        else:
            s = _clamp(0.0)
            return (
                s, s,
                f"Invalid category '{content.strip()}'. "
                f"Must be one of: {', '.join(sorted(VALID_CATEGORIES))}."
            )

    if predicted == ground_truth:
        s = _clamp(1.0)
        return s, s, f"Correct! Email is '{ground_truth}'."
    s = _clamp(0.0)
    return s, s, f"Incorrect. Got '{predicted}', expected '{ground_truth}'."


# ─── Task 2: prioritize_inbox (medium) ────────────────────────────────────────

def _kendall_tau_distance(a: List[int], b: List[int]) -> int:
    """Count discordant pairs between two orderings of the same elements."""
    pos_b = {v: i for i, v in enumerate(b)}
    discordant = 0
    n = len(a)
    for i in range(n):
        for j in range(i + 1, n):
            if pos_b[a[i]] > pos_b[a[j]]:
                discordant += 1
    return discordant


def _parse_ranking(content: str, expected_ids: List[int]) -> Optional[List[int]]:
    numbers = re.findall(r"\d+", content)
    try:
        ranking = [int(n) for n in numbers]
    except ValueError:
        return None

    ranking = [r for r in ranking if r in expected_ids]
    seen: set = set()
    unique: List[int] = []
    for r in ranking:
        if r not in seen:
            seen.add(r)
            unique.append(r)

    return unique if set(unique) == set(expected_ids) else None


def grade_prioritize(content: str, correct_ranking: List[int]) -> Tuple[float, float, str]:
    """
    Score = 1 − (kendall_tau / max_distance). Partial credit for partial orderings.
    """
    n = len(correct_ranking)
    max_dist = n * (n - 1) // 2

    parsed = _parse_ranking(content, correct_ranking)
    if parsed is None:
        s = _clamp(0.0)
        return (
            s, s,
            f"Could not parse ranking. "
            f"Expected comma-separated IDs like '{','.join(map(str, correct_ranking))}'. "
            f"Got: '{content[:150]}'"
        )

    dist = _kendall_tau_distance(parsed, correct_ranking)
    score = _clamp(round(1.0 - dist / max_dist, 4))

    if score == 1.0:
        feedback = f"Perfect ranking! Correct: {correct_ranking}."
    elif score >= 0.6:
        feedback = (
            f"Good ranking. {dist} pair(s) out of order. "
            f"Correct: {correct_ranking}. Yours: {parsed}."
        )
    else:
        feedback = (
            f"Poor ranking. {dist} pair(s) out of order. "
            f"Correct: {correct_ranking}. Yours: {parsed}."
        )
    return score, score, feedback


# ─── Task 3: draft_reply (hard) ───────────────────────────────────────────────

_GREETING_RE = [
    r"\bhi\b", r"\bhello\b", r"\bdear\b", r"\bgreetings\b",
    r"\bgood\s+(morning|afternoon|evening)\b",
    r"\bthanks?\s+for\b", r"\bthank\s+you\s+for\b",
]
_CLOSING_RE = [
    r"\bbest\s+regards?\b", r"\bkind\s+regards?\b", r"\bsincerely\b",
    r"\bthanks?\b", r"\bthank\s+you\b", r"\bcheers\b",
    r"\bwarm\s+regards?\b", r"\blooking\s+forward\b", r"\brespectfully\b",
]


def grade_draft_reply(content: str, email_data: Dict[str, Any]) -> Tuple[float, float, str]:
    """
    Rubric-based grader (deterministic, no LLM):
      greeting        0.10
      body ≥30 words  0.20
      closing         0.10
      length ok       0.20
      keyword overlap 0.40
    """
    reply = content.strip()
    low = reply.lower()
    parts: Dict[str, float] = {}

    parts["greeting"] = 0.10 if any(re.search(p, low) for p in _GREETING_RE) else 0.0
    parts["body"] = 0.20 if len(reply.split()) >= 30 else 0.0
    parts["closing"] = 0.10 if any(re.search(p, low) for p in _CLOSING_RE) else 0.0

    char_len = len(reply)
    if 50 <= char_len <= 1000:
        parts["length"] = 0.20
    elif char_len < 50:
        parts["length"] = 0.0
    else:
        excess = char_len - 1000
        parts["length"] = round(max(0.0, 0.20 - (excess / 1000) * 0.20), 4)

    keywords: List[str] = email_data.get("keywords", [])
    subject_words = email_data.get("email", {}).get("subject", "").lower().split()
    all_kw = [k.lower() for k in keywords] + [w for w in subject_words if len(w) > 4]
    if all_kw:
        matched = sum(1 for kw in all_kw if kw in low)
        parts["keywords"] = round(min(1.0, matched / len(all_kw)) * 0.40, 4)
    else:
        parts["keywords"] = 0.0

    total = _clamp(round(sum(parts.values()), 4))
    quality = "Excellent" if total >= 0.8 else "Good" if total >= 0.6 else "Fair" if total >= 0.4 else "Poor"
    breakdown = ", ".join(f"{k}={v:.2f}" for k, v in parts.items())
    feedback = f"{quality} reply (score={total:.2f}). {breakdown}. Words: {len(reply.split())}."
    return total, total, feedback
