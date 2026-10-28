# 📺 TV Remote MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Protocol: FastMCP](https://img.shields.io/badge/Protocol-FastMCP%20%7C%20JSON--RPC-green.svg)](docs/ai-setup.md)
[![Platforms: 10+ Brands](https://img.shields.io/badge/TV%20Brands-LG%20%7C%20Samsung%20%7C%20Roku%20%7C%20Android%20%7C%20Sony-purple.svg)](docs/brands.md)
[![Tests: 7/7 Passing](https://img.shields.io/badge/Tests-7%2F7%20Passing-brightgreen.svg)](tests/)
[![Zero Cloud](https://img.shields.io/badge/Privacy-100%25%20Local%20LAN-emerald.svg)](#privacy-security)

Control your smart TV from any phone or laptop browser over your local Wi-Fi — with zero app store downloads, zero logins, and zero cloud tracking. 

It also includes a local Model Context Protocol (MCP) server so your AI assistants (**Claude, Cursor, Hermes, Antigravity, Gemini**) can adjust volume, switch HDMI inputs, launch streaming apps, or turn off the TV when a task finishes.

- 📱 **Open Web Remote**: [projects.shivalgupta.me/tv-remote-mcp/remote/](https://projects.shivalgupta.me/tv-remote-mcp/remote/)
- 🌐 **Project Home**: [projects.shivalgupta.me/tv-remote-mcp/](https://projects.shivalgupta.me/tv-remote-mcp/) *(Mirror: [Shival-Gupta.github.io/tv-remote-mcp](https://Shival-Gupta.github.io/tv-remote-mcp))*
- 📖 **Documentation**: [docs/](docs/)

> 🤖 **Using an AI assistant or coding agent?**  
> Jump to [**AI Assistant & MCP Setup**](#ai-assistant-mcp-setup) for one-command installation, MCP tool schemas, and agent skill integration.

---

## ⚡ Quick Start

### 1. Open the Remote
Open **[projects.shivalgupta.me/tv-remote-mcp/remote/](https://projects.shivalgupta.me/tv-remote-mcp/remote/)** on your phone (make sure you are connected to the same Wi-Fi network as your TV).

- **For Roku TVs**: Works immediately from the browser without running any software on your computer.
- **For LG, Samsung, Android TV, Sony, or Vizio**: Start the lightweight companion relay on your computer:

```bash
# Clone the repository
git clone https://github.com/Shival-Gupta/tv-remote-mcp.git
cd tv-remote-mcp

# Run the automated installer (installs dependencies & verifies setup)
python install.py

# Start the local relay
python server/relay.py
```

### 2. Connect to Your TV
Tap **Settings (⚙)** in the remote header, select your TV brand, and enter your TV's local IP address (e.g. `192.168.1.11`).

If you're using the remote from your phone, enter your computer's local IP address as the relay server (e.g. `http://192.168.1.12:7070`). You can also open `http://<YOUR_PC_IP>:7070/remote/` directly in your phone's browser.

---

## 📺 Supported Brands & Technical Specs

| Brand | Protocol | Default Port(s) | Auth / Pairing Method | Power On (Wake-on-LAN) |
|---|---|---|---|:---:|
| **LG WebOS (3.0+)** | WebSocket (`wss://` / `ws://`) | `3001` (SSL) / `3000` | Click "Yes" on TV screen | ✅ UDP Magic Packet |
| **Samsung Tizen (2016+)** | HTTP REST + WebSocket | `8001` / `8002` | Accept on-screen popup | ✅ UDP Magic Packet |
| **Roku TV** | HTTP ECP | `8060` | None (open REST) | ✅ ECP / Magic Packet |
| **Android TV / Google TV** | ADB | `5555` | Allow Network Debugging prompt | ✅ ADB Keyevent / WoL |
| **Fire TV** | ADB | `5555` | Allow Network Debugging prompt | ✅ ADB Keyevent / WoL |
| **Sony Bravia** | HTTP REST / IRCC | `80` | Pre-Shared Key (PSK) or PIN | ✅ HTTP / Magic Packet |
| **Vizio SmartCast** | HTTPS REST | `7345` / `9000` | On-screen 4-digit PIN | ✅ HTTPS / Magic Packet |
| **Philips (JointSpace)** | HTTP REST | `1925` / `1926` | Digest Auth / PIN | ✅ HTTP / Magic Packet |
| **Panasonic Viera** | HTTP SOAP | `55000` | None / PIN | ✅ HTTP / Magic Packet |
| **TCL / Hisense** | ADB or Roku ECP | `5555` / `8060` | Dependent on TV OS | ✅ Supported |

---

## 🛠️ How It Works

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

1. **Why the local relay exists**: Web browsers running an HTTPS page cannot open direct TCP sockets or unencrypted HTTP connections to local network IPs due to CORS and mixed-content security rules. The lightweight Python relay (`server/relay.py`) runs on your PC and acts as a transparent local bridge.
2. **Smart Power via Wake-on-LAN**: When smart TVs are powered off, their operating systems enter low-power standby and shut down their network listening ports. TV Remote MCP uses a 5-packet UDP magic packet burst (broadcast + subnet broadcast + unicast) to wake the TV hardware over Wi-Fi/Ethernet.
3. **Phone-first UI**: Built with vanilla HTML5, CSS (Tailwind CDN), and JavaScript (<200KB total, no npm build step). It includes haptic feedback, D-pad angle mathematics, hold-to-repeat volume buttons, and offline caching via Service Worker.

---

<a id="ai-assistant-mcp-setup"></a>
## 🤖 AI Assistant & MCP Setup

TV Remote MCP provides a dedicated FastMCP server and Agent Skill so coding assistants and AI agents can interact with your TV using natural language:

> *"Turn down the volume by 5 steps and open YouTube on the TV."*  
> *"Switch the TV input to HDMI 2 for the console."*  
> *"Turn off the living room TV when this test suite finishes."*

### One-Command Automated Setup
From your terminal (or when asking an AI assistant to set up this repository), run:

```bash
python install.py
```
*(On Linux/macOS, `./install.sh` also works).*

#### What `install.py` does:
- Installs dependencies from [`requirements.txt`](requirements.txt) (`pywebostv`, `requests`, `websockets`, `fastmcp`).
- Auto-detects and writes MCP configuration for:
  - **Claude Desktop**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) / `~/Library/Application Support/Claude/` (macOS) / `~/.config/Claude/` (Linux).
  - **Cursor**: Workspace configuration in `.cursor/mcp.json`.
- Registers the [`smart-tv-control`](skills/smart-tv-control/SKILL.md) skill into `.agents/skills/`, `.claude/skills/`, and machine-global agent directories (`~/.gemini/config/skills/`, `~/.claude/skills/`).
- Runs [`tests/test_mcp_server.py`](tests/test_mcp_server.py) to confirm all 7 test cases pass.
- Scans your local network subnet and reports discovered smart TVs.

### MCP Tools Reference

| Tool Name | Arguments | Description |
|---|---|---|
| `universal_action` | `host`, `brand`, `action`, `arg` | Executes a TV command (see Action list below) |
| `discover` | `network` *(optional)* | Scans the local network subnet for active smart TVs |
| `list_brands` | *(none)* | Returns the list of supported smart TV brand IDs |

### Supported Actions
- **Power**: `power_on` (Wake-on-LAN), `power_off`
- **Volume**: `volume_up`, `volume_down`, `mute`, `volume_set` (arg: `0`–`100`)
- **Navigation**: `up`, `down`, `left`, `right`, `enter`, `back`, `home`
- **Media**: `media_play`, `media_pause`, `media_stop`
- **Apps**: `launch_app` (arg: app ID), `list_apps`
- **Inputs**: `set_input` (arg: `HDMI_1`, `HDMI_2`, etc.)

### Direct CLI Control (No Server Daemon Required)
You can also send commands directly from your terminal or shell scripts:

```bash
# Discover TVs on your local Wi-Fi
python skills/smart-tv-control/scripts/tv_cli.py discover

# Wake up TV via Wake-on-LAN
python skills/smart-tv-control/scripts/tv_cli.py power_on 192.168.1.11

# Adjust volume or launch apps
python skills/smart-tv-control/scripts/tv_cli.py action 192.168.1.11 lg volume_up
python skills/smart-tv-control/scripts/tv_cli.py launch 192.168.1.11 lg youtube.leanback.v4
```

### Agent Instruction Files
- **For Claude Code & Hermes**: Read [`CLAUDE.md`](CLAUDE.md)
- **For Antigravity & Pair Programming**: Read [`AGENTS.md`](AGENTS.md)
- **Complete Skill Playbook**: Read [`skills/smart-tv-control/SKILL.md`](skills/smart-tv-control/SKILL.md)

---

## 🎮 Streaming App Identifiers

When launching apps via MCP or CLI, use these platform identifiers:

| Service | LG WebOS ID | Roku App ID | Android TV / Fire TV Package |
|---|---|---|---|
| **YouTube** | `youtube.leanback.v4` | `837` | `com.google.android.youtube.tv` |
| **Netflix** | `netflix` | `12` | `com.netflix.ninja` |
| **Prime Video** | `amazon` | `13` | `com.amazon.amazonvideo.livingroom` |
| **Disney+** | `com.disney.disneyplus-prod` | `291097` | `com.disney.disneyplus` |
| **Spotify** | `spotify-beehive` | `22271` | `com.spotify.tv.android` |
| **Apple TV+** | `com.apple.appletv` | `551012` | `com.apple.atve.androidtv.appletv` |

*(See [`skills/smart-tv-control/references/app-ids.md`](skills/smart-tv-control/references/app-ids.md) for complete lookup table).*

---

## 📁 Project Structure

```text
tv-remote-mcp/
├── install.py              # Automated installer (dependencies + MCP config + skills + tests)
├── install.sh              # Unix/macOS shell installer wrapper
├── requirements.txt        # Python package dependencies
├── CLAUDE.md               # Claude Code & Hermes agent instructions
├── AGENTS.md               # Antigravity developer rules & brand reference
├── index.html              # Landing page (GitHub Pages root)
├── manifest.json           # Progressive Web App manifest
├── sw.js                   # Service Worker (offline cache)
├── remote/
│   └── index.html          # Universal Smart TV Web Remote application
├── server/
│   ├── relay.py            # Local relay server (browser → TV bridge, port 7070)
│   └── mcp-server.py       # FastMCP server & HTTP RPC bridge (port 8000)
├── skills/
│   └── smart-tv-control/   # AI Agent Skill package
│       ├── SKILL.md        # Procedural playbook with YAML frontmatter
│       ├── scripts/
│       │   └── tv_cli.py   # Standalone CLI helper (discover, action, power_on, launch)
│       └── references/
│           ├── brand-protocols.md  # Port, transport, and auth guide
│           └── app-ids.md          # Complete app IDs & HDMI input mappings
├── tests/
│   ├── test_mcp_server.py  # 7-step automated MCP server test suite
│   └── test_lg_tv.py       # 9-step physical hardware validation suite
├── docs/                   # Setup guides, pairing recipes, and troubleshooting
└── assets/                 # Shared CSS, JS, and SVG icons
```

---

<a id="privacy-security"></a>
## 🔒 Privacy & Security

- **100% Local**: All commands travel exclusively over your home Wi-Fi network. No cloud accounts, no third-party telemetry, and no external tracking.
- **Local Token Storage**: Pairing tokens and TV MAC addresses are stored in `tv-tokens/tokens.json` locally on your machine.
- **Git Protection**: `tv-tokens/`, `*.token`, `*.key`, and `.env` are strictly gitignored to prevent accidental credential commits.

---

## 🧪 Testing & Validation

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
On your TV remote, navigate to <b>Settings &rarr; Network &rarr; Connection Status / IP Settings</b>. Look for an address starting with <code>192.168.1.X</code> or <code>10.0.0.X</code>. Alternatively, run:
<pre><code>python skills/smart-tv-control/scripts/tv_cli.py discover</code></pre>
</details>

<details>
<summary><b>2. Why won't my TV turn on via the power button?</b></summary>
When smart TVs power down into standby mode, their network cards disconnect from Wi-Fi unless <b>Mobile TV On / Wake on Wi-Fi</b> (or <b>Quick Start+</b> on LG WebOS) is enabled in your TV's settings. Once enabled, the remote's smart power button automatically uses Wake-on-LAN to wake the TV.
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

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code standards, phone-first responsive design, and atomic commits.

## 📄 License

This project is open source and licensed under the [MIT License](LICENSE).
