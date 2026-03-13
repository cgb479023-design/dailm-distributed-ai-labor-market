import re
from typing import Dict


_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_CN_PHONE_RE = re.compile(r"\b1[3-9]\d{9}\b")
_US_PHONE_RE = re.compile(r"\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
_ID_CN_RE = re.compile(r"\b\d{17}[\dXx]\b")


def scrub_pii(text: str) -> str:
    if not text:
        return text
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _CN_PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = _US_PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = _ID_CN_RE.sub("[REDACTED_ID]", text)
    return text


def scrub_map(data: Dict[str, str]) -> Dict[str, str]:
    return {k: scrub_pii(v) if isinstance(v, str) else v for k, v in data.items()}
