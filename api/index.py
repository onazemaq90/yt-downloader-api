from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import yt_dlp
import re
from pydantic import HttpUrl

app = FastAPI(
    title="YouTube Downloader API",
    description="API to get downloadable YouTube video links",
    version="1.0.0"
)

def validate_youtube_url(url: str) -> str:
    """Validate and normalize YouTube URL"""
    # Handle various YouTube URL formats including shorts
    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be/([0-9A-Za-z_-]{11}).*",
        r"shorts/([0-9A-Za-z_-]{11}).*"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    raise ValueError("Invalid YouTube URL format")

@app.get("/")
async def home():
    """Root endpoint"""
    return {"message": "Welcome to YouTube Downloader API"}

@app.get("/download", response_model=dict)
async def download_video(
    url: HttpUrl = Query(
        ...,
        title="YouTube Video URL",
        description="Valid YouTube video URL",
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
) -> dict:
    """
    Get downloadable video URL from YouTube link
    """
    try:
        # Convert URL to string and validate
        video_url = str(url)
        normalized_url = validate_youtube_url(video_url)

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "noprogress": True,
            "sleep_interval": 1,
            "max_sleep_interval": 5,
            "youtube_include_dash_manifest": False,
            "cookiefile": "api/cookies.txt",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(normalized_url, download=False)
            
            if not info_dict or "url" not in info_dict:
                raise ValueError("Could not extract video information")

            return {
                "title": info_dict.get("title", "Unknown"),
                "download_url": info_dict["url"],
                "duration": info_dict.get("duration", None),
                "uploader": info_dict.get("uploader", "Unknown"),
                "thumbnail": info_dict.get("thumbnail", None)
            }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing request: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000
