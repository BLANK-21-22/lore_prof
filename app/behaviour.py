# Этот модуль предназначен исключительно для методов, относящимися к Базе Данных.

from models import Event, EventSpheres
from models import EventRegistered, ProfessionSpheres
from models import Profession, ProfessionPhotos, User, Sphere
from models import Token
from models import Session
from sqlalchemy.orm import Session as SessionObject

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
