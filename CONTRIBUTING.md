# Contributing to TV Remote MCP

Thanks for your interest! Here's how to contribute.

## Getting Started

1. Fork the repo
2. Clone your fork: `git clone https://github.com/<you>/tv-remote-mcp.git`
3. Create a branch: `git checkout -b feat/your-feature`
4. Make changes
5. Test locally (open `index.html` in a browser, run `python server/relay.py`)
6. Commit with a clear message
7. Push and open a PR

## Guidelines

- **No build tooling** — This project uses vanilla HTML/CSS/JS with Tailwind CDN. No webpack, no bundler, no npm.
- **Phone-first** — The remote control is primarily used on phones. Test at 375px width.
- **Performance** — Every millisecond matters for a remote control. No heavy libraries.
- **One file per concern** — Keep HTML, CSS (in `<style>` or `assets/css/`), and JS (`assets/js/`) separate when files grow large.
- **Atomic commits** — Each commit should do one thing and be deployable.

## Adding a New TV Brand

1. Add protocol handler in `server/relay.py`
2. Add brand option in `remote/index.html`
3. Add pairing guide in `docs/pairing.md`
4. Update the brand table in `README.md`
5. Test with an actual TV if possible

## Reporting Issues

Open a GitHub issue with:
- Your TV brand and model
- Your OS and browser
- What you tried and what happened
- Any console errors (F12 → Console)

## Code of Conduct

Be kind. Be helpful. No brand wars.
