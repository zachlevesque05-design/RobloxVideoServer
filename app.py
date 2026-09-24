from flask import Flask, request, jsonify
from supabase import create_client
import os
import json

app = Flask(__name__)


# -------------------------------
# SUPABASE
# -------------------------------

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


# -------------------------------
# VIDEO
# -------------------------------

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


# -------------------------------
# IMAGE UPLOAD
# -------------------------------

@app.post("/image")
def upload_image():

    data = request.json

    if not data:
        return jsonify({
            "error": "No image data received"
        }), 400

    name = data.get("name")

    if not name:
        return jsonify({
            "error": "Missing image name"
        }), 400

    file_path = f"{name}.json"

    json_data = json.dumps(
        data,
        separators=(",", ":")
    ).encode("utf-8")

    try:

        url = (
            SUPABASE_URL
            + "/storage/v1/object/images/"
            + file_path
        )

        headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            headers=headers,
            data=json_data,
            timeout=60
        )

        print("Supabase status:", response.status_code)
        print("Supabase response:", response.text)

        if response.status_code >= 400:

            return jsonify({
                "error": "Supabase upload failed",
                "status": response.status_code,
                "details": response.text
            }), 500

        print("Image uploaded:", file_path)

        return jsonify({
            "success": True,
            "name": name
        })

    except Exception as e:

        print("IMAGE UPLOAD FAILED")
        print("Error:", repr(e))

        return jsonify({
            "error": str(e)
        }), 500

# -------------------------------
# IMAGE DOWNLOAD
# -------------------------------

@app.get("/image/<name>")
def get_image(name):

    file_path = f"{name}.json"


    try:

        response = supabase.storage \
            .from_("images") \
            .download(file_path)


        data = json.loads(
            response.decode("utf-8")
        )


        return jsonify(data)


    except Exception as e:

        print(
            "Image download error:",
            e
        )


        return jsonify({

            "error": "Image not found"

        }), 404
