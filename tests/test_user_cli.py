from unittest import TestCase
from user_cli import Validation
from exceptions import SpecialSymbols


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
