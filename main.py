from pathlib import Path

from transcriber import fetch_youtube_captions
from status_utils import safe_notes

INPUT_FILE = Path("input_urls.txt")
OUTPUT_DIR = Path("transcripts")
COMBINED_FILE = OUTPUT_DIR / "combined_transcripts.txt"
STATUS_FILE = OUTPUT_DIR / "status.csv"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)


def read_urls():
    if not INPUT_FILE.exists():
        print(f"Missing {INPUT_FILE}")
        return []

    lines = INPUT_FILE.read_text(encoding="utf-8").splitlines()
    urls = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "youtube.com" in line or "youtu.be" in line:
            urls.append(line)

    return urls


def write_status_header():
    if not STATUS_FILE.exists():
        STATUS_FILE.write_text("url,status,notes\n", encoding="utf-8")


def append_status(url, status, notes=""):
    with STATUS_FILE.open("a", encoding="utf-8") as f:
        clean_notes = safe_notes(notes)
        f.write(f"{url},{status},{clean_notes}\n")


def append_combined_transcript(url, transcript_text):
    with COMBINED_FILE.open("a", encoding="utf-8") as f:
        f.write(f"=== {url} ===\n")
        f.write(transcript_text.strip() + "\n\n")


def save_individual_transcript(index, transcript_text):
    out_file = OUTPUT_DIR / f"transcript_{index:03d}.txt"
    out_file.write_text(transcript_text, encoding="utf-8")


def main():
    ensure_output_dir()
    write_status_header()

    urls = read_urls()

    if not urls:
        print("No valid YouTube URLs found in input_urls.txt")
        return

    for i, url in enumerate(urls, start=1):
        try:
            transcript_text = fetch_youtube_captions(url)
            save_individual_transcript(i, transcript_text)
            append_combined_transcript(url, transcript_text)
            append_status(url, "ok", "captions")
            print(f"Processed {url}")
        except Exception as e:
            append_status(url, "failed", str(e))
            print(f"Failed: {url} -> {e}")

    print("Done.")


if __name__ == "__main__":
    main()
