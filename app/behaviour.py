# Этот модуль предназначен исключительно для методов, относящимися к Базе Данных.

from models import Event, EventSpheres
from models import EventRegistered
from models import Profession, ProfessionPhotos, ProfessionSpheres
from models import Token, User
from models import Session
import answers
from configs import token_symbols, token_size

from sqlalchemy.orm import Session as SessionObject, Query
import datetime
from random import choice as random_choice


def add_profession(name: str, article: str, short_article: str, icon_link: str):
    if len(name) >= 50:
        return False, answers.profession_name_len_limit

    session: SessionObject
    with Session(expire_on_commit=False) as session:
        new_profession = Profession(
            name=name,
            article=article,
            short_article=short_article,
            icon_link=icon_link
        )
        session.add(new_profession)
        session.commit()

    return True, new_profession


def delete_profession_by_id(profession_id: int):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        profession = session.query(Profession).get(profession_id)
        if profession:
            session.delete(profession)
            session.commit()
    return bool(profession), profession


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


def add_user(full_name: str, email: str, hashed_password: str):
    if not check_free_email(email):
        return False, answers.busy_email

    session: SessionObject
    with Session(expire_on_commit=False) as session:
        new_user = User(
            full_name=full_name,
            email=email,
            hash_password=hashed_password
        )
        session.add(new_user)
        session.commit()
    return True, new_user


def delete_user(user_id: int):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        user = session.query(User).get(user_id)
        if user:
            session.delete(user)
            session.commit()

    return bool(user), user


def generate_token(session: SessionObject):
    """Генерация абсолютно нового токена."""
    busy_token = True
    new_token = ""

    while busy_token:
        new_token = ""
        for _ in range(token_size):
            symbol: str
            symbol = random_choice(token_symbols)
            new_token += random_choice((symbol, symbol.upper()))
        busy_token = bool(session.query(Token).filter(Token.key == new_token).count())

    return new_token


def get_active_token(user_id: int):
    """Получение активного токена."""
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        active_tokens = session.query(Token).filter(
            Token.user_id == user_id, Token.expiration_date > datetime.datetime.now()
        ).all()
        if active_tokens:
            return active_tokens[-1]

        key = generate_token(session)
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
        token = Token(
            user_id=user_id,
            key=key,
            expiration_date=expiration_date
        )
        session.add(token)
        session.commit()
    return token


def authenticate_user(email: str, hash_password: str):
    """
    Проверка логина и пароля.
    Получение действующего токена.
    """
    session: SessionObject
    with Session() as session:
        user: User
        user = session.query(User).filter(User.email == email and User.hash_password == hash_password).all()
        if not user:
            return False, None
        user = user[0]
        token = get_active_token(user.id)

    return True, token


def check_free_email(email: str):
    """
    Проверка свободной почты.
    True: почта свободна.
    False: почта занята.
    """
    session: SessionObject
    with Session() as session:
        query = session.query(User).filter(User.email == email)
        count = bool(query.count())

    return not count


def get_user_by_token(token: str):
    """
    Получение пользователя, исходя из его токена.
    """
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        token = session.query(Token).get(token)
        if not token:
            return None

        if token.expiration_date <= datetime.datetime.now():
            return None
        user_id = token.user_id
        user = session.query(User).get(user_id)

    return user


def add_event(event_name: str, date_of_the_event: datetime,
              description: str, short_description: str,
              place: str, form_of_the_event: str,
              duration_in_hours: float, speaker_id: int,
              icon_link: str):
    """Добавление мероприятия."""
    if len(event_name) >= 50:
        return answers.event_name_len_limit

    session: SessionObject
    with Session(expire_on_commit=False) as session:
        event = Event(
            name=event_name,
            date_of_the_event=date_of_the_event,
            description=description,
            short_description=short_description,
            place=place,
            duration_in_hours=duration_in_hours,
            form_of_the_event=form_of_the_event,
            speaker_id=speaker_id,
            icon_link=icon_link
        )
        session.add(event)
        session.commit()
    return event


def delete_event(event_id: int):
    """Удаление мероприятия."""
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        event = session.query(Event).get(event_id)
        if event:
            session.delete(event)
        query = session.query(EventRegistered).filter(
            EventRegistered.event_id == event_id
        )
        for registered in query.all():
            session.delete(registered)

        query = session.query(EventSpheres).filter(
            EventSpheres.event_id == event_id
        )
        for spheres in query.all():
            session.delete(spheres)

        session.commit()

    return True, event


def add_sphere_to_event(event_id: int, sphere: str):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        events_sphere = EventSpheres(
            event_id=event_id,
            name=sphere
        )
        session.add(events_sphere)
        session.commit()
    return True


def delete_sphere_from_event(event_id: int, sphere: str = "*"):
    session: SessionObject
    with Session() as session:
        query: Query
        query = session.query(EventSpheres)
        query = query.filter(EventSpheres.event_id == event_id)
        if sphere != "*":
            for event_sphere in query.filter(EventSpheres.name.ilike(sphere)).all():
                session.delete(event_sphere)
        else:
            query.delete()
        session.commit()
    return True


def get_events(limit: int, offset: int,
               from_date: datetime.datetime,
               to_date: datetime.datetime,
               query: str):
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


def register_user_on_event(user_id: int, event_id: int):
    """
    Регистрация пользователя на событие.
    """
    session: SessionObject
    with Session() as session:
        new_event_registered = EventRegistered(
            user_id=user_id,
            event_id=event_id
        )
        session.add(new_event_registered)
        session.commit()

    return bool(new_event_registered)


def delete_registration_on_event(user_id: int, event_id: int):
    """
    Удалить запись о регистрации пользователя.
    """
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        event_registered = session.query(EventRegistered).filter(
            EventRegistered.user_id == user_id,
            EventRegistered.event_id == event_id
        )
        event_registered = event_registered.get()
        if not event_registered:
            return False, None

        session.delete(event_registered)
        session.commit()
    return True, event_registered


def user_registered(user_id: int):
    """
    Список мероприятий, на которые пользователь зарегистрирован.

    [(EventRegistered, EventObject), (EventRegistered, EventObject)...]
    """
    session: SessionObject
    with Session() as session:
        query: Query
        query = session.query(EventRegistered, Event).filter(
            EventRegistered.user_id == user_id
        )
        query = query.join(Event, Event.id == EventRegistered.event_id)
    return query.all()


def count_registered(event_id: int):
    """
    Сколько зарегистрировалось на мероприятия.
    """
    session: SessionObject
    with Session() as session:
        query: Query
        query = session.query(EventRegistered).filter(
            EventRegistered.event_id == event_id
        )
    return query.count()


def add_sphere_to_profession(profession_id: int, sphere: str):
    session: SessionObject
    with Session() as session:
        profession_sphere = ProfessionSpheres(
            profession_id=profession_id,
            name=sphere
        )
        session.add(profession_sphere)
        session.commit()
    return True


def delete_sphere_from_profession(profession_id: int, sphere: str = "*"):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(ProfessionSpheres)
        query = query.filter(ProfessionSpheres.profession_id == profession_id)
        if sphere != "*":
            query.filter(ProfessionSpheres.name == sphere).delete()
        else:
            query.delete()
        session.commit()
    return True


def add_photo_to_profession(profession_id: int, link: str):
    session: SessionObject
    with Session() as session:
        profession_photo = ProfessionPhotos(
            prof_id=profession_id,
            link=link
        )
        session.add(profession_photo)
        session.commit()
    return profession_photo


def delete_photo_from_profession(profession_id: int, link: str):
    session: SessionObject
    with Session(expire_on_commit=False) as session:
        query: Query
        query = session.query(ProfessionPhotos)
        query = query.filter(ProfessionPhotos.profession_id == profession_id)
        query = query.filter(ProfessionPhotos.link == link)
        result = query.first()
        if not result:
            return False, None
        session.delete(result)
        session.commit()
    return True, result


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
        query = session.query(Event, EventSpheres)
        query = query.join(EventSpheres, EventSpheres.event_id == Event.id, isouter=True)

        query = query.filter(Event.id == event_id)
        result = query.all()
        if result:
            result = result[0]

            result = {
                "event": result[0],
                "spheres": result[1]
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
        query = session.query(Profession)
        profession = query.get(profession_id)
        if not profession:
            return None

        spheres = session.query(ProfessionSpheres).filter(
            ProfessionSpheres.profession_id == profession_id
        )
        spheres = spheres.all()
        photos = session.query(ProfessionPhotos).filter(
            ProfessionPhotos.profession_id == profession_id
        )
        photos = photos.all()
        beauty_result = {
            "profession": profession,
            "spheres": spheres,
            "photos": photos
        }
        return beauty_result
