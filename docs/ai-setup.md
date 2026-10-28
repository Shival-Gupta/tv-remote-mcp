# AI Assistant Integration (MCP Server)

TV Remote MCP provides a Model Context Protocol (MCP) server allowing AI assistants—such as **Claude, Gemini, Antigravity, ChatGPT, and Codex**—to interact with and control your smart TV using natural language.

---

## 1. Quick Start for AI Agents

To equip any AI coding agent with smart TV control capabilities, provide this prompt:

> *"I want to control my smart TV via AI using TV Remote MCP. The relay server is running at `http://localhost:7070` and my TV is at `192.168.1.11` (brand: LG WebOS). Use the MCP tools or HTTP endpoints to control volume, power, navigation, and apps."*

---

## 2. MCP Server Configuration

TV Remote MCP provides a dedicated FastMCP server at `server/mcp-server.py`.

### Installation
```bash
pip install fastmcp pywebostv requests websockets
python server/mcp-server.py --port 8000
```

### Adding to Claude Desktop
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "smart-tv": {
      "command": "python",
      "args": [
        "D:\\Projects\\tv-mcp\\server\\mcp-server.py"
      ],
      "env": {
        "STV_HOST": "0.0.0.0",
        "STV_PORT": "8000"
      }
    }
  }
}
```

---

## 3. Available MCP Tools

| Tool Name | Arguments | Description |
|---|---|---|
| `universal_action` | `host`, `brand`, `action`, `arg` | Execute TV command (`power_off`, `volume_up`, `send_key`, `launch_app`, etc.) |
| `discover` | `network` | Automatically discover smart TVs on local network subnet |
| `list_brands` | *none* | Returns list of supported smart TV brands |

### Natural Language Examples

- *"Turn the TV volume down by 5 steps."*
- *"Launch YouTube on the living room TV."*
- *"Switch TV input to HDMI 2 for the gaming console."*
- *"Turn off the TV when this task finishes."*
