# Agent Instructions — TV Remote MCP

## Project Overview
Browser-based universal smart TV remote control + MCP server for AI assistants.
- **Landing page**: `index.html` (GitHub Pages root)
- **Remote control**: `remote/index.html`
- **Local relay**: `server/relay.py`
- **MCP server**: `server/mcp-server.py` (Phase 2)

## Commit Rules
- **Atomic commits**: Each commit does ONE thing and leaves the project deployable
- **Commit message format**: `type: short description` where type is `feat`, `fix`, `docs`, `style`, `refactor`, `chore`
- **Push after each milestone** to keep GitHub Pages current
- **Never commit**: API keys, pairing tokens, `.env` files, `__pycache__/`

## Code Rules
- **No build tooling** — Vanilla HTML/CSS/JS. Tailwind via CDN only.
- **No JS frameworks** — No React, Vue, Svelte, etc.
- **Phone-first** — Design for 375px, scale up
- **Performance** — No animation libraries. CSS transitions only. < 200KB total.
- **Touch targets** — Minimum 48×48px on all interactive elements
- **Dark theme** — Background `#0a0a0a`, cards `#141414`, accent `#3b82f6`

## File Organization
```
index.html           → Landing page
remote/index.html    → Remote control (self-contained)
server/relay.py      → Local relay server
server/mcp-server.py → MCP server (Phase 2)
docs/                → Markdown documentation
assets/css/          → Shared stylesheets
assets/js/           → Shared scripts
assets/icons/        → SVG icons
```

## Testing
- Open HTML files directly in browser for visual check
- Run `python server/relay.py` for relay testing
- Test remote on mobile viewport (Chrome DevTools → 375×812 iPhone)
- Verify GitHub Pages deployment after push

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
