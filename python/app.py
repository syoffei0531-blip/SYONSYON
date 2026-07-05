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
        
        print("IMAGE SIZE:", os.path.getsize(image_path))
        print("AUDIO SIZE:", os.path.getsize(audio_path))
        print("IMAGE FILE:", image.filename)
        print("AUDIO FILE:", audio.filename)
        # -----------------------
        # FFmpeg
        # -----------------------

        output = "/tmp/video/output.mp4"

        command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output
        ]
        print("FFMPEG START")
        print(command)
        print("RUNNING...")
        print(" ".join(command))
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
            )
        print(result.returncode)
        print(result.stderr)
        if result.returncode != 0:
            return {
            "error": "FFmpeg failed",
            "stderr": result.stderr
            }, 500
            
        print("FFMPEG FINISHED")
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
           as_attachment=False
           )

    except Exception as e:
        import traceback

        return {
        "error": str(e),
        "traceback": traceback.format_exc()
        }, 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
