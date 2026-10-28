#!/usr/bin/env python3
"""
TV Remote MCP — Local Relay Server

Bridges browser-based remote control to smart TV APIs on LAN.
Start: python relay.py [--port 7070] [--host 0.0.0.0]

Supports: LG WebOS, Samsung Tizen, Roku, Android TV, Fire TV,
          Vizio SmartCast, Sony Bravia, Philips, Panasonic
"""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import socketserver
import struct
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# Ensure stdout/stderr handles UTF-8 (emojis and arrows) on all platforms/consoles
for stream in (sys.stdout, sys.stderr):
    if stream and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Optional external dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from pywebostv.connection import WebOSClient
    from pywebostv.controls import (
        ApplicationControl,
        InputControl,
        MediaControl,
        SourceControl,
        SystemControl,
        TvControl,
    )
    HAS_PYWEBOSTV = True
except ImportError:
    HAS_PYWEBOSTV = False

# Global Server Configuration
DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_PORT: int = 7070
DEFAULT_TIMEOUT: float = 3.0
SERVER_VERSION: str = "1.0.0"

# TV Pairing tokens persistence (gitignored in tv-tokens/)
REPO_ROOT: Path = Path(__file__).resolve().parent.parent
TOKENS_DIR: Path = REPO_ROOT / "tv-tokens"
TOKENS_FILE: Path = TOKENS_DIR / "tokens.json"

CACHE_LOCK: threading.Lock = threading.Lock()
CONNECTION_CACHE: Dict[str, Any] = {}
PAIRING_TOKENS: Dict[str, Dict[str, Any]] = {}


def load_pairing_tokens() -> None:
    """Load stored pairing tokens from disk into memory."""
    global PAIRING_TOKENS
    try:
        if TOKENS_FILE.exists():
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                PAIRING_TOKENS = json.load(f)
    except Exception as exc:
        print(f"[WARN] Failed loading tokens: {exc}", file=sys.stderr)


def save_pairing_tokens() -> None:
    """Persist current in-memory pairing tokens to disk."""
    try:
        TOKENS_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(PAIRING_TOKENS, f, indent=2)
    except Exception as exc:
        print(f"[WARN] Failed saving tokens: {exc}", file=sys.stderr)


def log_command(brand: str, ip: str, action: str, success: bool, note: Optional[str] = None) -> None:
    """Log commands to stdout in format: [HH:MM:SS] BRAND IP ACTION → OK/FAIL"""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    b = (brand or "UNKNOWN").upper()
    a = (action or "UNKNOWN").upper()
    status = "OK" if success else (f"FAIL ({note})" if note else "FAIL")
    print(f"[{now}] {b} {ip} {a} → {status}", flush=True)


# ============================================================================
# Network Utilities
# ============================================================================

def get_local_ip() -> str:
    """Detect the host machine's primary LAN IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def send_wol(ip: str) -> bool:
    """Send Wake-on-LAN magic packet using ARP cache lookup for MAC."""
    try:
        cmd = ["arp", "-a", ip] if sys.platform.startswith("win") else ["arp", "-n", ip]
        out = subprocess.check_output(cmd, text=True, timeout=1.0)
        m = re.search(r"([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})", out)
        if not m:
            return False
        mac_bytes = bytes.fromhex(m.group(0).replace(":", "").replace("-", ""))
        packet = b"\xff" * 6 + mac_bytes * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(packet, ("255.255.255.255", 9))
            s.sendto(packet, (ip, 9))
        return True
    except Exception:
        return False


def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Union[bytes, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Tuple[int, bytes]:
    """Unified HTTP request helper with fallback to urllib."""
    h = headers or {}
    b = body.encode("utf-8") if isinstance(body, str) else body
    if HAS_REQUESTS:
        resp = requests.request(method=method, url=url, headers=h, data=b, timeout=timeout)
        return resp.status_code, resp.content
    req = urllib.request.Request(url, data=b, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.status, res.read()


def samsung_ws_send_key(ip: str, key_code: str, port: int = 8001) -> bool:
    """Send Samsung remote key via lightweight WebSocket handshake and frame."""
    b64_name = base64.b64encode(b"TVRemote").decode("utf-8")
    path = f"/api/v2/channels/samsung.remote.control?name={b64_name}"
    ws_key = base64.b64encode(os.urandom(16)).decode("utf-8")
    req = (
        f"GET {path} HTTP/1.1\r\nHost: {ip}:{port}\r\n"
        f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {ws_key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    ).encode("utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(DEFAULT_TIMEOUT)
    try:
        sock.connect((ip, port))
        sock.sendall(req)
        resp = sock.recv(2048).decode("utf-8", errors="ignore")
        if "101" not in resp:
            raise ConnectionError("WebSocket handshake rejected")
        payload = json.dumps({
            "method": "ms.remote.control",
            "params": {"Cmd": "Click", "DataOfCmd": key_code, "Option": "false", "TypeOfRemote": "SendRemoteKey"}
        }).encode("utf-8")
        mask = os.urandom(4)
        header = bytes([0x81, 0x80 | len(payload)]) + mask
        sock.sendall(header + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))
        time.sleep(0.05)
        return True
    finally:
        sock.close()


# ============================================================================
# Brand Protocols
# ============================================================================

class LGWebOSHandler:
    """LG WebOS WebSocket control via pywebostv."""

    @staticmethod
    def _create_connected_client(ip: str) -> Any:
        # Try secure=True first (WebOS 4.0+ uses SSL on port 3001), fallback to secure=False
        try:
            c = WebOSClient(ip, secure=True)
            c.connect()
            return c
        except Exception:
            c = WebOSClient(ip, secure=False)
            c.connect()
            return c

    @classmethod
    def get_client(cls, ip: str) -> Any:
        cache_key = f"lg:{ip}"
        with CACHE_LOCK:
            if cache_key in CONNECTION_CACHE:
                return CONNECTION_CACHE[cache_key]
        if not HAS_PYWEBOSTV:
            raise RuntimeError("pywebostv not installed. Run 'pip install pywebostv'")

        store = PAIRING_TOKENS.setdefault(ip, {})
        client = cls._create_connected_client(ip)
        for status in client.register(store):
            if status == WebOSClient.REGISTERED:
                save_pairing_tokens()
                break
        bundle = {
            "client": client, "media": MediaControl(client), "system": SystemControl(client),
            "app": ApplicationControl(client), "tv": TvControl(client),
            "inp": InputControl(client), "source": SourceControl(client), "mouse": False
        }
        with CACHE_LOCK:
            CONNECTION_CACHE[cache_key] = bundle
        return bundle

    @classmethod
    def pair(cls, ip: str) -> Dict[str, Any]:
        if not HAS_PYWEBOSTV:
            return {"status": "error", "message": "pywebostv not installed"}
        store = PAIRING_TOKENS.setdefault(ip, {})
        try:
            client = cls._create_connected_client(ip)
            reg = client.register(store)
            status = next(reg)
            if status == WebOSClient.PROMPTED:
                def _wait() -> None:
                    try:
                        for s in reg:
                            if s == WebOSClient.REGISTERED:
                                save_pairing_tokens()
                                break
                    except Exception:
                        pass
                threading.Thread(target=_wait, daemon=True).start()
                return {"status": "pairing", "message": "Approve on TV screen"}
            elif status == WebOSClient.REGISTERED:
                save_pairing_tokens()
                return {"status": "paired", "message": "Paired successfully"}
            return {"status": "paired", "message": "Paired successfully"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    @classmethod
    def execute(cls, ip: str, action: str, arg: Any = None) -> Tuple[bool, Any, Optional[str]]:
        if action == "power_on":
            return send_wol(ip), None, None
        try:
            b = cls.get_client(ip)
            if not b["mouse"] and action in ("up", "down", "left", "right", "enter", "back", "home", "menu"):
                try:
                    b["inp"].connect_input()
                    b["mouse"] = True
                except Exception:
                    pass

            # Actions
            if action == "power_off":
                b["system"].power_off()
                with CACHE_LOCK:
                    CONNECTION_CACHE.pop(f"lg:{ip}", None)
            elif action == "volume_up": b["media"].volume_up()
            elif action == "volume_down": b["media"].volume_down()
            elif action == "volume_set": b["media"].set_volume(int(arg or 10))
            elif action == "mute": b["media"].mute(bool(arg) if arg is not None else True)
            elif action == "channel_up": b["tv"].channel_up()
            elif action == "channel_down": b["tv"].channel_down()
            elif action == "up": b["inp"].up()
            elif action == "down": b["inp"].down()
            elif action == "left": b["inp"].left()
            elif action == "right": b["inp"].right()
            elif action == "enter": b["inp"].ok()
            elif action == "back": b["inp"].back()
            elif action == "home": b["inp"].home()
            elif action == "menu": b["inp"].menu()
            elif action == "play": b["media"].play()
            elif action == "pause": b["media"].pause()
            elif action == "stop": b["media"].stop()
            elif action == "rewind": b["media"].rewind()
            elif action == "fast_forward": b["media"].fast_forward()
            elif action == "list_apps":
                def _app_dict(a: Any) -> Dict[str, Any]:
                    d = getattr(a, "data", a) if not isinstance(a, dict) else a
                    aid = d.get("id") if isinstance(d, dict) else getattr(a, "id", str(a))
                    title = d.get("title", aid) if isinstance(d, dict) else getattr(a, "title", str(aid))
                    return {"id": aid, "name": title}
                return True, [_app_dict(a) for a in b["app"].list_apps()], None
            elif action == "launch_app":
                target = str(arg or "")
                apps = b["app"].list_apps()
                def _match_app(a: Any) -> bool:
                    d = getattr(a, "data", a) if not isinstance(a, dict) else a
                    aid = d.get("id", "") if isinstance(d, dict) else getattr(a, "id", "")
                    title = d.get("title", "") if isinstance(d, dict) else getattr(a, "title", "")
                    return aid == target or str(title).lower() == target.lower()
                found = next((a for a in apps if _match_app(a)), None)
                if not found: return False, None, f"App '{arg}' not found"
                b["app"].launch(found)
            elif action == "list_inputs":
                def _src_dict(s: Any) -> Dict[str, Any]:
                    d = getattr(s, "data", s) if not isinstance(s, dict) else s
                    sid = d.get("id") if isinstance(d, dict) else getattr(s, "id", str(s))
                    label = d.get("label", sid) if isinstance(d, dict) else getattr(s, "label", str(sid))
                    return {"id": sid, "name": label}
                return True, [_src_dict(s) for s in b["source"].list_sources()], None
            elif action == "set_input":
                target = str(arg or "")
                srcs = b["source"].list_sources()
                def _match_src(s: Any) -> bool:
                    d = getattr(s, "data", s) if not isinstance(s, dict) else s
                    sid = d.get("id", "") if isinstance(d, dict) else getattr(s, "id", "")
                    label = d.get("label", "") if isinstance(d, dict) else getattr(s, "label", "")
                    return sid == target or str(label).lower() == target.lower()
                found = next((s for s in srcs if _match_src(s)), None)
                if not found: return False, None, f"Input '{arg}' not found"
                b["source"].set_source(found)
            else:
                return False, None, f"Unsupported action: {action}"
            return True, None, None
        except Exception as exc:
            with CACHE_LOCK:
                CONNECTION_CACHE.pop(f"lg:{ip}", None)
            return False, None, str(exc)


class SamsungHandler:
    """Samsung Tizen TV REST & WebSocket control."""
    KEYS: Dict[str, str] = {
        "power_on": "KEY_POWER", "power_off": "KEY_POWER", "volume_up": "KEY_VOLUP",
        "volume_down": "KEY_VOLDOWN", "mute": "KEY_MUTE", "channel_up": "KEY_CHUP",
        "channel_down": "KEY_CHDOWN", "up": "KEY_UP", "down": "KEY_DOWN", "left": "KEY_LEFT",
        "right": "KEY_RIGHT", "enter": "KEY_ENTER", "back": "KEY_RETURN", "home": "KEY_HOME",
        "menu": "KEY_MENU", "play": "KEY_PLAY", "pause": "KEY_PAUSE", "stop": "KEY_STOP",
        "rewind": "KEY_REWIND", "fast_forward": "KEY_FF", "set_input": "KEY_SOURCE"
    }

    @staticmethod
    def pair(ip: str) -> Dict[str, Any]:
        try:
            http_request("GET", f"http://{ip}:8001/api/v2/", timeout=2.0)
            return {"status": "pairing", "message": "Approve remote on TV screen if prompted"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    @classmethod
    def execute(cls, ip: str, action: str, arg: Any = None) -> Tuple[bool, Any, Optional[str]]:
        if action == "power_on": send_wol(ip)
        if action == "list_apps":
            try:
                _, body = http_request("GET", f"http://{ip}:8001/api/v2/applications")
                data = json.loads(body.decode("utf-8")).get("data", [])
                return True, [{"id": a.get("appId"), "name": a.get("name")} for a in data], None
            except Exception as exc:
                return False, None, str(exc)
        if action == "launch_app":
            try:
                http_request("POST", f"http://{ip}:8001/api/v2/applications/{arg}")
                return True, None, None
            except Exception as exc:
                return False, None, str(exc)
        key = cls.KEYS.get(action)
        if not key:
            return False, None, f"Unsupported action: {action}"
        try:
            samsung_ws_send_key(ip, key)
            return True, None, None
        except Exception as exc:
            return False, None, str(exc)


class RokuHandler:
    """Roku External Control Protocol (ECP) over HTTP."""
    KEYS: Dict[str, str] = {
        "power_on": "PowerOn", "power_off": "PowerOff", "volume_up": "VolumeUp",
        "volume_down": "VolumeDown", "mute": "VolumeMute", "channel_up": "ChannelUp",
        "channel_down": "ChannelDown", "up": "Up", "down": "Down", "left": "Left",
        "right": "Right", "enter": "Select", "back": "Back", "home": "Home",
        "menu": "Info", "play": "Play", "pause": "Play", "stop": "Home",
        "rewind": "Rev", "fast_forward": "Fwd"
    }

    @staticmethod
    def pair(ip: str) -> Dict[str, Any]:
        return {"status": "paired", "message": "No pairing required"}

    @classmethod
    def execute(cls, ip: str, action: str, arg: Any = None) -> Tuple[bool, Any, Optional[str]]:
        base = f"http://{ip}:8060"
        if action == "power_on": send_wol(ip)
        if action == "list_apps":
            try:
                _, body = http_request("GET", f"{base}/query/apps")
                root = ET.fromstring(body)
                return True, [{"id": e.attrib.get("id"), "name": e.text} for e in root.findall("app")], None
            except Exception as exc:
                return False, None, str(exc)
        if action == "launch_app":
            try:
                http_request("POST", f"{base}/launch/{arg}")
                return True, None, None
            except Exception as exc:
                return False, None, str(exc)
        if action == "list_inputs":
            return True, [{"id": f"InputHDMI{i}", "name": f"HDMI {i}"} for i in range(1, 5)] + [{"id": "InputTuner", "name": "TV Tuner"}], None
        if action == "set_input":
            inp = str(arg or "InputHDMI1").strip()
            key_name = inp if inp.startswith("Input") else f"Input{inp.upper()}"
            try:
                http_request("POST", f"{base}/keypress/{key_name}")
                return True, None, None
            except Exception as exc:
                return False, None, str(exc)
        key = cls.KEYS.get(action)
        if not key:
            return False, None, f"Unsupported action: {action}"
        try:
            http_request("POST", f"{base}/keypress/{key}")
            return True, None, None
        except Exception as exc:
            return False, None, str(exc)


class AndroidADBHandler:
    """Android TV & Fire TV control via ADB CLI."""
    KEYCODES: Dict[str, int] = {
        "power_on": 224, "power_off": 223, "volume_up": 24, "volume_down": 25,
        "mute": 164, "channel_up": 166, "channel_down": 167, "up": 19, "down": 20,
        "left": 21, "right": 22, "enter": 66, "back": 4, "home": 3, "menu": 82,
        "play": 126, "pause": 127, "stop": 86, "rewind": 89, "fast_forward": 90
    }
    APP_MAP: Dict[str, str] = {
        "netflix": "com.netflix.ninja", "youtube": "com.google.android.youtube.tv",
        "prime": "com.amazon.amazonvideo.livingroom", "disney": "com.disney.disneyplus",
        "spotify": "com.spotify.tv.android", "plex": "com.plexapp.android"
    }

    @classmethod
    def _adb(cls, args: List[str]) -> Tuple[int, str]:
        adb = shutil.which("adb")
        if not adb:
            raise FileNotFoundError("ADB CLI not found in system PATH")
        p = subprocess.run([adb] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=DEFAULT_TIMEOUT)
        return p.returncode, p.stdout + p.stderr

    @classmethod
    def pair(cls, ip: str) -> Dict[str, Any]:
        try:
            _, out = cls._adb(["connect", f"{ip}:5555"])
            return {"status": "paired" if "connected" in out.lower() else "pairing", "message": out.strip()}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    @classmethod
    def execute(cls, ip: str, action: str, arg: Any = None) -> Tuple[bool, Any, Optional[str]]:
        dev = f"{ip}:5555"
        if action == "power_on": send_wol(ip)
        try:
            cls._adb(["connect", dev])
            if action == "volume_set":
                cls._adb(["-s", dev, "shell", "media", "volume", "--stream", "3", "--set", str(arg or 10)])
                return True, None, None
            if action == "list_apps":
                _, out = cls._adb(["-s", dev, "shell", "pm", "list", "packages", "-3"])
                apps = [{"id": l.replace("package:", "").strip(), "name": l.replace("package:", "").strip()} for l in out.splitlines() if l.startswith("package:")]
                return True, apps, None
            if action == "launch_app":
                pkg = cls.APP_MAP.get(str(arg or "").lower(), str(arg or ""))
                cls._adb(["-s", dev, "shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
                return True, None, None
            kc = cls.KEYCODES.get(action)
            if kc is None:
                return False, None, f"Unsupported action: {action}"
            cls._adb(["-s", dev, "shell", "input", "keyevent", str(kc)])
            return True, None, None
        except Exception as exc:
            return False, None, str(exc)


class OtherBrandsHandler:
    """Handlers for Vizio SmartCast, Sony Bravia, Philips JointSpace, Panasonic Viera."""
    VIZIO_KEYS: Dict[str, Tuple[int, int]] = {
        "power_on": (11, 1), "power_off": (11, 2), "volume_up": (5, 0), "volume_down": (5, 1),
        "mute": (5, 2), "channel_up": (8, 0), "channel_down": (8, 1), "up": (11, 8),
        "down": (11, 0), "left": (11, 1), "right": (11, 7), "enter": (11, 2), "back": (11, 4),
        "home": (11, 3), "menu": (11, 48), "play": (4, 3), "pause": (4, 2), "stop": (4, 0),
        "rewind": (4, 0), "fast_forward": (4, 1), "set_input": (11, 5)
    }
    SONY_IRCC: Dict[str, str] = {
        "power_on": "AAAAAQAAAAEAAAAuAw==", "power_off": "AAAAAQAAAAEAAAAvAw==", "volume_up": "AAAAAQAAAAEAAAASAw==",
        "volume_down": "AAAAAQAAAAEAAAATAw==", "mute": "AAAAAQAAAAEAAAAUAw==", "channel_up": "AAAAAQAAAAEAAAAQAw==",
        "channel_down": "AAAAAQAAAAEAAAARAw==", "up": "AAAAAQAAAAEAAAB0Aw==", "down": "AAAAAQAAAAEAAAB1Aw==",
        "left": "AAAAAQAAAAEAAAA0Aw==", "right": "AAAAAQAAAAEAAAAzAw==", "enter": "AAAAAQAAAAEAAABlAw==",
        "back": "AAAAAgAAAJcAAAAjAw==", "home": "AAAAAQAAAAEAAABgAw==", "menu": "AAAAAgAAABoAAABbAw==",
        "play": "AAAAAgAAAJcAAAAaAw==", "pause": "AAAAAgAAAJcAAAAZAw==", "stop": "AAAAAgAAAJcAAAAYAw==",
        "rewind": "AAAAAgAAAJcAAAAbAw==", "fast_forward": "AAAAAgAAAJcAAAAcAw=="
    }
    PHILIPS_KEYS: Dict[str, str] = {
        "power_on": "Standby", "power_off": "Standby", "volume_up": "VolumeUp", "volume_down": "VolumeDown",
        "mute": "Mute", "channel_up": "ChannelStepUp", "channel_down": "ChannelStepDown", "up": "CursorUp",
        "down": "CursorDown", "left": "CursorLeft", "right": "CursorRight", "enter": "Confirm",
        "back": "Back", "home": "Home", "play": "Play", "pause": "Pause", "stop": "Stop"
    }

    @classmethod
    def execute_vizio(cls, ip: str, action: str) -> Tuple[bool, Any, Optional[str]]:
        if action == "power_on": send_wol(ip)
        target = cls.VIZIO_KEYS.get(action)
        if not target: return False, None, f"Unsupported action: {action}"
        body = json.dumps({"KEYLIST": [{"CODESET": target[0], "CODE": target[1], "ACTION": "KEYPRESS"}]})
        for port in (7345, 9000):
            try:
                http_request("PUT", f"http://{ip}:{port}/key_command/", headers={"Content-Type": "application/json"}, body=body)
                return True, None, None
            except Exception:
                continue
        return False, None, "Vizio connection failed"

    @classmethod
    def execute_sony(cls, ip: str, action: str) -> Tuple[bool, Any, Optional[str]]:
        if action == "power_on": send_wol(ip)
        code = cls.SONY_IRCC.get(action)
        if not code: return False, None, f"Unsupported action: {action}"
        soap = (
            '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
            f'<s:Body><u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1"><IRCCCode>{code}</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>'
        )
        try:
            http_request("POST", f"http://{ip}/sony/IRCC", headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPACTION": '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"', "X-Auth-PSK": "0000"}, body=soap)
            return True, None, None
        except Exception as exc:
            return False, None, str(exc)

    @classmethod
    def execute_philips(cls, ip: str, action: str) -> Tuple[bool, Any, Optional[str]]:
        if action == "power_on": send_wol(ip)
        key = cls.PHILIPS_KEYS.get(action)
        if not key: return False, None, f"Unsupported action: {action}"
        try:
            http_request("POST", f"http://{ip}:1925/1/input/key", headers={"Content-Type": "application/json"}, body=json.dumps({"key": key}))
            return True, None, None
        except Exception as exc:
            return False, None, str(exc)


# ============================================================================
# Dispatcher & Device Discovery
# ============================================================================

def normalize_brand(brand: str) -> str:
    b = (brand or "").lower().strip()
    if b in ("lg", "webos", "lgwebos"): return "lg"
    if b in ("samsung", "tizen"): return "samsung"
    if b in ("roku", "rokutv"): return "roku"
    if b in ("android", "androidtv", "firetv", "google_tv", "googletv"): return "android"
    if b in ("vizio", "smartcast"): return "vizio"
    if b in ("sony", "bravia"): return "sony"
    if b in ("philips", "jointspace"): return "philips"
    return b


def execute_command(ip: str, brand: str, action: str, arg: Any = None) -> Tuple[bool, Any, Optional[str]]:
    b = normalize_brand(brand)
    act = action.lower().strip()
    if b == "lg": return LGWebOSHandler.execute(ip, act, arg)
    if b == "samsung": return SamsungHandler.execute(ip, act, arg)
    if b == "roku": return RokuHandler.execute(ip, act, arg)
    if b == "android": return AndroidADBHandler.execute(ip, act, arg)
    if b == "vizio": return OtherBrandsHandler.execute_vizio(ip, act)
    if b == "sony": return OtherBrandsHandler.execute_sony(ip, act)
    if b == "philips": return OtherBrandsHandler.execute_philips(ip, act)
    # Generic fallback
    success, res, err = AndroidADBHandler.execute(ip, act, arg)
    if success: return True, res, None
    return RokuHandler.execute(ip, act, arg)


def execute_pair(ip: str, brand: str) -> Dict[str, Any]:
    b = normalize_brand(brand)
    if b == "lg": return LGWebOSHandler.pair(ip)
    if b == "samsung": return SamsungHandler.pair(ip)
    if b == "roku": return RokuHandler.pair(ip)
    if b == "android": return AndroidADBHandler.pair(ip)
    return {"status": "paired", "message": "Ready to receive commands"}


def discover_devices() -> List[Dict[str, Any]]:
    """Scan pragmatic local network IPs for common smart TV ports."""
    local_ip = get_local_ip()
    parts = local_ip.split(".")
    if len(parts) != 4: return []
    prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."

    candidate_ips = [f"{prefix}{i}" for i in range(1, 31)] + [f"{prefix}{i}" for i in range(100, 151)]
    ports = [(3000, "lg", "LG WebOS TV"), (8001, "samsung", "Samsung Tizen TV"),
             (8060, "roku", "Roku TV"), (5555, "android", "Android TV / Fire TV"),
             (7345, "vizio", "Vizio SmartCast TV"), (80, "sony", "Sony Bravia TV"),
             (1925, "philips", "Philips Smart TV")]

    results: List[Dict[str, Any]] = []
    seen: set = set()

    def check(ip: str, port: int, brand: str, name: str) -> Optional[Dict[str, Any]]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        try:
            if s.connect_ex((ip, port)) != 0: return None
        except Exception:
            return None
        finally:
            s.close()
        # Friendly name probe
        if brand == "roku":
            try:
                _, body = http_request("GET", f"http://{ip}:8060/query/device-info", timeout=1.0)
                root = ET.fromstring(body)
                elem = root.find("user-device-name") or root.find("friendly-device-name") or root.find("model-name")
                if elem is not None and elem.text: name = elem.text.strip()
            except Exception:
                pass
        return {"ip": ip, "port": port, "brand": brand, "name": name}

    with ThreadPoolExecutor(max_workers=50) as ex:
        futs = [ex.submit(check, ip, p, b, n) for ip in candidate_ips for p, b, n in ports]
        for f in as_completed(futs):
            r = f.result()
            if r and (r["ip"], r["brand"]) not in seen:
                seen.add((r["ip"], r["brand"]))
                results.append(r)
    return results


# ============================================================================
# HTTP Server & CLI
# ============================================================================

class RelayHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """CORS-enabled REST API handler for remote control."""

    def send_cors_headers(self, status: int = 200, ctype: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", ctype)
        self.end_headers()

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/health":
            self.send_cors_headers(200)
            self.wfile.write(json.dumps({"status": "ok", "version": SERVER_VERSION}).encode("utf-8"))
            return
        if path == "/api/discover":
            self.send_cors_headers(200)
            self.wfile.write(json.dumps({"devices": discover_devices()}).encode("utf-8"))
            return

        # Serve static web assets directly from repository root
        clean_path = path.lstrip("/")
        if not clean_path:
            file_path = REPO_ROOT / "index.html"
        elif clean_path in ("remote", "remote/"):
            file_path = REPO_ROOT / "remote" / "index.html"
        elif clean_path in ("docs", "docs/"):
            file_path = REPO_ROOT / "docs" / "index.html"
        else:
            file_path = (REPO_ROOT / clean_path).resolve()
            if not str(file_path).startswith(str(REPO_ROOT)):
                self.send_cors_headers(403)
                self.wfile.write(b"Forbidden")
                return
            if file_path.is_dir():
                file_path = file_path / "index.html"

        if file_path.is_file():
            ext = file_path.suffix.lower()
            content_types = {
                ".html": "text/html; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".json": "application/json; charset=utf-8",
                ".svg": "image/svg+xml",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".md": "text/markdown; charset=utf-8",
            }
            ctype = content_types.get(ext, "application/octet-stream")
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_cors_headers(200, ctype)
                self.wfile.write(content)
                return
            except Exception as exc:
                self.send_cors_headers(500)
                self.wfile.write(str(exc).encode("utf-8"))
                return

        self.send_cors_headers(404)
        self.wfile.write(json.dumps({"error": f"Path '{path}' not found"}).encode("utf-8"))

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
        except Exception:
            self.send_cors_headers(200)
            self.wfile.write(json.dumps({"success": False, "error": "Invalid JSON"}).encode("utf-8"))
            return

        if path == "/api/command":
            ip, brand, action, arg = data.get("ip", "").strip(), data.get("brand", "").strip(), data.get("action", "").strip(), data.get("arg")
            if not ip or not brand or not action:
                self.send_cors_headers(200)
                log_command(brand, ip, action, False, "Missing fields")
                self.wfile.write(json.dumps({"success": False, "error": "Missing ip, brand, or action"}).encode("utf-8"))
                return
            success, res, err = execute_command(ip, brand, action, arg)
            log_command(brand, ip, action, success, err)
            self.send_cors_headers(200)
            self.wfile.write(json.dumps({"success": success, "result": res} if success else {"success": False, "error": err or "Failed"}).encode("utf-8"))
            return

        if path == "/api/pair":
            ip, brand = data.get("ip", "").strip(), data.get("brand", "").strip()
            if not ip or not brand:
                self.send_cors_headers(200)
                self.wfile.write(json.dumps({"status": "error", "message": "Missing ip or brand"}).encode("utf-8"))
                return
            self.send_cors_headers(200)
            self.wfile.write(json.dumps(execute_pair(ip, brand)).encode("utf-8"))
            return

        self.send_cors_headers(404)
        self.wfile.write(json.dumps({"error": f"Path '{path}' not found"}).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def print_banner(host: str, port: int, local_ip: str) -> None:
    banner = f"""
==================================================================
  📺 TV Remote MCP — Local Relay Server v{SERVER_VERSION}
==================================================================
  Web Remote:   http://localhost:{port}/remote/
  Phone Remote: http://{local_ip}:{port}/remote/
  API Health:   http://localhost:{port}/api/health
  Listening:    {host}:{port}

  API Endpoints:
    GET  /remote/         → Browser Remote UI (Zero Mixed-Content)
    GET  /api/health      → Server health status
    GET  /api/discover    → Smart TV local discovery
    POST /api/command     → Send command (power, volume, d-pad, apps)
    POST /api/pair        → Initiate pairing (LG WebOS, Samsung, etc.)
==================================================================
  Ready for remote control connections. Press Ctrl+C to stop.
"""
    print(banner.strip(), flush=True)


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TV Remote MCP Local Relay Server")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help=f"Host to bind (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to listen (default: {DEFAULT_PORT})")
    return parser.parse_args()


def main() -> None:
    args = parse_cli_args()
    load_pairing_tokens()
    local_ip = get_local_ip()

    try:
        httpd = ThreadedHTTPServer((args.host, args.port), RelayHTTPRequestHandler)
    except OSError as err:
        print(f"[FATAL] Binding failed on {args.host}:{args.port} - {err}", file=sys.stderr)
        sys.exit(1)

    print_banner(args.host, args.port, local_ip)

    def handle_shutdown(signum: int, frame: Any) -> None:
        print("\n[INFO] Shutting down relay server gracefully...", flush=True)
        threading.Thread(target=httpd.shutdown).start()

    signal.signal(signal.SIGINT, handle_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        save_pairing_tokens()
        print("[INFO] Server stopped. Goodbye!", flush=True)


if __name__ == "__main__":
    main()
