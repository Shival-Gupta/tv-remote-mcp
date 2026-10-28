# 📺 TV Remote MCP

**One URL, any smart TV, zero install.**

Control any smart TV on your local network — from your phone's browser. No app download, no accounts, no cloud dependency. Works with 10+ brands over WiFi/LAN.

🌐 **Live**: [Shival-Gupta.github.io/tv-remote-mcp](https://Shival-Gupta.github.io/tv-remote-mcp)

---

## Supported Brands

| Brand | Protocol | Pairing Required |
|-------|----------|:----------------:|
| LG WebOS | WebSocket (pywebostv) | ✅ On-screen approval |
| Samsung Tizen | HTTP REST | ⚠️ Token auth |
| Android TV / Google TV | ADB | ⚠️ ADB debugging |
| Roku | HTTP ECP | ❌ |
| Fire TV | ADB / REST | ⚠️ ADB debugging |
| Vizio SmartCast | HTTP REST | ❌ |
| Sony Bravia | HTTP REST | ❌ |
| Philips (JointSpace) | HTTP REST | ⚠️ Varies |
| Panasonic Viera | HTTP REST | ❌ |
| TCL / Hisense / VIDAA | ADB + HTTP | ❌ |

## Quick Start

### 1. Open the Remote
Visit **[Shival-Gupta.github.io/tv-remote-mcp/remote/](https://Shival-Gupta.github.io/tv-remote-mcp/remote/)** on your phone (same WiFi as your TV).

### 2. Start the Local Relay (recommended)
The relay bridges your browser to your TV's control APIs:

```bash
# Requires Python 3.8+
pip install pywebostv requests
python server/relay.py
```

The relay starts on port `7070`. The remote UI auto-detects it.

### 3. Enter Your TV's IP
Type your TV's local IP address (e.g., `192.168.1.11`) in the remote UI and select your brand. That's it.

## How It Works

```
📱 Phone Browser ──HTTP──▶ 🖥️ relay.py (your PC) ──TV Protocol──▶ 📺 Smart TV
                              port 7070                            on LAN
```

The remote UI (static HTML on GitHub Pages) sends commands to the lightweight Python relay running on your PC. The relay translates these into the correct protocol for your TV brand (WebSocket for LG, HTTP for Roku/Vizio, ADB for Android TV, etc.).

## Project Structure

```
tv-remote-mcp/
├── index.html              # Landing page
├── remote/                 # Remote control web app
│   └── index.html
├── server/
│   ├── relay.py            # Local relay (browser → TV bridge)
│   └── mcp-server.py       # FastMCP server & HTTP RPC bridge
├── skills/
│   └── smart-tv-control/   # AI Agent Skill (instructions, CLI, references)
├── docs/                   # Setup guides, AI integration, brand support
└── assets/                 # Shared CSS, JS, icons
```

## AI Assistant Integration (MCP Server & Agent Skill)

TV Remote MCP provides a dedicated FastMCP server and Agent Skill allowing AI assistants (Claude, Gemini, Antigravity, ChatGPT, Cursor) to control smart TVs using natural language:

> *"Turn down the volume by 5 steps and open YouTube on the living room TV"*

- **MCP Server**: `server/mcp-server.py` (FastMCP tools + HTTP `/rpc` bridge)
- **Agent Skill**: `skills/smart-tv-control/SKILL.md` (CLI runner, brand protocols, app IDs)
- **Documentation**: [AI Assistant Setup Guide](docs/ai-setup.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) — Shival Gupta
