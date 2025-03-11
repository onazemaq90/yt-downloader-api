from fastapi import FastAPI, Query
import yt_dlp
import re

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to YouTube Downloader API"}

@app.get("/download")
def download_video(url: str = Query(..., title="YouTube Video URL")):
    try:
        # 🔹 শর্টস লিংক ফিক্স করা
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id_match:
            url = f"https://www.youtube.com/watch?v={video_id_match.group(1)}"

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "noprogress": True,
            "sleep_interval": 1,
            "youtube_include_dash_manifest": False,
            "cookiefile": "api/cookies.txt",  # 🔹 কুকিজ ব্যবহার করা
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
                "Accept-Language": "en-US,en;q=0.5",
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

        if not info_dict or "url" not in info_dict:
            return {"error": "Failed to retrieve video info"}

        return {
            "title": info_dict.get("title", "Unknown"),
            "download_url": info_dict["url"]
        }

    except Exception as e:
        return {"error": str(e)}
