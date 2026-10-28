# Agent Instructions — TV Remote MCP

## Project Overview
Browser-based universal smart TV remote control + MCP server for AI assistants (LG, Samsung, Roku, Android TV, Fire TV, Sony, Vizio, etc.).
- **Installer**: `install.py` (Automated dependencies + MCP setup + Skill registration + verification)
- **Landing page**: `index.html` (GitHub Pages root)
- **Remote control**: `remote/index.html`
- **Local relay**: `server/relay.py` (port 7070)
- **MCP server**: `server/mcp-server.py` (port 8000)
- **Agent Skill**: `skills/smart-tv-control/` & `.agents/skills/smart-tv-control/` & `.claude/skills/smart-tv-control/`

## Automated Agent Installation
When asked to install or configure this repository, run:
```bash
python install.py
```
This automatically installs dependencies from `requirements.txt`, configures Claude Desktop and Cursor, copies skills, runs verification tests, and discovers smart TVs.

## Commit Rules
- **Atomic commits**: Each commit does ONE thing and leaves the project deployable
- **Commit message format**: `type: short description` where type is `feat`, `fix`, `docs`, `style`, `refactor`, `chore`
- **Push after each milestone** to keep GitHub Pages current
- **Never commit**: API keys, pairing tokens, `.env` files, `__pycache__/`, `tv-tokens/`

## Code Rules
- **No build tooling** — Vanilla HTML/CSS/JS. Tailwind via CDN only.
- **No JS frameworks** — No React, Vue, Svelte, etc.
- **Phone-first** — Design for 375px, scale up
- **Performance** — No animation libraries. CSS transitions only. < 200KB total.
- **Touch targets** — Minimum 48×48px on all interactive elements
- **Dark theme** — Background `#0a0a0a`, cards `#141414`, accent `#3b82f6`

## Testing
- Automated MCP server test: `python tests/test_mcp_server.py`
- Hardware validation test: `python tests/test_lg_tv.py`
- Run relay: `python server/relay.py`
- Run MCP: `python server/mcp-server.py`

## Brand Protocol Quick Reference
| Brand | Port | Protocol | Library |
|-------|------|----------|---------|
| LG WebOS | 3000/3001 | WebSocket | pywebostv |
| Samsung | 8001/8002 | HTTP REST | requests |
| Android TV | 5555 | ADB | adb CLI |
| Roku | 8060 | HTTP ECP | requests |
| Fire TV | 5555 | ADB | adb CLI |
| Vizio | 7345/9000 | HTTP REST | requests |
| Sony | 80 | HTTP REST | requests |
