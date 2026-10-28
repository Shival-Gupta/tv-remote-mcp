# Setup Guide — TV Remote MCP

This guide walks you through connecting your smart TV to TV Remote MCP using either direct browser control or the local relay server.

---

## 1. Network Requirements

For TV Remote MCP to work, **your phone/computer and your Smart TV must be on the same local Wi-Fi / LAN network**.

- Ensure your phone is not on a Guest network or mobile data (4G/5G).
- Ensure AP Isolation (Client Isolation) is disabled on your Wi-Fi router so LAN devices can communicate with each other.

---

## 2. Quick Setup (Browser Remote)

1. Open **[Shival-Gupta.github.io/tv-remote-mcp/remote/](https://Shival-Gupta.github.io/tv-remote-mcp/remote/)** on your phone or computer.
2. Tap the connection bar at the top or open **Settings**.
3. Enter your TV's local IP address (e.g. `192.168.1.11`).
   - *How to find TV IP:* TV Settings &rarr; Network &rarr; Connection Status / IP Settings.
4. Select your TV brand from the list.
5. Tap **Save & Connect**.

> **Note on Browser Capabilities:**  
> Roku TVs support direct HTTP control from the browser without any extra software. Most other brands (LG WebOS, Samsung Tizen, Android TV, Fire TV, Vizio, Sony) require the **Local Relay Server** because web browsers block raw TCP/WebSocket ports for security.

---

## 3. Local Relay Server Setup (Recommended)

The local relay server (`server/relay.py`) is a lightweight, zero-configuration Python script that runs on any computer (Windows, macOS, Linux, or Raspberry Pi) on your home network. It translates browser commands into native TV protocols.

### Prerequisites
- Python 3.8 or newer
- `pip` (Python package installer)

### Installation

```bash
# Clone the repository
git clone https://github.com/Shival-Gupta/tv-remote-mcp.git
cd tv-remote-mcp

# Run the automated installer (installs dependencies + configures MCP & skills)
python install.py

# Start the relay server
python server/relay.py
```

By default, the relay starts at `http://0.0.0.0:7070` and binds to all network interfaces on your PC.

### Connecting the Web Remote to Your Relay

- If using the web remote on the **same PC**: The default relay URL `http://localhost:7070` works automatically.
- If using the web remote on your **phone**:
  1. Note the PC's local IP printed in the relay startup banner (e.g. `192.168.1.15`).
  2. In the remote web app on your phone, tap **Settings (⚙)**.
  3. Change the Relay Server URL to `http://192.168.1.15:7070`.
  4. Tap **Test**. The relay indicator will turn green (`Relay OK`).

---

## 4. Automatic Network Discovery

With the relay running:
1. Open the remote setup dialog.
2. Tap the **Scan** button next to the IP address input.
3. The relay will scan standard TV control ports across your subnet and list discovered devices.
4. Tap your TV from the list to populate its IP and brand automatically.
