"""YouTube transcript extraction tool.

Extracts transcripts from YouTube videos for compliance analysis.
Uses youtube-transcript-api v1.x (instance-based API).
"""

import re

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return as-is if already an ID."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def get_transcript_impl(youtube_url: str) -> dict:
    """Extract transcript from a YouTube video.

    Args:
        youtube_url: YouTube URL or video ID.

    Returns:
        dict with status, transcript text, and metadata.
    """
    try:
        video_id = extract_video_id(youtube_url)
        ytt_api = YouTubeTranscriptApi()

        # Fetch English transcript (auto-generated or manual)
        fetched = ytt_api.fetch(video_id, languages=["en"])

        snippets = list(fetched)
        full_text = " ".join(s.text for s in snippets)
        duration_seconds = int(snippets[-1].start + snippets[-1].duration) if snippets else 0

        return {
            "status": "success",
            "content": [{"text": full_text}],
            "video_id": video_id,
            "transcript": full_text,
            "duration_seconds": duration_seconds,
            "segment_count": len(snippets),
        }

    except Exception as e:
        # Try without language filter as fallback
        try:
            video_id = extract_video_id(youtube_url)
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            # Get first available transcript
            first = next(iter(transcript_list))
            fetched = first.fetch()
            snippets = list(fetched)
            full_text = " ".join(s.text for s in snippets)
            duration_seconds = int(snippets[-1].start + snippets[-1].duration) if snippets else 0

            return {
                "status": "success",
                "content": [{"text": full_text}],
                "video_id": video_id,
                "transcript": full_text,
                "duration_seconds": duration_seconds,
                "segment_count": len(snippets),
            }
        except Exception as e2:
            return {
                "status": "error",
                "content": [{"text": f"Failed to extract transcript: {e2}"}],
            }
