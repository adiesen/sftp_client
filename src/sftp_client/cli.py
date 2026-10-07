import argparse
import cmd
import getpass
import os
import posixpath
import shlex
import sys

import paramiko


class SFTPConsole(cmd.Cmd):
    intro = "Connected. Type help for a list of commands."
    prompt = "sftp> "

    def __init__(self, sftp):
        super().__init__()
        self.sftp = sftp

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except (OSError, paramiko.SSHException, ValueError) as error:
            print(f"SFTP error: {error}", file=sys.stderr)
            return False

    def emptyline(self):
        pass

    def do_pwd(self, _argument):
        """Show the current remote directory."""
        print(self.sftp.getcwd() or "/")

    def do_ls(self, argument):
        """List a remote directory: ls [path]"""
        path = argument.strip() or "."
        for entry in self.sftp.listdir_attr(path):
            print(entry.filename)

    def do_cd(self, argument):
        """Change the remote directory: cd path"""
        path = argument.strip()
        if not path:
            print("Usage: cd path")
            return
        self.sftp.chdir(path)

    def do_get(self, argument):
        """Download a remote file: get remote_path [local_path]"""
        self._transfer(argument, self.sftp.get, "Usage: get remote_path [local_path]")

    def do_put(self, argument):
        """Upload a local file: put local_path [remote_path]"""
        self._transfer(
            argument, self.sftp.put, "Usage: put local_path [remote_path]", os.path.basename
        )

    def _transfer(self, argument, transfer, usage, basename=posixpath.basename):
        try:
            paths = shlex.split(argument)
        except ValueError as error:
            print(error)
            return
        if not 1 <= len(paths) <= 2:
            print(usage)
            return
        source = paths[0]
        destination = paths[1] if len(paths) == 2 else basename(source)
        transfer(source, destination)
        print(f"Transferred {source} -> {destination}")

    def do_mkdir(self, argument):
        """Create a remote directory: mkdir path"""
        if not argument.strip():
            print("Usage: mkdir path")
            return
        self.sftp.mkdir(argument.strip())

    def do_rm(self, argument):
        """Delete a remote file: rm path"""
        if not argument.strip():
            print("Usage: rm path")
            return
        self.sftp.remove(argument.strip())

    def do_rename(self, argument):
        """Rename a remote file: rename old_path new_path"""
        paths = shlex.split(argument)
        if len(paths) != 2:
            print("Usage: rename old_path new_path")
            return
        self.sftp.rename(*paths)

    def do_exit(self, _argument):
        """Close the connection and exit."""
        return True

    do_quit = do_exit
    do_EOF = do_exit


def build_parser():
    parser = argparse.ArgumentParser(description="Interactive SFTP client")
    parser.add_argument("host", help="SFTP server hostname")
    parser.add_argument("-p", "--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("-u", "--username", help="SSH username (defaults to the local user)")
    parser.add_argument("-i", "--identity-file", help="private key file for public-key authentication")
    parser.add_argument(
        "--password",
        action="store_true",
        help="prompt for a password instead of using public-key authentication",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    password = getpass.getpass("SFTP password: ") if args.password else None
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(
            args.host,
            port=args.port,
            username=args.username,
            password=password,
            key_filename=args.identity_file,
            look_for_keys=not args.password,
            allow_agent=not args.password,
        )
        with client.open_sftp() as sftp:
            SFTPConsole(sftp).cmdloop()
    except (OSError, paramiko.SSHException) as error:
        print(f"SFTP connection failed: {error}", file=sys.stderr)
        return 1
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
