from flask import Flask, render_template

from routes.youtube import youtube_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(youtube_bp)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/twitter")
def twitter():
    return render_template("twitter.html")


@app.route("/instagram")
def instagram():
    return render_template("instagram.html")


@app.route("/spotify")
def spotify():
    return render_template("spotify.html")


if __name__ == "__main__":
    app.run(debug=True)