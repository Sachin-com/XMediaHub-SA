from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

# Downloads folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# FFmpeg path
FFMPEG_PATH = r"C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]

    try:
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "format": "best",
            "quiet": True,
            "ffmpeg_location": FFMPEG_PATH,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            title = info.get("title", "No Title")

            # Find downloaded filename
            filename = ydl.prepare_filename(info)
            filename = os.path.basename(filename)

        return render_template(
            "result.html",
            title=title,
            filename=filename
        )

    except Exception as e:
        return f"""
        <h2>❌ Error</h2>
        <pre>{e}</pre>
        <a href="/">⬅ Back</a>
        """


@app.route("/file/<path:filename>")
def download_file(filename):
    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)