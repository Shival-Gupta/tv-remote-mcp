#!/usr/bin/env python3
"""
TV Remote MCP — Model Context Protocol Server

FastMCP server exposing smart TV controls to AI assistants
(Claude Desktop, Cursor, Antigravity, ChatGPT, etc.).

Usage:
    python mcp-server.py [--host 0.0.0.0] [--port 8000]
"""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional
import urllib.request

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
TOKENS_FILE = ROOT_DIR / "tv-tokens" / "tokens.json"

# Optional protocol libraries
try:
    from pywebostv.connection import WebOSClient
    from pywebostv.controls import ApplicationControl, MediaControl, SystemControl, TvControl
    LG_AVAILABLE = True
except Exception:
    LG_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

HOST = os.environ.get("STV_HOST", "0.0.0.0")
PORT = int(os.environ.get("STV_PORT", "8000"))

lg_client_cache: Dict[str, Any] = {}
samsung_session_cache: Dict[str, str] = {}


def is_port_open(ip: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, OSError):
        return False


def get_lg_client(host: str) -> Optional[Any]:
    if not LG_AVAILABLE:
        return None
    if host in lg_client_cache:
        client = lg_client_cache[host]
        ws = getattr(client, "ws", None)
        if ws and not getattr(ws, "terminated", False) and getattr(ws, "sock", None):
            return client
        lg_client_cache.pop(host, None)

    # Check reachability before attempting WebSocket connection
    p3001 = is_port_open(host, 3001, timeout=1.0)
    p3000 = is_port_open(host, 3000, timeout=0.8) if not p3001 else False
    if not p3001 and not p3000:
        return None

    try:
        if p3001:
            try:
                client = WebOSClient(host, secure=True)
                client.connect()
            except Exception:
                client = WebOSClient(host, secure=False)
                client.connect()
        else:
            client = WebOSClient(host, secure=False)
            client.connect()

        # Load stored pairing token from tokens.json
        store = {}
        if TOKENS_FILE.exists():
            try:
                with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                    store = json.load(f).get(host, {})
            except Exception:
                pass

        for s in client.register(store):
            if s == 2:  # REGISTERED
                try:
                    all_tokens = {}
                    if TOKENS_FILE.exists():
                        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                            all_tokens = json.load(f)
                    all_tokens.setdefault(host, {}).update(store)
                    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                        json.dump(all_tokens, f, indent=2)
                except Exception:
                    pass
                break
        lg_client_cache[host] = client
        return client
    except Exception as exc:
        print(f"[LG TV] Connection failed: {exc}", file=sys.stderr)
        return None


def send_wol(ip: str, mac: Optional[str] = None) -> bool:
    """Send Wake-on-LAN magic packet burst."""
    try:
        target_mac = mac
        if not target_mac:
            tokens_file = ROOT_DIR / "tv-tokens" / "tokens.json"
            if tokens_file.exists():
                with open(tokens_file, "r", encoding="utf-8") as f:
                    tok = json.load(f)
                    target_mac = tok.get(ip, {}).get("mac")
        if not target_mac:
            cmd = ["arp", "-a", ip] if sys.platform.startswith("win") else ["arp", "-n", ip]
            out = subprocess.check_output(cmd, text=True, timeout=1.0)
            m = re.search(r"([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})", out)
            if m:
                target_mac = m.group(0)
        if not target_mac:
            return False
        clean = target_mac.replace(":", "").replace("-", "")
        pkt = b"\xff" * 6 + bytes.fromhex(clean) * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for _ in range(5):
                s.sendto(pkt, ("255.255.255.255", 9))
                s.sendto(pkt, (ip, 9))
                time.sleep(0.02)
        return True
    except Exception:
        return False


def lg_action(host: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
    if action == "power_on":
        ok = send_wol(host)
        return {"success": ok, "message": "Wake-on-LAN packet sent" if ok else "MAC address not found for WoL"}
    client = get_lg_client(host)
    if not client:
        return {"success": False, "error": "Could not connect to LG TV"}
    try:
        sys_ctrl = SystemControl(client)
        app_ctrl = ApplicationControl(client)
        media_ctrl = MediaControl(client)
        tv_ctrl = TvControl(client)

        if action == "power_off":
            sys_ctrl.power_off()
        elif action == "volume_up":
            media_ctrl.volume_up()
        elif action == "volume_down":
            media_ctrl.volume_down()
        elif action == "mute":
            media_ctrl.mute(True)
        elif action == "volume_set" and arg is not None:
            media_ctrl.set_volume(int(arg))
        elif action == "media_play":
            media_ctrl.play()
        elif action == "media_pause":
            media_ctrl.pause()
        elif action == "media_stop":
            media_ctrl.stop()
        elif action == "launch_app" and arg:
            app_ctrl.launch(arg)
        elif action == "list_apps":
            return {"success": True, "apps": app_ctrl.list_apps()}
        elif action == "set_input" and arg:
            tv_ctrl.set_input_source(arg)
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def roku_action(host: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
    key_map = {
        "power_off": "PowerOff",
        "power_on": "PowerOn",
        "volume_up": "VolumeUp",
        "volume_down": "VolumeDown",
        "mute": "VolumeMute",
        "up": "Up",
        "down": "Down",
        "left": "Left",
        "right": "Right",
        "enter": "Select",
        "home": "Home",
        "back": "Back",
        "media_play": "Play",
        "media_pause": "Play",
        "media_stop": "Stop",
    }
    target_key = key_map.get(action, action)
    try:
        url = f"http://{host}:8060/keypress/{target_key}"
        req = urllib.request.Request(url, data=b"", method="POST")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return {"success": resp.status in (200, 204)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def adb_action(host: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
    key_map = {
        "power_off": "26",
        "power_on": "26",
        "volume_up": "24",
        "volume_down": "25",
        "mute": "164",
        "up": "19",
        "down": "20",
        "left": "21",
        "right": "22",
        "enter": "23",
        "home": "3",
        "back": "4",
        "media_play": "126",
        "media_pause": "127",
        "media_stop": "86",
    }
    kc = key_map.get(action)
    if not kc:
        return {"success": False, "error": f"Unsupported ADB action: {action}"}
    try:
        subprocess.run(["adb", "connect", f"{host}:5555"], timeout=3, capture_output=True)
        res = subprocess.run(
            ["adb", "-s", f"{host}:5555", "shell", "input", "keyevent", kc],
            timeout=3,
            capture_output=True,
        )
        return {"success": res.returncode == 0}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def execute_tv_action(host: str, brand: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
    b = (brand or "").lower()
    if b == "lg":
        return lg_action(host, action, arg)
    elif b == "roku":
        return roku_action(host, action, arg)
    elif b in ("android", "fire_tv", "google_tv", "tcl"):
        return adb_action(host, action, arg)
    else:
        # Fallback to relay command endpoint if relay is active
        try:
            req = urllib.request.Request(
                "http://localhost:7070/api/command",
                data=json.dumps({"ip": host, "brand": brand, "action": action, "arg": arg}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            return {"success": False, "error": f"Unsupported brand '{brand}' without relay: {exc}"}


def universal_action(host: str, brand: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
    """Execute a smart TV action across LG, Samsung, Roku, Android TV, Sony, etc.

    Actions include: power_off, power_on, volume_up, volume_down, mute,
    volume_set, up, down, left, right, enter, back, home, media_play,
    media_pause, media_stop, launch_app, list_apps, set_input.
    """
    return execute_tv_action(host, brand, action, arg)


def list_brands() -> List[str]:
    """List all supported smart TV brand identifiers."""
    return ["lg", "samsung", "android", "roku", "fire_tv", "vizio", "sony", "philips", "panasonic", "tcl"]


def discover(network: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scan local network for smart TVs (LG, Samsung, Roku, Android TV, Sony, etc.)."""
    # 1. If local relay is running on port 7070, delegate to its rich scanner
    try:
        req = urllib.request.Request("http://localhost:7070/api/discover", method="GET")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                return data
    except Exception:
        pass

    # 2. Collect known paired devices from tokens.json
    results: List[Dict[str, Any]] = []
    seen: set = set()
    if TOKENS_FILE.exists():
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                toks = json.load(f)
                for ip, info in toks.items():
                    b = "lg" if "client_key" in info else "generic"
                    results.append({
                        "ip": ip,
                        "brand": b,
                        "name": f"Paired {b.upper()} TV ({ip})",
                        "mac": info.get("mac")
                    })
                    seen.add(ip)
        except Exception:
            pass

    # 3. Quick TCP probe of current subnet
    target_prefix = network
    if not target_prefix:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                lip = s.getsockname()[0]
                parts = lip.split(".")
                target_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."
        except Exception:
            target_prefix = "192.168.1."

    ports = [
        (3001, "lg", "LG WebOS TV (SSL)"),
        (3000, "lg", "LG WebOS TV"),
        (8001, "samsung", "Samsung Tizen TV"),
        (8060, "roku", "Roku TV"),
        (5555, "android", "Android TV / Fire TV"),
        (7345, "vizio", "Vizio SmartCast TV"),
        (80, "sony", "Sony Bravia TV")
    ]

    candidates = [f"{target_prefix}{i}" for i in range(1, 31)] + [f"{target_prefix}{i}" for i in range(100, 131)]

    def probe(ip_str: str) -> Optional[Dict[str, Any]]:
        for port, brand, name in ports:
            if is_port_open(ip_str, port, timeout=0.25):
                return {"ip": ip_str, "port": port, "brand": brand, "name": name}
        return None

    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=30) as executor:
            for item in executor.map(probe, candidates):
                if item and item["ip"] not in seen:
                    results.append(item)
                    seen.add(item["ip"])
    except Exception:
        pass

    return results


# FastMCP Tool Registration (if installed)
MCP_AVAILABLE = False
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("universal-smart-tv")
    mcp.tool()(universal_action)
    mcp.tool()(discover)
    mcp.tool()(list_brands)
    MCP_AVAILABLE = True
except ImportError:
    pass


class RestRpcHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if self.path in ("/api/discover", "/discover"):
            self.wfile.write(json.dumps(discover()).encode("utf-8"))
        elif self.path in ("/api/brands", "/brands"):
            self.wfile.write(json.dumps(list_brands()).encode("utf-8"))
        elif self.path in ("/api/health", "/health"):
            self.wfile.write(json.dumps({"status": "ok", "service": "tv-remote-mcp", "fastmcp": MCP_AVAILABLE}).encode("utf-8"))
        else:
            self.wfile.write(json.dumps({"status": "running", "tools": ["universal_action", "discover", "list_brands"]}).encode("utf-8"))

    def do_POST(self):
        if self.path in ("/rpc", "/api/rpc", "/api/command"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body) if body else {}
            action = data.get("action", "")
            if action == "discover":
                result = discover(data.get("network") or data.get("arg"))
            elif action == "list_brands":
                result = list_brands()
            else:
                host = data.get("host") or data.get("ip")
                brand = data.get("brand", "generic")
                arg = data.get("arg")
                result = execute_tv_action(host, brand, action, arg)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        elif self.path in ("/api/discover", "/discover"):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(discover()).encode("utf-8"))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass


def start_rest_bridge(host: str, port: int):
    server = HTTPServer((host, port), RestRpcHandler)
    print(f"[TV Remote MCP] RPC bridge listening on http://{host}:{port}/rpc")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TV Remote MCP Server")
    parser.add_argument("--host", default=HOST, help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=PORT, help="Port (default: 8000)")
    args = parser.parse_args()

    threading.Thread(target=start_rest_bridge, args=(args.host, args.port), daemon=True).start()

    if MCP_AVAILABLE:
        print(f"[TV Remote MCP] FastMCP server initialized. Running...")
        mcp.run()
    else:
        print("[TV Remote MCP] FastMCP package not installed; RPC HTTP bridge active.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nShutting down TV Remote MCP Server.")
