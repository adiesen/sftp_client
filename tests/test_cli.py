import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from sftp_client import cli
from sftp_client.cli import SFTPConsole, build_parser


class SFTPConsoleTests(unittest.TestCase):
    def setUp(self):
        self.sftp = Mock()
        self.console = SFTPConsole(self.sftp)

    def test_get_uses_remote_basename_when_local_path_is_omitted(self):
        self.console.do_get("/remote/report.txt")
        self.sftp.get.assert_called_once_with("/remote/report.txt", "report.txt")

    def test_put_parses_quoted_paths(self):
        self.console.do_put('"local report.txt" "/incoming/report.txt"')
        self.sftp.put.assert_called_once_with("local report.txt", "/incoming/report.txt")

    def test_invalid_transfer_shows_usage_without_transfer(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.console.do_get("")
        self.assertIn("Usage: get", output.getvalue())
        self.sftp.get.assert_not_called()

    def test_parser_defaults_to_standard_ssh_port(self):
        args = build_parser().parse_args(["example.com"])
        self.assertEqual(args.port, 22)
        self.assertIsNone(args.username)

    @patch("sftp_client.cli.paramiko.SSHClient")
    def test_main_loads_known_hosts_and_rejects_unknown_hosts(self, ssh_client):
        client = ssh_client.return_value
        client.open_sftp.return_value.__enter__.return_value = self.sftp

        self.assertEqual(cli.main(["example.com"]), 0)

        client.load_system_host_keys.assert_called_once_with()
        policy = client.set_missing_host_key_policy.call_args.args[0]
        self.assertIsInstance(policy, cli.paramiko.RejectPolicy)
        client.connect.assert_called_once()
        client.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
