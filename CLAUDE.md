# CLAUDE.md — Agent Guidelines & Setup Instructions

Welcome, AI Assistant! This repository contains **TV Remote MCP**, a universal smart TV controller and Model Context Protocol (MCP) server for LG WebOS, Samsung Tizen, Roku, Android/Google TV, Fire TV, Sony Bravia, and Vizio TVs.

---

## ⚡ 1-Step Installation for AI Agents

When the user asks you to **install, configure, or test** this repository (e.g., *"Install this https://github.com/Shival-Gupta/tv-remote-mcp"*), execute:

```bash
python install.py
```

`install.py` will automatically:
1. Install Python dependencies (`pywebostv`, `requests`, `websockets`, `fastmcp`).
2. Register the `smart-tv` MCP server in Claude Desktop config (`claude_desktop_config.json`) and Cursor (`.cursor/mcp.json`).
3. Install and register the `smart-tv-control` skill in `.claude/skills/` and `.agents/skills/`.
4. Run the automated test suite (`tests/test_mcp_server.py`) to verify functionality.
5. Probe the local network and report any detected smart TVs.

---

## 🎮 How to Control Smart TVs

### Method A: Use the Agent Skill
Read and follow [`skills/smart-tv-control/SKILL.md`](skills/smart-tv-control/SKILL.md) (or `.claude/skills/smart-tv-control/SKILL.md`).

### Method B: Fast CLI Script (No server process required)
You can directly run commands using the included CLI helper:
```bash
# Scan local Wi-Fi for TVs
python skills/smart-tv-control/scripts/tv_cli.py discover

# Wake up TV via Wake-on-LAN
python skills/smart-tv-control/scripts/tv_cli.py power_on <ip>

# Adjust volume or navigate
python skills/smart-tv-control/scripts/tv_cli.py action <ip> <brand> volume_up
python skills/smart-tv-control/scripts/tv_cli.py action <ip> <brand> enter
python skills/smart-tv-control/scripts/tv_cli.py action <ip> <brand> home

# Launch streaming apps
python skills/smart-tv-control/scripts/tv_cli.py launch <ip> <brand> youtube
```

### Method C: FastMCP Tool Calling
When the MCP server is mounted, invoke:
- `universal_action(host="192.168.1.11", brand="lg", action="volume_up")`
- `discover()`
- `list_brands()`

---

## 🧪 Testing and Verification

To verify that the MCP server and control endpoints are working properly:
```bash
python tests/test_mcp_server.py
```

---

## 🔒 Security Guidelines
- Never commit pairing tokens, MAC addresses, or keys in `tv-tokens/` or `.env`.
- All commands execute strictly over the local private network (LAN).
