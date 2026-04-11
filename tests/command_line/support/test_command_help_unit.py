"""
Unit tests for daf.command_line.support.command_help module
"""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestShellColors(unittest.TestCase):
    def test_shell_colors_defined(self):
        """Test that ShellColors class has expected color attributes"""
        from daf.command_line.support.command_help import ShellColors

        self.assertEqual(ShellColors.NO_COLOR, "\033[39;49m")
        self.assertEqual(ShellColors.BLACK, "\033[30m")
        self.assertEqual(ShellColors.RED, "\033[31m")
        self.assertEqual(ShellColors.GREEN, "\033[32m")
        self.assertEqual(ShellColors.YELLOW, "\033[33m")
        self.assertEqual(ShellColors.BLUE, "\033[34m")
        self.assertEqual(ShellColors.PURPLE, "\033[35m")
        self.assertEqual(ShellColors.CYAN, "\033[36m")
        self.assertEqual(ShellColors.WHITE, "\033[37m")

    def test_shell_colors_are_strings(self):
        """Test that ShellColors values are strings"""
        from daf.command_line.support.command_help import ShellColors

        for attr in dir(ShellColors):
            if not attr.startswith("_"):
                value = getattr(ShellColors, attr)
                self.assertIsInstance(value, str)


class TestCommandHelp(unittest.TestCase):
    def test_command_help_desc_defined(self):
        """Test that CommandHelp has DESC attribute"""
        from daf.command_line.support.command_help import CommandHelp

        self.assertTrue(hasattr(CommandHelp, "DESC"))
        self.assertIsInstance(CommandHelp.DESC, str)

    def test_command_help_epi_defined(self):
        """Test that CommandHelp has EPI attribute"""
        from daf.command_line.support.command_help import CommandHelp

        self.assertTrue(hasattr(CommandHelp, "EPI"))
        self.assertIsInstance(CommandHelp.EPI, str)

    def test_print_all_commands_exists(self):
        """Test that print_all_commands is a static method"""
        from daf.command_line.support.command_help import CommandHelp

        self.assertTrue(callable(CommandHelp.print_all_commands))

    def test_print_all_commands_outputs_content(self):
        """Test that print_all_commands produces expected output"""
        from daf.command_line.support.command_help import CommandHelp

        # Capture stdout
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            CommandHelp.print_all_commands()

        output = f.getvalue()

        # Should contain section headers and command names
        self.assertIn("SUPPORT", output)
        self.assertIn("GUIs", output)
        self.assertIn("CONFIGURE THE EXPERIMENT", output)
        self.assertIn("QUERY INFORMATION", output)
        self.assertIn("MOVE MOTORS", output)
        self.assertIn("SCANS", output)

    def test_print_all_commands_contains_init(self):
        """Test that print_all_commands includes daf.init"""
        from daf.command_line.support.command_help import CommandHelp

        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            CommandHelp.print_all_commands()

        output = f.getvalue()
        self.assertIn("daf.init", output)

    def test_print_all_commands_contains_status(self):
        """Test that print_all_commands includes daf.status"""
        from daf.command_line.support.command_help import CommandHelp

        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            CommandHelp.print_all_commands()

        output = f.getvalue()
        self.assertIn("daf.status", output)

    def test_print_all_commands_contains_scan(self):
        """Test that print_all_commands includes scan commands"""
        from daf.command_line.support.command_help import CommandHelp

        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            CommandHelp.print_all_commands()

        output = f.getvalue()
        self.assertIn("daf.scan", output)


class TestCommandHelpWithMocks(unittest.TestCase):
    def test_command_help_instantiation(self):
        """Test that CommandHelp can be instantiated with mocked DAFIO"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            with patch.object(sys, "argv", ["daf.help"]):
                from daf.command_line.support.command_help import CommandHelp

                # Should not raise
                help_cmd = CommandHelp()
                self.assertIsNotNone(help_cmd)

    def test_run_cmd_calls_print_all_commands(self):
        """Test that run_cmd calls print_all_commands"""
        with patch("daf.command_line.support.support_utils.du.DAFIO"):
            with patch.object(sys, "argv", ["daf.help"]):
                with patch(
                    "daf.command_line.support.command_help.CommandHelp.print_all_commands"
                ) as mock_print:
                    from daf.command_line.support.command_help import CommandHelp

                    help_cmd = CommandHelp()
                    help_cmd.run_cmd()

                    mock_print.assert_called_once()


if __name__ == "__main__":
    unittest.main()
