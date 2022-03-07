import datetime
from sqlalchemy.exc import IntegrityError

import behaviour
from models import Profession, Event
from configs import event_date_format, admin_user

users_have_permission = [admin_user, ]

errors_dict = {
    400: "One or more params missed/Wrong params type.",
    403: "Forbidden",
    404: "Not found",

    500: "Server error",
    200: "Success"
}

methods_dict = {
    "POST": "Adding",
    "DELETE": "Deleting"
}


class Response:
    def __init__(self, code: int, method: str):
        self.code = code
        self.method = method

    def __dict__(self):
        response_dict = {
            "code": self.code
        }
        if self.code in errors_dict:
            response_dict["description"] = errors_dict[self.code]
        if self.method in methods_dict:
            response_dict["method"] = methods_dict[self.method]

        return response_dict

    def __bool__(self):
        return self.code == 200


class ProfessionResponse(Response):
    needed_params_to_add = [
        "name", "article", "spheres",
        "token", "short_article", "icon_link",
    ]
    needed_params_to_delete = ["id", "token"]

    def __init__(self, code: int, method: str, new_profession: Profession = None):
        super(ProfessionResponse, self).__init__(code, method)
        self.profession = new_profession

    def __dict__(self):
        response_dict = super(ProfessionResponse, self).__dict__()
        if self.profession and bool(self):
            profession_dict = dict()
            profession_dict["name"] = self.profession.name
            profession_dict["id"] = self.profession.id
            response_dict["profession"] = profession_dict

        return response_dict


class EventResponse(Response):
    needed_params_to_add = [
        "name", "date_of_the_event", "description", "spheres",
        "short_description", "duration_in_hours", "speaker_id",
        "icon_link", "place", "form_of_the_event", "token"
    ]
    needed_params_to_delete = ["id", "token"]

    def __init__(self, code: int, method: str, new_event: Event = None):
        super(EventResponse, self).__init__(code, method)
        self.event = new_event

    def __dict__(self):
        response_dict = super(EventResponse, self).__dict__()

        if self.event and bool(self):
            event_dict = dict()
            event_dict["name"] = self.event.name
            event_dict["id"] = self.event.id
            event_dict["date_of_the_event"] = self.event.date_of_the_event
            event_dict["place"] = self.event.place
            event_dict["form_of_the_event"] = self.event.form_of_the_event
            event_dict["short_description"] = self.event.short_description
            event_dict["description"] = self.event.description

            response_dict["event"] = event_dict
        return response_dict


class ProfessionSphereResponse(Response):
    needed_params_to_add = ["profession_id", "sphere", "token"]
    needed_params_to_delete = ["profession_id", "sphere", "token"]

    def __init__(self, code: int, method: str, new_sphere=None, comments: str = None):
        super(ProfessionSphereResponse, self).__init__(code, method)
        self.sphere = new_sphere
        self.comments = comments

    def __dict__(self):
        response_dict = super(ProfessionSphereResponse, self).__dict__()
        if self.sphere and bool(self):
            sphere_dict = dict()
            sphere_dict["profession_id"] = self.sphere.profession_id
            sphere_dict["name"] = self.sphere.name
            response_dict["sphere"] = sphere_dict
        if self.comments:
            response_dict["comments"] = self.comments
        return response_dict


class EventSphereResponse(Response):
    needed_params_to_add = ["event_id", "sphere", "token"]
    needed_params_to_delete = ["event_id", "sphere", "token"]

    def __init__(self, code: int, method: str, new_sphere=None, comments: str = None):
        super(EventSphereResponse, self).__init__(code, method)
        self.sphere = new_sphere
        self.comments = comments

    def __dict__(self):
        response_dict = super(EventSphereResponse, self).__dict__()
        if self.sphere and bool(self):
            sphere_dict = dict()
            sphere_dict["event_id"] = self.sphere.event_id
            sphere_dict["name"] = self.sphere.name
            response_dict["sphere"] = sphere_dict
        if self.comments:
            response_dict["comments"] = self.comments
        return response_dict


def all_params_in(params: list, special_dict: dict):
    return all([x in special_dict for x in params])


def add_profession(method: str, request: dict):
    """Добавление новой профессии с необходимыми проверками."""
    if not all_params_in(ProfessionResponse.needed_params_to_add, request):
        return ProfessionResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return ProfessionResponse(403, method)
    if user.email not in users_have_permission:
        return ProfessionResponse(403, method)

    success, new_profession = behaviour.add_profession(
        name=request["name"],
        article=request["article"],
        short_article=request["short_article"],
        icon_link=request["icon_link"]
    )
    for sphere in request["spheres"]:
        success = behaviour.add_sphere_to_profession(
            profession_id=new_profession.id,
            sphere=sphere
        )
        if not success:
            return ProfessionResponse(500, method)

    if not success:
        return ProfessionResponse(500, method)
    return ProfessionResponse(200, method, new_profession)


def delete_profession(method: str, request: dict):
    """Удаление профессии с необходимыми проверками."""
    if not all_params_in(ProfessionResponse.needed_params_to_delete, request):
        return ProfessionResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return ProfessionResponse(403, method)
    if user.email not in users_have_permission:
        return ProfessionResponse(403, method)

    profession_id = int(request["id"])

    success = behaviour.delete_sphere_from_profession(profession_id)
    if not success:
        return ProfessionResponse(500, method)

    success, that_profession = behaviour.delete_profession_by_id(profession_id)
    if not success:
        return ProfessionResponse(500, method, that_profession)

    return ProfessionResponse(200, method, that_profession)


def add_event(method: str, request: dict):
    """Добавление нового мероприятия с необходимыми проверками."""
    if not all_params_in(EventResponse.needed_params_to_add, request):
        print(request)
        return EventResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return EventResponse(403, method)
    if user.email not in users_have_permission:
        return EventResponse(403, method)

    try:
        date_of_the_event = datetime.datetime.strptime(request["date_of_the_event"], event_date_format)
        request["duration_in_hours"] = float(request["duration_in_hours"])
        request["speaker_id"] = int(request["speaker_id"])
    except ValueError:
        return EventResponse(400, method)

    new_event = behaviour.add_event(
        event_name=request["name"],
        date_of_the_event=date_of_the_event,
        description=request["description"],
        short_description=request["short_description"],
        place=request["place"],
        form_of_the_event=request["form_of_the_event"],
        duration_in_hours=request["duration_in_hours"],
        speaker_id=request["speaker_id"],
        icon_link=request["icon_link"]
    )

    if not new_event:
        return EventResponse(500, method)

    for sphere in request["spheres"]:
        success = behaviour.add_sphere_to_event(
            sphere=sphere,
            event_id=new_event.id
        )
        if not success:
            return EventResponse(500, method)

    return EventResponse(200, method, new_event)


def delete_event(method: str, request: dict):
    """Удаление мероприятия с необходимыми проверками."""
    if not all_params_in(EventResponse.needed_params_to_delete, request):
        return EventResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return EventResponse(403, method)
    if user.email not in users_have_permission:
        return EventResponse(403, method)

    event_id = int(request["id"])

    success = behaviour.delete_sphere_from_event(event_id)
    if not success:
        return EventResponse(500, method)

    success, that_event = behaviour.delete_event(event_id)

    if success:
        return EventResponse(200, method, that_event)
    return EventResponse(500, method, that_event)


def add_sphere_profession(method: str, request: dict):
    """Добавление сферы со всеми необходимыми проверками."""
    if not all_params_in(ProfessionSphereResponse.needed_params_to_add, request):
        return ProfessionSphereResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return ProfessionSphereResponse(403, method)
    if user.email not in users_have_permission:
        return ProfessionSphereResponse(403, method)
    try:
        success = behaviour.add_sphere_to_profession(
            profession_id=request["profession_id"],
            sphere=request["sphere"]
        )
    except IntegrityError:
        return ProfessionSphereResponse(500, method, comments="Уже существует эта сфера!")
    if not success:
        return ProfessionSphereResponse(500, method)
    return ProfessionSphereResponse(200, method)


def delete_sphere_profession(method: str, request: dict):
    """Удаление сферы с необходимыми проверками."""
    if not all_params_in(ProfessionSphereResponse.needed_params_to_delete, request):
        return ProfessionSphereResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return ProfessionSphereResponse(403, method)
    if user.email not in users_have_permission:
        return ProfessionSphereResponse(403, method)

    success = behaviour.delete_sphere_from_profession(
        profession_id=request["profession_id"],
        sphere=request["sphere"]
    )
    if not success:
        return ProfessionSphereResponse(500, method)
    return ProfessionSphereResponse(200, method)


def add_sphere_event(method: str, request: dict):
    """Добавление сферы со всеми необходимыми проверками."""
    if not all_params_in(EventSphereResponse.needed_params_to_add, request):
        return EventSphereResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return EventSphereResponse(403, method)
    if user.email not in users_have_permission:
        return EventSphereResponse(403, method)
    try:
        success = behaviour.add_sphere_to_event(
            event_id=request["event_id"],
            sphere=request["sphere"]
        )
    except IntegrityError:
        return EventSphereResponse(500, method, comments="Уже есть такое!")
    if not success:
        return EventSphereResponse(500, method)
    return EventSphereResponse(200, method)


def delete_sphere_event(method: str, request: dict):
    """Удаление сферы с необходимыми проверками."""
    if not all_params_in(EventSphereResponse.needed_params_to_delete, request):
        return EventSphereResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return EventSphereResponse(403, method)
    if user.email not in users_have_permission:
        return EventSphereResponse(403, method)

    success = behaviour.delete_sphere_from_event(
        event_id=request["event_id"],
        sphere=request["sphere"]
    )
    if not success:
        return EventSphereResponse(500, method)
    return EventSphereResponse(200, method)


def profession(method: str, request: dict):
    """Ответ для /api/profession."""
    if method == "POST":
        return add_profession(method, request)
    elif method == "DELETE":
        return delete_profession(method, request)

    return Response(404, method)


def spheres_profession(method: str, request: dict):
    """Ответ для /api/spheres/profession"""
    if method == "POST":
        return add_sphere_profession(method, request)
    elif method == "DELETE":
        return delete_sphere_profession(method, request)

    return Response(404, method)


def spheres_event(method: str, request: dict):
    """Ответ для /api/spheres/profession"""
    if method == "POST":
        return add_sphere_event(method, request)
    elif method == "DELETE":
        return delete_sphere_event(method, request)

    return Response(404, method)


def event(method: str, request: dict):
    """Ответ для /api/event"""
    if method == "POST":
        return add_event(method, request)
    elif method == "DELETE":
        return delete_event(method, request)

    return Response(404, method)
