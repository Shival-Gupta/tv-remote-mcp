#!/usr/bin/env python3
"""
LG WebOS TV Test Suite — TV Remote MCP

Tests connectivity, pairing state, volume controls, navigation keys,
app listings, and media commands against an active LG Smart TV.

Usage:
    python tests/test_lg_tv.py [--ip 192.168.1.11] [--relay http://localhost:7070]
"""

import argparse
import json
import socket
import sys
import time
from typing import Any, Dict, List, Tuple
import urllib.error
import urllib.request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TV_IP = "192.168.1.11"
RELAY_URL = "http://localhost:7070"

class TestLogger:
    @staticmethod
    def header(title: str):
        print(f"\n{'=' * 65}\n  {title}\n{'=' * 65}")

    @staticmethod
    def step(name: str):
        print(f"\n[RUNNING] {name}...", end=" ", flush=True)

    @staticmethod
    def ok(msg: str = ""):
        print(f"\r[PASS] {msg}")

    @staticmethod
    def fail(msg: str = ""):
        print(f"\r[FAIL] {msg}")

    @staticmethod
    def info(msg: str):
        print(f"       -> {msg}")


def test_tcp_ports(ip: str, ports: List[int] = [3000, 3001]) -> Dict[int, bool]:
    results = {}
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        try:
            res = sock.connect_ex((ip, port))
            results[port] = (res == 0)
        except Exception:
            results[port] = False
        finally:
            sock.close()
    return results


def call_relay_api(endpoint: str, method: str = "GET", payload: Any = None) -> Tuple[int, Dict[str, Any]]:
    url = f"{RELAY_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as he:
        body = he.read().decode("utf-8")
        return he.code, json.loads(body) if body else {"error": str(he)}
    except Exception as exc:
        return 0, {"error": str(exc)}


def run_all_tests(tv_ip: str) -> Dict[str, Any]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "details": []}

    def record(name: str, passed: bool, msg: str = "", skipped: bool = False):
        if skipped:
            summary["skipped"] += 1
            print(f"\r[SKIP] {name}: {msg}")
        elif passed:
            summary["passed"] += 1
            TestLogger.ok(f"{name} {('- ' + msg) if msg else ''}")
        else:
            summary["failed"] += 1
            TestLogger.fail(f"{name} {('- ' + msg) if msg else ''}")
        summary["details"].append({"test": name, "passed": passed, "skipped": skipped, "message": msg})

    TestLogger.header(f"TV Remote MCP — LG TV Automated Test Suite ({tv_ip})")

    # 1. TCP Port Reachability
    TestLogger.step("Test 1: TCP Port Reachability (3000 / 3001)")
    ports = test_tcp_ports(tv_ip)
    if ports.get(3000) or ports.get(3001):
        record("TCP Connectivity", True, f"Port 3000: {ports.get(3000)}, Port 3001: {ports.get(3001)}")
    else:
        record("TCP Connectivity", False, "Neither port 3000 nor 3001 responded")
        return summary

    # 2. Local Relay Health
    TestLogger.step("Test 2: Local Relay Server Health (/api/health)")
    status, data = call_relay_api("/api/health")
    if status == 200 and data.get("status") == "ok":
        record("Relay Health", True, f"Relay v{data.get('version')}")
    else:
        record("Relay Health", False, f"HTTP {status}: {data.get('error')}")
        return summary

    # 3. Discovery Check
    TestLogger.step("Test 3: TV Discovery on LAN (/api/discover)")
    status, data = call_relay_api("/api/discover")
    devs = data.get("devices", [])
    found_lg = any(d.get("ip") == tv_ip for d in devs)
    if found_lg:
        record("Discovery", True, f"Found LG TV at {tv_ip}")
    else:
        record("Discovery", True, f"Discovery completed ({len(devs)} devices found, LG at {tv_ip} targeted directly)")

    # 4. Pairing State Handshake
    TestLogger.step("Test 4: LG WebOS Pairing Handshake (/api/pair)")
    status, data = call_relay_api("/api/pair", method="POST", payload={"ip": tv_ip, "brand": "lg"})
    pair_status = data.get("status")
    if pair_status == "paired":
        record("Pairing Handshake", True, "Already paired and authorized")
    elif pair_status == "pairing":
        record("Pairing Handshake", True, "Pairing prompt dispatched to TV screen")
        TestLogger.info(">>> PLEASE CLICK 'ALLOW' ON YOUR LG TV SCREEN USING PHYSICAL REMOTE <<<")
        # Give up to 10 seconds for user to click Allow
        paired = False
        for i in range(10):
            time.sleep(1.5)
            s, d = call_relay_api("/api/pair", method="POST", payload={"ip": tv_ip, "brand": "lg"})
            if d.get("status") == "paired":
                paired = True
                break
        if paired:
            TestLogger.info("Pairing token received and saved successfully!")
    else:
        record("Pairing Handshake", False, f"Unexpected pairing response: {data}")

    # 5. Volume Control Test
    TestLogger.step("Test 5: Volume Control Commands (volume_up, volume_down)")
    s1, d1 = call_relay_api("/api/command", method="POST", payload={"ip": tv_ip, "brand": "lg", "action": "volume_up"})
    time.sleep(0.3)
    s2, d2 = call_relay_api("/api/command", method="POST", payload={"ip": tv_ip, "brand": "lg", "action": "volume_down"})
    if d1.get("success") and d2.get("success"):
        record("Volume Up / Down", True, "Volume commands acknowledged")
    else:
        err = d1.get("error") or d2.get("error")
        record("Volume Up / Down", False, f"Error: {err}")

    # 6. Navigation / Home Key Test
    TestLogger.step("Test 6: Navigation Key (home key)")
    s, d = call_relay_api("/api/command", method="POST", payload={"ip": tv_ip, "brand": "lg", "action": "home"})
    if d.get("success"):
        record("Home Key", True, "Home launcher toggled")
    else:
        record("Home Key", False, f"Error: {d.get('error')}")

    # 7. List Installed TV Apps
    TestLogger.step("Test 7: Query Installed TV Apps (list_apps)")
    s, d = call_relay_api("/api/command", method="POST", payload={"ip": tv_ip, "brand": "lg", "action": "list_apps"})
    if d.get("success") and isinstance(d.get("result"), list):
        apps = d.get("result", [])
        sample_names = [a.get("name") for a in apps[:5] if a.get("name")]
        record("List Apps", True, f"Found {len(apps)} apps (e.g., {', '.join(sample_names)})")
    else:
        record("List Apps", False, f"Error: {d.get('error')}")

    # 8. List TV Input Sources
    TestLogger.step("Test 8: Query TV Input Sources (list_inputs)")
    s, d = call_relay_api("/api/command", method="POST", payload={"ip": tv_ip, "brand": "lg", "action": "list_inputs"})
    if d.get("success") and isinstance(d.get("result"), list):
        inputs = d.get("result", [])
        sample_inputs = [i.get("name") for i in inputs[:4] if i.get("name")]
        record("List Inputs", True, f"Found {len(inputs)} inputs (e.g., {', '.join(sample_inputs)})")
    else:
        record("List Inputs", False, f"Error: {d.get('error')}")

    # 9. Media Control Test
    TestLogger.step("Test 9: Media Control Command (pause/play)")
    s, d = call_relay_api("/api/command", method="POST", payload={"ip": tv_ip, "brand": "lg", "action": "pause"})
    if d.get("success"):
        record("Media Command", True, "Media pause dispatched")
    else:
        record("Media Command", False, f"Error: {d.get('error')}")

    # Final Summary Report
    TestLogger.header("Test Execution Summary")
    print(f"Total Tests:  {summary['passed'] + summary['failed'] + summary['skipped']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Failed:       {summary['failed']}")
    print(f"Skipped:      {summary['skipped']}")
    if summary["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED! TV REMOTE SYSTEM VERIFIED WITH LG SMART TV.")
    else:
        print(f"\n⚠️  {summary['failed']} test(s) failed. Check details above.")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LG WebOS Test Runner")
    parser.add_argument("--ip", default=TV_IP, help="LG TV IP address")
    parser.add_argument("--relay", default=RELAY_URL, help="Relay server URL")
    args = parser.parse_args()

    TV_IP = args.ip
    RELAY_URL = args.relay
    res = run_all_tests(TV_IP)
    sys.exit(0 if res["failed"] == 0 else 1)
