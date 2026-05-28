from urllib.parse import parse_qs, urlparse

from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")

    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "v" in query and query["v"]:
            return query["v"][0]

    raise ValueError(f"Could not extract video id from URL: {url}")


def clean_video_url(url: str) -> str:
    video_id = extract_video_id(url)
    return f"https://www.youtube.com/watch?v={video_id}"


def is_playlist_url(url: str) -> bool:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return "youtube.com" in parsed.netloc and "list" in query


def expand_playlist_url(url: str):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "noplaylist": False,
    }

    urls = []

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries") or []
    for entry in entries:
        video_id = entry.get("id")
        if video_id:
            urls.append(f"https://www.youtube.com/watch?v={video_id}")

    return urls


def get_youtube_urls_from_input(lines):
    urls = []

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if is_playlist_url(line):
            urls.extend(expand_playlist_url(line))
        elif "youtube.com" in line or "youtu.be" in line:
            urls.append(clean_video_url(line))

    seen = set()
    final_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            final_urls.append(url)

    return final_urls


def get_video_title(url: str) -> str:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info.get("title") or extract_video_id(url)


def fetch_captions_for_url(url: str):
    clean_url = clean_video_url(url)
    video_id = extract_video_id(clean_url)
    title = get_video_title(clean_url)

    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    parts = [item["text"].strip() for item in transcript if item.get("text")]
    text = "\n".join(parts).strip()

    if not text:
        raise ValueError("No captions found.")

    return title, text
