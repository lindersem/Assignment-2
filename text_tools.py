"""Regex sanitization, stable-sequence, and incident-index functions."""

import re

def sanitize(text):
    text = re.sub(r"\b[a-zA-Z]{4}\d{7}\b", "[CONTAINER]",text, flags=re.IGNORECASE)
    text = re.sub(r"\bSEAL-\d{6}\b", "[SEAL]",text, flags=re.IGNORECASE)
    text = re.sub(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "[EMAIL]",text)
    return text