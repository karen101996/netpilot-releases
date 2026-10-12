<div align="center">

# NetPilot

### Fast Telnet access for Windows network administrators

**Connect to network devices in one command. Save time on repetitive logins. Keep credentials on your PC.**

[![Windows](https://img.shields.io/badge/Windows-10%20%2F%2011-0078D4?logo=windows&logoColor=white)](https://github.com/karen101996/netpilot-releases)
[![Latest version](https://img.shields.io/badge/version-1.2.5-2563eb)](version.json)
[![Update channel](https://img.shields.io/badge/updates-GitHub%20API-24292f?logo=github)](https://github.com/karen101996/netpilot-releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

[**Download ZIP**](https://github.com/karen101996/netpilot-releases/archive/refs/heads/main.zip) · [**Quick start**](#quick-start) · [**Commands**](#commands) · [**Русский**](#на-русском)

</div>

---

## What is NetPilot?

**NetPilot** is a lightweight Windows command-line utility for connecting to switches, OLTs and other Telnet-enabled network devices. Instead of opening a separate client and repeatedly entering credentials, connect directly from **CMD** or **Windows Terminal**:

```bat
t 192.168.1.10
```

On the first connection, NetPilot asks for the username and password and can remember them **locally, encrypted with Windows DPAPI**. On subsequent connections, it reuses the saved credentials for that IP address.

### Highlights

| Feature | What it does |
| :--- | :--- |
| **One-command access** | Connect using `t IP`, without opening a separate Telnet application |
| **Per-device credentials** | Remember a different username and password for each IP address |
| **Windows DPAPI encryption** | Encrypt saved passwords for the current Windows user |
| **Enable mode support** | Optionally authenticate to privileged mode on supported devices |
| **Interactive terminal** | Work with the device CLI directly in the console |
| **Simple updates** | Install newer versions with `np update` |
| **Update notifications** | Check for a newer release when connecting, at most once every 24 hours |
| **No GitHub login required** | Install and update from this public repository |

> [!NOTE]
> NetPilot is a **Telnet** client, not an SSH client. Device login prompts and CLI behavior vary between vendors; compatibility with every model is not guaranteed.

## Quick start

### Requirements

- **Windows 10 or Windows 11**
- Network access to the device's **Telnet port (usually TCP 23)**
- Internet access during initial installation to download Python/dependencies, if they are not already available
- Python **3.10+** (the installer looks for a supported Python installation and can install Python 3.13 using `winget`)

### Install

1. **[Download NetPilot as ZIP](https://github.com/karen101996/netpilot-releases/archive/refs/heads/main.zip)**.
2. Extract the ZIP to any folder.
3. Double-click **`INSTALL.bat`** and follow the installer output.
4. Open a **new CMD / Windows Terminal** window.
5. Connect to your device:

   ```bat
   t 192.168.1.10
   ```

The installer creates a local Python environment under `%LOCALAPPDATA%\NetPilot`, adds a command launcher under `%USERPROFILE%\bin`, and updates your user `PATH` if necessary. **Administrator privileges are not normally required**, though Python installation and certain legacy launchers may require additional permissions.

### First connection

```text
C:\> t 192.168.1.10

First connection: 192.168.1.10
Login: admin
Password:
Use enable? [y/N]: n

Connecting to 192.168.1.10:23...
...
--- Interactive console ---
```

After a successful login, credentials can be saved for that IP address. Later connections can reuse them.

## Commands

| Command | Description |
| :--- | :--- |
| `t 192.168.1.10` | Connect to a device on port 23 |
| `t 192.168.1.10 2323` | Connect using a custom Telnet port |
| `t 192.168.1.10 --reset` | Remove the saved credentials for this IP and enter them again |
| `np update` | Check for and install the latest version |

### Updates

When you start a Telnet connection, NetPilot checks for a new version **no more than once every 24 hours**. If an update is available, it prints a notice and continues connecting normally.

```text
[UPDATE] NetPilot v1.2.5 available (installed: v1.2.4)
Run: np update

Connecting to 192.168.1.10:23...
```

To update manually:

```bat
np update
```

The updater uses the **public GitHub API**, so end users do **not** need GitHub CLI, an account, or an access token. Downloaded files are checked against the Git blob hashes listed in [`version.json`](version.json) before installation. Existing saved credentials are kept.

> [!IMPORTANT]
> Hash comparison checks file integrity against the published manifest; it is **not a cryptographic release signature**. Review scripts before executing them if required by your organization's security policy.

## Security & privacy

- **Local credential storage:** `%USERPROFILE%\TelnetManager\credentials.json`
- **Encryption:** Windows DPAPI; encrypted secrets are bound to the relevant Windows user context.
- **No credential sync:** NetPilot does not upload stored usernames or passwords to GitHub.
- **Update requests:** GitHub receives standard network requests when NetPilot checks for or downloads updates.
- **Transport security:** **Telnet is unencrypted.** DPAPI protects passwords *at rest*, **not** while they travel over Telnet. Use NetPilot only on trusted, isolated management networks. Prefer SSH where supported.

The distribution scripts in this repository are public and readable. The development repository is separate.

## Troubleshooting

<details>
<summary><strong>`t` or `np` is not recognized</strong></summary>

Open a **new** CMD window after installation. Check:

```bat
where t
where np
```

The installer places the launchers in `%USERPROFILE%\bin`. If an older `t.bat` appears first, check whether it forwards to `%USERPROFILE%\bin\t.cmd`.

</details>

<details>
<summary><strong>Connection fails or times out</strong></summary>

Check the IP address, network routing, firewall, and whether the device has Telnet enabled on the selected port. NetPilot does not enable Telnet on the device.

</details>

<details>
<summary><strong>Need to change a saved password</strong></summary>

Run `t DEVICE_IP --reset` to enter fresh credentials for that device.

</details>

<details>
<summary><strong>An update is available, but no notification appears</strong></summary>

Update checks are cached for up to 24 hours. You can always run `np update` to check manually.

</details>

---

## На русском

**NetPilot** — небольшая утилита для Windows, позволяющая подключаться к коммутаторам, OLT и другому сетевому оборудованию по Telnet прямо из CMD или Windows Terminal.

**Возможности:** команда `t IP`, сохранение логинов и паролей отдельно для каждого IP, локальное шифрование паролей через Windows DPAPI, поддержка `enable`, интерактивная консоль и обновления через `np update`.

**Установка:**

1. [Скачать ZIP](https://github.com/karen101996/netpilot-releases/archive/refs/heads/main.zip) и распаковать.
2. Запустить **`INSTALL.bat`**.
3. Открыть **новое** окно CMD.
4. Ввести `t 192.168.1.10` и при первом подключении указать данные авторизации.

**Основные команды:**

```bat
t 192.168.1.10           REM Подключиться по Telnet
t 192.168.1.10 2323      REM Подключиться к другому порту
t 192.168.1.10 --reset   REM Сбросить сохранённые данные для IP
np update                REM Проверить и установить обновление
```

При наличии новой версии NetPilot показывает уведомление **перед подключением**, но не прерывает работу с оборудованием. Обновление запускается только по команде пользователя.

> **Безопасность:** пароли в файле на компьютере зашифрованы, но **сам протокол Telnet не шифрует трафик**. Используйте только в доверенных сетях управления. Для оборудования с SSH предпочтительнее SSH.

---

<div align="center">

**Built for network administrators who prefer a fast, simple CLI.**

[Download](https://github.com/karen101996/netpilot-releases/archive/refs/heads/main.zip) · [Report an issue](https://github.com/karen101996/netpilot-releases/issues) · [Version manifest](version.json)

</div>
