# NetPilot — Official Updates

Public distribution channel for **NetPilot**, a Windows Telnet CLI tool.

## Install on Windows

1. Download this repository as ZIP (**Code → Download ZIP**).
2. Extract it.
3. Double-click **INSTALL.bat**.
4. Open a new CMD and run `t 10.137.1.19`.

## Commands

- `t IP` — connect to a network switch over Telnet
- `t IP --reset` — change saved device credentials
- `np update` — download and install the latest public update without a GitHub account

Updates are checked when starting Telnet at most once every 24 hours; the program only notifies, never updates without the user's command.

## Privacy and security

The source development repository is private. These **distributed Python files are public** and can be read by anyone. No user credentials or device configurations are published here.

Passwords are saved locally with Windows DPAPI under `%USERPROFILE%\TelnetManager\credentials.json`. Telnet itself sends data in plaintext: use only on trusted management networks.

`version.json` contains Git blob SHA-1 values used to verify that downloaded files match the published manifest. These are integrity checks, **not digital signatures**.

## Current version

**1.2.0** — public update channel without GitHub authentication.
