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
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional
import urllib.request

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


def get_lg_client(host: str) -> Optional[Any]:
    if not LG_AVAILABLE:
        return None
    if host not in lg_client_cache:
        try:
            client = WebOSClient(host)
            client.connect()
            store = {}
            for s in client.register(store):
                if s == 2:
                    print(f"[LG TV] Pairing prompted on {host} - approve on screen")
                elif s == 3:
                    print(f"[LG TV] Paired with {host}")
            lg_client_cache[host] = client
        except Exception as exc:
            print(f"[LG TV] Connection failed: {exc}", file=sys.stderr)
            return None
    return lg_client_cache.get(host)


def lg_action(host: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
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


# FastMCP Tool Registration (if installed)
MCP_AVAILABLE = False
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("universal-smart-tv")

    @mcp.tool()
    def universal_action(host: str, brand: str, action: str, arg: Optional[str] = None) -> Dict[str, Any]:
        """Execute a smart TV action across LG, Samsung, Roku, Android TV, Sony, etc.

        Actions include: power_off, power_on, volume_up, volume_down, mute,
        volume_set, up, down, left, right, enter, back, home, media_play,
        media_pause, media_stop, launch_app, list_apps, set_input.
        """
        return execute_tv_action(host, brand, action, arg)

    @mcp.tool()
    def list_brands() -> List[str]:
        """List all supported smart TV brand identifiers."""
        return ["lg", "samsung", "android", "roku", "fire_tv", "vizio", "sony", "philips", "panasonic", "tcl"]

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

    def do_POST(self):
        if self.path == "/rpc":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body) if body else {}
            host = data.get("host") or data.get("ip")
            brand = data.get("brand", "generic")
            action = data.get("action", "")
            arg = data.get("arg")
            result = execute_tv_action(host, brand, action, arg)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
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
