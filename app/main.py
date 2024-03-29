import datetime

from flask import render_template
from flask import Flask, session, request, abort
from behaviour import get_user_by_token, authenticate_user, add_user
from configs import token_expire_date, events_thru_to_date_in_seconds, token_symbols, token_size
import behaviour
import api
from hashlib import md5
from random import choice as random_choice

app = Flask(__name__)
app.secret_key = "".join([random_choice(token_symbols) for _ in range(token_size)])


def hash_password(password: str):
    return md5(bytes(password, encoding="utf-8")).hexdigest()


def set_token(response, token: str):
    """Ставим Куки, чтобы пользователь имел возможность для авторизации..."""

    session.setdefault("token", token)
    session.setdefault("expiration_date", token_expire_date)

    return response


def authorize(url_was_visited: str):
    if url_was_visited:
        session["url"] = url_was_visited

    token = session.get("token")
    if token:
        account = get_user_by_token(token)
    else:
        account = None
    return account


def get_first_picture(profession_id: int):
    profession = behaviour.get_profession(profession_id)
    if profession:
        return profession["profession"].icon_link
    return None


@app.errorhandler(404)
def not_found(error):
    account = authorize("")
    return render_template("notFound.html", account=account, error=error)


@app.route("/", methods=["GET", "POST"])
@app.route("/main", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def main_page():
    url = "/main"
    account = authorize(url)
    return render_template("index.html", account=account)


@app.route("/aboutMeet/<int:meet_id>", methods=["GET"])
def get_meet(meet_id: int):
    url = f"/aboutMeet/{meet_id}"
    account = authorize(url)
    event = behaviour.get_event(meet_id)

    if not event:
        return abort(404)
    spheres = event["spheres"]
    event = event["event"]

    return render_template("aboutMeet.html", account=account, event=event, spheres=spheres)


@app.route("/archive", methods=["GET"])
def get_archive():
    url = "/archive"
    account = authorize(url)

    query = dict(request.values).get("query")

    from_date = datetime.datetime(year=2020, month=1, day=1)
    to_date = datetime.datetime.now()
    meetings = behaviour.get_events(10, 0, from_date, to_date, query)

    if query and not meetings:
        return render_template("notFoundSearch.html", account=account)

    return render_template("archive.html", account=account, meetings=meetings)


@app.route("/professionsInfo", methods=["GET"])
def get_professions():
    url = "/professionsInfo"
    account = authorize(url)

    query = dict(request.values).get("query")
    professions = behaviour.get_all_professions(10, 0, query)

    if query and not professions:
        return render_template("notFoundSearch.html", account=account)

    return render_template(
        "professionsInfo.html",
        account=account,
        professions=professions,
        get_first_picture=get_first_picture,
        get_short_article=lambda x: x.short_article,
        enumerate=enumerate
    )


@app.route("/profession/<int:profession_id>", methods=["GET"])
def get_profession(profession_id: int):
    url = f"/profession/{profession_id}"
    account = authorize(url)

    profession = behaviour.get_profession(profession_id)

    if not profession:
        return abort(404)

    return render_template(
        "aboutProf.html",
        account=account,
        profession=profession["profession"],
        spheres=profession["spheres"],
        photos=profession["photos"]
    )


@app.route("/event/<int:event_id>", methods=["GET"])
def get_event(event_id: int):
    url = f"/event/{event_id}"
    account = authorize(url)
    event = behaviour.get_event(event_id)

    if not event:
        return abort(404)

    return render_template(
        "aboutMeet.html",
        account=account,
        event=event["event"],
        spheres=event["spheres"]
    )


@app.route("/calendar", methods=["GET"])
def get_calendar():
    url = "/calendar"
    account = authorize(url)
    query = dict(request.values).get("query")

    from_date = datetime.datetime.now()
    to_date = datetime.timedelta(
        seconds=events_thru_to_date_in_seconds
    )
    to_date = from_date + to_date
    events = behaviour.get_events(10, 0, from_date, to_date, query)

    if query and not events:
        return render_template("notFoundSearch.html", account=account)

    return render_template("calendar.html", account=account, events=events)


# Ниже блоки определяют работу с аккаунтом и получение токена.
@app.route("/login", methods=["POST"])
def logining_request():
    info = dict(request.values.items())
    if "login" not in info or "password" not in info:
        return {
            "error": "А где мои логины и пароли всякие?.."
        }

    login = info["login"]
    hashed_password = hash_password(info["password"])

    success, token = authenticate_user(login, hashed_password)

    if success:
        return {"token": token.key, "expire_date": token.expiration_date}
    else:
        return {"error": "Неверный логин или пароль."}


@app.route("/api/profession", methods=["POST", "DELETE"])
def api_profession():
    request_json = dict(request.values.copy())
    if "spheres" in request_json:
        request_json["spheres"] = str(request_json["spheres"]).split(",")
    return api.profession(request.method, request_json).__dict__()


@app.route("/api/event", methods=["POST", "DELETE"])
def api_meet():
    request_json = dict(request.values.copy())
    if "spheres" in request_json:
        request_json["spheres"] = str(request_json["spheres"]).split(",")
    return api.event(request.method, request_json).__dict__()


@app.route("/api/sphere/profession", methods=["POST", "DELETE"])
def api_spheres_profession():
    request_json = dict(request.values)
    return api.spheres_profession(request.method, request_json).__dict__()


@app.route("/api/sphere/event", methods=["GET", "POST", "DELETE"])
def api_spheres_event():
    request_json = dict(request.values)
    return api.spheres_event(request.method, request_json).__dict__()


@app.before_first_request
def initializing():
    from configs import admin_user, admin_password, admin_name

    hashed_pass = hash_password(admin_password)
    success, token = authenticate_user(admin_user, hashed_pass)

    if not success:
        add_user(
            full_name=admin_name,
            email=admin_user,
            hashed_password=hashed_pass
        )
