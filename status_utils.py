import re


def safe_notes(text):
    return str(text).replace(",", ";").replace("\n", " ").strip()


def slugify(text):
    text = str(text).strip().lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_") or "transcript"
