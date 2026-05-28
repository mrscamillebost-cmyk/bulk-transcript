import re


def is_obvious_junk(line: str) -> bool:
    test = line.strip().lower()

    if not test:
        return True
    if test == "webvtt":
        return True
    if "-->" in test:
        return True
    if re.fullmatch(r"\d+", test):
        return True
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", test):
        return True

    standalone_noise = {
        "[music]",
        "music",
        "[applause]",
        "applause",
        "[laughter]",
        "laughter",
        "[noise]",
        "[background noise]",
    }
    if test in standalone_noise:
        return True

    return False


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\s+([,.;:!?])", r"\1", line)
    return line.strip()


def clean_transcript_text(text: str) -> str:
    raw_lines = text.splitlines()
    kept_lines = []
    previous = None

    for raw_line in raw_lines:
        line = normalize_line(raw_line)

        if is_obvious_junk(line):
            continue

        if previous and line.lower() == previous.lower():
            continue

        kept_lines.append(line)
        previous = line

    paragraphs = []
    current = []

    for line in kept_lines:
        current.append(line)
        if len(" ".join(current)) >= 1200:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs).strip()
