class MyException(Exception):
    def __init__(self):
        self.type = 'input error'
        self.message = ''

    def print(self):
        print(f"[{self.type}]: {self.message}")


class SpecialSymbols(MyException):
    def __init__(self):
        super().__init__()
        self.message = "Do not use special characters"


class NotOnlyDigits(MyException):
    def __init__(self):
        super().__init__()
        self.message = "When entering, use only numbers"


class NotElevenDigits(MyException):
    def __init__(self, count):
        super().__init__()
        self.message = f'The phone number consists of 11 digits, you entered: {count}'


class EmptyInput(MyException):
    def __init__(self):
        super().__init__()
        self.message = "Empty input, please, try again"


class WrongDateFormat(MyException):
    def __init__(self):
        super().__init__()
        self.message = "You entered the date in the wrong format, the correct format: dd.mm.yyyy"


class NonExistentDate(MyException):
    def __init__(self):
        super().__init__()
        self.message = "You entered a non-existent date"
        self.type = "logic error"