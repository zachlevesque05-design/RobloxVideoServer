from flask import Flask, request, jsonify
import requests
import os
import json
import base64


app = Flask(__name__)


# ==================================================
# GITHUB SETTINGS
# ==================================================

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_OWNER = os.environ["GITHUB_OWNER"]
GITHUB_REPO = os.environ["GITHUB_REPO"]


GITHUB_API = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/contents"
)


def github_headers():

    return {

        "Authorization":
            f"Bearer {GITHUB_TOKEN}",

        "Accept":
            "application/vnd.github+json",

        "X-GitHub-Api-Version":
            "2022-11-28"

    }


# ==================================================
# VIDEO CACHE
# ==================================================

video = None


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return "Roblox video server is alive!"


# ==================================================
# VIDEO
# ==================================================

@app.post("/video")
def upload_video():

    global video

    video =
        request.json

    print("Video uploaded!")

    return "OK"


@app.get("/video")
def get_video():

    if video is None:

        return {
            "error":
                "No video uploaded yet"
        }

    return jsonify(video)


# ==================================================
# IMAGE UPLOAD
# ==================================================

@app.post("/image")
def upload_image():

    data =
        request.json


    if not data:

        return jsonify({

            "error":
                "No image data received"

        }), 400


    name =
        data.get("name")


    if not name:

        return jsonify({

            "error":
                "Missing image name"

        }), 400


    # ----------------------------------------------
    # GITHUB FILE PATH
    # ----------------------------------------------

    file_path =
        f"Images/{name}.json"


    print("================================")
    print("IMAGE UPLOAD")
    print("Image name:", name)
    print("GitHub path:", file_path)


    # ----------------------------------------------
    # CONVERT JSON TO BASE64
    # ----------------------------------------------

    json_data =
        json.dumps(
            data,
            separators=(",", ":")
        ).encode("utf-8")


    encoded_content =
        base64.b64encode(
            json_data
        ).decode("utf-8")


    try:

        headers =
            github_headers()


        # ------------------------------------------
        # CHECK IF FILE ALREADY EXISTS
        # ------------------------------------------

        check_url =
            f"{GITHUB_API}/{file_path}"


        check_response =
            requests.get(

                check_url,

                headers=headers,

                timeout=30

            )


        print(
            "GitHub check status:",
            check_response.status_code
        )


        sha = None


        if check_response.status_code == 200:

            existing_file =
                check_response.json()


            sha =
                existing_file.get("sha")


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


        # ------------------------------------------
        # UPLOAD / UPDATE
        # ------------------------------------------

        upload_url =
            f"{GITHUB_API}/{file_path}"


        upload_data = {

            "message":
                f"Upload image {name}",

            "content":
                encoded_content

        }


        # Updating an existing file requires SHA

        if sha:

            upload_data["sha"] =
                sha


        response =
            requests.put(

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


        if response.status_code not in (
            200,
            201
        ):

            return jsonify({

                "error":
                    "GitHub upload failed",

                "status":
                    response.status_code,

                "details":
                    response.text

            }), 500


        print(
            "Image uploaded successfully:",
            file_path
        )


        return jsonify({

            "success":
                True,

            "name":
                name,

            "path":
                file_path

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


# ==================================================
# IMAGE DOWNLOAD
# ==================================================

@app.get("/image/<name>")
def get_image(name):

    print("================================")
    print("IMAGE REQUEST")

    print(
        "Requested name:",
        repr(name)
    )


    # ----------------------------------------------
    # GITHUB PATH
    # ----------------------------------------------

    file_path =
        f"Images/{name}.json"


    print(
        "GitHub path:",
        file_path
    )


    try:

        url =
            f"{GITHUB_API}/{file_path}"


        print(
            "GitHub URL:",
            url
        )


        # ------------------------------------------
        # DOWNLOAD FROM GITHUB
        # ------------------------------------------

        response =
            requests.get(

                url,

                headers=
                    github_headers(),

                timeout=30

            )


        print(
            "GitHub status:",
            response.status_code
        )


        print(
            "GitHub response:",
            response.text[:500]
        )


        # ------------------------------------------
        # FILE NOT FOUND
        # ------------------------------------------

        if response.status_code != 200:

            return jsonify({

                "error":
                    "Image not found",

                "requested":
                    name,

                "github_path":
                    file_path,

                "github_status":
                    response.status_code,

                "github_response":
                    response.text

            }), 404


        # ------------------------------------------
        # GET GITHUB JSON
        # ------------------------------------------

        github_data =
            response.json()


        encoded_content =
            github_data.get(
                "content",
                ""
            )


        # GitHub sometimes inserts
        # newlines into Base64

        encoded_content =
            encoded_content.replace(
                "\n",
                ""
            )


        # ------------------------------------------
        # DECODE BASE64
        # ------------------------------------------

        json_data =
            base64.b64decode(
                encoded_content
            ).decode(
                "utf-8"
            )


        # ------------------------------------------
        # DECODE JSON
        # ------------------------------------------

        data =
            json.loads(
                json_data
            )


        print(
            "Successfully downloaded:",
            file_path
        )


        print(
            "Image name:",
            data.get("name")
        )


        print(
            "Quality:",
            data.get("q")
        )


        print(
            "Palette:",
            len(
                data.get("p", [])
            )
        )


        print(
            "Rectangles:",
            len(
                data.get("r", [])
            )
        )


        print(
            "================================"
        )


        return jsonify(data)


    except Exception as e:

        print(
            "IMAGE DOWNLOAD ERROR:"
        )


        print(
            repr(e)
        )


        return jsonify({

            "error":
                "Image download failed",

            "details":
                str(e)

        }), 500


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=
            int(
                os.environ.get(
                    "PORT",
                    5000
                )
            )
    )
