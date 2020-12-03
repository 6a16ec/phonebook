import os
from config import db
from database import Person
from database import Phone

if __name__ == '__main__':
    os.remove("tests/phonebook.db")  # dev
    # print("Hello, phonebook!")
    db.connect()
    db.create_tables([Person, Phone])
    person = Person.create(first_name="Nikita2", last_name="Semaev")
    # phone = Phone.create(number="891594018942", owner=person)
    # phone = Phone.create(number="891594018941", owner=person)
    data = Person.select().execute()
    # # data =
    for person in data:
        print(person.id, person.first_name, person.last_name, person.phones.execute())
