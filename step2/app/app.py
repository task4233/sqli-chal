import sqlite3
from flask import Flask, request, abort, render_template
import traceback
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

app = Flask(__name__)

cipher = "\\\x0b\x0b\x08I\x0b^TT\x15g?\x0cXk\t\x04BH>UP\x03Cf\x03kRWV\x0f\r\x0c\\\x13gC\x0b\x02\tF[\r\x02\x19\x06\r\x1b"
db_name = "step1.db"


class Result:
    def __init__(self, id: int, name: str, key: str, is_admin: int) -> None:
        self.id = id
        self.name = name
        self.key = key
        self.is_admin = is_admin


@app.route("/<path:path>")
def missing_handler(path):
    abort(404, "ページが見つかりません")


@app.route("/", methods=["GET"])
def index_get():
    name = request.args.get("name")
    if name is None:
        name = ""

    c = None
    results = None
    try:
        c = sqlite3.connect(db_name)
        query = f"SELECT * FROM users WHERE name LIKE '%{name}%' AND is_admin=0"
        cur = c.cursor()
        cur.execute(query)
        results = cur.fetchall()
    except Exception as e:
        traceback.print_exc()
        return render_template("error.html", message=str(e))
    finally:
        if c is not None:
            c.close()

    return render_template(
        "index.html",
        raw_sql=query,
        results=[Result(r[0], r[1], r[2], r[3]) for r in results],
    )


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
