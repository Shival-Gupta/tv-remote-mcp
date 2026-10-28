#!/usr/bin/env python3
"""
Smart TV CLI Helper Script — TV Remote MCP Skill

Allows agents and users to execute smart TV commands directly from the shell.
Tries MCP RPC bridge (port 8000), Relay API (port 7070), or standalone python engine.

Usage:
    python tv_cli.py discover
    python tv_cli.py brands
    python tv_cli.py action <ip> <brand> <action> [<arg>]
    python tv_cli.py power_on <ip> [<mac>]
    python tv_cli.py power_off <ip> <brand>
    python tv_cli.py launch <ip> <brand> <app_name_or_id>
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SERVER_DIR = PROJECT_ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


def try_mcp_rpc(payload: dict) -> dict:
    """Attempt execution via MCP server HTTP bridge on port 8000."""
    try:
        req = urllib.request.Request(
            "http://localhost:8000/rpc",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def try_relay_api(endpoint: str, payload: dict = None, method: str = "GET") -> dict:
    """Attempt execution via Local Relay server on port 7070."""
    try:
        url = f"http://localhost:7070{endpoint}"
        data = json.dumps(payload).encode("utf-8") if payload else None
        headers = {"Content-Type": "application/json"} if payload else {}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def execute_standalone(action: str, host: str = None, brand: str = None, arg: str = None):
    """Fallback to direct python execution via server/mcp-server.py."""
    import importlib
    mcp_mod = importlib.import_module("mcp-server")
    if action == "discover":
        return mcp_mod.discover()
    elif action == "brands":
        return mcp_mod.list_brands()
    elif action == "power_on":
        return {"success": mcp_mod.send_wol(host, mac=arg)}
    else:
        return mcp_mod.execute_tv_action(host, brand, action, arg)


def cmd_discover(args):
    # Try relay first
    res = try_relay_api("/api/discover")
    if res is None:
        res = try_mcp_rpc({"action": "discover", "network": args.network})
    if res is None:
        res = execute_standalone("discover")
    print(json.dumps(res, indent=2))


def cmd_brands(args):
    res = try_relay_api("/api/brands")
    if res is None:
        res = try_mcp_rpc({"action": "list_brands"})
    if res is None:
        res = execute_standalone("brands")
    print(json.dumps(res, indent=2))


def cmd_action(args):
    payload = {
        "host": args.ip,
        "brand": args.brand,
        "action": args.action,
        "arg": args.arg
    }
    res = try_mcp_rpc(payload)
    if res is None:
        res = try_relay_api("/api/command", {"ip": args.ip, "brand": args.brand, "action": args.action, "arg": args.arg}, method="POST")
    if res is None:
        res = execute_standalone(args.action, host=args.ip, brand=args.brand, arg=args.arg)
    print(json.dumps(res, indent=2))


def cmd_power_on(args):
    payload = {
        "host": args.ip,
        "brand": "generic",
        "action": "power_on",
        "arg": args.mac
    }
    res = try_mcp_rpc(payload)
    if res is None:
        res = try_relay_api("/api/command", {"ip": args.ip, "brand": "generic", "action": "power_on", "mac": args.mac}, method="POST")
    if res is None:
        res = execute_standalone("power_on", host=args.ip, arg=args.mac)
    print(json.dumps(res, indent=2))


def cmd_power_off(args):
    args.action = "power_off"
    args.arg = None
    cmd_action(args)


def cmd_launch(args):
    args.action = "launch_app"
    args.arg = args.app
    cmd_action(args)


def main():
    parser = argparse.ArgumentParser(description="Smart TV CLI Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Discover
    p_disc = subparsers.add_parser("discover", help="Scan local network for smart TVs")
    p_disc.add_argument("--network", help="Subnet prefix (e.g. 192.168.1.)", default=None)
    p_disc.set_defaults(func=cmd_discover)

    # Brands
    p_brands = subparsers.add_parser("brands", help="List supported TV brands")
    p_brands.set_defaults(func=cmd_brands)

    # Action
    p_act = subparsers.add_parser("action", help="Send command to TV")
    p_act.add_argument("ip", help="TV IP address")
    p_act.add_argument("brand", help="TV brand (lg, samsung, roku, android, sony, etc.)")
    p_act.add_argument("action", help="Action (volume_up, volume_down, mute, enter, back, home, etc.)")
    p_act.add_argument("arg", nargs="?", default=None, help="Optional argument (e.g. volume level, app id)")
    p_act.set_defaults(func=cmd_action)

    # Power On
    p_pon = subparsers.add_parser("power_on", help="Wake TV via Wake-on-LAN")
    p_pon.add_argument("ip", help="TV IP address")
    p_pon.add_argument("mac", nargs="?", default=None, help="TV MAC address (optional if paired)")
    p_pon.set_defaults(func=cmd_power_on)

    # Power Off
    p_poff = subparsers.add_parser("power_off", help="Turn off TV")
    p_poff.add_argument("ip", help="TV IP address")
    p_poff.add_argument("brand", help="TV brand")
    p_poff.set_defaults(func=cmd_power_off)

    # Launch App
    p_app = subparsers.add_parser("launch", help="Launch app on TV")
    p_app.add_argument("ip", help="TV IP address")
    p_app.add_argument("brand", help="TV brand")
    p_app.add_argument("app", help="App ID or package name (youtube, netflix, etc.)")
    p_app.set_defaults(func=cmd_launch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
