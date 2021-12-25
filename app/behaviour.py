# Этот модуль предназначен исключительно для методов, относящимися к Базе Данных.

from models import Event, EventSpheres
from models import EventRegistered, ProfessionSpheres
from models import Profession, ProfessionPhotos, User, Sphere
from models import Token
from models import Session
from sqlalchemy.orm import Session as SessionObject, Query

from random import choice as random_choice
from configs import token_symbols, token_size
from datetime import datetime, timedelta


def add_object(func_to_create):
    """
    Оборачиваемая функция должна вернуть полноценный объект:
    Это реализация класса, который необходимо добавить.
    """
    def wrapper(*args, **kwargs):
        session: SessionObject
        session = Session(expire_on_commit=False)

        result_object = func_to_create(*args, **kwargs)
        if result_object:
            session.add(result_object)
            session.commit()

            session.close()
            return True, result_object
        return False, None
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
    new_sphere = Sphere(name=sphere_name)
    return new_sphere


@delete_object_by_id
def del_sphere_by_id(sphere_id: int):
    return Sphere, sphere_id


def get_all_spheres():
    session: SessionObject
    session = Session()

    result_object = session.query(Sphere).all()

    session.close()
    return result_object


@add_object
def add_profession(name: str, article: str):
    new_profession = Profession(
        name=name,
        article=article
    )
    return new_profession


@delete_object_by_id
def delete_profession_by_id(profession_id: int):
    return Profession, profession_id


def get_all_professions():
    session: SessionObject
    session = Session()

    result_object = session.query(Profession).all()

    session.close()
    return result_object


@add_object
def add_user(full_name: str, email: str, hash_password: str):
    if check_free_email(email):
        new_user = User(
            full_name=full_name,
            email=email,
            hash_password=hash_password
        )
        return new_user
    return None


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
    expiration_date = datetime.now() + timedelta(days=1)
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


def authorize_user(token: str):
    """
    Разрешение доступа к ресурсу.
    """
    session: SessionObject
    session = Session()
    info: Token
    info = session.query(Token).filter(Token.token == token).count()
    return bool(info)


@add_object
def add_event(event_name: str, date_of_the_event: datetime,
              description: str, place: str,
              form_of_the_event: str):
    """Добавление мероприятия."""
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


def get_all_events(limit: int, offset: int, from_date: datetime, to_date: datetime):
    """
    Получение списка всех мероприятий за определённый срок.
    """
    session: SessionObject
    with Session() as session:
        result: Query
        result = session.query(Event)

        result = result.filter(Event.date_of_the_event <= to_date)
        result = result.filter(Event.date_of_the_event >= from_date)

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
