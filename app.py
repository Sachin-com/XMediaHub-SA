from flask import Flask, render_template, request
import yt_dlp
import os
import json
from datetime import datetime
import imageio_ffmpeg

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
HISTORY_FILE = "history.json"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]

    # Auto select cookies
    cookie_file = None

    if "x.com" in url or "twitter.com" in url:
        cookie_file = "cookies/cookies.txt"

    elif "youtube.com" in url or "youtu.be" in url:
        cookie_file = "cookies/youtube_cookies.txt"

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "ffmpeg_location": FFMPEG_PATH,
        "quiet": True,
        "noplaylist": True,
        "retries": 10,
        "fragment_retries": 10,
        "extractor_retries": 10,
        "socket_timeout": 30,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }

    # Add cookie file only if it exists
    if cookie_file and os.path.exists(cookie_file):
        ydl_opts["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        title = info.get("title", "Unknown Video")

        history = []

        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []

        history.append({
            "title": title,
            "url": url,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        return f"""
        <h2>✅ Download Complete</h2>
        <p><b>{title}</b></p>
        <p>Your file has been saved successfully.</p>
        <a href="/">⬅ Download Another</a>
        """

    except Exception as e:
        return f"""
        <h2>❌ Error</h2>
        <pre>{str(e)}</pre>
        <a href="/">⬅ Back</a>
        """


if __name__ == "__main__":
    app.run(debug=True)