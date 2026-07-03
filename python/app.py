from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Python API OK!"


@app.route("/create-video", methods=["POST"])
def create_video():
    return {
        "status": "OK",
        "message": "create-video API is working!"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
