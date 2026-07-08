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

        image1 = request.files["image1"]
        image2 = request.files["image2"]
        image3 = request.files["image3"]
        image4 = request.files["image4"]

        audio = request.files["audio"]
        bgm = request.files["bgm"]
        
        # -----------------------
        # 一時保存
        # -----------------------

        image1_path = "/tmp/video/img1.png"
        image2_path = "/tmp/video/img2.png"
        image3_path = "/tmp/video/img3.png"
        image4_path = "/tmp/video/img4.png"
        
        audio_path = "/tmp/video/audio.mp3"
        bgm_path = "/tmp/video/bgm.mp3"
        
        image1.save(image1_path)
        image2.save(image2_path)
        image3.save(image3_path)
        image4.save(image4_path)

        audio.save(audio_path)
        bgm.save(bgm_path)
        
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
        print("AUDIO:", audio.filename)

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

            "[0:v]scale=1080:1920,setsar=1[v0];"
            "[1:v]scale=1080:1920,setsar=1[v1];"
            "[2:v]scale=1080:1920,setsar=1[v2];"
            "[3:v]scale=1080:1920,setsar=1[v3];"
            "[v0][v1][v2][v3]concat=n=4:v=1:a=0[video];"
            "[4:a]volume=1.0[narration];"
            "[5:a]volume=0.15,"
            "afade=t=in:st=0:d=2,"
            f"afade=t=out:st={duration-2}:d=2"
            "[bgm];"
            "[narration][bgm]amix=inputs=2:duration=first[audio]",
            
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
