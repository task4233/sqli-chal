from flask import Flask, request, abort, render_template

app = Flask(__name__)

cipher = "\x1e\x1c\x1e\x0c\t+\x1b\x0c\x10-\x0c\x07\x00\n:\x12\x16\x0cQRGgAT\x1e"


@app.route("/<path:path>")
def missing_handler(path):
    abort(404, "ページが見つかりません")


@app.route("/", methods=["GET"])
def index_get():
    return render_template("index.html")


@app.route("/flag", methods=["GET"])
def flag_get():
    key = request.args.get("key")
    if key is None:
        key = "empty"
    return render_template("flag.html", flag=decrypt(key, cipher))


def decrypt(k: str, c: str) -> str:
    max_len = max(len(k), len(c))
    k += k
    c += c
    return "".join([chr(ord(kk) ^ ord(cc)) for kk, cc in zip(k[:max_len], c[:max_len])])
