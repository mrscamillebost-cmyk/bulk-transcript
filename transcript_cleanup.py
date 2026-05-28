import re


def looks_like_obvious_error(line: str) -> bool:
    lower = line.lower().strip()

    if not lower:
        return True

    obvious_noise = {
        "[music]",
        "music",
        "[applause]",
        "applause",
        "[laughter]",
        "laughter",
        "[noise]",
        "[background noise]",
    }

    if lower in obvious_noise:
        return True

    # pure timestamps or counters
    if re.fullmatch(r"\d+", lower):
        return True
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", lower):
        return True

    # clear parsing artifacts
    if "-->" in line:
        return True
    if lower == "webvtt":
        return True

    return False


def normalize_line(line: str) -> str:
    line = line.strip()

    # collapse repeated whitespace
    line = re.sub(r"\s+", " ", line)

    # remove spaces before punctuation
    line = re.sub(r"\s+([,.;:!?])", r"\1", line)

    return line.strip()


def clean_transcript_text(text: str) -> str:
    raw_lines = text.splitlines()
    cleaned_lines = []

    previous_normalized = None

    for raw_line in raw_lines:
        line = normalize_line(raw_line)

        if looks_like_obvious_error(line):
            continue

        # remove obvious adjacent duplicates only
        if previous_normalized and line.lower() == previous_normalized.lower():
            continue

        cleaned_lines.append(line)
        previous_normalized = line

    # preserve as much wording as possible; only rebuild into readable paragraphs
    paragraphs = []
    current = []

    for line in cleaned_lines:
        current.append(line)

        # create a new paragraph when enough text has accumulated
        if len(" ".join(current)) >= 900:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs).strip()
