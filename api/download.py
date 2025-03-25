from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Pinterest URL regex pattern
PINTEREST_REGEX = r'https?:\/\/(?:www\.)?pinterest\.(?:com|fr|de|co\.uk|it|es|ca|com\.au|ru|co\.jp|nl|co\.kr|pt|co\.in|co\.nz|com\.mx|com\.br|at|ch|dk|fi|ie|no|pl|se|com\.tr)'

# Headers for HTTP requests
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_pinterest_media(url):
    """Scrape Pinterest URL and extract media (image/video) links."""
    if not re.match(PINTEREST_REGEX, url):
        return {"error": "Invalid Pinterest URL"}

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract image
        image = soup.find('img', {'src': re.compile(r'https://i.pinimg.com/originals/.*')})
        image_url = image['src'] if image else None

        # Extract video
        video = soup.find('video', {'src': re.compile(r'https://v.pinimg.com/videos/.*')})
        video_url = video['src'] if video else None

        # Example response structure
        result = {
            "url": url,
            "image": image_url,
            "video": video_url,
            "status": "success" if image_url or video_url else "no_media_found"
        }
        return result

    except requests.RequestException as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}

@app.route('/api/download', methods=['GET'])
def api_download():
    """API endpoint to download Pinterest media."""
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    result = download_pinterest_media(url)
    return jsonify(result)

@app.route('/docs', methods=['GET'])
def api_docs():
    """Simple API documentation endpoint."""
    docs = {
        "endpoints": {
            "/api/download": {
                "method": "GET",
                "description": "Download media from a Pinterest URL",
                "parameters": {
                    "url": "The Pinterest URL to scrape (required)"
                },
                "example": "GET /api/download?url=https://www.pinterest.com/pin/123456789/",
                "response": {
                    "url": "https://www.pinterest.com/pin/123456789/",
                    "image": "https://i.pinimg.com/originals/ab/cd/ef/abcdef123456.jpg",
                    "video": "https://v.pinimg.com/videos/xyz/123456.mp4",
                    "status": "success"
                }
            }
        }
    }
    return jsonify(docs)

@app.route('/webpage', methods=['GET'])
def webpage_downloader():
    """Download entire Pinterest webpage content (images and videos)."""
    url = request.args.get('url')
    if not url or not re.match(PINTEREST_REGEX, url):
        return jsonify({"error": "Valid Pinterest URL is required"}), 400

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all images
        images = [img['src'] for img in soup.find_all('img', {'src': re.compile(r'https://i.pinimg.com/originals/.*')})]
        # Extract all videos
        videos = [video['src'] for video in soup.find_all('video', {'src': re.compile(r'https://v.pinimg.com/videos/.*')})]

        return jsonify({
            "url": url,
            "images": images,
            "videos": videos,
            "status": "success"
        })
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch webpage: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
