from flask import Flask, request, send_file
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Python API OK!"


@app.route("/create-video", methods=["POST"])
def create_video():

    try:

        os.makedirs("/tmp/video", exist_ok=True)

        # -----------------------
        # n8nからファイル受信
        # -----------------------

        image = request.files["image"]
        audio = request.files["audio"]

        # -----------------------
        # 一時保存
        # -----------------------

        image_path = "/tmp/video/img0.jpg"
        audio_path = "/tmp/video/audio.mp3"

        image.save(image_path)
        audio.save(audio_path)

        image_files = [image_path]

        # -----------------------
        # list.txt作成
        # -----------------------

        list_path = "/tmp/video/list.txt"

        with open(list_path, "w") as f:
            for img in image_files:
                f.write(f"file '{img}'\n")
                f.write("duration 5\n")

            f.write(f"file '{image_files[-1]}'\n")

        # -----------------------
        # FFmpeg
        # -----------------------

        output = "/tmp/video/output.mp4"

        command = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-i", audio_path,
            "-shortest",
            "-pix_fmt", "yuv420p",
            output
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        print("=== FFMPEG STDOUT ===")
        print(result.stdout)

        print("=== FFMPEG STDERR ===")
        print(result.stderr)

        if not os.path.exists(output):
            return {
                "error": "動画生成失敗",
                "ffmpeg": result.stderr
            }, 500

        return send_file(
            output,
            mimetype="video/mp4",
            as_attachment=True,
            download_name="video.mp4"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "error": str(e)
        }, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
