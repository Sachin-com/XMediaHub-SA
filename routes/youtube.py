from flask import Blueprint, render_template, request, jsonify, send_file
import yt_dlp
import os
import glob
import tempfile
import imageio_ffmpeg

youtube_bp = Blueprint("youtube", __name__)

TEMP_FOLDER = tempfile.gettempdir()
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

YDL_BASE = {
    "quiet": True,
    "noplaylist": True,
    "ffmpeg_location": FFMPEG_PATH,
}

@youtube_bp.route("/youtube")
def youtube():
    return render_template("youtube.html")


@youtube_bp.route("/youtube/info", methods=["POST"])
def youtube_info():

    url = request.form.get("url")

    ydl_opts = YDL_BASE.copy()
    ydl_opts["skip_download"] = True

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "channel": info.get("uploader"),
            "duration": info.get("duration"),
            "views": info.get("view_count")
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })
@youtube_bp.route("/youtube/formats", methods=["POST"])
def youtube_formats():

    url = request.form.get("url")

    ydl_opts = YDL_BASE.copy()
    ydl_opts["skip_download"] = True

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        added = set()

        for f in info.get("formats", []):

            height = f.get("height")

            if not height or height in added:
                continue

            added.add(height)

            filesize = (
                f.get("filesize")
                or f.get("filesize_approx")
            )

            if filesize:
                size = f"{round(filesize / 1024 / 1024, 1)} MB"
            else:
                size = "Unknown"

            formats.append({
                "quality": f"{height}p",
                "height": height,
                "size": size
            })

        formats.sort(
            key=lambda x: x["height"],
            reverse=True
        )

        formats.append({
            "quality": "MP3",
            "height": 0,
            "size": "Audio"
        })

        return jsonify(formats)

    except Exception as e:
        return jsonify({
            "error": str(e)
        })
@youtube_bp.route("/youtube/download", methods=["POST"])
def youtube_download():

    url = request.form.get("url")
    quality = request.form.get("quality", "best")

    if quality == "1080p":
        video_format = "bestvideo[height<=1080]+bestaudio/best"
    elif quality == "720p":
        video_format = "bestvideo[height<=720]+bestaudio/best"
    elif quality == "480p":
        video_format = "bestvideo[height<=480]+bestaudio/best"
    elif quality == "MP3":
        video_format = "bestaudio"
    else:
        video_format = "bestvideo+bestaudio/best"

    outtmpl = os.path.join(TEMP_FOLDER, "xmediahub_%(id)s.%(ext)s")

    ydl_opts = YDL_BASE.copy()
    ydl_opts.update({
        "format": video_format,
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
    })

    if quality == "MP3":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        video_id = info["id"]

        matches = glob.glob(
            os.path.join(TEMP_FOLDER, f"xmediahub_{video_id}*")
        )

        if not matches:
            return "Downloaded file not found."

        filepath = max(matches, key=os.path.getmtime)

        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return f"""
        <h2>❌ Download Failed</h2>
        <pre>{str(e)}</pre>
        <br>
        <a href="/youtube">⬅ Back</a>
        """        