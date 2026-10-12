import asyncio
import getpass
import ipaddress
import json
import msvcrt
import re
import sys
import time
import urllib.request
import base64
from pathlib import Path

import telnetlib3
import win32crypt

BASE = Path.home() / "TelnetManager"
STORE = BASE / "credentials.json"
PROMPTS = {
    "login": r"(?:login|username)\s*:\s*$",
    "password": r"(?:password|passwd)\s*:\s*$",
    "failed": r"(?:login failed|authentication failed|incorrect|access denied|login incorrect)",
    "prompt": r"(?m)^[^\r\n]{1,120}[>#]\s*$",
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
                await asyncio.to_thread(msvcrt.getwch)
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
            url = "https://api.github.com/repos/karen101996/netpilot-releases/contents/version.json"
            request = urllib.request.Request(url, headers={
                "User-Agent": "NetPilot", "Accept": "application/vnd.github+json"
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
            print(f"\\n[UPDATE] NetPilot v{remote} available (installed: v{local})")
            print("Run: np update\\n")
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
            })
        if result in ("failed", "login"):
            print(f"\nAuthentication failed. Run: t {ip} --reset")
            return
        if result != "prompt":
            raise RuntimeError("Could not confirm login")

        if entry["use_enable"]:
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


def main():
    if len(sys.argv) < 2:
        print("Usage: t IP [PORT] [--reset]")
        return
    ip = sys.argv[1]
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print("Invalid IP address.")
        return
    reset = "--reset" in sys.argv
    port = 23
    for arg in sys.argv[2:]:
        if arg.isdigit():
            port = int(arg)
    if not 1 <= port <= 65535:
        print("Invalid port.")
        return
    try:
        asyncio.run(connect(ip, port, reset))
    except KeyboardInterrupt:
        print("\nDisconnected.")
    except Exception as exc:
        print(f"\nConnection error: {exc}")


if __name__ == "__main__":
    main()
