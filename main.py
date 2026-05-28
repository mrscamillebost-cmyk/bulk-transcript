from pathlib import Path

from status_utils import safe_notes
from transcriber import extract_video_id, transcribe_youtube_url
from transcript_cleanup import clean_transcript_text

INPUT_FILE = Path("input_urls.txt")
OUTPUT_DIR = Path("transcripts")
COMBINED_FILE = OUTPUT_DIR / "combined_transcripts.md"
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
        STATUS_FILE.write_text("url,video_id,status,notes\n", encoding="utf-8")


def append_status(url, video_id, status, notes=""):
    with STATUS_FILE.open("a", encoding="utf-8") as f:
        clean_notes = safe_notes(notes)
        f.write(f"{url},{video_id},{status},{clean_notes}\n")


def append_combined_transcript(title, url, transcript_text):
    with COMBINED_FILE.open("a", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Source URL: {url}\n\n")
        f.write(transcript_text.strip())
        f.write("\n\n")


def main():
    ensure_output_dir()
    write_status_header()

    urls = read_urls()

    if not urls:
        print("No valid YouTube URLs found in input_urls.txt")
        return

    # start fresh each run
    COMBINED_FILE.write_text("", encoding="utf-8")

    for url in urls:
        try:
            video_id = extract_video_id(url)
        except Exception as e:
            append_status(url, "unknown", "failed", f"bad url: {e}")
            print(f"Failed URL parse: {url} -> {e}")
            continue

        try:
            print(f"Starting: {url}")
            title, raw_transcript = transcribe_youtube_url(url)
            cleaned_transcript = clean_transcript_text(raw_transcript)

            append_combined_transcript(title, url, cleaned_transcript)
            append_status(url, video_id, "ok", "combined markdown saved")
            print(f"Finished: {title}")
        except Exception as e:
            append_status(url, video_id, "failed", str(e))
            print(f"Failed: {url} -> {e}")

    print("Done.")


if __name__ == "__main__":
    main()
