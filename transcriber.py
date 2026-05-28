from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    raise ValueError(f"Could not extract video id from URL: {url}")


def fetch_youtube_captions(url: str) -> str:
    video_id = extract_video_id(url)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    parts = [item["text"].strip() for item in transcript if item.get("text")]
    return "\n".join(parts)
