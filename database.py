from peewee import *
from datetime import date

import config


class BaseModel(Model):
    class Meta:
        database = config.db


class Person(BaseModel):
    first_name = CharField()
    last_name = CharField()
    birth_date = DateField(null=True)

    def __str__(self):
        string = f"{self.first_name}\t{self.last_name}"
        if self.birth_date:
            string += f"\t{self.birth_date}"
        string += f"\t->\t{len(self.phones)} phones"
        for phone in self.phones:
            string += f'\n\t{phone.number} {phone.type}'
        return string

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
