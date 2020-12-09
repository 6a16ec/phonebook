from config import version
from re import findall
from re import sub
from re import fullmatch
from exceptions import *
from database import Person
from database import Phone
from peewee import DoesNotExist
from config import db
from peewee import IntegrityError
from datetime import datetime
from datetime import date


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

    @staticmethod
    @normalize_input
    def short_birth_date(line):
        line = sub(r'[\\/-]', '.', line)
        if result := fullmatch(r'[\d]{1,2}[.][\d]{1,2}', line):
            string = result.string
            day, month = map(int, string.split('.'))
            try:
                date = datetime(2020, month, day)
                return date
            except ValueError:
                raise NonExistentDate
        else:
            raise WrongDateFormat

    @staticmethod
    @normalize_input
    def phone_type(line):
        result = fullmatch(r'.+', line)
        return result.string

    @staticmethod
    @normalize_input
    def age(line):
        result = fullmatch(r'\d*', line)
        try:
            return int(result.string)
        except:
            raise NotOnlyDigits

    @staticmethod
    @normalize_input
    def age_symbol(line):
        result = fullmatch(r'[<>=]', line)
        if result:
            return result.string




class CLI:
    @staticmethod
    def get_field(name, validation, may_be_empty=False):
        result = None
        while result is None:
            try:
                welcome_line = f'Enter {name} >> ' if not may_be_empty else f'Enter {name} (press enter to skip) >> '
                line = input(welcome_line)
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
        print()
        print('[<< - M A I N  -  M E N U - >>]')
        print('1 - new contact, 2 - show all, 3 - search in phonebook, 4 - delete contact')
        print('5 - age of person, 6 - change contact, 7 - delete by number')
        print('8 - find by date, 9 - b-day soon, 10 - find by age')
        print('13 - quit')

    def loop(self):
        event = self.read_event()
        if event == '1':
            self.next_state = AddNewContact()
        elif event == '2':
            persons = Person.select().execute()
            for i, person in enumerate(persons):
                print(f'{i + 1}.', person)
            self.next_state = MainMenu()
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
        elif event == '4':
            first_name = CLI.get_field("first name", Validation.name)
            last_name = CLI.get_field("last name", Validation.name)
            try:
                person = Person.get(Person.first_name == first_name, Person.last_name == last_name)
            except DoesNotExist:
                print("There is no such contact")
            else:
                person.delete_instance(recursive=True)
                print("This contact has been successfully removed")
            self.next_state = MainMenu()
        elif event == '5':
            first_name = CLI.get_field("first name", Validation.name)
            last_name = CLI.get_field("last name", Validation.name)
            try:
                person = Person.get(Person.first_name == first_name, Person.last_name == last_name)
            except DoesNotExist:
                print('>> Person does not exist')
                self.next_state = MainMenu()
            else:
                birth_date = person.birth_date
                if birth_date is not None:
                    age = int((date.today() - birth_date).total_seconds() / 60 / 60 / 24 / 365)
                    print(f'>> Age: {age}')
                else:
                    print('>> Date of Birth is not specified')
                self.next_state = MainMenu()
        elif event == '6':
            first_name = CLI.get_field("first name", Validation.name)
            last_name = CLI.get_field("last name", Validation.name)
            try:
                person = Person.get(Person.first_name == first_name, Person.last_name == last_name)
            except DoesNotExist:
                print('>> Person does not exist')
                self.next_state = MainMenu()
            else:
                self.next_state = UpdateUser(person)
        elif event == '7':
            phone_number = CLI.get_field("phone number", Validation.phone_number)
            person = Person.select().join(Phone).where(Phone.number == phone_number)
            person = person[0] if person else None
            if person:
                person.delete_instance()
                print('>> Deleted')
            else:
                print('>> Records with this number were not found')
            self.next_state = MainMenu()

        elif event == '8':
            short_birth_date = CLI.get_field("short birth date (dd.mm)", Validation.short_birth_date)
            persons = Person.select().where(
                Person.birth_date.day == short_birth_date.day,
                Person.birth_date.month == short_birth_date.month
            )
            if persons:
                for person in persons:
                    print(person)
            else:
                print('>> People with such dates of birth are not found')
            self.next_state = MainMenu()

        elif event == '9':
            count = 0
            today = date.today()
            persons = Person.select()
            for person in persons:
                birth_date = person.birth_date
                if birth_date:
                    birth_date = date(today.year, birth_date.month, birth_date.day)
                    delta = birth_date - date.today()
                    if delta.days < 0:
                        birth_date = date(today.year + 1, birth_date.month, birth_date.day)
                        delta = birth_date - date.today()
                    if delta.days <= 30:
                        print(person)
                        count += 1
            if count == 0:
                print('>> No one has a birthday in the next month.')
            self.next_state = MainMenu()

        elif event == '10':
            input_age = CLI.get_field("step_age", Validation.age)
            print('>> Enter < or > or =')
            symbol = CLI.get_field("symbol", Validation.age_symbol)
            today = date.today()
            persons = Person.select()
            for person in persons:
                birth_date = person.birth_date
                if birth_date:
                    person_age = (today.year - birth_date.year)
                    if birth_date.month > today.month or (birth_date.month == today.month and birth_date.day >= today.day):
                        person_age += 1
                    if (person_age < input_age and symbol == '<') or (person_age == input_age and symbol == '=') or \
                            (person_age > input_age and symbol == '>'):
                        print(person)
                        print(f"Age: {person_age}")
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
                person.birth_date = birth_date
                person.save()
            print(">> Person successfully added")
            self.next_state = CreatePhone(person, phone_type="default")


class CreatePhone(MainState):
    def __init__(self, person, phone_type=None):
        super().__init__()
        self.person = person
        self.phone_type = phone_type

    def loop(self):
        phone_number = CLI.get_field("phone number", Validation.phone_number)
        self.next_state = AddNewPhone(self.person, phone_number, self.phone_type)


class AddNewPhone(MainState):
    def __init__(self, person, phone_number, phone_type):
        super().__init__()
        self.person = person
        self.phone_number = phone_number
        self.phone_type = phone_type

    def loop(self):
        phone_number = self.phone_number
        phone_type = self.phone_type
        if phone_type is None:
            phone_type = CLI.get_field("phone type", Validation.phone_type)
        try:
            Phone.create(number=phone_number, owner=self.person, type=phone_type)
        except IntegrityError:
            try:
                phone = Phone.get(Phone.number == phone_number)
            except DoesNotExist:
                print(">> Busy phone type for this user")
                self.phone_type = None
            else:
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
        print("1 - change personal data, 2 - change phone number, "
              "3 - add new phone number, 0 - main menu")

    def loop(self):
        event = self.read_event()
        if event == '1':
            first_name = CLI.get_field("first name", Validation.name, may_be_empty=True)
            last_name = CLI.get_field("last name", Validation.name, may_be_empty=True)
            birth_date = CLI.get_field("birth date", Validation.birth_date, may_be_empty=True)
            if first_name is not None:
                self.person.first_name = first_name
            if last_name is not None:
                self.person.last_name = last_name
            if birth_date is not None:
                self.person.birth_date = birth_date
            if first_name or last_name or birth_date:
                self.person.save()
                print(">> Personal data has been successfully changed")
            else:
                print(">> You have not entered any fields to change")
            self.next_state = MainMenu()
        elif event == '2':
            for phone in self.person.phones:
                if phone.type == 'default':
                    phone.delete_instance()
            self.next_state = CreatePhone(self.person, phone_type='default')
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
