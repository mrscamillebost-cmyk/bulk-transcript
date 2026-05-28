from pathlib import Path

from transcript_cleanup import clean_transcript_text
from transcriber import get_youtube_urls_from_input, transcribe_youtube_url

INPUT_FILE = Path("input_urls.txt")
OUTPUT_DIR = Path("transcripts")
COMBINED_FILE = OUTPUT_DIR / "combined_transcripts.md"
STATUS_FILE = OUTPUT_DIR / "status.csv"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)


def read_input_lines():
    if not INPUT_FILE.exists():
        print(f"Missing {INPUT_FILE}")
        return []
    return INPUT_FILE.read_text(encoding="utf-8").splitlines()


def build_video_section(title, url, transcript_text, method):
    return f"""# {title}

Source URL: {url}
Transcript source: {method}

{transcript_text}
"""


def write_status_header():
    if not STATUS_FILE.exists():
        STATUS_FILE.write_text("url,status,method,notes\n", encoding="utf-8")


def append_status(url, status, method="", notes=""):
    safe_notes = str(notes).replace(",", ";").replace("\n", " ").strip()
    with STATUS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{url},{status},{method},{safe_notes}\n")


def main():
    ensure_output_dir()
    write_status_header()

    input_lines = read_input_lines()
    if not input_lines:
        print("No valid input found in input_urls.txt")
        return

    urls = get_youtube_urls_from_input(input_lines)
    if not urls:
        print("No valid YouTube video URLs found.")
        return

    COMBINED_FILE.write_text("", encoding="utf-8")

    for i, url in enumerate(urls, start=1):
        try:
            print(f"[{i}/{len(urls)}] Starting: {url}")
            title, raw_transcript, method = transcribe_youtube_url(url)
            cleaned_transcript = clean_transcript_text(raw_transcript)

            section = build_video_section(title, url, cleaned_transcript, method)

            with COMBINED_FILE.open("a", encoding="utf-8") as f:
                f.write(section)
                f.write("\n\n")

            append_status(url, "finished", method, title)
            print(f"[{i}/{len(urls)}] Finished: {title}")
        except Exception as e:
            append_status(url, "failed", "", str(e))
            print(f"[{i}/{len(urls)}] Failed: {url} -> {e}")

    print(f"Saved: {COMBINED_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()
