from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def main_page():
    return render_template("index.html")
