import asyncio
import getpass
import ipaddress
import json
import msvcrt
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import base64
from pathlib import Path

import telnetlib3
import win32crypt

def configure_console_encoding():
    """Prefer UTF-8 for multilingual messages in Windows terminals."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError, TypeError):
                pass


BASE = Path.home() / "TelnetManager"
STORE = BASE / "credentials.json"

# Aliases are separate from encrypted per-IP credentials.
ADDRESS_BOOK = BASE / "devices.json"
RESERVED = {"add", "list", "search", "help", "ping", "backup", "history", "update", "doctor"}

PROTOCOLS = BASE / "device_protocols.json"
SSH_USERS = BASE / "ssh_users.json"
SSH_PASSWORDS = BASE / "ssh_passwords.json"
LAUNCHER_DIR = Path.home() / "bin"
WINDOWS_COMMANDS = {"cmd", "powershell", "pwsh", "explorer", "control", "regedit",
                    "notepad", "calc", "taskmgr", "services", "msconfig", "mstsc",
                    "ping", "ipconfig", "net", "netsh", "ssh", "telnet", "python",
                    "py", "where", "start", "exit", "dir", "copy", "del", "type",
                    "cls", "cd", "t", "s", "np", "rv", "ravlan", "con", "prn", "aux",
                    "nul", "com1", "lpt1"}

def load_devices():
    if not ADDRESS_BOOK.exists():
        return {}
    data = json.loads(ADDRESS_BOOK.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid device address book")
    return data

def load_protocols():
    if not PROTOCOLS.exists():
        return {}
    data = json.loads(PROTOCOLS.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or any(k not in load_devices() or v not in ("telnet", "ssh")
                                           for k, v in data.items()):
        raise ValueError("Invalid device protocols")
    return data

def load_ssh_users():
    if not SSH_USERS.exists():
        return {}
    data = json.loads(SSH_USERS.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid SSH user settings")
    return data

def validate_ssh_user(username):
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", username):
        raise ValueError("Invalid SSH username")
    return username

def edit_ssh_user(alias, username):
    alias = alias.lower()
    if alias not in load_devices():
        raise ValueError(f"Unknown device: {alias}")
    if load_protocols().get(alias, "telnet") != "ssh":
        raise ValueError("SSH username can only be set for SSH devices")
    users = load_ssh_users()
    users[alias] = validate_ssh_user(username)
    _save_json(SSH_USERS, users)
    print(f"SSH login for {alias}: {username}")

def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(path)

def _launcher_path(alias):
    return LAUNCHER_DIR / (alias + ".cmd")

def _check_alias(alias):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,39}", alias):
        raise ValueError("Alias must start with a letter and contain only letters, digits, - or _")
    if alias.lower() in RESERVED | WINDOWS_COMMANDS:
        raise ValueError("Alias conflicts with a Windows or RAVLAN command")
    launcher = _launcher_path(alias.lower())
    if launcher.exists() or any(LAUNCHER_DIR.glob(alias.lower() + ".*")):
        raise ValueError("A command with this name already exists in the RAVLAN launcher folder")
    if shutil.which(alias) or any(shutil.which(alias + ext) for ext in (".cmd", ".bat", ".exe", ".com")):
        raise ValueError("Alias conflicts with an existing command on PATH")
    # Windows Run also resolves executables from the Windows and System32 directories.
    for folder in (Path.home(), Path(__import__("os").environ.get("WINDIR", "C:/Windows")),
                   Path(__import__("os").environ.get("WINDIR", "C:/Windows")) / "System32"):
        if any((folder / (alias + ext)).exists() for ext in (".cmd", ".bat", ".exe", ".com")):
            raise ValueError("Alias conflicts with an existing Windows command")

def _create_launcher(alias, protocol):
    """Generate a fixed launcher: no user-controlled shell arguments."""
    if protocol not in ("telnet", "ssh"):
        raise ValueError("Unsupported protocol")
    launcher = _launcher_path(alias)
    if launcher.exists():
        raise ValueError("Launcher already exists; refusing to overwrite it")
    launcher.parent.mkdir(parents=True, exist_ok=True)
    mode = " --ssh" if protocol == "ssh" else ""
    script = ('@echo off\r\n'
              '"%LOCALAPPDATA%\\NetPilot\\.venv\\Scripts\\python.exe" '
              '"%LOCALAPPDATA%\\NetPilot\\telnet_manager.py"' + mode + ' ' + alias + '\r\n'
              'if errorlevel 1 pause\r\n')
    with launcher.open("x", encoding="ascii", newline="") as handle:
        handle.write(script)
    return launcher

def add_device(alias, ip, protocol="telnet", username=None):
    alias = alias.lower()
    ipaddress.ip_address(ip)
    if protocol not in ("telnet", "ssh"):
        raise ValueError("Protocol must be telnet or ssh")
    if protocol == "ssh":
        username = validate_ssh_user(username or "admin")
    elif username is not None:
        raise ValueError("Username is only supported for SSH")
    devices = load_devices()
    if alias in devices:
        raise ValueError(f"Alias '{alias}' already exists for {devices[alias]}; choose another name")
    _check_alias(alias)
    protocols = load_protocols()
    launcher = _create_launcher(alias, protocol)
    try:
        devices[alias] = ip
        protocols[alias] = protocol
        _save_json(ADDRESS_BOOK, devices)
        _save_json(PROTOCOLS, protocols)
        if protocol == "ssh":
            users = load_ssh_users()
            users[alias] = username
            _save_json(SSH_USERS, users)
    except Exception:
        launcher.unlink(missing_ok=True)
        raise
    print(f"Saved: {alias} -> {ip} ({protocol}). Win+R: {alias}")

def sync_launchers():
    """Safely create launchers for existing aliases after an upgrade."""
    devices = load_devices()
    protocols = load_protocols()
    created = 0
    for alias in devices:
        try:
            _check_alias(alias)
            _create_launcher(alias, protocols.get(alias, "telnet"))
            created += 1
        except (ValueError, OSError) as exc:
            print(f"Skipped launcher {alias}: {exc}")
    print(f"RAVLAN launchers created: {created}")

def list_devices(query=None):
    devices = load_devices()
    matches = [(alias, ip) for alias, ip in sorted(devices.items())
               if not query or query.lower() in alias.lower() or query.lower() in ip]
    if not matches:
        print("No matching devices." if query else "Address book is empty. Add one with: t add office 192.168.1.10")
        return
    print(f"{'ALIAS':<22} IP")
    print("-" * 43)
    for alias, ip in matches:
        print(f"{alias:<22} {ip}")

def resolve_device(target):
    try:
        return str(ipaddress.ip_address(target))
    except ValueError:
        devices = load_devices()
        if target.lower() not in devices:
            raise ValueError(f"Unknown device '{target}'. Use 't list' or 't add NAME IP'.")
        return devices[target.lower()]

PROMPTS = {
    "login": r"(?:login|username|user)\s*:\s*$",
    "password": r"(?:password|passwd)\s*:\s*$",
    "failed": r"(?:login failed|authentication failed|incorrect|access denied|login incorrect)",
    "login_success": r"\[User\]/3/Login the CLI by\s+[^\r\n]+\s+on\s+vty\d+",
    "prompt": r"(?m)^[A-Za-z0-9][A-Za-z0-9_.()/-]{0,119}[>#](?=\s*(?:$|#[0-9]{4}-[0-9]{2}-[0-9]{2}\b))",
}


def load_all():
    if not STORE.exists():
        return {}
    return json.loads(STORE.read_text(encoding="utf-8"))


def save_all(data):
    BASE.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def encrypt(value):
    blob = win32crypt.CryptProtectData(
        value.encode("utf-8"), "NetPilot", None, None, None, 0
    )
    return blob.hex()


def decrypt(value):
    return win32crypt.CryptUnprotectData(
        bytes.fromhex(value), None, None, None, 0
    )[1].decode("utf-8")


def credentials(ip, reset=False):
    data = load_all()
    if reset:
        data.pop(ip, None)
        save_all(data)
    if ip in data:
        try:
            entry = data[ip]
            return {
                "login": entry["login"],
                "password": decrypt(entry["password"]),
                "enable": decrypt(entry["enable"]) if entry.get("enable") else None,
                "use_enable": entry.get("use_enable", False),
                "saved": True,
            }
        except Exception:
            print("Cannot decrypt saved credentials; enter them again.")

    print(f"First connection: {ip}")
    login = input("Login: ").strip()
    password = getpass.getpass("Password: ")
    use_enable = input("Use enable? [y/N]: ").strip().lower() == "y"
    enable_password = (
        getpass.getpass("Enable password (Enter if none): ")
        if use_enable else None
    )
    return {
        "login": login, "password": password, "enable": enable_password,
        "use_enable": use_enable, "saved": False,
    }


def save_credentials(ip, entry):
    data = load_all()
    data[ip] = {
        "login": entry["login"],
        "password": encrypt(entry["password"]),
        "enable": encrypt(entry["enable"]) if entry["enable"] else None,
        "use_enable": entry["use_enable"],
    }
    save_all(data)
    print("\nCredentials saved.")


async def wait_for(reader, patterns, timeout=20):
    buffer = ""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise TimeoutError("Device response timeout")
        chunk = await asyncio.wait_for(reader.read(1), remaining)
        if not chunk:
            raise ConnectionError("Device closed connection")
        print(chunk, end="", flush=True)
        buffer = (buffer + chunk)[-2000:]
        for name, pattern in patterns.items():
            if re.search(pattern, buffer, re.I):
                return name


async def send_line(writer, value):
    writer.write(value + "\r\n")
    await writer.drain()


async def interactive(reader, writer):
    print("\n--- Interactive console ---")
    print("Use 'exit' to leave the switch.\n")

    async def output():
        while True:
            text = await reader.read(1024)
            if not text:
                return
            print(text, end="", flush=True)

    async def keyboard():
        while True:
            char = await asyncio.to_thread(msvcrt.getwch)
            if char in ("\x00", "\xe0"):
                scan = await asyncio.to_thread(msvcrt.getwch)
                keys = {
                    "H": "\x1b[A",
                    "P": "\x1b[B",
                    "M": "\x1b[C",
                    "K": "\x1b[D",
                    "G": "\x1b[H",
                    "O": "\x1b[F",
                    "S": "\x1b[3~",
                }
                sequence = keys.get(scan)
                if sequence:
                    writer.write(sequence)
                    await writer.drain()
                continue
            if char == "\x03":
                return
            if char == "\r":
                writer.write("\r\n")
            elif char == "\x08":
                writer.write("\x08")
            else:
                writer.write(char)
            await writer.drain()

    tasks = [asyncio.create_task(output()), asyncio.create_task(keyboard())]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    for task in done:
        if not task.cancelled():
            task.result()



def check_updates():
    """Best-effort public version notice, cached for 24 hours."""
    root = Path.home() / "AppData" / "Local" / "NetPilot"
    manifest = root / "version.json"
    cache = root / "update-check.json"
    try:
        local = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        cached = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
        if time.time() - cached.get("checked_at", 0) > 86400:
            url = ("https://api.github.com/repos/karen101996/ravlan-releases/contents/version.json"
                   f"?ref=main&nocache={time.time_ns()}")
            request = urllib.request.Request(url, headers={
                "User-Agent": "RAVLAN", "Accept": "application/vnd.github+json"
            })
            with urllib.request.urlopen(request, timeout=3) as response:
                item = json.loads(response.read(65536).decode("utf-8"))
            remote = json.loads(base64.b64decode(item["content"]).decode("utf-8"))["version"]
            cached = {"checked_at": time.time(), "version": remote}
            cache.write_text(json.dumps(cached), encoding="utf-8")
        remote = cached.get("version", local)
        def parts(value):
            return tuple(int(x) for x in value.split("."))
        if parts(remote) > parts(local):
            print(f"\\n[UPDATE] RAVLAN v{remote} available (installed: v{local})")
            print("Run: rv update\\n")
    except (OSError, ValueError, KeyError, TimeoutError):
        pass


async def connect(ip, port=23, reset=False):
    check_updates()
    entry = credentials(ip, reset)
    print(f"\nConnecting to {ip}:{port}...")
    reader, writer = await telnetlib3.open_connection(
        host=ip, port=port, connect_minwait=0.1, connect_maxwait=2,
        encoding="utf8", encoding_errors="replace"
    )
    try:
        result = await wait_for(reader, {
            "login": PROMPTS["login"], "password": PROMPTS["password"],
            "prompt": PROMPTS["prompt"],
        })
        if result == "login":
            await send_line(writer, entry["login"])
            result = await wait_for(reader, {
                "password": PROMPTS["password"], "failed": PROMPTS["failed"],
                "prompt": PROMPTS["prompt"],
            })
        if result == "password":
            await send_line(writer, entry["password"])
            result = await wait_for(reader, {
                "failed": PROMPTS["failed"], "login": PROMPTS["login"],
                "prompt": PROMPTS["prompt"],
                "login_success": PROMPTS["login_success"],
            })
        tp_link_login_event = result == "login_success"
        if tp_link_login_event:
            # The event can arrive before the trailing login-log text is complete.
            # Let the device finish printing before sending privileged commands.
            result = "prompt"
        if result in ("failed", "login"):
            print(f"\nAuthentication failed. Run: t {ip} --reset")
            return
        if result != "prompt":
            raise RuntimeError("Could not confirm login")

        if entry["use_enable"]:
            if tp_link_login_event:
                # TP-Link CLI consumes the first character if enable is sent
                # while its login notification is still being printed.
                await asyncio.sleep(1.0)
            await send_line(writer, "enable")
            result = await wait_for(reader, {
                "password": PROMPTS["password"], "prompt": PROMPTS["prompt"],
                "failed": PROMPTS["failed"],
            })
            if result == "password":
                if entry["enable"] is None:
                    print("\nEnable password not configured.")
                    return
                await send_line(writer, entry["enable"])
                result = await wait_for(reader, {
                    "prompt": PROMPTS["prompt"], "failed": PROMPTS["failed"],
                })
            if result == "failed":
                print("\nEnable authentication failed.")
                return

        if not entry["saved"]:
            save_credentials(ip, entry)
        await send_line(writer, "")
        await interactive(reader, writer)
    finally:
        writer.close()
        await writer.wait_closed()



def ssh_connect(ip, port=22, username=None, reset=False):
    """Connect with a saved, DPAPI-protected SSH password."""
    from ssh_password import connect as password_connect
    username = username or "admin"
    key = f"{username}@{ip}:{port}"
    saved = json.loads(SSH_PASSWORDS.read_text(encoding="utf-8")) if SSH_PASSWORDS.exists() else {}
    if reset and key in saved:
        saved.pop(key)
        _save_json(SSH_PASSWORDS, saved)
        print("Saved SSH password cleared. Enter the new password.")
    password = None
    if key in saved:
        try:
            password = decrypt(saved[key])
        except (ValueError, TypeError, OSError):
            print("Cannot decrypt SSH password; enter it again.")
    if password is None:
        password = getpass.getpass(f"SSH password for {username}@{ip}: ")
    check_updates()
    def save_on_authentication():
        if key not in saved:
            saved[key] = encrypt(password)
            _save_json(SSH_PASSWORDS, saved)
            print("SSH password saved securely.")
    try:
        password_connect(ip, port, username, password, BASE / "ssh_known_hosts",
                         on_authenticated=save_on_authentication)
    except Exception as exc:
        print(f"SSH connection failed: {exc}")
        return


SETTINGS = BASE / "settings.json"
LANGUAGES = ("ru", "en", "uz")
MESSAGES = {
    "ru": {
        "title": "RAVLAN — справка по командам",
        "connection": "Подключение к оборудованию",
        "devices": "Адресная книга и быстрый запуск через Win+R",
        "management": "Управление RAVLAN",
        "telnet": "Telnet по IP или имени устройства",
        "ssh": "SSH по IP или имени устройства",
        "add_t": "Добавить устройство с протоколом Telnet",
        "add_s": "Добавить устройство с протоколом SSH",
        "list": "Показать сохранённые устройства",
        "search": "Найти устройство по имени или IP",
        "reset": "Сбросить сохранённый пароль Telnet",
        "user": "Указать пользователя SSH",
        "winr": "Win+R, затем имя устройства — быстрое подключение",
        "help": "Показать эту справку",
        "language": "Изменить язык интерфейса: ru, en, uz",
        "version": "Показать установленную версию",
        "update": "Проверить и установить обновление",
        "changed": "Язык интерфейса: {language}",
        "invalid": "Неизвестный язык. Доступны: ru, en, uz",
        "usage": "Использование: rv language ru|en|uz",
        "unknown": "Неизвестная команда. Выполните rv help",
    },
    "en": {
        "title": "RAVLAN — command reference",
        "connection": "Connect to network devices",
        "devices": "Address book and quick launch from Win+R",
        "management": "Manage RAVLAN",
        "telnet": "Telnet using an IP address or device alias",
        "ssh": "SSH using an IP address or device alias",
        "add_t": "Add a device using Telnet",
        "add_s": "Add a device using SSH",
        "list": "List saved devices",
        "search": "Search by device name or IP",
        "reset": "Reset saved Telnet credentials",
        "user": "Specify the SSH username",
        "winr": "Win+R, then type the device alias to connect",
        "help": "Show this command reference",
        "language": "Change interface language: ru, en, uz",
        "version": "Show the installed version",
        "update": "Check for and install updates",
        "changed": "Interface language: {language}",
        "invalid": "Unknown language. Available: ru, en, uz",
        "usage": "Usage: rv language ru|en|uz",
        "unknown": "Unknown command. Run rv help",
    },
    "uz": {
        "title": "RAVLAN — buyruqlar bo‘yicha yordam",
        "connection": "Tarmoq qurilmalariga ulanish",
        "devices": "Qurilmalar ro‘yxati va Win+R orqali tezkor ulanish",
        "management": "RAVLAN boshqaruvi",
        "telnet": "IP manzil yoki qurilma nomi orqali Telnet",
        "ssh": "IP manzil yoki qurilma nomi orqali SSH",
        "add_t": "Telnet qurilmasini qo‘shish",
        "add_s": "SSH qurilmasini qo‘shish",
        "list": "Saqlangan qurilmalarni ko‘rsatish",
        "search": "Qurilmani nomi yoki IP bo‘yicha qidirish",
        "reset": "Telnet parolini qayta kiritish",
        "user": "SSH foydalanuvchi nomini ko‘rsatish",
        "winr": "Win+R, so‘ng qurilma nomini kiriting",
        "help": "Buyruqlar bo‘yicha yordam",
        "language": "Interfeys tilini o‘zgartirish: ru, en, uz",
        "version": "O‘rnatilgan versiyani ko‘rsatish",
        "update": "Yangilanishlarni tekshirish va o‘rnatish",
        "changed": "Interfeys tili: {language}",
        "invalid": "Noma’lum til. Mavjud: ru, en, uz",
        "usage": "Foydalanish: rv language ru|en|uz",
        "unknown": "Noma’lum buyruq. rv help buyrug‘ini kiriting",
    },
}

def current_language():
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        return data.get("language", "ru") if data.get("language") in LANGUAGES else "ru"
    except (OSError, ValueError, TypeError):
        return "ru"

def _help_color(text, color):
    """Color only real interactive terminals; keep logs and tests readable."""
    if not getattr(sys.stdout, "isatty", lambda: False)():
        return text
    if sys.platform == "win32":
        try:
            import ctypes
            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if not ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return text
            if not ctypes.windll.kernel32.SetConsoleMode(handle, mode.value | 0x0004):
                return text
        except (AttributeError, OSError):
            return text
    return f"\x1b[{color}m{text}\x1b[0m"


def ravlan_help():
    """A readable, localized terminal dashboard without extra dependencies."""
    m = MESSAGES[current_language()]
    language = current_language()
    title = {"ru": "Справка по командам", "en": "Command reference",
             "uz": "Buyruqlar bo‘yicha yordam"}[language]
    labels = {
        "ru": ("Примеры", "Язык", "Быстрый запуск", "Вводите имя устройства через Win+R"),
        "en": ("Examples", "Language", "Quick launch", "Type a device alias in Win+R"),
        "uz": ("Misollar", "Til", "Tezkor ulanish", "Win+R orqali qurilma nomini kiriting"),
    }
    examples_label, language_label, quick_label, quick_note = labels[language]
    sections = [
        (m["connection"], [
            ("t IP [PORT]", m["telnet"]),
            ("s IP [PORT]", m["ssh"]),
            ("s IP --user LOGIN", m["user"]),
            ("t IP --reset", m["reset"]),
            ("s NAME --reset", m["reset"]),
        ]),
        (m["devices"], [
            ("t add NAME IP", m["add_t"]),
            ("s add NAME IP [LOGIN]", m["add_s"]),
            ("s edit NAME LOGIN", m["user"]),
            ("t list / s list", m["list"]),
            ("t search QUERY", m["search"]),
            ("t NAME / s NAME", m["winr"]),
        ]),
        (m["management"], [
            ("rv help", m["help"]),
            ("rv language ru|en|uz", m["language"]),
            ("rv version", m["version"]),
            ("rv update", m["update"]),
        ]),
        (examples_label, [
            ("t 192.168.1.10", "Telnet"),
            ("s 192.168.88.1", "SSH"),
            ("t add office 192.168.1.10", "office"),
            ("s add router 192.168.88.1 admin", "router"),
            ("Win+R: office", "Telnet"),
            ("Win+R: router", "SSH"),
        ]),
    ]
    width = 94
    inner = width - 4
    command_width = 31
    print()
    print(_help_color("  RAVLAN", "1;36") + "  " + title)
    print("  " + language_label + ": " + language.upper() +
          "    rv language ru|en|uz")
    print(_help_color("╔" + "═" * (width - 2) + "╗", "36"))
    for heading, items in sections:
        print(_help_color("║ ", "36") +
              _help_color(heading.ljust(inner), "1;33") + _help_color(" ║", "36"))
        print(_help_color("╟" + "─" * (width - 2) + "╢", "36"))
        for command, description in items:
            # Truncate only the description, never the actual command.
            available = inner - command_width
            desc = description[:available]
            print(_help_color("║ ", "36") +
                  _help_color(("  " + command).ljust(command_width), "1;36") +
                  desc.ljust(available) + _help_color(" ║", "36"))
        print(_help_color("╟" + "─" * (width - 2) + "╢", "36"))
    print(_help_color("║ ", "36") +
          (quick_label + ": " + quick_note)[:inner].ljust(inner) +
          _help_color(" ║", "36"))
    print(_help_color("╚" + "═" * (width - 2) + "╝", "36"))
    print()


def rv_main(args):
    command = args[0].lower() if args else "help"
    if command in ("help", "-h", "--help") and len(args) <= 1:
        ravlan_help()
    elif command == "language":
        if len(args) != 2:
            print(MESSAGES[current_language()]["usage"])
            return
        language = args[1].lower()
        if language not in LANGUAGES:
            print(MESSAGES[current_language()]["invalid"])
            return
        _save_json(SETTINGS, {"language": language})
        print(MESSAGES[language]["changed"].format(language=language))
    elif command == "version" and len(args) == 1:
        manifest = Path(__import__("os").environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "NetPilot" / "version.json"
        try:
            version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        except (OSError, ValueError, KeyError):
            version = "unknown"
        print("RAVLAN " + str(version))
    else:
        print(MESSAGES[current_language()]["unknown"])

def main():
    args = sys.argv[1:]
    if args and args[0] in ("--rv", "--np"):
        rv_main(args[1:])
        return
    if not args or args[0].lower() in ("help", "--help", "-h"):
        print("RAVLAN: t IP [PORT] [--reset] | s IP [PORT] [--user LOGIN] [--reset] | t/s ALIAS | t/s add NAME IP [LOGIN] | s edit NAME LOGIN | t/s list | t/s search QUERY")
        return
    if args == ["--sync-launchers"]:
        sync_launchers()
        return
    ssh_mode = False
    if args[0] == "--ssh":
        ssh_mode = True
        args = args[1:]
        if not args:
            print("Usage: s IP [PORT] [--user LOGIN] | s ALIAS | s list | s add NAME IP")
            return
    command = args[0].lower()
    try:
        if command == "add":
            if len(args) not in ((3, 4) if ssh_mode else (3,)):
                raise ValueError("Usage: s add NAME IP [LOGIN]" if ssh_mode else "Usage: t add NAME IP")
            add_device(args[1], args[2], "ssh" if ssh_mode else "telnet",
                       args[3] if len(args) == 4 else None)
            return
        if command == "edit" and ssh_mode:
            if len(args) != 3:
                raise ValueError("Usage: s edit NAME LOGIN")
            edit_ssh_user(args[1], args[2])
            return
        if command == "list":
            if len(args) != 1:
                raise ValueError("Usage: t list")
            list_devices()
            return
        if command == "search":
            if len(args) != 2:
                raise ValueError("Usage: t search QUERY")
            list_devices(args[1])
            return
        if command in RESERVED:
            raise ValueError(f"Command '{command}' is not available yet")
        ip = resolve_device(args[0])
        reset = False
        port = 22 if ssh_mode else 23
        username = None
        options = iter(args[1:])
        for arg in options:
            if arg == "--reset":
                if ssh_mode:
                    reset = True
                reset = True
            elif arg == "--user" and ssh_mode:
                username = next(options, None)
                if not username or not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
                    raise ValueError("Usage: s IP --user LOGIN")
            elif arg.isdigit() and 1 <= int(arg) <= 65535:
                port = int(arg)
            else:
                raise ValueError(f"Invalid option: {arg}")
        if ssh_mode:
            username = username or load_ssh_users().get(args[0].lower(), "admin")
            if reset:
                ssh_connect(ip, port, username, reset=True)
            else:
                ssh_connect(ip, port, username)
        else:
            asyncio.run(connect(ip, port, reset))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"RAVLAN: {exc}")
    except KeyboardInterrupt:
        print("\\nDisconnected.")
    except Exception as exc:
        print(f"\\nConnection error: {exc}")


if __name__ == "__main__":
    configure_console_encoding()
    main()
