from flask import Flask, request, jsonify

app = Flask(__name__)

video = None


@app.get("/")
def home():
    return "Roblox video server is alive!"


@app.post("/video")
def upload_video():

    global video

    video = request.json

    print("Video uploaded!")

    return "OK"


@app.get("/video")
def get_video():

    if video is None:
        return {
            "error": "No video uploaded yet"
        }

    return jsonify(video)