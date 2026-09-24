from flask import Flask, request, jsonify
import requests
import os
import json
import base64


app = Flask(__name__)


# -------------------------------
# GITHUB
# -------------------------------

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_OWNER = os.environ["GITHUB_OWNER"]
GITHUB_REPO = os.environ["GITHUB_REPO"]

GITHUB_API = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/contents"
)


def github_headers():

    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


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


    file_path = f"Images/{name}.json"


    # Convert image JSON into bytes
    json_data = json.dumps(
        data,
        separators=(",", ":")
    ).encode("utf-8")


    # GitHub requires Base64 file content
    encoded_content = base64.b64encode(
        json_data
    ).decode("utf-8")


    try:

        headers = github_headers()


        # --------------------------------
        # Check if file already exists
        # --------------------------------

        check_url = (
            f"{GITHUB_API}/{file_path}"
        )


        check_response = requests.get(
            check_url,
            headers=headers,
            timeout=30
        )


        sha = None


        if check_response.status_code == 200:

            existing_file = check_response.json()

            sha = existing_file.get("sha")

            print(
                "Existing image found."
            )

            print(
                "Updating:",
                file_path
            )


        elif check_response.status_code == 404:

            print(
                "Image does not exist yet."
            )

            print(
                "Creating:",
                file_path
            )


        else:

            print(
                "GitHub check failed:"
            )

            print(
                check_response.status_code
            )

            print(
                check_response.text
            )

            return jsonify({

                "error":
                    "GitHub file check failed",

                "status":
                    check_response.status_code,

                "details":
                    check_response.text

            }), 500


        # --------------------------------
        # Create / update GitHub file
        # --------------------------------

        upload_url = (
            f"{GITHUB_API}/{file_path}"
        )


        upload_data = {

            "message":
                f"Upload image {name}",

            "content":
                encoded_content

        }


        # Existing file requires SHA
        if sha:

            upload_data["sha"] = sha


        response = requests.put(

            upload_url,

            headers=headers,

            json=upload_data,

            timeout=60
        )


        print(
            "GitHub upload status:",
            response.status_code
        )

        print(
            "GitHub response:",
            response.text
        )


        if response.status_code not in (200, 201):

            return jsonify({

                "error":
                    "GitHub upload failed",

                "status":
                    response.status_code,

                "details":
                    response.text

            }), 500


        print(
            "Image uploaded:",
            file_path
        )


        return jsonify({

            "success": True,

            "name": name

        })


    except Exception as e:

        print(
            "IMAGE UPLOAD FAILED"
        )

        print(
            "Error:",
            repr(e)
        )


        return jsonify({

            "error":
                str(e)

        }), 500


# -------------------------------
# IMAGE DOWNLOAD
# -------------------------------

@app.get("/image/<name>")
def get_image(name):

    file_path = f"images/{name}.json"


    try:

        url = (
            f"{GITHUB_API}/{file_path}"
        )


        response = requests.get(

            url,

            headers=github_headers(),

            timeout=30
        )


        print(
            "GitHub download status:",
            response.status_code
        )


        if response.status_code != 200:

            print(
                "GitHub download error:",
                response.text
            )

            return jsonify({

                "error":
                    "Image not found"

            }), 404


        github_data = response.json()


        # GitHub returns the file content as Base64
        encoded_content = github_data.get(
            "content",
            ""
        )


        # Remove newlines GitHub may include
        encoded_content = (
            encoded_content
            .replace("\n", "")
        )


        json_data = base64.b64decode(
            encoded_content
        ).decode("utf-8")


        data = json.loads(
            json_data
        )


        return jsonify(data)


    except Exception as e:

        print(
            "Image download error:",
            repr(e)
        )


        return jsonify({

            "error":
                "Image not found"

        }), 404
