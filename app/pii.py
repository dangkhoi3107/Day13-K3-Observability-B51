from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Do not match the lowercase hex portion of IDs such as req-a1234567.
    "passport": r"(?<![\w-])(?i:[A-Z]\d{7,8})\b",
    # Redact the address value as well as the identifying keyword.
    "address_vn": (
        r"\b(?:\d{1,5}\s+)?(?i:s\u1ed1\s+nh\u00e0|\u0111\u01b0\u1eddng|ph\u1ed1|ph\u01b0\u1eddng|qu\u1eadn|huy\u1ec7n|"
        r"t\u1ec9nh|th\u00e0nh\s+ph\u1ed1|x\u00e3|ng\u00f5|ng\u00e1ch|h\u1ebbm|\u1ea5p|th\u00f4n|tp\.|q\.|p\.)\s+[^,;\n]+"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
