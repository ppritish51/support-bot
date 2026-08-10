"""Deterministic safety envelope: PII/sensitivity pre-flight + confidence post-flight.

These run in code, NOT in the model — a safety guarantee we never let the agent
"forget" to apply.
"""
import re

from app.config import settings

# --- Sensitivity signal (pre-flight) ---------------------------------------

_PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "api_key": re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9_\-]{12,}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}

# Topics a support bot should never auto-resolve.
_SENSITIVE_TOPICS = [
    "refund", "chargeback", "cancel my account", "close my account",
    "delete my account", "password", "reset my password", "security breach",
    "hacked", "lawsuit", "legal", "gdpr", "data deletion",
]


def scan_sensitivity(text: str) -> tuple[bool, str | None]:
    """Return (is_sensitive, detail). True forces escalation before the agent runs."""
    for name, pat in _PII_PATTERNS.items():
        if pat.search(text):
            return True, f"pii:{name}"
    low = text.lower()
    for topic in _SENSITIVE_TOPICS:
        if topic in low:
            return True, f"topic:{topic}"
    return False, None


# --- Confidence signal (post-flight) ---------------------------------------

def compute_confidence(cited_scores: list[float], is_grounded: bool) -> str:
    """Confidence from retrieval scores + the model's grounding self-report.

    Computed in code so the model can't self-declare 'High' to dodge escalation.
    """
    if not is_grounded or not cited_scores:
        return "Low"
    top = max(cited_scores)
    if top >= settings.conf_high:
        return "High"
    if top >= settings.conf_medium:
        return "Medium"
    return "Low"
