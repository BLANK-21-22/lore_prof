# Этот модуль предназначен исключительно для методов, относящимися к Базе Данных.

from models import Event, EventSpheres
from models import EventRegistered, ProfessionSphere
from models import Profession, ProfessionPhotos, User, Sphere
from models import Token
from models import Session
from sqlalchemy.orm import Session as SessionObject, Query

from random import choice as random_choice
from configs import token_symbols, token_size

import datetime


def add_object(func_to_create):
    """
    Оборачиваемая функция должна вернуть полноценный объект:
    Это реализация класса, который необходимо добавить.
    """
    def wrapper(*args, **kwargs):
        session: SessionObject
        session = Session(expire_on_commit=False)

        result_object = func_to_create(*args, **kwargs)
        if result_object and not isinstance(result_object, str):
            session.add(result_object)
            session.commit()

            session.close()
            return True, result_object
        return False, result_object
    return wrapper


def delete_object_by_id(func_to_get):
    """
    Оборачиваемая функция должна вернуть два параметра:
    1. Класс объекта, являющейся представлением таблицы.
    2. Уникальный ID объекта (как spheres.id).
    """
    def wrapper(*args, **kwargs):
        session: SessionObject
        session = Session(expire_on_commit=False)
        object_class, object_id = func_to_get(*args, **kwargs)

        result_object = session.query(object_class).get(object_id)
        if result_object:
            session.delete(result_object)
            session.commit()

        session.close()

        return bool(result_object), result_object
    return wrapper


@add_object
def add_sphere(sphere_name: str):
    if len(sphere_name) >= 20:
        return "Название сферы должны быть менее 20 символов."

    new_sphere = Sphere(name=sphere_name)
    return new_sphere


@delete_object_by_id
def del_sphere_by_id(sphere_id: int):
    return Sphere, sphere_id


def get_sphere_by_name(sphere_name: str):
    session: SessionObject
    with Session() as session:
        query = session.query(Sphere).filter(Sphere.name == sphere_name)
        spheres = query.all()
        if not spheres:
            return None
    return spheres[0]


def get_all_spheres():
    session: SessionObject
    session = Session()

    result_object = session.query(Sphere).all()

    session.close()
    return result_object


@add_object
def add_profession(name: str, article: str):
    if len(name) >= 25:
        return "Название профессии должно быть менее 25 символов."

    new_profession = Profession(
        name=name,
        article=article
    )
    return new_profession


@delete_object_by_id
def delete_profession_by_id(profession_id: int):
    return Profession, profession_id


def get_all_professions(limit: int, offset: int, query: str):
    """
    Возвращает список из объектов Profession.
    [ProfessionObject, ProfessionObject...]
    """
    session: SessionObject
    with Session() as session:
        all_professions = session.query(Profession)
        if query:
            all_professions = all_professions.filter(Profession.name.ilike(f"%{query.lower()}%"))
        all_professions = all_professions.order_by(Profession.name.desc())
        all_professions = all_professions.offset(offset).limit(limit)
        all_professions = all_professions.all()
    return all_professions


@add_object
def add_user(full_name: str, email: str, hashed_password: str):
    if not check_free_email(email):
        return "Почта занята."
    if len(email) >= 255:
        return "Количество символов почты не должно превышать 255 символов."
    if len(full_name) >= 100:
        return "Полное имя должно быть менее 100 символов."

    new_user = User(
        full_name=full_name,
        email=email,
        hash_password=hashed_password
    )
    return new_user


@delete_object_by_id
def delete_user(user_id: int):
    return User, user_id


@add_object
def get_new_token(user_id: int):
    new_token = ""
    not_free_token = True
    session: SessionObject
    session = Session()
    while not_free_token:
        new_token = ""
        for _ in range(token_size):
            symbol: str
            symbol = random_choice(token_symbols)
            new_token += random_choice((symbol, symbol.upper()))
        not_free_token = bool(session.query(Token).filter(Token.token == new_token).count())

    session.close()
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
    return Token(
        user_id=user_id,
        token=new_token,
        expiration_date=expiration_date
    )


def authenticate_user(email: str, hash_password: str):
    """
    Проверка логина и пароля.
    Получение токена.
    """
    session: SessionObject
    session = Session()
    user: User
    user = session.query(User).filter(User.email == email and User.hash_password == hash_password).all()
    session.close()
    if not user:
        return False, None
    user = user[0]
    token: Token
    is_token, token = get_new_token(user.id)

    if not is_token:
        return False, None

    return True, token


def check_free_email(email: str):
    """
    Проверка свободной почты.
    True: почта свободна.
    False: почта занята.
    """
    session: SessionObject
    session = Session()
    query = session.query(User).filter(User.email == email)
    session.close()
    return not bool(query.count())


def get_user_by_token(token: str):
    """
    Получение пользователя, исходя из его токена.
    """
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        token = session.query(Token).get(token)
        if token:
            if token.expiration_date > datetime.datetime.now():
                user_id = token.user_id
                user = session.query(User).get(user_id)
            else:
                user = None
        else:
            user = None

    return user


@add_object
def add_event(event_name: str, date_of_the_event: datetime,
              description: str, place: str,
              form_of_the_event: str):
    """Добавление мероприятия."""
    if len(event_name) >= 50:
        return "Название мероприятия должно быть менее 50 символов."
    if len(place) >= 255:
        return "Местоположение должно быть менее 255 символов."
    if len(form_of_the_event) >= 15:
        return "Форма проведения мероприятия должна быть менее 15 символов."

    return Event(
        name=event_name,
        date_of_the_event=date_of_the_event,
        description=description,
        place=place,
        form_of_the_event=form_of_the_event
    )


@delete_object_by_id
def delete_event(event_id):
    """Удаление мероприятия"""
    return Event, event_id


def get_events(limit: int, offset: int, from_date: datetime, to_date: datetime, query: str):
    """
    Получение списка всех мероприятий за определённый срок.

    [EventObject, EventObject...]
    """
    session: SessionObject
    with Session() as session:
        result: Query
        result = session.query(Event)

        result = result.filter(Event.date_of_the_event <= to_date)
        result = result.filter(Event.date_of_the_event >= from_date)
        if query:
            result = result.filter(Event.name.ilike(f"%{query.lower()}%"))

        result = result.order_by(Event.date_of_the_event.desc())
        result = result.offset(offset).limit(limit)
        result = result.all()
    return result


@add_object
def register_user_on_event(user_id: int, event_id: int):
    """
    Регистрация пользователя на событие.
    """
    return EventRegistered(
        user_id=user_id,
        event_id=event_id
    )


def delete_registration_on_event(user_id: int, event_id: int):
    """
    Удалить запись о регистрации пользователя.
    """
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        event_registered = session.query(EventRegistered).filter(EventRegistered.user_id == user_id)
        event_registered = event_registered.filter(EventRegistered.event_id == event_id).first()
        if event_registered:
            session.delete(event_registered)
            session.commit()
            return True, event_registered
        return False, None


def user_registered(user_id: int):
    """
    Куда зарегистрирован пользователь.
    """
    session: SessionObject
    with Session() as session:
        query: Query
        query = session.query(EventRegistered).filter(user_id == EventRegistered.user_id)
        return query.all()


def count_registered(event_id: int):
    """
    Сколько зарегистрировалось на мероприятия.
    """
    session: SessionObject
    with Session() as session:
        query: Query
        query = session.query(EventRegistered).filter(event_id == EventRegistered.event_id)
        return query.count()


@add_object
def add_sphere_to_event(sphere_id: int, event_id: int):
    return EventSpheres(
        sphere_id=sphere_id,
        event_id=event_id
    )


def delete_sphere_from_event(event_id: int, sphere_id: int = "*"):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(EventSpheres)
        query = query.filter(EventSpheres.event_id == event_id)
        if isinstance(sphere_id, int):
            query.filter(EventSpheres.sphere_id == sphere_id).delete()
        else:
            query.delete()
        session.commit()
    return True


@add_object
def add_sphere_to_profession(profession_id: int, sphere_id: int):
    return ProfessionSphere(
        prof_id=profession_id,
        sphere_id=sphere_id
    )


def delete_sphere_from_profession(profession_id: int, sphere_id: int = "*"):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(ProfessionSphere)
        query = query.filter(ProfessionSphere.prof_id == profession_id)
        if isinstance(sphere_id, int):
            query.filter(ProfessionSphere.sphere_id == sphere_id).delete()
        else:
            query.delete()
        session.commit()
    return True


@add_object
def add_photo_to_profession(profession_id: int, link: str):
    return ProfessionPhotos(
        prof_id=profession_id,
        link=link
    )


def delete_photo_from_profession(profession_id: int, link: str):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(ProfessionPhotos)
        query = query.filter(ProfessionPhotos.prof_id == profession_id)
        query = query.filter(ProfessionPhotos.link == link)
        result = query.first()
        if result:
            session.delete(result)
            session.commit()
            return True, result
        return False, None


def delete_links_for_spheres(sphere_id: int):
    session: SessionObject
    with Session() as session:
        query = session.query(EventSpheres).filter(EventSpheres.sphere_id == sphere_id)
        query.delete()
        query = session.query(ProfessionSphere).filter(ProfessionSphere.sphere_id == sphere_id)
        query.delete()
    return True


def get_event(event_id: int):
    """
    Получение конкретного события.
    None/Dict
    Форма Dict:
    {
        "event": EventObject,
        "spheres": [EventSpheresObject, ]
    }
    """
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(Event, Sphere)
        query = query.outerjoin(EventSpheres, EventSpheres.event_id == Event.id)
        query = query.outerjoin(Sphere, Sphere.id == EventSpheres.sphere_id)

        query = query.filter(Event.id == event_id)
        result = query.all()
        if result:
            result = {
                "event": result[0][0],
                "spheres": [x[1] for x in result]
            }
            return result


def get_profession(profession_id: int):
    """
    Получение конкретной профессии.
    Форма ответа:
    None/Dict
    Форма Dict:
    {
        "profession": ProfessionObject,
        "spheres": [ProfessionSphereObject, ],
        "photos": [ProfessionPhotosObject, ]
    }
    """
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(Profession, ProfessionSphere, ProfessionPhotos)
        query = query.outerjoin(ProfessionSphere, ProfessionSphere.prof_id == Profession.id)
        query = query.outerjoin(ProfessionPhotos, ProfessionPhotos.prof_id == Profession.id)
        query = query.filter(Profession.id == profession_id)
        result = query.all()
        if result:
            beauty_result = {
                "profession": result[0][0],
                "spheres": [],
                "photos": []
            }
            for _, sphere, photo in result:
                if sphere and sphere not in beauty_result["spheres"]:
                    beauty_result["spheres"].append(sphere)
                if photo and photo not in beauty_result["photos"]:
                    beauty_result["photos"].append(photo)
        else:
            beauty_result = None

        return beauty_result
