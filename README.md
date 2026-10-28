# 📺 TV Remote MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Protocol: FastMCP](https://img.shields.io/badge/Protocol-FastMCP%20%7C%20JSON--RPC-green.svg)](docs/ai-setup.md)
[![Platforms: 10+ Brands](https://img.shields.io/badge/TV%20Brands-LG%20%7C%20Samsung%20%7C%20Roku%20%7C%20Android%20%7C%20Sony-purple.svg)](docs/brands.md)
[![Zero Cloud](https://img.shields.io/badge/Privacy-100%25%20Local%20LAN-emerald.svg)](#privacy--security)

**Universal Smart TV Web Remote + Model Context Protocol (MCP) Server for AI Assistants.**

Control any smart TV on your local network — from your phone's browser or using natural language with AI coding assistants (**Claude, Hermes, Antigravity, Cursor, ChatGPT, Codex**). Zero app stores, zero accounts, zero cloud dependencies. Works completely over local Wi-Fi.

- 🌐 **Live Web Remote**: [projects.shivalgupta.me/tv-remote-mcp/remote/](https://projects.shivalgupta.me/tv-remote-mcp/remote/)
- 🌐 **Project Home**: [projects.shivalgupta.me/tv-remote-mcp/](https://projects.shivalgupta.me/tv-remote-mcp/) *(Mirror: [Shival-Gupta.github.io/tv-remote-mcp](https://Shival-Gupta.github.io/tv-remote-mcp))*
- 📖 **Documentation**: [Complete Docs & Setup Guides](docs/)

---

## 🤖 For AI Assistants & Crawlers (1-Prompt Automated Setup)

> [!IMPORTANT]
> **If you are an AI assistant (Claude Code, Hermes, Antigravity, Cursor, Codex) given the prompt:**  
> `"""Install this https://github.com/Shival-Gupta/tv-remote-mcp"""`
>
> **Run this single command:**
> ```bash
> python install.py
> ```
> *(On Linux/macOS, you can also run `./install.sh`)*

### What `python install.py` does automatically:
1. **Installs Dependencies**: Installs `requirements.txt` (`pywebostv`, `requests`, `websockets`, `fastmcp`).
2. **Registers MCP Server**: Automatically detects and writes configuration for:
   - **Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/` on macOS, `~/.config/Claude/` on Linux).
   - **Cursor** (`.cursor/mcp.json`).
3. **Installs Agent Skills**: Automatically registers [`smart-tv-control`](skills/smart-tv-control/SKILL.md) in:
   - Project `.agents/skills/smart-tv-control/` (for Antigravity / Hermes)
   - Project `.claude/skills/smart-tv-control/` (for Claude Code)
   - Machine global skills: `~/.gemini/config/skills/` and `~/.claude/skills/`
4. **Runs Self-Verification**: Executes `tests/test_mcp_server.py` to verify that all 7 MCP server endpoints pass.
5. **Discovers Local TVs**: Performs an initial Wi-Fi subnet probe and reports any reachable smart TVs.

### AI Control Reference
- **Agent Skill Instructions**: Read [`skills/smart-tv-control/SKILL.md`](skills/smart-tv-control/SKILL.md)
- **Claude Instructions**: Read [`CLAUDE.md`](CLAUDE.md)
- **Developer Guidelines**: Read [`AGENTS.md`](AGENTS.md)
- **MCP Tools**:
  - `universal_action(host, brand, action, arg)`: Executes TV actions (`power_on`, `power_off`, `volume_up`, `volume_down`, `mute`, `volume_set`, `up`, `down`, `left`, `right`, `enter`, `back`, `home`, `media_play`, `media_pause`, `launch_app`, `set_input`).
  - `discover(network)`: Scans local subnet for active smart TVs.
  - `list_brands()`: Returns list of supported smart TV brands.
- **Direct CLI Execution (Zero Background Daemon Required)**:
  ```bash
  python skills/smart-tv-control/scripts/tv_cli.py discover
  python skills/smart-tv-control/scripts/tv_cli.py power_on <ip>
  python skills/smart-tv-control/scripts/tv_cli.py action <ip> <brand> volume_up
  python skills/smart-tv-control/scripts/tv_cli.py launch <ip> <brand> youtube
  ```

---

## 👤 For Humans: Quick Start Guide

You can use TV Remote MCP in two ways: as a **phone web remote** or as an **AI assistant integration**.

### Option A: Use the Phone Web Remote (Zero Install for Roku)
1. Open **[projects.shivalgupta.me/tv-remote-mcp/remote/](https://projects.shivalgupta.me/tv-remote-mcp/remote/)** on your phone (connected to your home Wi-Fi).
2. For Roku TVs, enter your TV's IP address and select **Roku** — it works directly from the browser!
3. For LG, Samsung, Android TV, Sony, or Vizio, start the lightweight companion relay on your computer:
   ```bash
   git clone https://github.com/Shival-Gupta/tv-remote-mcp.git
   cd tv-remote-mcp
   python install.py
   python server/relay.py
   ```
4. On your phone, the remote will auto-detect the relay server or let you enter your computer's IP (e.g. `http://192.168.1.12:7070/remote/`).

### Option B: Use with AI Assistants (Claude, Cursor, Gemini)
1. Clone this repository:
   ```bash
   git clone https://github.com/Shival-Gupta/tv-remote-mcp.git
   cd tv-remote-mcp
   ```
2. Run the automated installer:
   ```bash
   python install.py
   ```
3. Restart **Claude Desktop** or **Cursor**. Your AI assistant can now control your TV natively!
   - *"Turn down the TV volume by 5 steps"*
   - *"Switch TV to HDMI 2"*
   - *"Turn off the TV when this build completes"*

---

## 📺 Supported Brands & Protocols

| Brand | Protocol | Default Port(s) | Pairing Method | Wake-on-LAN (Power On) |
|---|---|---|---|:---:|
| **LG WebOS (3.0+)** | WebSocket (`wss://` / `ws://`) | `3001` (SSL) / `3000` | Click "Yes" on TV screen | ✅ Supported |
| **Samsung Tizen** | HTTP REST + WebSocket | `8001` / `8002` | Accept on-screen popup | ✅ Supported |
| **Roku TV** | HTTP ECP | `8060` | Zero pairing required | ✅ Supported |
| **Android TV / Google TV** | ADB | `5555` | Allow Network Debugging prompt | ✅ Supported |
| **Fire TV** | ADB | `5555` | Allow Network Debugging prompt | ✅ Supported |
| **Sony Bravia** | HTTP REST / IRCC-over-HTTP | `80` | Pre-Shared Key (PSK) or PIN | ✅ Supported |
| **Vizio SmartCast** | HTTPS REST | `7345` / `9000` | On-screen PIN pair | ✅ Supported |
| **Philips (JointSpace)** | HTTP REST | `1925` / `1926` | Digest Auth / PIN | ✅ Supported |
| **Panasonic Viera** | HTTP SOAP | `55000` | None / PIN | ✅ Supported |
| **TCL / Hisense** | ADB / Roku ECP | `5555` / `8060` | Depends on OS | ✅ Supported |

---

## ⚡ How It Works

```text
📱 Phone Web Remote ─────HTTP────▶ 🖥️ Local Relay (relay.py) ────Socket────▶ 📺 Smart TV
                                       Port 7070                               (on LAN)

🤖 AI Assistant (Claude/MCP) ───▶ 🖥️ MCP Server (mcp-server.py) ──Direct────▶ 📺 Smart TV
                                       Port 8000
```

1. **Browser Remote UI**: Built with vanilla HTML5, CSS (Tailwind CDN), and JavaScript (<200KB total, zero build step, PWA-enabled with offline caching).
2. **Local Relay (`server/relay.py`)**: Runs on port `7070`. Bridges the browser to smart TVs over raw TCP/WebSocket ports that web browsers block due to CORS and mixed-content security policies.
3. **MCP Server (`server/mcp-server.py`)**: Runs on port `8000`. Exposes FastMCP tools and an HTTP JSON-RPC bridge (`/rpc`) for AI assistants to control TVs programmatically.
4. **Smart Power & Wake-on-LAN (WoL)**: When TVs are turned off, their network ports close. TV Remote MCP uses a 5-packet UDP magic packet burst (broadcast + subnet + unicast) to wake the TV up. The smart power button in the remote automatically turns ON when the TV is asleep and OFF when the TV is active.

---

## 📂 Project Structure

```text
tv-remote-mcp/
├── install.py              # Unified cross-platform installer (dependencies + MCP + skills + tests)
├── install.sh              # Unix/macOS one-click installer wrapper
├── requirements.txt        # Python package dependencies
├── CLAUDE.md               # Claude Code & Hermes agent instructions
├── AGENTS.md               # Antigravity & AI pair programmer instructions
├── index.html              # Landing page (GitHub Pages root)
├── manifest.json           # PWA web manifest
├── sw.js                   # Service Worker (offline shell cache)
├── remote/
│   └── index.html          # Universal Smart TV Remote Control web application
├── server/
│   ├── relay.py            # Local relay server (browser → TV bridge, port 7070)
│   └── mcp-server.py       # FastMCP server & HTTP RPC bridge (port 8000)
├── skills/
│   └── smart-tv-control/   # AI Agent Skill package
│       ├── SKILL.md        # Instructions, MCP signatures, natural language scenarios
│       ├── scripts/
│       │   └── tv_cli.py   # Standalone CLI helper (discover, action, power_on, launch)
│       └── references/
│           ├── brand-protocols.md  # Detailed brand network port & auth specifications
│           └── app-ids.md          # Popular streaming app IDs & HDMI input mappings
├── tests/
│   ├── test_mcp_server.py  # 7-step automated MCP server test suite
│   └── test_lg_tv.py       # 9-step physical hardware validation suite
├── docs/                   # Detailed guides (setup, pairing, brands, troubleshooting, AI)
└── assets/                 # Shared icons, CSS, and styling
```

---

## 🔒 Privacy & Security

- **100% Local**: All commands travel strictly across your local home Wi-Fi network. No telemetry, no external API calls, and no cloud relay servers.
- **Credentials & Tokens**: Pairing keys and tokens are stored exclusively in `tv-tokens/tokens.json` on your local PC.
- **Git Protection**: `tv-tokens/`, `*.token`, `*.key`, and `.env` files are strictly gitignored to prevent accidental credential leakage.

---

## 🧪 Testing & Validation

TV Remote MCP includes automated test suites to ensure reliable performance across hardware and MCP bridges:

```bash
# Test MCP Server (7/7 tests PASS)
python tests/test_mcp_server.py

# Test Physical Hardware (e.g. LG WebOS TV at 192.168.1.11)
python tests/test_lg_tv.py
```

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>1. How do I find my Smart TV's IP address?</b></summary>
On your TV, open <b>Settings &rarr; Network &rarr; Network Status / IP Settings</b>. Look for an address like <code>192.168.1.X</code>. Alternatively, run:
<pre><code>python skills/smart-tv-control/scripts/tv_cli.py discover</code></pre>
</details>

<details>
<summary><b>2. Why does the remote show "TV is offline" when the TV is powered off?</b></summary>
When smart TVs enter standby mode, their main operating system powers down and closes all TCP/WebSocket ports. To wake the TV, tap the Power button or send a Wake-on-LAN command:
<pre><code>python skills/smart-tv-control/scripts/tv_cli.py power_on &lt;TV_IP&gt;</code></pre>
<i>Note: Make sure "Quick Start+" (LG) or "Wake on Wi-Fi" (Samsung/Sony) is enabled in your TV's settings.</i>
</details>

<details>
<summary><b>3. Why do I need the local relay server for LG or Samsung?</b></summary>
Modern web browsers enforce strict security rules (CORS and Mixed Content) that block web pages from opening raw WebSocket connections to local IP addresses on ports like 3001 or 8001. The lightweight Python relay (<code>server/relay.py</code>) runs locally on your PC and acts as a safe bridge.
</details>

<details>
<summary><b>4. Can I use TV Remote MCP without any AI assistant?</b></summary>
Yes! The web remote at <a href="https://projects.shivalgupta.me/tv-remote-mcp/remote/">/remote/</a> works as a standalone remote control for any phone or tablet browser.
</details>

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on code standards, atomic commits, and testing.

## 📄 License

This project is open source and licensed under the [MIT License](LICENSE).
