# Этот модуль предназначен исключительно для методов, относящимися к Базе Данных.

from models import Event, EventSpheres
from models import EventRegistered, ProfessionSpheres
from models import Profession, ProfessionPhotos, User, Sphere
from models import Session
from sqlalchemy.orm import Session as SessionObject


def add_object(func_to_create):
    """
    Оборачиваемая функция должна вернуть полноценный объект:
    Это реализация класса, который необходимо добавить.
    """
    def wrapper(*args, **kwargs):
        session: SessionObject
        session = Session()

        result_object = func_to_create(*args, **kwargs)

        session.add(result_object)
        session.commit()

        session.close()
        return True, result_object
    return wrapper


def delete_object_by_id(func_to_get):
    """
    Оборачиваемая функция должна вернуть два параметра:
    1. Класс объекта, являющейся представлением таблицы.
    2. Уникальный ID объекта (как spheres.id).
    """
    def wrapper(*args, **kwargs):
        session: SessionObject
        session = Session()
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
