import datetime

import behaviour
from models import Profession, Event
from configs import event_date_format

users_have_permission = ["test@specialdomain.com", ]

errors_dict = {
    400: "One or more params missed",
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
    needed_params_to_add = ["name", "article", "token"]
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
        "name", "date_of_the_event", "description",
        "place", "form_of_the_event", "token"
    ]
    needed_params_to_delete = [
        "id", "token"
    ]

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
            response_dict["event"] = event_dict
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
        article=request["article"]
    )
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

    success, that_profession = behaviour.delete_profession_by_id(request["id"])
    if success:
        return ProfessionResponse(200, method, that_profession)
    return ProfessionResponse(500, method, that_profession)


def add_event(method: str, request: dict):
    """Добавление нового мероприятия с необходимыми проверками."""
    if not all_params_in(EventResponse.needed_params_to_add, request):
        return EventResponse(400, method)

    user = behaviour.get_user_by_token(request["token"])
    if not user:
        return EventResponse(403, method)
    if user.email not in users_have_permission:
        return EventResponse(403, method)

    date_of_the_event = datetime.datetime.strptime(request["date_of_the_event"], event_date_format)

    success, new_event = behaviour.add_event(
        event_name=request["name"],
        date_of_the_event=date_of_the_event,
        description=request["description"],
        place=request["place"],
        form_of_the_event=request["form_of_the_event"]
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

    success, that_event = behaviour.delete_event(request["id"])
    if success:
        return EventResponse(200, method, that_event)
    return EventResponse(500, method, that_event)


def profession(method: str, request: dict):
    """Ответ для /api/profession."""
    if method == "POST":
        return add_profession(method, request)
    elif method == "DELETE":
        return delete_profession(method, request)

    return Response(404, method)


def spheres(method: str, request: dict):
    pass


def event(method: str, request: dict):
    """Ответ для /api/event"""
    if method == "POST":
        return add_event(method, request)
    elif method == "DELETE":
        return delete_event(method, request)

    return Response(404, method)
