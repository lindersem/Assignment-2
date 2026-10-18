"""Regex sanitization, stable-sequence, and incident-index functions."""

import re


def sanitize(text):
    text = re.sub(r"\b[a-zA-Z]{4}\d{7}\b", "[CONTAINER]", text, flags=re.IGNORECASE)
    text = re.sub(r"\bSEAL-\d{6}\b", "[SEAL]", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "[EMAIL]", text
    )
    return text


# task 7
def get_longest_stable_sequence(event_codes):
    start = 0
    max_start = 0
    max_length = 0
    last_seen = {}

    for end, code in enumerate(event_codes):
        if code in last_seen and last_seen[code] >= start:
            start = last_seen[code] + 1

        last_seen[code] = end
        current_length = end - start + 1

        if current_length > max_length:
            max_length = current_length
            max_start = start

    longest_seq = event_codes[max_start : max_start + max_length]
    return longest_seq, max_length


# task 9
def clean_text(text):
    text = text.lower()
    # remove punctuation:
    # replace everything that is not (\w) or (\s) with nothing
    text = re.sub(r"[^\w\s]", "", text)
    return text


def tokenize(text):
    cleaned = clean_text(text)
    return cleaned.split()
