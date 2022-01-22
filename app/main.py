from flask import render_template
from flask import Flask, session, request


app = Flask(__name__)
app.secret_key = "22JJJd8888**eds___Dss09((((ejwsk4ll"


@app.route("/", methods=["GET", "POST"])
@app.route("/main", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def main_page():
    return render_template("index.html")


@app.route("/aboutMeet/<int:meet_id>", methods=["GET"])
def get_meet(meet_id: int):
    return {
        "text": f"What about of some meeting? I know a lot about {meet_id}"
    }


@app.route("/archive", methods=["GET"])
def get_archive():
    return {
        "text": "In this way I prefer to archive"
    }


@app.route("/professionsInfo", methods=["GET"])
def get_professions():
    return {
        "text": "It's time to get some info!"
    }


@app.route("/profession/<int:profession_id>", methods=["GET"])
def get_profession(profession_id):
    return {
        "text": f"Oh, you want to know about {profession_id}?"
    }


@app.route("/calendar", methods=["GET"])
def get_calendar():
    return {
        "text": "You know your date now."
    }


# Ниже блоки определяют работу с аккаунтом и получение токена.
@app.route("/login", methods=["POST"])
def logining_request():
    return {
        "text": "Logining in the POST."
    }


@app.route("/registration", methods=["GET", "POST"])
def register_request():
    return {
        "text": "Registration."
    }
