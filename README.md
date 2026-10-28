# 📺 TV Remote MCP

**One URL, any smart TV, zero install + Model Context Protocol (MCP) server for AI assistants.**

Control any smart TV on your local network — from your phone's browser or via AI assistants (Claude, Hermes, Antigravity, Cursor, ChatGPT). No app download, no accounts, no cloud dependency. Works with 10+ brands over WiFi/LAN.

🌐 **Live Web Remote**: [projects.shivalgupta.me/tv-remote-mcp](https://projects.shivalgupta.me/tv-remote-mcp) *(Mirror: [Shival-Gupta.github.io/tv-remote-mcp](https://Shival-Gupta.github.io/tv-remote-mcp))*

---

## 🤖 1-Prompt Setup for AI Chatbots

Give this exact prompt to any AI coding assistant (**Claude Code, Hermes, Antigravity, Cursor, Codex**):

> *"Install and configure this repository https://github.com/Shival-Gupta/tv-remote-mcp. Run `python install.py` to install dependencies, register the MCP server, add the smart-tv-control skill, and verify tests."*

The automated installer (`python install.py`) handles everything:
1. **Installs dependencies**: `pywebostv`, `requests`, `websockets`, `fastmcp`.
2. **Registers MCP Server**: Automatically detects and writes configuration for Claude Desktop (`claude_desktop_config.json`) and Cursor (`.cursor/mcp.json`).
3. **Installs Agent Skill**: Places [`smart-tv-control`](skills/smart-tv-control/SKILL.md) into `.agents/skills/`, `.claude/skills/`, and your machine's global agent skill directory.
4. **Verifies Everything**: Runs automated unit tests (`tests/test_mcp_server.py`) and scans your local Wi-Fi to detect smart TVs.

---

## Supported Brands

| Brand | Protocol | Pairing Required |
|---|---|:---:|
| LG WebOS | WebSocket (SSL port 3001 / port 3000) | ✅ On-screen approval |
| Samsung Tizen | HTTP REST + WebSocket | ⚠️ Token auth |
| Android TV / Google TV | ADB (port 5555) | ⚠️ Network debugging |
| Roku | HTTP ECP (port 8060) | ❌ None |
| Fire TV | ADB / REST (port 5555) | ⚠️ Network debugging |
| Vizio SmartCast | HTTPS REST (port 7345/9000) | ❌ None |
| Sony Bravia | HTTP REST / IRCC (port 80) | ❌ None |
| Philips (JointSpace) | HTTP REST (port 1925) | ⚠️ Varies |
| Panasonic Viera | HTTP REST (port 55000) | ❌ None |
| TCL / Hisense / VIDAA | ADB + HTTP | ❌ None |

---

## Quick Start (Human or AI)

### 1. Run the Installer
```bash
# Clone the repository
git clone https://github.com/Shival-Gupta/tv-remote-mcp.git
cd tv-remote-mcp

# Run the automated installer
python install.py
```
*(On Linux/macOS, you can also run `./install.sh`)*

### 2. Start the Local Relay (for Web Remote)
```bash
python server/relay.py
```
Open **[http://localhost:7070/remote/](http://localhost:7070/remote/)** on your browser or visit the live web app from your phone on the same Wi-Fi.

### 3. Start the MCP Server (for AI Assistants)
```bash
python server/mcp-server.py
```
Or use the standalone CLI without running any background server:
```bash
# Discover smart TVs on your Wi-Fi
python skills/smart-tv-control/scripts/tv_cli.py discover

# Wake TV via Wake-on-LAN
python skills/smart-tv-control/scripts/tv_cli.py power_on <ip>

# Volume and app control
python skills/smart-tv-control/scripts/tv_cli.py action <ip> <brand> volume_up
python skills/smart-tv-control/scripts/tv_cli.py launch <ip> <brand> youtube
```

---

## How It Works

```
📱 Phone Browser ──HTTP──▶ 🖥️ relay.py (your PC) ──TV Protocol──▶ 📺 Smart TV
                               port 7070                            on LAN
🤖 AI Assistants ──MCP───▶ 🖥️ mcp-server.py ───Direct Socket─▶ 📺 Smart TV
                               port 8000
```

1. **Browser Remote**: The static HTML remote communicates with `relay.py` on your PC, which translates commands into TV-native protocols (WebSocket for LG, REST for Roku, ADB for Android TV).
2. **AI Control**: AI assistants call FastMCP tools (`universal_action`, `discover`, `list_brands`) or use the HTTP RPC bridge (`/rpc`).
3. **Smart Power (Wake-on-LAN)**: Powered-off TVs close network ports; the system uses multi-burst UDP magic packets to wake them up.

---

## Project Structure

```
tv-remote-mcp/
├── install.py              # Turnkey automated installer (MCP + Skills + Tests)
├── install.sh              # Unix/macOS installer wrapper
├── requirements.txt        # Python dependencies (pywebostv, requests, websockets, fastmcp)
├── CLAUDE.md               # Claude Code & Hermes agent instructions
├── AGENTS.md               # Antigravity & AI developer instructions
├── index.html              # Landing page
├── remote/                 # Remote control web app
│   └── index.html
├── server/
│   ├── relay.py            # Local relay (browser → TV bridge, port 7070)
│   └── mcp-server.py       # FastMCP server & HTTP RPC bridge (port 8000)
├── skills/
│   └── smart-tv-control/   # AI Agent Skill (instructions, CLI, references)
│       ├── SKILL.md
│       ├── scripts/tv_cli.py
│       └── references/
├── tests/                  # Automated hardware & MCP server test suites
├── docs/                   # Setup guides, AI integration, brand support
└── assets/                 # Shared CSS, JS, icons
```

---

## AI Assistant Integration (MCP Server & Agent Skill)

TV Remote MCP provides a dedicated FastMCP server and Agent Skill allowing AI assistants to control smart TVs using natural language:

> *"Turn down the volume by 5 steps and open YouTube on the living room TV"*

- **MCP Server**: `server/mcp-server.py` (FastMCP tools + HTTP `/rpc` bridge)
- **Agent Skill**: `skills/smart-tv-control/SKILL.md` (CLI runner, brand protocols, app IDs)
- **Setup Guide**: [AI Assistant Setup Guide](docs/ai-setup.md)
- **Claude & Hermes**: Configured automatically via `python install.py` and documented in `CLAUDE.md`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) — Shival Gupta
