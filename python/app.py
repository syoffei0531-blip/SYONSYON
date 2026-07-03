from flask import Flask, request, send_file
import requests
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Python API OK!"


@app.route("/create-video", methods=["POST"])
def create_video():

    data = request.get_json()

    images = data["images"]
    voice = data["voice"]

    os.makedirs("/tmp/video", exist_ok=True)

    # -----------------------
    # 音声ダウンロード
    # -----------------------

    audio_path = "/tmp/video/audio.mp3"

    r = requests.get(voice)

    with open(audio_path, "wb") as f:
        f.write(r.content)

    # -----------------------
    # 画像ダウンロード
    # -----------------------

    image_files = []

    for i, url in enumerate(images):

        filename = f"/tmp/video/img{i}.jpg"

        r = requests.get(url)

        with open(filename, "wb") as f:
            f.write(r.content)

        image_files.append(filename)

    # -----------------------
    # list.txt作成
    # -----------------------

    list_path = "/tmp/video/list.txt"

    with open(list_path, "w") as f:

        for img in image_files:

            f.write(f"file '{img}'\n")
            f.write("duration 5\n")

        f.write(f"file '{image_files[-1]}'\n")

    output = "/tmp/video/output.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-f","concat",
        "-safe","0",
        "-i",list_path,
        "-i",audio_path,
        "-shortest",
        "-pix_fmt","yuv420p",
        output
    ]

    subprocess.run(command)

    return send_file(
        output,
        mimetype="video/mp4",
        as_attachment=True,
        download_name="video.mp4"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
