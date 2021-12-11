from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, VARCHAR, TIMESTAMP, Text
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

from configs import database_configs

engine = create_engine(url=database_configs["url"])
Session = sessionmaker(bind=engine)

Base = declarative_base(bind=engine)


class Users(Base):
    __tablename__ = "users"

    id = Column("id", Integer, autoincrement=True)
    full_name = Column("full_name", VARCHAR(100))
    email = Column("email", VARCHAR(255))
    hash_password = Column("hash_password", VARCHAR(60))

    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )


class Events(Base):
    __tablename__ = "events"

    id = Column("id", Integer, autoincrement=True)
    name = Column("name", VARCHAR(50))
    date_of_the_event = Column("date_of_the_event", TIMESTAMP)
    description = Column("description", Text)
    place = Column("place", VARCHAR(255))
    form_of_the_event = Column("form_of_the_event", VARCHAR(5))

    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )


class Spheres(Base):
    __tablename__ = "spheres"

    id = Column("id", Integer)
    name = Column("name", VARCHAR(20))

    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )


class Professions(Base):
    __tablename__ = "professions"

    id = Column("id", Integer)
    name = Column("name", VARCHAR(25))
    article = Column("article", Text)

    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )


class EventsRegistered(Base):
    __tablename__ = "events_registered"

    event_id = Column("event_id", Integer)
    user_id = Column("user_id", Integer)

    __table_args__ = (
        PrimaryKeyConstraint("event_id", "user_id"),
        ForeignKeyConstraint(("user_id", ), ("users.id", ))
    )


class EventsSpheres(Base):
    __tablename__ = "events_spheres"

    sphere_id = Column("sphere_id", Integer)
    event_id = Column("event_id", Integer)

    __table_args__ = (
        PrimaryKeyConstraint("event_id", "sphere_id"),
        ForeignKeyConstraint(("event_id",), ("events.id",)),
        ForeignKeyConstraint(("sphere_id", ), ("spheres.id", ))
    )


class ProfessionsSpheres(Base):
    __tablename__ = "professions_spheres"

    prof_id = Column("prof_id", Integer)
    sphere_id = Column("sphere_id", Integer)

    __table_args__ = (
        PrimaryKeyConstraint("prof_id", "sphere_id"),
        ForeignKeyConstraint(("prof_id", ), ("professions.id", )),
        ForeignKeyConstraint(("sphere_id", ), ("spheres.id", ))
    )


class ProfessionsPhotos(Base):
    __tablename__ = "professions_photos"

    prof_id = Column("prof_id", Integer)
    link = Column("link", VARCHAR(25))

    __table_args__ = (
        PrimaryKeyConstraint("prof_id", "link"),
        ForeignKeyConstraint(("prof_id", ), ("professions.id", ))
    )


if database_configs["recreate_database"]:
    # Пересоздание всей БД. Очищение от всех данных.

    session = Session()
    for _class in [
        Users, Events, Spheres, Professions,
        EventsRegistered, EventsSpheres, ProfessionsSpheres,
        ProfessionsPhotos
    ]:
        session.query(_class).delete()
    Base.metadata.create_all(bind=engine)
    session.commit()
    session.close()
else:
    Base.metadata.create_all(bind=engine)
