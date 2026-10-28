#!/usr/bin/env python3
"""
Test Suite for TV Remote MCP Server (Phase 2 Validation)
"""

import json
import os
import pathlib
import subprocess
import sys
import threading
import time
import unittest
import urllib.request

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "server"))

import importlib
mcp_server = importlib.import_module("mcp-server")


class TestMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8765
        cls.server_thread = threading.Thread(
            target=mcp_server.start_rest_bridge,
            args=("127.0.0.1", cls.port),
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(0.5)

    def test_01_list_brands(self):
        brands = mcp_server.list_brands()
        self.assertIn("lg", brands)
        self.assertIn("samsung", brands)
        self.assertIn("roku", brands)
        self.assertIn("android", brands)
        self.assertGreaterEqual(len(brands), 8)

    def test_02_rpc_options_cors(self):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/rpc",
            method="OPTIONS"
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")

    def test_03_rpc_unknown_device_offline_fast_fail(self):
        # Probing an offline / non-existent IP must fail fast (not hang 40 seconds)
        start = time.time()
        payload = json.dumps({
            "host": "192.0.2.1",
            "brand": "lg",
            "action": "volume_up"
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/rpc",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - start
            self.assertFalse(data.get("success"))
            self.assertLess(elapsed, 3.5, "Offline check hung for too long")

    def test_04_send_wol_with_explicit_mac(self):
        res = mcp_server.send_wol("192.168.1.11", mac="8c:77:79:67:e6:28")
        self.assertTrue(res)

    def test_05_universal_action_dispatch(self):
        # Testing action execution for roku (returns formatted dict)
        res = mcp_server.execute_tv_action("192.0.2.1", "roku", "volume_up")
        self.assertIn("success", res)


if __name__ == "__main__":
    unittest.main()
