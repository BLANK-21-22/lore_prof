from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, VARCHAR, TIMESTAMP, Text, Float
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

from configs import database_configs

engine = create_engine(url=database_configs["url"])
Session = sessionmaker(bind=engine)

Base = declarative_base(bind=engine)


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, autoincrement=True)
    full_name = Column("full_name", VARCHAR(100))
    email = Column("email", VARCHAR(255))
    hash_password = Column("hash_password", Text)

    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )


class Token(Base):
    __tablename__ = "tokens"

    user_id = Column("user_id", Integer)
    key = Column("token", Text)
    expiration_date = Column("expiration_date", TIMESTAMP)

    __table_args__ = (
        PrimaryKeyConstraint("token"),
        ForeignKeyConstraint(("user_id", ), ("users.id", ))
    )


class Event(Base):
    def __repr__(self):
        return f"<Event id={self.id}, name='{self.name}'>"
    __tablename__ = "events"

    id = Column("id", Integer, autoincrement=True)
    name = Column("name", VARCHAR(50))
    date_of_the_event = Column("date_of_the_event", TIMESTAMP)
    duration_in_hours = Column("duration_in_hours", Float)
    speaker_id = Column("speaker_id", Integer)
    description = Column("description", Text)
    short_description = Column("short_description", Text)
    place = Column("place", Text)
    form_of_the_event = Column("form_of_the_event", Text)
    icon_link = Column("icon_link", Text)

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(("speaker_id", ), ("users.id", ))
    )


class Profession(Base):
    def __repr__(self):
        return f"<Profession id={self.id}, name='{self.name}'>"
    __tablename__ = "professions"

    id = Column("id", Integer, autoincrement=True)
    name = Column("name", VARCHAR(50))
    short_article = Column("short_article", Text)
    article = Column("article", Text)
    icon_link = Column("icon_link", Text)

    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )


class EventRegistered(Base):
    def __repr__(self):
        return f"<EventRegistered user_id={self.user_id}, event_id={self.event_id}>"
    __tablename__ = "events_registered"

    event_id = Column("event_id", Integer)
    user_id = Column("user_id", Integer)

    __table_args__ = (
        PrimaryKeyConstraint("event_id", "user_id"),
        ForeignKeyConstraint(("user_id", ), ("users.id", ))
    )


class ProfessionPhotos(Base):
    def __repr__(self):
        return f"<ProfessionPhoto prof_id={self.prof_id}, link='{self.link}'>"
    __tablename__ = "professions_photos"

    profession_id = Column("prof_id", Integer)
    link = Column("link", Text)

    __table_args__ = (
        PrimaryKeyConstraint("prof_id", "link"),
        ForeignKeyConstraint(("prof_id", ), ("professions.id", ))
    )


class ProfessionSpheres(Base):
    __tablename__ = "profession_spheres"

    profession_id = Column("profession_id", Integer)
    name = Column("name", Text)

    __table_args__ = (
        PrimaryKeyConstraint("profession_id", "name"),
        ForeignKeyConstraint(("profession_id",), ("professions.id",))
    )


class EventSpheres(Base):
    __tablename__ = "event_spheres"

    event_id = Column("event_id", Integer)
    name = Column("name", Text)

    __table_args__ = (
        PrimaryKeyConstraint("event_id", "name"),
        ForeignKeyConstraint(("event_id",), ("events.id",))
    )


if database_configs["recreate_database"]:
    # Пересоздание всей БД. Очищение от всех данных.
    Base.metadata.drop_all(engine)
    session = Session()
    Base.metadata.create_all(bind=engine)
    session.commit()
    session.close()
else:
    Base.metadata.create_all(bind=engine)
