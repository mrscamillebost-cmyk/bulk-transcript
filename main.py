from pathlib import Path

from transcript_cleanup import clean_transcript_text
from transcriber import get_youtube_urls_from_input, transcribe_youtube_url

INPUT_FILE = Path("input_urls.txt")
OUTPUT_DIR = Path("transcripts")
COMBINED_FILE = OUTPUT_DIR / "combined_transcripts.md"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)


def read_input_lines():
    if not INPUT_FILE.exists():
        print(f"Missing {INPUT_FILE}")
        return []

    return INPUT_FILE.read_text(encoding="utf-8").splitlines()


def build_video_section(title, url, transcript_text):
    return f"""# {title}

Source URL: {url}

{transcript_text}
"""


def main():
    ensure_output_dir()

    input_lines = read_input_lines()
    if not input_lines:
        print("No valid input found in input_urls.txt")
        return

    urls = get_youtube_urls_from_input(input_lines)

    if not urls:
        print("No valid YouTube video URLs found.")
        return

    COMBINED_FILE.write_text("", encoding="utf-8")

    for url in urls:
        try:
            print(f"Starting: {url}")
            title, raw_transcript = transcribe_youtube_url(url)
            cleaned_transcript
