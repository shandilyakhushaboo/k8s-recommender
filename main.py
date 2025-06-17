from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, world from Cloud Run!", 200

@app.route("/healthz")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
