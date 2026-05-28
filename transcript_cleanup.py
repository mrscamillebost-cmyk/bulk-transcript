import re


def clean_transcript_markdown(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    previous = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # remove timestamp-like lines
        if "-->" in line:
            continue
        if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", line):
            continue
        if re.match(r"^\d+$", line):
            continue

        # normalize whitespace
        line = re.sub(r"\s+", " ", line)

        # skip repeated adjacent lines
        if previous and line.lower() == previous.lower():
            continue

        cleaned.append(line)
        previous = line

    # join into readable paragraphs
    paragraphs = []
    current = []

    for line in cleaned:
        current.append(line)
        if len(" ".join(current)) > 500:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs).strip()
