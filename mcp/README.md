# AI Assistant MCP Configurations

This directory contains pre-built configuration files to connect **TV Remote MCP** to AI assistants like Claude Desktop, Cursor, Antigravity, and Gemini.

---

## 1. Claude Desktop Setup

1. Open your Claude Desktop configuration file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add the configuration from `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "tv-remote": {
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
3. Restart Claude Desktop. The hammer/tools icon will appear with `universal_action`, `discover`, and `list_brands`.

---

## 2. Antigravity / Gemini CLI Setup

Include `mcp/gemini_mcp.json` or register as a local command:

```bash
python server/mcp-server.py --port 8000
```

---

## 3. Available AI Tools

| Tool Name | Parameters | Description |
|---|---|---|
| `universal_action` | `host`, `brand`, `action`, `arg` | Send TV action (`power_on`, `power_off`, `volume_up`, `mute`, `launch_app`, `set_input`, etc.) |
| `discover` | *none* | Scan local network subnet for smart TVs |
| `list_brands` | *none* | Enumerate all 10+ supported smart TV brands |

### Sample Prompts

- *"Mute the living room TV."*
- *"Turn the TV volume down by 3."*
- *"Switch the TV input to HDMI 2."*
- *"Wake up the LG TV."*
- *"Launch YouTube on the TV."*
