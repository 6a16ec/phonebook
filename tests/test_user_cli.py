from unittest import TestCase
from user_cli import Validation
from user_cli import normalize
from exceptions import *
# from exceptions import
from random import choices
from string import digits
from string import ascii_letters


class TestNameValidation(TestCase):

    def test_001_correct(self):
        Validation.name("Petr")

    def test_002_different_formats(self):
        line = "Petr-Ivan"
        result = Validation.name(line)
        self.assertEqual(line, result)

    def test_003_different_formats(self):
        line = "Tom Petr"
        result = Validation.name(line)
        self.assertEqual(line, result)

    def test_004_different_formats(self):
        line = "Petr 1"
        result = Validation.name(line)
        self.assertEqual(line, result)

    def test_005_paddings(self):
        line = "    John "
        result = Validation.name(line)
        print(result)
        self.assertEqual("John", result)

    def test_006_incorrect(self):
        line = "Sonya!"
        self.assertRaises(SpecialSymbols, Validation.name, line)


class TestNormalize(TestCase):

    def test_001_simple(self):
        line = "John"
        self.assertEqual("John", normalize(line))

    def test_002_one_word(self):
        line = "    John "
        self.assertEqual("John", normalize(line))

    def test_003_one_word_tabs(self):
        line = "        John    "
        self.assertEqual("John", normalize(line))

    def test_005_two_words(self):
        line = "    John    Smith "
        self.assertEqual("John Smith", normalize(line))

    def test_006_three_words(self):
        line = "    John   Senior   Smith "
        self.assertEqual("John Senior Smith", normalize(line))

    def test_007_normalize_date(self):
        line = "    11.11.2011 "
        self.assertEqual("11.11.2011", normalize(line))


class TestPhoneNumberValidation(TestCase):

    def test_001_simple(self):
        line = "89009003030"
        result = Validation.phone_number(line)
        self.assertEqual(line, result)

    def test_002_country_code(self):
        line = "+79009003030"
        result = Validation.phone_number(line)
        self.assertEqual("89009003030", result)

    def test_003_less_eleven_digits(self):
        for i in range(1, 11):
            line = ''.join(choices(digits, k=i))
            self.assertRaises(NotElevenDigits, Validation.phone_number, line)

    def test_004_more_eleven_digits(self):
        for i in range(12, 15):
            line = ''.join(choices(digits, k=i))
            self.assertRaises(NotElevenDigits, Validation.phone_number, line)

    def test_005_not_digits(self):
        line = "Nikita"
        self.assertRaises(NotOnlyDigits, Validation.phone_number, line)


class TestBirthDateValidation(TestCase):

    def test_001_simple(self):
        line = "06.06.1799"
        date = Validation.birth_date(line)
        self.assertEqual(6, date.day)
        self.assertEqual(6, date.month)
        self.assertEqual(1799, date.year)

    def test_002_wrong(self):
        line = "00.00.0000"
        self.assertRaises(NonExistentDate, Validation.birth_date, line)

    def test_003_wrong(self):
        line = ''.join(choices(ascii_letters, k=10))
        self.assertRaises(WrongDateFormat, Validation.birth_date, line)

    def test_004_other(self):
        line = '1.1.2020'
        date = Validation.birth_date(line)
        self.assertEqual(1, date.day)
        self.assertEqual(1, date.month)
        self.assertEqual(2020, date.year)
