# SFTP Client

A small interactive command-line client for transferring files over SFTP.

## Install

Requires Python 3.9 or newer.

```sh
python -m pip install .
```

The `sftp-client` command uses Paramiko and the system SSH known-hosts file.
Unknown server keys are rejected; add and verify a server key through your
usual SSH process before connecting.

## Connect

Authenticate with SSH keys from your agent or default key locations:

```sh
sftp-client example.com --username alice
```

To authenticate with a password, which is entered securely at the prompt:

```sh
sftp-client example.com --username alice --password
```

Use `--identity-file ~/.ssh/id_ed25519` for a specific private key, or `--port`
to select a nonstandard SSH port.

## Commands

At the `sftp>` prompt, use `help` to see available commands. The client supports
`pwd`, `ls`, `cd`, `get`, `put`, `mkdir`, `rm`, `rename`, and `exit`. Quote paths
that contain spaces. `get` downloads to the local current directory by default;
`put` uploads to the remote current directory by default.

## Tests

```sh
python -m unittest discover -s tests
```
