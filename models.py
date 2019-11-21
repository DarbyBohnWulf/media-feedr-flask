from peewee import *
from flask_login import UserMixin

DATABASE = SqliteDatabase('media.sqlite', pragmas={'foreign_keys': 1})


class User(UserMixin, Model):
    username = CharField(64, unique=True)
    email = CharField(64, unique=True)
    password = CharField()

    class Meta:
        database = DATABASE


class Media(Model):
    title = CharField()
    year_of_release = IntegerField(
        constraints=[
            Check('year_of_release > 1905'),
            Check('year_of_release < 2021')
        ]
    )
    genre = CharField(32)
    poster_url = CharField()
    external_id = IntegerField(unique=True)

    class Meta:
        database = DATABASE


class Viewership(Model):
    user_id = ForeignKeyField(User, backref='viewerships')
    media_id = ForeignKeyField(Media, backref='viewerships')

    class Meta:
        database = DATABASE


class Review(Model):
    rating = IntegerField(constraints=[Check('rating < 6')])
    body = TextField()
    user_id = ForeignKeyField(User, backref='reviews')
    media_id = ForeignKeyField(Media, backref='reviews')
    date_added = TimestampField()

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Media, Viewership, Review], safe=True)
    print("Tables Flipped")
    DATABASE.close()
