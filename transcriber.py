from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlparse

from faster_whisper import WhisperModel
from yt_dlp import YoutubeDL


_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    return _MODEL


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")

    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "v" in query and query["v"]:
            return query["v"][0]

    raise ValueError(f"Could not extract video id from URL: {url}")


def clean_youtube_url(url: str) -> str:
    video_id = extract_video_id(url)
    return f"https://www.youtube.com/watch?v={video_id}"


def download_audio(url: str, work_dir: Path):
    output_template = str(work_dir / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_path = Path(ydl.prepare_filename(info))
        title = info.get("title") or info.get("id") or "untitled"

    if not downloaded_path.exists():
        raise FileNotFoundError(f"Downloaded audio file not found: {downloaded_path}")

    return title, downloaded_path


def transcribe_audio_file(audio_path: Path) -> str:
    model = get_model()
    segments, _info = model.transcribe(str(audio_path), beam_size=5)

    parts = []
    for segment in segments:
        text = segment.text.strip()
        if text:
            parts.append(text)

    transcript_text = "\n".join(parts).strip()

    if not transcript_text:
        raise ValueError("Transcription returned empty text.")

    return transcript_text


def transcribe_youtube_url(url: str):
    clean_url = clean_youtube_url(url)

    with TemporaryDirectory() as tmp_dir:
        work_dir = Path(tmp_dir)
        title, audio_path = download_audio(clean_url, work_dir)
        transcript_text = transcribe_audio_file(audio_path)

    return title, transcript_text
