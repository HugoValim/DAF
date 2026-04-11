"""
Unit tests for daf.utils.print_utils module
"""
import unittest
from daf.utils.print_utils import TablePrinter, format_5_decimals


class TestTablePrinter(unittest.TestCase):

    def test_table_printer_initialization(self):
        """Test TablePrinter initialization with format"""
        fmt = [
            ("Name", "name", 10),
            ("Age", "age", 5),
        ]
        printer = TablePrinter(fmt)

        self.assertIsNotNone(printer.fmt)
        self.assertEqual(printer.head["name"], "Name")
        self.assertEqual(printer.head["age"], "Age")

    def test_table_printer_row_formatting(self):
        """Test row formatting with data"""
        fmt = [
            ("Name", "name", 10),
            ("Age", "age", 5),
        ]
        printer = TablePrinter(fmt)

        data = {"name": "John", "age": 30}
        row = printer.row(data)

        self.assertIn("John", row)
        self.assertIn("30", row)

    def test_table_printer_row_truncation(self):
        """Test that long values are truncated to column width"""
        fmt = [
            ("Name", "name", 5),
        ]
        printer = TablePrinter(fmt)

        data = {"name": "VeryLongName"}
        row = printer.row(data)

        # Should be truncated to 5 characters
        self.assertEqual(len(row.strip()), 5)

    def test_table_printer_missing_key(self):
        """Test row formatting with missing key returns empty"""
        fmt = [
            ("Name", "name", 10),
            ("Age", "age", 5),
        ]
        printer = TablePrinter(fmt)

        data = {"name": "John"}  # Missing 'age'
        row = printer.row(data)

        self.assertIn("John", row)

    def test_table_printer_call(self):
        """Test TablePrinter callable returns formatted string"""
        fmt = [
            ("Name", "name", 10),
        ]
        printer = TablePrinter(fmt)

        data_list = [{"name": "John"}, {"name": "Jane"}]
        result = printer(data_list)

        self.assertIsInstance(result, str)
        self.assertIn("John", result)
        self.assertIn("Jane", result)

    def test_table_printer_with_separator(self):
        """Test TablePrinter with custom separator"""
        fmt = [
            ("Name", "name", 10),
            ("Age", "age", 5),
        ]
        printer = TablePrinter(fmt, sep=" | ")

        data = {"name": "John", "age": 30}
        row = printer.row(data)

        self.assertIn("|", row)

    def test_table_printer_with_underline(self):
        """Test TablePrinter with underline"""
        fmt = [
            ("Name", "name", 10),
        ]
        printer = TablePrinter(fmt, ul="-")

        data_list = [{"name": "John"}]
        result = printer(data_list)

        self.assertIn("-", result)

    def test_table_printer_head_insertion(self):
        """Test that header row is inserted"""
        fmt = [
            ("Name", "name", 10),
        ]
        printer = TablePrinter(fmt)

        data_list = [{"name": "John"}]
        result = printer(data_list)

        lines = result.split("\n")
        self.assertEqual(len(lines), 2)  # Header + data


class TestFormat5Decimals(unittest.TestCase):

    def test_format_integer(self):
        """Test formatting integer"""
        result = format_5_decimals(42)
        self.assertEqual(result, "42.00000")

    def test_format_float(self):
        """Test formatting float"""
        result = format_5_decimals(3.14159)
        self.assertEqual(result, "3.14159")

    def test_format_string_number(self):
        """Test formatting string number"""
        result = format_5_decimals("2.5")
        self.assertEqual(result, "2.50000")

    def test_format_zero(self):
        """Test formatting zero"""
        result = format_5_decimals(0)
        self.assertEqual(result, "0.00000")

    def test_format_negative(self):
        """Test formatting negative number"""
        result = format_5_decimals(-5.5)
        self.assertEqual(result, "-5.50000")


if __name__ == '__main__':
    unittest.main()
