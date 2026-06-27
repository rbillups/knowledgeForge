import logging
import re

logger = logging.getLogger(__name__)

PRIVACY_BLOCKED_ANSWER = (
    "I can't provide personal contact details or private location information. "
    "Please use Key'Shawn's portfolio contact page or public GitHub profile to get in touch."
)

_PUBLIC_CONTACT_PHRASES = (
    "how can i contact",
    "how can someone contact",
    "how to contact",
    "contact professionally",
    "public contact",
    "portfolio contact",
    "view his portfolio",
    "view his github",
    "get in touch professionally",
    "reach out professionally",
)

_SENSITIVE_PATTERNS = (
    re.compile(r"\b(home|street|residential|mailing) address\b"),
    re.compile(r"\b(personal|private) (phone|email|contact)\b"),
    re.compile(r"\bphone number\b"),
    re.compile(r"\bcell phone\b"),
    re.compile(r"\bmobile number\b"),
    re.compile(r"\bprivate email\b"),
    re.compile(r"\bemail address\b"),
    re.compile(r"\bwhere does .+ live\b"),
    re.compile(r"\bwhere .+ lives exactly\b"),
    re.compile(r"\blive exactly\b"),
    re.compile(r"\bexact (home|location|address)\b"),
    re.compile(r"\bprecise (location|address)\b"),
    re.compile(r"\bcurrent location\b"),
    re.compile(r"\bgps coordinates\b"),
    re.compile(r"\bhome location\b"),
)


def is_privacy_sensitive_question(question: str) -> bool:
    normalized = _normalize_question(question)

    if not normalized:
        return False

    if _is_public_contact_request(normalized):
        return False

    if "phone" in normalized and "address" in normalized:
        return True

    return any(pattern.search(normalized) for pattern in _SENSITIVE_PATTERNS)


def _normalize_question(question: str) -> str:
    return " ".join(question.lower().strip().split())


def _is_public_contact_request(normalized_question: str) -> bool:
    asks_for_public_contact = any(
        phrase in normalized_question for phrase in _PUBLIC_CONTACT_PHRASES
    )
    if not asks_for_public_contact:
        return False

    return not any(
        pattern.search(normalized_question) for pattern in _SENSITIVE_PATTERNS
    )
