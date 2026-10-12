"""Password-based SSH with DPAPI storage and interactive Windows console."""
import getpass
import hashlib
import msvcrt
import socket
import sys
import time

import paramiko


class ConfirmHostKey(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        fingerprint = ":".join(f"{b:02x}" for b in hashlib.sha256(key.asbytes()).digest())
        print(f"Unknown SSH host key for {hostname} ({key.get_name()}).")
        print(f"SHA256 fingerprint: {fingerprint}")
        if input("Trust and save this host key? [y/N]: ").strip().lower() != "y":
            raise paramiko.SSHException("Host key not trusted")
        client.get_host_keys().add(hostname, key.get_name(), key)
        client.save_host_keys(str(self.known_hosts))

    def __init__(self, known_hosts):
        self.known_hosts = known_hosts


def connect(ip, port, username, password, known_hosts, on_authenticated=None):
    client = paramiko.SSHClient()
    known_hosts.parent.mkdir(parents=True, exist_ok=True)
    if known_hosts.exists():
        client.load_host_keys(str(known_hosts))
    client.set_missing_host_key_policy(ConfirmHostKey(known_hosts))
    try:
        client.connect(ip, port=port, username=username, password=password,
                       look_for_keys=False, allow_agent=False, timeout=12,
                       auth_timeout=12, banner_timeout=12)
        if on_authenticated is not None:
            on_authenticated()
        channel = client.invoke_shell(term="xterm", width=120, height=36)
        channel.settimeout(0.0)
        print("Connected. Press Ctrl+C to disconnect.")
        while not channel.closed and not channel.exit_status_ready():
            try:
                if channel.recv_ready():
                    data = channel.recv(65535)
                    if not data:
                        break
                    sys.stdout.write(data.decode("utf-8", errors="replace"))
                    sys.stdout.flush()
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ("\x00", "\xe0"):
                        msvcrt.getwch()
                    else:
                        channel.send("\r" if key == "\r" else key.encode("utf-8"))
                time.sleep(0.015)
            except (socket.timeout, BlockingIOError):
                continue
    finally:
        client.close()
