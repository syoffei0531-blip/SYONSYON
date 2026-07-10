from flask import Flask, request, send_file, Response
import subprocess
import os
import requests
import json

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Japan Hidden Stories</title>
    </head>
    <body>
        <h1>Japan Hidden Stories</h1>

        <p>
            AI platform for automatically publishing educational videos
            about Japanese culture to TikTok.
        </p>

        <p><a href="/privacy">Privacy Policy</a></p>
        <p><a href="/terms">Terms of Service</a></p>

        <p>Contact: syoffei0531@gmail.com</p>
    </body>
    </html>
    """
def home():
    return """
    <h1>Japan Hidden Stories</h1>

    <p>AI platform for automatically publishing educational videos about Japanese culture.</p>

    <p><a href="/privacy">Privacy Policy</a></p>

    <p><a href="/terms">Terms of Service</a></p>

    <p>Contact: syoffei0531@gmail.com</p>
    """

@app.route("/tiktokd4nUffblE8bbcZnU3otgBCAB")
def tiktok_verify():
    return Response(
        "tiktok-developers-site-verification=d4nUffblE8bbcZnU3otgBCAByFcyTvaQ",
        mimetype="text/plain"
    )
from flask import Response

@app.route("/tiktokzzL3jSgljn7HlUWykqiO3sGmR5MKhD7q.txt")
def tiktok_verify_new():
    return Response(
        "tiktok-developers-site-verification=zzL3jSgljn7HlUWykqiO3sGmR5MKhD7q",
        mimetype="text/plain"
    )

@app.route("/privacy")
def privacy():
    return """
    <h1>Privacy Policy</h1>
    <p>This application only uses TikTok APIs to publish videos authorized by the user.</p>
    <p>No personal information is sold or shared with third parties.</p>
    <p>Contact: syoffei0531@gmail.com</p>
    """

@app.route("/terms")
def terms():
    return """
    <h1>Terms of Service</h1>
    <p>This application is used to automatically publish educational videos about Japanese culture.</p>
    <p>Users are responsible for the content they publish.</p>
    """


@app.route("/create-video", methods=["POST"])
def create_video():

    try:

        os.makedirs("/tmp/video", exist_ok=True)

        # -----------------------
        # n8nからファイル受信
        # -----------------------

        image1 = request.files["image1"]
        image2 = request.files["image2"]
        image3 = request.files["image3"]
        image4 = request.files["image4"]

        audio = request.files["audio"]
        bgm = request.files["bgm"]
        script = request.files["script"]
        
        # -----------------------
        # 一時保存
        # -----------------------

        image1_path = "/tmp/video/img1.png"
        image2_path = "/tmp/video/img2.png"
        image3_path = "/tmp/video/img3.png"
        image4_path = "/tmp/video/img4.png"
        
        audio_path = "/tmp/video/audio.mp3"
        bgm_path = "/tmp/video/bgm.mp3"
        subtitle_path = "/tmp/video/subtitle.srt"
        script_path = "/tmp/video/script.txt"
        
        image1.save(image1_path)
        image2.save(image2_path)
        image3.save(image3_path)
        image4.save(image4_path)

        audio.save(audio_path)
        bgm.save(bgm_path)
        script.save(script_path)
        
        print("========== SAVED FILES ==========")

        for path in [image1_path, image2_path, image3_path, image4_path]:
            print(
                path,
                "exists=", os.path.exists(path),
                "size=", os.path.getsize(path) if os.path.exists(path) else "NOT FOUND"
                )

        print("=================================")
        
        # 保存されたファイルサイズ確認
        print("IMAGE1 SIZE:", os.path.getsize(image1_path))
        print("IMAGE2 SIZE:", os.path.getsize(image2_path))
        print("IMAGE3 SIZE:", os.path.getsize(image3_path))
        print("IMAGE4 SIZE:", os.path.getsize(image4_path))

        print("IMAGE1:", image1.filename)
        print("IMAGE2:", image2.filename)
        print("IMAGE3:", image3.filename)
        print("IMAGE4:", image4.filename)

        print("AUDIO:", audio.filename)
        print("BGM:", bgm.filename)
        print("SCRIPT:", script.filename)

        # -----------------------
        # 音声の長さ取得
        # -----------------------

        probe = subprocess.run(
        [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
        ],
        capture_output=True,
        text=True
        )

        duration = float(probe.stdout.strip())
        scene_duration = duration / 4

        # -----------------------
        # script.txt → subtitle.srt
        # -----------------------

        with open(script_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # 1行あたり約8単語で改行
        words = text.split()

        lines = []

        for i in range(0, len(words), 8):
            lines.append(" ".join(words[i:i+8]))

        subtitle_duration = duration / len(lines)


        def to_srt_time(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec - int(sec)) * 1000)

            return f"{h:02}:{m:02}:{s:02},{ms:03}"


        with open(subtitle_path, "w", encoding="utf-8") as f:

           current = 0

           for index, line in enumerate(lines):

               start = current
               end = current + subtitle_duration

               f.write(f"{index+1}\n")
               f.write(f"{to_srt_time(start)} --> {to_srt_time(end)}\n")
               f.write(f"{line}\n\n")

               current = end

        print("SRT CREATED")
        print(subtitle_path)
        
        # -----------------------
        # list.txt 作成
        # -----------------------

        list_path = "/tmp/video/list.txt"

        with open(list_path, "w") as f:
            f.write(f"file '{image1_path}'\n")
            f.write(f"duration {scene_duration}\n")

            f.write(f"file '{image2_path}'\n")
            f.write(f"duration {scene_duration}\n")

            f.write(f"file '{image3_path}'\n")
            f.write(f"duration {scene_duration}\n")

            f.write(f"file '{image4_path}'\n")
            f.write(f"duration {scene_duration}\n")

            # 最後はもう一度同じ画像を書く（FFmpeg concatの仕様）
            f.write(f"file '{image4_path}'\n")

        print("========== LIST.TXT ==========")

        with open(list_path, "r") as f:
            print(f.read())

        print("==============================")
            
        print("DURATION:", duration)
        print("SCENE:", scene_duration)

  
        # -----------------------
        # FFmpeg
        # -----------------------

        output = "/tmp/video/output.mp4"

        fade = 0.5

        scene_duration += (fade * 3) / 4

        offset1 = scene_duration - fade
        offset2 = (scene_duration * 2) - (fade * 2)
        offset3 = (scene_duration * 3) - (fade * 3)
        
        command = [
            "ffmpeg",
            "-y",

            "-loop", "1",
            "-t", str(scene_duration),
            "-i", image1_path,

            "-loop", "1",
            "-t", str(scene_duration),
            "-i", image2_path,

            "-loop", "1",
            "-t", str(scene_duration),
            "-i", image3_path,

            "-loop", "1",
            "-t", str(scene_duration),
            "-i", image4_path,

            "-i", audio_path,
            "-i", bgm_path,
            
            "-filter_complex",

            "[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v0];"
            "[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v1];"
            "[2:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v2];"
            "[3:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v3];"
            
            f"[v0][v1]xfade=transition=fade:duration={fade}:offset={offset1}[x1];"
            f"[x1][v2]xfade=transition=fade:duration={fade}:offset={offset2}[x2];"
            f"[x2][v3]xfade=transition=fade:duration={fade}:offset={offset3}[base];"
            
            f"[base]subtitles={subtitle_path}[video];"
            
            "[4:a]volume=1.3[narration];"
            "[5:a]volume=0.15,"
            "afade=t=in:st=0:d=2,"
            f"afade=t=out:st={duration-2}:d=2"
            "[bgm];"
            "[narration][bgm]amix=inputs=2:duration=first:normalize=0[audio]",
            
            "-map", "[video]",
            "-map", "[audio]",

            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",

            "-c:a", "aac",

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

        # -----------------------
        # ffprobeで動画情報を確認
        # -----------------------

        probe = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration,size",
                "-of", "default=noprint_wrappers=1",
                output
            ],
            capture_output=True,
            text=True
        )

        print("========== FFPROBE ==========")
        print(probe.stdout)
        print("=============================")

        print("OUTPUT EXISTS:", os.path.exists(output))
        print("OUTPUT SIZE:", os.path.getsize(output))

        return send_file(
            output,
            mimetype="video/mp4",
            as_attachment=False
        )
    except Exception as e:
        import traceback

        print("========== ERROR ==========")
        print(traceback.format_exc())
        print("===========================")

        return {
            "error": str(e),
            "traceback": traceback.format_exc()
            }, 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
