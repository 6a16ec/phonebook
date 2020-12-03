from unittest import TestCase
from random import choice
from string import ascii_letters
from string import digits
from database import Person
from database import Phone
from peewee import IntegrityError
from config import db
from datetime import datetime


def new_name():
    return ''.join(choice(ascii_letters) for i in range(10))


def new_phone_number():
    return '8' + ''.join(choice(digits) for i in range(10))


class TestCreation(TestCase):
    def setUp(self) -> None:
        db.create_tables([Person, Phone])
        self.first_name = new_name()
        self.last_name = new_name()
        self.phone_number = new_phone_number()
        self.birth_date = datetime.now()

    def test_001_simple(self):
        Person.create(first_name=self.first_name, last_name=self.last_name)

    def test_002_not_unique_person(self):
        kwargs = {"first_name": self.first_name, "last_name": self.last_name}
        Person.create(**kwargs)
        self.assertRaises(IntegrityError, Person.create, **kwargs)

    def test_003_person_with_phone(self):
        person = Person.create(first_name=self.first_name, last_name=self.last_name)
        Phone.create(number=self.phone_number, owner=person)

    def test_003_person_with_two_phones(self):
        person = Person.create(first_name=self.first_name, last_name=self.last_name)
        Phone.create(number=self.phone_number, owner=person)
        phone_number2 = new_phone_number()
        Phone.create(number=phone_number2, owner=person, type="second")

    def test_004_not_unique_phone_number(self):
        person = Person.create(first_name=self.first_name, last_name=self.last_name)
        Phone.create(number=self.phone_number, owner=person)
        first_name2 = new_name()
        last_name2 = new_name()
        person2 = Person.create(first_name=first_name2, last_name=last_name2)
        self.assertRaises(IntegrityError, Phone.create, number=self.phone_number, owner=person2)
