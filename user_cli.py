from config import version
from re import findall
from re import sub
from exceptions import *
from database import Person
from database import Phone
from config import db
from peewee import IntegrityError
from datetime import datetime


class Validation:
    @staticmethod
    def name(line):
        if line:
            if result := findall(r"^\s*([a-zA-Z0-9\s\-]+?)\s*$", line):
                result = result[0]
                result = ' '.join(word.title() for word in result.split())
                return result
            else:
                raise SpecialSymbols
        else:
            raise EmptyInput

    @staticmethod
    def phone_number(line):
        line = sub(r'^\s*', '', line)
        line = sub(r'\s*$', '', line)
        line = sub(r'^\+7', '8', line)
        if line:
            if findall(r"^([0-9]+)$", line):
                if result := findall(r"^([0-9]{11})$", line):
                    result = result[0]
                    return result
                else:
                    raise NotElevenDigits
            else:
                raise NotOnlyDigits
        else:
            raise EmptyInput

    @staticmethod
    def birth_date(line):
        line = sub(r'^\s*', '', line)
        line = sub(r'\s*$', '', line)
        if line:
            if result := findall(r'^\d\d[.\\/]\d\d[.\\/]\d\d\d\d', line):
                result = result[0]
                day, month, year = result.split('.')
                date = datetime(year, month, day)
                if date.day == day and date.month == month and date.year == year:
                    pass
                else:
                    raise NonExistentDate
            else:
                raise DataFormat
        else:
            raise EmptyInput




class CLI:
    @staticmethod
    def get_field(name, validation, may_be_empty=False):
        result = None
        while result is None:
            try:
                line = input(f"Enter {name} >> ")
                result = validation(line)
            except SpecialSymbols:
                print("[input error] Do not use special characters")
            except NotOnlyDigits:
                print('[input error] There can be only digits in the number record')
            except NotElevenDigits:
                print('[input error] There must be 11 digits in the number record')
            except EmptyInput:
                if may_be_empty:
                    result = ""
                else:
                    print('[input error] Empty input, please, try again')
            except DataFormat:
                print('[input error] Вы ввели дату в неверном формате dd.mm.yyyy')
            except NonExistentDate:
                print('[error] You entered a non-existent date')
        return result

    @staticmethod
    def get_names():
        first = CLI.get_field("first name", Validation.name)
        last = CLI.get_field("last name", Validation.name)
        return first, last


if __name__ == '__main__':
    db.connect()
    db.create_tables([Person, Phone])
    print(f"Phonebook by @6a16ec v {version}")
    while True:
        command = input(f"Enter command >> ")
        if command == 'добавить новую запись' or command == '0':
            first_name, last_name = CLI.get_names()
            birth_date = CLI.get_field("birth sate", Validation.birth_date, may_be_empty=True)
            try:
                person = Person.create(first_name=first_name, last_name=last_name)
                phone_number = CLI.get_field("phone number", Validation.phone_number)
                try:
                    Phone.create(number=phone_number, owner=person)
                except IntegrityError:
                    phone = Phone.get(Phone.number == phone_number)
                    print(f"Данный номер принадлежит {phone.owner.first_name} {phone.owner.last_name}")
            except IntegrityError:
                person = Person.get(Person.first_name == first_name, Person.last_name == last_name)
                print("Запись на этого человека уже есть")
                command = input("1 - change, 2 - change id, enter - main menu")
                if command == 'change' or command == '1':
                    pass
                elif command == 'change id' or command == '2':
                    first_name, last_name = CLI.get_names()
                    person.update(first_name=first_name, last_name=last_name)
        elif command == '1':
            print()
        #         phones_amount = len(person.phones)
        #         print(f"The person was found, he has {phones_amount} numbers.")
        #
        #         line = input(f"Press 0 to enter the main menu, enter to add a one new phone number.\n>> ")
        #         if line == "меню" or line == '0':
        #             continue
        #     else:
        #         person = Person.create(first_name=first_name, last_name=last_name)
        #     phone_number = CLI.get_field("phone number", Validation.phone_number)
        #     if phone := CLI.is_phone_exists(phone_number):
        #         pass
        #     else:
        #         Phone.create(number=phone_number, owner=person)
        # elif string == 'посмотреть все записи' or string == '1':
        #     data = Person.select().execute()
        #     for person in data:
        #         print(f"{person.first_name} {person.last_name}")
        #
        # for person in data:
        #     for phone in person.phones:
        #         print(f"{person.first_name}\t{person.last_name}\t{phone.number}\t{phone.type}")
        #     print("!")
