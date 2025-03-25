import re
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Updated Pinterest URL regex with your provided pattern
PINTEREST_URL_PATTERN = r'https?:\/\/(?:www\.)?pinterest\.(?:com|fr|de|co\.uk|it|es|ca|com\.au|ru|co\.jp|nl|co\.kr|pt|co\.in|co\.nz|com\.mx|com\.br|at|ch|dk|fi|ie|no|pl|se|com\.tr)\/(?:pin|board)\/[a-zA-Z0-9-\/]+'

# Headers with your requested edits
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_pinterest_content(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Extract video/image from Pinterest page (simplified example)
        content = response.text
        video_match = re.search(r'"url":"(https?:\/\/[^"]+\.(mp4|mov))"', content)
        image_match = re.search(r'"url":"(https?:\/\/[^"]+\.(jpg|jpeg|png|gif))"', content)
        
        if video_match:
            return {"type": "video", "url": video_match.group(1)}
        elif image_match:
            return {"type": "image", "url": image_match.group(1)}
        else:
            raise HTTPException(status_code=404, detail="No downloadable content found")
            
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(e)}")

@app.get("/download")
async def download(url: str):
    if not re.match(PINTEREST_URL_PATTERN, url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL")
    
    result = get_pinterest_content(url)
    return result

# API Docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return {
        "message": "Pinterest Downloader API",
        "endpoints": {
            "/download": {
                "method": "GET",
                "params": {"url": "Pinterest URL to download from"},
                "description": "Download video or image from Pinterest"
            }
        },
        "example_request": "GET /download?url=https://www.pinterest.com/pin/123456789/",
        "example_response": {
            "type": "video",
            "url": "https://v.pinimg.com/videos/123456789.mp4"
        }
    }
