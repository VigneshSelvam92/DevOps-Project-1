from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

VERSION = os.environ.get("APP_VERSION", "v1.0.0")


@app.route("/")
def home():
    return jsonify({
        "message": "Hello from EKS via Jenkins + ArgoCD GitOps!",
        "version": VERSION,
        "hostname": socket.gethostname(),
    })


@app.route("/healthz")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)