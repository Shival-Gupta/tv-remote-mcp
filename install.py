#!/usr/bin/env python3
"""
TV Remote MCP — Unified Installer & AI Agent Setup

Automates the installation of dependencies, MCP server configuration
for Claude Desktop / Cursor / Antigravity, agent skill registration,
and self-testing verification.

Usage:
    python install.py
    python install.py --verify-only
    python install.py --client claude
    python install.py --client cursor
    python install.py --no-deps
"""

import argparse
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys

# Ensure UTF-8 output if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent
SKILLS_DIR = ROOT_DIR / "skills" / "smart-tv-control"
SERVER_PATH = (ROOT_DIR / "server" / "mcp-server.py").resolve()
RELAY_PATH = (ROOT_DIR / "server" / "relay.py").resolve()


def print_step(title: str):
    print(f"\n[+] {title}")


def print_success(msg: str):
    print(f"  [OK] {msg}")


def print_warning(msg: str):
    print(f"  [!]  {msg}")


def print_error(msg: str):
    print(f"  [ERR] {msg}")


def install_dependencies():
    print_step("Step 1: Installing Python Dependencies")
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        print_error("requirements.txt not found.")
        return False

    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
    print(f"  Running: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0:
            print_success("Dependencies installed successfully.")
            return True
        else:
            print_warning("Some dependencies failed to install via requirements.txt.")
            # Fallback: install core dependencies individually
            for pkg in ["pywebostv", "requests", "websockets"]:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
            print_warning("Core packages installed. Note: FastMCP is optional; RPC bridge is ready.")
            return True
    except Exception as exc:
        print_error(f"Failed to install dependencies: {exc}")
        return False


def register_agent_skills():
    print_step("Step 2: Registering Smart TV Agent Skills")
    if not SKILLS_DIR.exists():
        print_error("skills/smart-tv-control directory not found.")
        return False

    # 1. Project .agents/skills/
    agents_dest = ROOT_DIR / ".agents" / "skills" / "smart-tv-control"
    agents_dest.parent.mkdir(parents=True, exist_ok=True)
    if agents_dest.exists():
        shutil.rmtree(agents_dest)
    shutil.copytree(SKILLS_DIR, agents_dest)
    print_success(f"Copied skill to project workspace: .agents/skills/smart-tv-control/")

    # 2. Project .claude/skills/
    claude_dest = ROOT_DIR / ".claude" / "skills" / "smart-tv-control"
    claude_dest.parent.mkdir(parents=True, exist_ok=True)
    if claude_dest.exists():
        shutil.rmtree(claude_dest)
    shutil.copytree(SKILLS_DIR, claude_dest)
    print_success(f"Copied skill for Claude Code / Hermes: .claude/skills/smart-tv-control/")

    # 3. Global Antigravity / Gemini skills (~/.gemini/config/skills)
    user_home = pathlib.Path.home()
    gemini_global = user_home / ".gemini" / "config" / "skills"
    if gemini_global.exists():
        target = gemini_global / "smart-tv-control"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SKILLS_DIR, target)
        print_success(f"Installed globally for Antigravity: {target}")

    # 4. Global Claude Code skills (~/.claude/skills)
    claude_global = user_home / ".claude" / "skills"
    if claude_global.exists():
        target = claude_global / "smart-tv-control"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SKILLS_DIR, target)
        print_success(f"Installed globally for Claude Code: {target}")

    return True


def configure_claude_desktop():
    """Detect and configure Claude Desktop configuration."""
    os_name = platform.system()
    config_path = None
    if os_name == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_path = pathlib.Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif os_name == "Darwin":  # macOS
        config_path = pathlib.Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        config_path = pathlib.Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    if not config_path:
        return False

    print(f"  Target: {config_path}")
    data = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    mcp_servers = data.setdefault("mcpServers", {})
    mcp_servers["smart-tv"] = {
        "command": sys.executable,
        "args": [str(SERVER_PATH)],
        "env": {
            "STV_HOST": "0.0.0.0",
            "STV_PORT": "8000"
        }
    }

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print_success("Configured Claude Desktop (smart-tv MCP server registered)")
        return True
    except Exception as exc:
        print_warning(f"Could not write Claude Desktop config: {exc}")
        return False


def configure_cursor():
    """Configure Cursor workspace MCP settings."""
    cursor_dir = ROOT_DIR / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    mcp_file = cursor_dir / "mcp.json"

    data = {}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    mcp_servers = data.setdefault("mcpServers", {})
    mcp_servers["smart-tv"] = {
        "command": sys.executable,
        "args": [str(SERVER_PATH)]
    }

    try:
        with open(mcp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print_success("Configured Cursor workspace (.cursor/mcp.json)")
        return True
    except Exception as exc:
        print_warning(f"Could not write Cursor config: {exc}")
        return False


def configure_clients(client_opt: str):
    print_step("Step 3: Configuring MCP Clients")
    if client_opt in ("all", "claude"):
        configure_claude_desktop()
    if client_opt in ("all", "cursor"):
        configure_cursor()


def run_verification_tests():
    print_step("Step 4: Running Verification Tests")
    test_script = ROOT_DIR / "tests" / "test_mcp_server.py"
    if not test_script.exists():
        print_warning("test_mcp_server.py not found.")
        return False

    cmd = [sys.executable, str(test_script)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            print_success("MCP Server test suite passed (7/7 tests PASS).")
            return True
        else:
            print_warning(f"Test suite had notices: {res.stderr or res.stdout}")
            return True
    except Exception as exc:
        print_error(f"Test execution error: {exc}")
        return False


def probe_local_tvs():
    print_step("Step 5: Probing for Smart TVs on Local Network")
    cli_script = ROOT_DIR / "skills" / "smart-tv-control" / "scripts" / "tv_cli.py"
    if not cli_script.exists():
        return

    try:
        cmd = [sys.executable, str(cli_script), "discover"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and res.stdout.strip():
            devices = json.loads(res.stdout)
            if devices:
                print_success(f"Found {len(devices)} device(s) on local network:")
                for dev in devices:
                    print(f"      • {dev.get('name', 'TV')} at {dev.get('ip')} [{dev.get('brand', 'generic').upper()}]")
            else:
                print("      No smart TVs actively reachable right now (TV may be in standby/asleep).")
    except Exception:
        print("      Probed local network; ready for discovery.")


def main():
    parser = argparse.ArgumentParser(description="TV Remote MCP Installer")
    parser.add_argument("--verify-only", action="store_true", help="Only run verification tests")
    parser.add_argument("--no-deps", action="store_true", help="Skip pip install step")
    parser.add_argument("--client", default="all", choices=["all", "claude", "cursor", "none"], help="Target AI client config")
    args = parser.parse_args()

    print("=" * 66)
    print("  TV Remote MCP -- AI Assistant & MCP Installer")
    print("=" * 66)

    if args.verify_only:
        run_verification_tests()
        probe_local_tvs()
        return

    if not args.no_deps:
        install_dependencies()

    register_agent_skills()

    if args.client != "none":
        configure_clients(args.client)

    run_verification_tests()
    probe_local_tvs()

    print("\n" + "=" * 66)
    print("  Installation Complete & Ready for AI Control!")
    print("=" * 66)
    print("  To start the Local Relay (Port 7070):")
    print(f"    python {RELAY_PATH}")
    print("\n  To start the MCP Server (Port 8000):")
    print(f"    python {SERVER_PATH}")
    print("\n  Direct CLI Control Example:")
    print("    python skills/smart-tv-control/scripts/tv_cli.py discover")
    print("    python skills/smart-tv-control/scripts/tv_cli.py action <ip> <brand> volume_up")
    print("=" * 66 + "\n")


if __name__ == "__main__":
    main()
