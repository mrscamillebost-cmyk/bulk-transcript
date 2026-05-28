import re
import urllib.request
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")

    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "v" in query and query["v"]:
            return query["v"][0]

    raise ValueError(f"Could not extract video id from URL: {url}")


def clean_vtt_text(vtt_text: str) -> str:
    lines = vtt_text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue
        if line == "WEBVTT":
            continue
        if "-->" in line:
            continue
        if re.match(r"^\d+$", line):
            continue

        line = re.sub(r"<[^>]+>", "", line)
        line = line.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

        if cleaned and cleaned[-1] == line:
            continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()


def fetch_with_youtube_transcript_api(video_id: str) -> str:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    parts = [item["text"].strip() for item in transcript if item.get("text")]
    text = "\n".join(parts).strip()

    if not text:
        raise ValueError("Transcript API returned empty text.")

    return text


def fetch_with_ytdlp(url: str) -> str:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    subtitles = info.get("subtitles") or {}
    automatic_captions = info.get("automatic_captions") or {}

    preferred_langs = ["en", "en-US", "en-GB"]
    caption_groups = [subtitles, automatic_captions]

    for group in caption_groups:
        for lang in preferred_langs:
            tracks = group.get(lang) or []
            for track in tracks:
                sub_url = track.get("url")
                ext = track.get("ext", "")
                if not sub_url:
                    continue

                with urllib.request.urlopen(sub_url) as response:
                    raw = response.read().decode("utf-8", errors="ignore")

                if ext == "vtt" or "WEBVTT" in raw:
                    text = clean_vtt_text(raw)
                else:
                    text = raw.strip()

                if text:
                    return text

    raise ValueError("No subtitles or automatic captions found via yt-dlp.")


def fetch_youtube_captions(url: str) -> str:
    video_id = extract_video_id(url)

    first_error = None

    try:
        return fetch_with_youtube_transcript_api(video_id)
    except Exception as e:
        first_error = e

    try:
        return fetch_with_ytdlp(url)
    except Exception as second_error:
        raise ValueError(
            f"Could not fetch captions. First method failed: {first_error}. "
            f"Second method failed: {second_error}"
        )
