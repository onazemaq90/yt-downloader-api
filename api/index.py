from fastapi import FastAPI, Query
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to TikTok Downloader API"}

@app.get("/download")
def download_video(url: str = Query(..., title="TikTok Video URL")):
    rapidapi_url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"

    payload = {"url": url}
    headers = {
        "x-rapidapi-key": "c7e2fc48e0msh077ba9d1e502feep11ddcbjsn4653c738de70",
        "x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(rapidapi_url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
