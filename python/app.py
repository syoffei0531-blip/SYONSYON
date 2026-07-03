from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Python API OK!"


@app.route("/create-video", methods=["POST"])
def create_video():
    data = request.get_json()

    print(data)

    return {
        "status": "OK",
        "received": data
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
