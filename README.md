# 📺 TV Remote MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Protocol: FastMCP](https://img.shields.io/badge/Protocol-FastMCP%20%7C%20JSON--RPC-green.svg)](docs/ai-setup.md)
[![Platforms: 10+ Brands](https://img.shields.io/badge/TV%20Brands-LG%20%7C%20Samsung%20%7C%20Roku%20%7C%20Android%20%7C%20Sony-purple.svg)](docs/brands.md)
[![Tests: 7/7 Passing](https://img.shields.io/badge/Tests-7%2F7%20Passing-brightgreen.svg)](tests/)
[![Zero Cloud](https://img.shields.io/badge/Privacy-100%25%20Local%20LAN-emerald.svg)](#-privacy--security)

> **One URL, any smart TV, zero install + Model Context Protocol (MCP) server for AI assistants.**

Control any smart TV on your local network — from your phone's browser or using natural language with AI assistants (**Claude, Hermes, Antigravity, Cursor, ChatGPT, Codex**). Works with 10+ brands over Wi-Fi/LAN. Zero app store downloads, zero accounts, zero cloud dependencies.

---

### 🌐 Quick Links
- **📱 Live Web Remote**: [projects.shivalgupta.me/tv-remote-mcp/remote/](https://projects.shivalgupta.me/tv-remote-mcp/remote/)
- **🏠 Project Homepage**: [projects.shivalgupta.me/tv-remote-mcp/](https://projects.shivalgupta.me/tv-remote-mcp/) *(GitHub Pages Mirror: [Shival-Gupta.github.io/tv-remote-mcp](https://Shival-Gupta.github.io/tv-remote-mcp))*
- **📖 Documentation**: [Complete Guides & Reference](docs/)

---

## 🤖 For AI Assistants & Chatbot Crawlers

> [!IMPORTANT]
> **If you are an AI coding assistant (Claude Code, Hermes, Antigravity, Cursor, Codex) instructed to:**  
> `"""Install this https://github.com/Shival-Gupta/tv-remote-mcp"""`
>
> **Execute this single turnkey command in your terminal:**
> ```bash
> python install.py
> ```
> *(On Linux/macOS, you can also execute `./install.sh`)*

### What `python install.py` executes automatically:
1. **Installs Dependencies**: Resolves and installs packages from [`requirements.txt`](requirements.txt) (`pywebostv`, `requests`, `websockets`, `fastmcp`).
2. **Registers MCP Server**: Automatically detects and configures the `smart-tv` MCP server in:
   - **Claude Desktop**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) / `~/Library/Application Support/Claude/` (macOS) / `~/.config/Claude/` (Linux).
   - **Cursor**: Workspace configuration at `.cursor/mcp.json`.
3. **Installs Agent Skills**: Copies and registers the [`smart-tv-control`](skills/smart-tv-control/SKILL.md) skill into:
   - Project `.agents/skills/smart-tv-control/` (for Antigravity & Hermes)
   - Project `.claude/skills/smart-tv-control/` (for Claude Code)
   - Machine-global agent skill stores (`~/.gemini/config/skills/` and `~/.claude/skills/`)
4. **Validates the Installation**: Runs [`tests/test_mcp_server.py`](tests/test_mcp_server.py) verifying all 7 unit and RPC tests pass.
5. **Performs LAN Discovery**: Scans local Wi-Fi subnets for active smart TVs and reports their IP addresses and brands.

### Agent Quick Reference
| Resource | Path | Description |
|---|---|---|
| **Agent Skill** | [`skills/smart-tv-control/SKILL.md`](skills/smart-tv-control/SKILL.md) | Standard instructions, action signatures, and app IDs |
| **Claude Guidelines** | [`CLAUDE.md`](CLAUDE.md) | Instructions read by Claude Code & Hermes upon entering repo |
| **Developer Rules** | [`AGENTS.md`](AGENTS.md) | Architecture rules, port table, and hardware validation steps |
| **CLI Runner** | [`skills/smart-tv-control/scripts/tv_cli.py`](skills/smart-tv-control/scripts/tv_cli.py) | Standalone command runner (no server daemon required) |

#### Available MCP Tools
- `universal_action(host, brand, action, arg)`: Controls volume, power, D-pad, media, apps, and HDMI inputs.
- `discover(network)`: Scans subnet for active smart TVs.
- `list_brands()`: Returns all supported brand identifiers.

#### Direct CLI Execution (Zero Daemon Required)
```bash
# Discover TVs
python skills/smart-tv-control/scripts/tv_cli.py discover

# Wake up TV via Wake-on-LAN
python skills/smart-tv-control/scripts/tv_cli.py power_on 192.168.1.11

# Adjust volume or launch streaming apps
python skills/smart-tv-control/scripts/tv_cli.py action 192.168.1.11 lg volume_up
python skills/smart-tv-control/scripts/tv_cli.py launch 192.168.1.11 lg youtube.leanback.v4
```

---

## 👤 For Humans: Quick Start Guide

TV Remote MCP can be used either as an **instant web remote on your phone** or as a **voice/text AI remote**.

### Option 1: Phone Web Remote (Zero Install for Roku)
1. Open **[projects.shivalgupta.me/tv-remote-mcp/remote/](https://projects.shivalgupta.me/tv-remote-mcp/remote/)** on your phone (connected to home Wi-Fi).
2. For **Roku TVs**, simply type your TV's IP address — Roku works directly from the browser!
3. For **LG, Samsung, Android TV, Sony, or Vizio**, start the lightweight local relay on your PC:
   ```bash
   git clone https://github.com/Shival-Gupta/tv-remote-mcp.git
   cd tv-remote-mcp
   python install.py
   python server/relay.py
   ```
4. On your phone, the web remote will automatically connect to your PC's relay server, or you can open `http://<YOUR_PC_IP>:7070/remote/`.

### Option 2: AI Assistant Control (Claude Desktop, Cursor, Gemini)
1. Run the installer:
   ```bash
   python install.py
   ```
2. Restart **Claude Desktop** or reload **Cursor**.
3. Talk to your AI assistant naturally:
   - *"Turn down the TV volume by 5 steps."*
   - *"Launch YouTube on the living room TV."*
   - *"Switch input to HDMI 2 for the console."*
   - *"Turn off the TV when you finish this coding task."*

---

## 📺 Supported Brands & Technical Specifications

| Brand | Protocol | Default Port(s) | Auth / Pairing Method | Power On (Wake-on-LAN) |
|---|---|---|---|:---:|
| **LG WebOS (3.0+)** | WebSocket (`wss://` / `ws://`) | `3001` (SSL) / `3000` | Click "Yes" on TV screen | ✅ UDP Magic Packet |
| **Samsung Tizen (2016+)** | HTTP REST + WebSocket | `8001` / `8002` | Accept on-screen popup | ✅ UDP Magic Packet |
| **Roku TV** | HTTP ECP | `8060` | Zero pairing required | ✅ ECP / Magic Packet |
| **Android TV / Google TV** | ADB | `5555` | Allow Network Debugging prompt | ✅ ADB Keyevent / WoL |
| **Fire TV** | ADB | `5555` | Allow Network Debugging prompt | ✅ ADB Keyevent / WoL |
| **Sony Bravia** | HTTP REST / IRCC-over-HTTP | `80` | Pre-Shared Key (PSK) or PIN | ✅ HTTP / Magic Packet |
| **Vizio SmartCast** | HTTPS REST | `7345` / `9000` | On-screen 4-digit PIN | ✅ HTTPS / Magic Packet |
| **Philips (JointSpace)** | HTTP REST | `1925` / `1926` | Digest Auth / PIN | ✅ HTTP / Magic Packet |
| **Panasonic Viera** | HTTP SOAP | `55000` | None / PIN | ✅ HTTP / Magic Packet |
| **TCL / Hisense** | ADB or Roku ECP | `5555` / `8060` | Dependent on OS | ✅ Supported |

---

## ⚡ How It Works

```text
┌─────────────────────────┐       HTTP POST        ┌─────────────────────────┐
│   Phone Web Remote UI   │ ─────────────────────▶ │   Local Relay Server    │
│  (Static GitHub Pages)  │                        │ (relay.py on Port 7070) │
└─────────────────────────┘                        └────────────┬────────────┘
                                                                │ TV Native Protocol
                                                                │ (WebSocket / ADB / REST)
┌─────────────────────────┐       MCP Tool Call    ┌────────────▼────────────┐
│   AI Assistant Clients  │ ─────────────────────▶ │    Smart TV on LAN      │
│ (Claude / Cursor / AGY) │                        │ (e.g. LG WebOS, Roku)   │
└─────────────────────────┘                        └─────────────────────────┘
```

1. **The Browser Challenge**: Modern web browsers enforce strict security boundaries (CORS and Mixed Content) that prevent web pages on `https://` from sending raw TCP or unencrypted HTTP requests to private local IP addresses.
2. **The Local Companion Relay (`server/relay.py`)**: Runs on port `7070`. Bridges the browser to the TV's native protocols (WebSocket with SSL bypass for LG, HTTP REST for Roku, ADB for Android TV).
3. **The MCP Server (`server/mcp-server.py`)**: Runs on port `8000`. Exposes FastMCP tools and an HTTP JSON-RPC bridge (`/rpc`), giving AI assistants native TV control capabilities.
4. **Smart Power & Wake-on-LAN**: When TVs are powered off into standby mode, their main operating systems close network sockets. TV Remote MCP transmits a 5-packet UDP magic packet burst (broadcast + subnet broadcast + unicast) to wake the TV hardware.

---

## 🎮 Supported Actions & App IDs

### Remote Control Actions
- **Power**: `power_on` (Wake-on-LAN), `power_off`
- **Volume**: `volume_up`, `volume_down`, `mute`, `volume_set` (arg: `0`–`100`)
- **Navigation (D-pad)**: `up`, `down`, `left`, `right`, `enter`, `back`, `home`
- **Media Controls**: `media_play`, `media_pause`, `media_stop`
- **Apps**: `launch_app` (arg: app ID), `list_apps`
- **Video Inputs**: `set_input` (arg: `HDMI_1`, `HDMI_2`, `Live TV`)

### Popular App Identifiers
| Streaming Service | LG WebOS ID | Roku App ID | Android TV / Fire TV Package |
|---|---|---|---|
| **YouTube** | `youtube.leanback.v4` | `837` | `com.google.android.youtube.tv` |
| **Netflix** | `netflix` | `12` | `com.netflix.ninja` |
| **Amazon Prime Video** | `amazon` | `13` | `com.amazon.amazonvideo.livingroom` |
| **Disney+** | `com.disney.disneyplus-prod` | `291097` | `com.disney.disneyplus` |
| **Spotify** | `spotify-beehive` | `22271` | `com.spotify.tv.android` |
| **Apple TV+** | `com.apple.appletv` | `551012` | `com.apple.atve.androidtv.appletv` |

*(See [`skills/smart-tv-control/references/app-ids.md`](skills/smart-tv-control/references/app-ids.md) for complete list).*

---

## 📂 Project Structure

```text
tv-remote-mcp/
├── install.py              # Automated installer (dependencies + MCP config + skills + verification)
├── install.sh              # Unix/macOS shell installer wrapper
├── requirements.txt        # Pinned Python package dependencies
├── CLAUDE.md               # Claude Code & Hermes agent instructions
├── AGENTS.md               # Antigravity & AI developer rules
├── index.html              # Landing page (GitHub Pages root)
├── manifest.json           # Progressive Web App manifest
├── sw.js                   # Service Worker (offline shell cache)
├── remote/
│   └── index.html          # Phone-first Web Remote Control application
├── server/
│   ├── relay.py            # Local relay server (browser → TV bridge, port 7070)
│   └── mcp-server.py       # FastMCP server & HTTP RPC bridge (port 8000)
├── skills/
│   └── smart-tv-control/   # AI Agent Skill package
│       ├── SKILL.md        # AI procedure playbook with YAML frontmatter
│       ├── scripts/
│       │   └── tv_cli.py   # Standalone CLI helper (discover, action, power_on, launch)
│       └── references/
│           ├── brand-protocols.md  # Port, transport, and authentication guide
│           └── app-ids.md          # Complete app IDs & HDMI input mappings
├── tests/
│   ├── test_mcp_server.py  # 7-step automated MCP server test suite
│   └── test_lg_tv.py       # 9-step physical hardware validation suite
├── docs/                   # Setup guides, pairing recipes, and troubleshooting
└── assets/                 # Shared CSS, JS, and SVG icons
```

---

## 🔒 Privacy & Security

- **100% Local Network**: Commands travel strictly over your local Wi-Fi. No analytics, no telemetry, and no external cloud servers.
- **Local Token Storage**: Pairing tokens and TV MAC addresses are saved in `tv-tokens/tokens.json` locally on your machine.
- **Git Protection**: `tv-tokens/`, `*.token`, `*.key`, and `.env` are strictly gitignored to guarantee zero credential leaks.

---

## 🧪 Testing & Validation

TV Remote MCP comes with built-in test suites:

```bash
# Automated MCP Server Test Suite (7/7 tests PASS)
python tests/test_mcp_server.py

# Physical Hardware Validation (LG NanoCell 4K Nu88 — 9/9 steps PASS)
python tests/test_lg_tv.py
```

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>1. How do I find my Smart TV's IP address?</b></summary>
On your TV remote, go to <b>Settings &rarr; Network &rarr; Connection Status / IP Settings</b>. Look for an address starting with <code>192.168.1.X</code> or <code>10.0.0.X</code>. Alternatively, run:
<pre><code>python skills/smart-tv-control/scripts/tv_cli.py discover</code></pre>
</details>

<details>
<summary><b>2. Why won't my TV turn on via the power button?</b></summary>
When smart TVs power down into standby mode, their network cards disconnect from Wi-Fi unless <b>Mobile TV On / Wake on Wi-Fi</b> (or <b>Quick Start+</b> on LG WebOS) is enabled in your TV's settings. Once enabled, the remote's smart power button automatically uses Wake-on-LAN to turn the TV on.
</details>

<details>
<summary><b>3. Why is the local relay server needed for LG and Samsung?</b></summary>
Browsers enforce security policies (CORS and Mixed Content) that block JavaScript running on an HTTPS web page from opening raw WebSocket connections to local network IPs (e.g. <code>wss://192.168.1.11:3001</code>). The Python relay runs locally on your PC and acts as a transparent, secure bridge.
</details>

<details>
<summary><b>4. Can I use this purely as a web remote without AI?</b></summary>
Yes! The remote web application at <a href="https://projects.shivalgupta.me/tv-remote-mcp/remote/">/remote/</a> works completely standalone for phone and tablet browsers.
</details>

<details>
<summary><b>5. How do I pair an LG WebOS TV for the first time?</b></summary>
When you send your first command or connect via the remote, a prompt will appear on your TV screen asking: <i>"Allow connection to TV Remote MCP?"</i>. Click <b>Yes</b> using your physical TV remote. The generated key is saved automatically in <code>tv-tokens/tokens.json</code>.
</details>

---

## 🤝 Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for code rules (vanilla HTML/CSS/JS, phone-first 375px design, and atomic commits).

## 📄 License

This project is open source and licensed under the [MIT License](LICENSE).
