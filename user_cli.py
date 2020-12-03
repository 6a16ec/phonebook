from config import version
from re import findall
from re import sub
from re import fullmatch
from exceptions import *
from database import Person
from database import Phone
from config import db
from peewee import IntegrityError
from datetime import datetime


def normalize(line):
    line = sub(r'^\s*', '', line)
    line = sub(r'\s*$', '', line)
    line = sub(r'\s+', ' ', line)
    line = sub(r'\\$', ' ', line)  # стоит ли
    return line


def find_one(pattern, string, flags):
    result = findall(pattern=pattern, string=string, flags=flags)
    return result[0] if result else None


def normalize_input(func):
    def wrapper(line):
        line = normalize(line)
        if line:
            return func(line)
        else:
            raise EmptyInput

    return wrapper


class Validation:

    @staticmethod
    @normalize_input
    def name(line):
        if result := fullmatch(r"[a-zA-Z0-9\s\-]+", line):
            string = result.string
            string = ' '.join(word.title() for word in string.split())
            return string
        else:
            raise SpecialSymbols

    @staticmethod
    @normalize_input
    def phone_number(line):
        line = sub(r'^\+7', '8', line)
        if result := fullmatch(r"\d{11}", line):
            return result.string
        elif fullmatch(r"\d+", line):
            raise NotElevenDigits(len(line))
        else:
            raise NotOnlyDigits

    @staticmethod
    @normalize_input
    def birth_date(line):
        line = sub(r'[\\/-]', '.', line)
        if result := fullmatch(r'[\d]{1,2}[.][\d]{1,2}[.]\d{4}', line):
            string = result.string
            day, month, year = map(int, string.split('.'))
            try:
                date = datetime(year, month, day)
                return date
            except ValueError:
                raise NonExistentDate
        else:
            raise WrongDateFormat


class CLI:
    @staticmethod
    def get_field(name, validation, may_be_empty=False):
        result = None
        while result is None:
            try:
                line = input(f"Enter {name} >> ")
                result = validation(line)
            except EmptyInput as e:
                if may_be_empty:
                    return None
                else:
                    e.print()
            except (SpecialSymbols, NotOnlyDigits, WrongDateFormat, NonExistentDate, NotElevenDigits) as e:
                e.print()
        return result

    @staticmethod
    def get_names():
        first = CLI.get_field("first name", Validation.name)
        last = CLI.get_field("last name", Validation.name)
        return first, last


class MainState:
    def __init__(self):
        self.person = None
        self.next_state = None
        self.quit = False

    def loop(self):
        pass

    @classmethod
    def read_event(cls):
        event = input(f"Enter command >> ")
        event = normalize(event)
        return event


class MainMenu(MainState):
    def __init__(self):
        super().__init__()
        print('Main Menu: 1 - new contact, 2 - show all, 3 - search in phonebook 13 - quit')

    def loop(self):
        event = self.read_event()
        if event == '1':
            self.next_state = AddNewContact()
        elif event == '2':
            persons = Person.select().execute()
            for i, person in enumerate(persons):
                print(f'{i + 1}.', person)
        elif event == '3':
            params = {
                Person.first_name: CLI.get_field("first name", Validation.name, may_be_empty=True),
                Person.last_name: CLI.get_field("last name", Validation.name, may_be_empty=True),
                Person.birth_date: CLI.get_field("birth date", Validation.birth_date, may_be_empty=True),
                Phone.number: CLI.get_field("phone number", Validation.phone_number, may_be_empty=True)
            }
            params = {key: value for (key, value) in params.items() if value}
            expressions = [
                key == value
                for (key, value) in params.items()
            ]
            if expressions:
                persons = Person.select().join(Phone).where(*expressions)
                if persons:
                    for person in persons:
                        print(person)
                else:
                    print("None of the records were found")
            else:
                print("You haven't introduced any filters")
            self.next_state = MainMenu()
        elif event == '13':
            self.next_state = True
            self.quit = True


class AddNewContact(MainState):
    def __init__(self):
        super().__init__()

    def loop(self):
        first_name = CLI.get_field("first name", Validation.name)
        last_name = CLI.get_field("last name", Validation.name)
        try:
            person = Person.create(first_name=first_name, last_name=last_name)
        except IntegrityError:
            print(">> There's already an entry for this person")
            person = Person.get(Person.first_name == first_name, Person.last_name == last_name)
            self.next_state = UpdateUser(person)
        else:
            birth_date = CLI.get_field("birth date", Validation.birth_date, may_be_empty=True)
            if birth_date is not None:
                person.update(birth_date=birth_date)
            print(">> Person successfully added")
            self.next_state = CreatePhone(person)


class CreatePhone(MainState):
    def __init__(self, person):
        super().__init__()
        self.person = person

    def loop(self):
        phone_number = CLI.get_field("phone number", Validation.phone_number)
        try:
            Phone.create(number=phone_number, owner=self.person)
        except IntegrityError:
            phone = Phone.get(Phone.number == phone_number)
            self.next_state = PhoneAlreadyInUse(self.person, phone)
        else:
            print(">> Phone successfully added")
            self.next_state = MainMenu()


class PhoneAlreadyInUse(MainState):
    def __init__(self, person, phone):
        super().__init__()
        self.person = person
        self.phone = phone
        print(">> Number is already in use")
        print("1 - continue, 2 - repeat phone number entry, 0 - main menu")

    def loop(self):
        event = self.read_event()
        if event == '1':
            phone_number = self.phone.number
            self.phone.delete_instance()
            Phone.create(number=phone_number, owner=self.person)
            print(">> Phone successfully added")
            self.next_state = MainMenu()
        elif event == '2':
            self.next_state = CreatePhone(self.person)
        elif event == '0':
            self.person.delete_instance()
            self.next_state = MainMenu()


class UpdateUser(MainState):
    def __init__(self, person):
        super().__init__()
        self.person = person
        print("1 - change birth date, 2 - change phone number, "
              "3 - add new phone number, 0 - main menu")

    def loop(self):
        event = self.read_event()
        if event == '1':
            birth_date = CLI.get_field("birth date", Validation.birth_date)
            self.person.update(birth_date=birth_date)
            print("Date of birth has been successfully changed")
            self.next_state = UpdateUser(self.person)
        elif event == '2':
            pass
        elif event == '3':
            self.next_state = CreatePhone(self.person)
        elif event == '0':
            self.next_state = MainMenu()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Person, Phone])
    print(f"Phonebook by @6a16ec v{version}")
    current = MainMenu()
    while True:
        while current.next_state is None:
            current.loop()
        if current.quit:
            break
        current = current.next_state

# if __name__ == '__main__1':
#     db.connect()
#     db.create_tables([Person, Phone])
#     print(f"Phonebook by @6a16ec v {version}")
#     while True:
#         command = input(f"Enter command >> ")
#         command = normalize(command)
#         if command == '0':
#             first_name, last_name = CLI.get_names()
#             birth_date = CLI.get_field("birth date", Validation.birth_date, may_be_empty=True)
#             try:
#                 if birth_date:
#                     person = Person.create(first_name=first_name, last_name=last_name, birth_date=birth_date)
#                 else:
#                     person = Person.create(first_name=first_name, last_name=last_name)
#                 phone_number = CLI.get_field("phone number", Validation.phone_number)
#                 try:
#                     Phone.create(number=phone_number, owner=person)
#                 except IntegrityError:
#                     phone = Phone.get(Phone.number == phone_number)
#                     print(f"This number belongs to {phone.owner.first_name} {phone.owner.last_name}")
#             except IntegrityError:
#                 person = Person.get(Person.first_name == first_name, Person.last_name == last_name)
#                 print("There's already an entry for this person.")
#                 command = input("1 - change birth date, 2 - change phone number, "
#                                 "3 - add new phone number, enter - main menu")
#                 command = normalize(command)
#                 if command == '1':
#                     birth_date = CLI.get_field("birth date", Validation.birth_date)
#                     person.update(birth_date=birth_date)
#                 elif command == '2':
#                     phone_number
#                     person.update(first_name=first_name, last_name=last_name)
#         # elif command == '1':
#         #     persons = Person.select().execute()
#         #     for person in persons:
#         #         phones = person.phones
#         #         print(f"{person.first_name} {person.last_name} {person.birth_date} ({len(phones)} phones): ")
#         #         for phone in phones:
#         #             print(f"\t{phone.number} {phone.type}")
#         #         phones_amount = len(person.phones)
#         #         print(f"The person was found, he has {phones_amount} numbers.")
#         #
#         #         line = input(f"Press 0 to enter the main menu, enter to add a one new phone number.\n>> ")
#         #         if line == "меню" or line == '0':
#         #             continue
#         #     else:
#         #         person = Person.create(first_name=first_name, last_name=last_name)
#         #     phone_number = CLI.get_field("phone number", Validation.phone_number)
#         #     if phone := CLI.is_phone_exists(phone_number):
#         #         pass
#         #     else:
#         #         Phone.create(number=phone_number, owner=person)
#         # elif string == 'посмотреть все записи' or string == '1':
#         #     data = Person.select().execute()
#         #     for person in data:
#         #         print(f"{person.first_name} {person.last_name}")
#         #
#         # for person in data:
#         #     for phone in person.phones:
#         #         print(f"{person.first_name}\t{person.last_name}\t{phone.number}\t{phone.type}")
#         #     print("!")
