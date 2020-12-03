from peewee import *

import config


class BaseModel(Model):
    class Meta:
        database = config.db


class Person(BaseModel):
    first_name = CharField()
    last_name = CharField()

    class Meta:
        pass
        # create a unique on first_name/last_name
        indexes = (
            (('first_name', 'last_name'), True),
        )
        # primary_key = CompositeKey('first_name', 'last_name')


class Phone(BaseModel):
    number = CharField(11, unique=True)
    type = CharField(default="default")
    owner = ForeignKeyField(Person, backref="phones")

    class Meta:
        indexes = (
            (('owner', 'type'), True),
        )