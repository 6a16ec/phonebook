from unittest import TestCase
from random import choice
from string import ascii_letters
from string import digits
from database import Person
from database import Phone
from peewee import IntegrityError
from config import db


class TestCreation(TestCase):
    def setUp(self) -> None:
        # db.create_tables([Person])
        db.create_tables([Person, Phone])
        self.first_name = ''.join(choice(ascii_letters) for i in range(10))
        self.last_name = ''.join(choice(ascii_letters) for i in range(10))
        self.phone_number = '8' + ''.join(choice(digits) for i in range(10))

    def test_001_simple(self):
        Person.create(first_name=self.first_name, last_name=self.last_name)

    def test_002_not_unique(self):
        kwargs = {"first_name": self.first_name, "last_name": self.last_name}
        Person.create(**kwargs)
        # Person.create(**kwargs)
        self.assertRaises(IntegrityError, Person.create, **kwargs)

    def test_003_person_plus_phone(self):
        person = Person.create(first_name=self.first_name, last_name=self.last_name)
        # phone = Phone.create(number=self.phone_number, owner=person)
