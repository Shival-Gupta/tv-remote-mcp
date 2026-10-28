# Supported Brands & Protocol Matrix

TV Remote MCP supports 10+ smart TV operating systems and hardware brands. This document details the protocols, default ports, and feature support for each brand.

---

## Brand Compatibility Matrix

| Brand / OS | Protocol | Port(s) | Pairing Required | Direct Browser | Relay Required |
|---|---|---|:---:|:---:|:---:|
| **LG WebOS** | WebSocket (`pywebostv`) | 3000 / 3001 | ✅ On-screen prompt | ❌ | ✅ |
| **Samsung Tizen** | REST & WebSocket | 8001 / 8002 | ⚠️ Auto session / token | ❌ | ✅ |
| **Roku TV & Stick** | HTTP ECP | 8060 | ❌ None | ✅ Direct | Optional |
| **Android TV / Google TV** | ADB (Android Debug Bridge) | 5555 | ⚠️ USB debugging enabled | ❌ | ✅ |
| **Amazon Fire TV** | ADB | 5555 | ⚠️ USB debugging enabled | ❌ | ✅ |
| **Vizio SmartCast** | HTTP REST | 7345 / 9000 | ❌ None for basic keys | ❌ | ✅ |
| **Sony Bravia** | HTTP IRCC SOAP | 80 | ❌ None (or PSK) | ❌ | ✅ |
| **Philips (JointSpace)** | HTTP REST | 1925 / 1926 | ⚠️ Firmware dependent | ❌ | ✅ |
| **Panasonic Viera** | HTTP SOAP | 55000 / 8080 | ❌ None | ❌ | ✅ |
| **TCL / Hisense** | ADB / HTTP ECP / REST | 5555 / 8060 | ⚠️ Depends on OS variant | ⚠️ Roku models yes | ✅ |

---

## Brand Details

### 1. LG WebOS
- **Supported Models:** All LG Smart TVs running webOS 3.0, 4.0, 5.0, 6.0, 22, 23, and 24.
- **Protocol:** Secure WebSocket over port 3000 (HTTP handshake on 3001).
- **Features:** Power off, Volume up/down/mute, D-Pad navigation, Media play/pause/stop, App launching (Netflix, YouTube, Prime, etc.), Input switching (HDMI 1–4, AV), Channel controls.
- **Pairing:** First connection prompts on the TV screen: *"Allow pairing with TV Remote MCP?"*. Select **Allow** using your TV remote. The relay securely caches the pairing key in `tv-tokens/tokens.json`.

### 2. Samsung Tizen
- **Supported Models:** 2016+ Tizen models (K-series and newer).
- **Protocol:** REST endpoint on port 8001 with WebSocket channel on `/api/v2/channels/samsung.remote.control`.
- **Features:** Power, Volume, Mute, D-Pad, Media controls, App switching, Key input.

### 3. Roku TV & Streaming Players
- **Supported Models:** TCL Roku TV, Hisense Roku TV, Onn Roku TV, Sharp Roku TV, Roku Express, Premiere, Streaming Stick, and Ultra.
- **Protocol:** Roku External Control Protocol (ECP) over HTTP port 8060.
- **Features:** Full D-Pad navigation, Media playback, Volume, Power, Direct App launching via channel IDs.
- **Direct Browser Control:** Because Roku ECP accepts HTTP POST requests without CORS preflight barriers on keypress endpoints, Roku is the only brand capable of receiving commands directly from your mobile browser without running `relay.py`.

### 4. Android TV & Google TV
- **Supported Models:** Sony Google TV, TCL Google TV, Hisense Android TV, Xiaomi Mi TV, Chromecast with Google TV, NVIDIA Shield TV.
- **Protocol:** ADB shell key events (`adb -s IP:5555 shell input keyevent ...`).
- **Prerequisite:** Enable **Developer Options** on your TV and turn on **Network Debugging / ADB Debugging**.

### 5. Amazon Fire TV
- **Supported Models:** Fire TV Stick, Fire TV Cube, Fire TV Edition smart TVs (Insignia, Toshiba).
- **Protocol:** ADB shell key events over port 5555.
- **Prerequisite:** Settings &rarr; My Fire TV &rarr; Developer Options &rarr; **ADB Debugging: ON**.

### 6. Sony Bravia
- **Supported Models:** Sony Bravia Smart TVs (Android TV and Linux-based).
- **Protocol:** Sony IRCC (Infrared Compatible Control) protocol over HTTP port 80.
- **Features:** Complete key emulation, input selection, power state.

### 7. Vizio SmartCast
- **Supported Models:** All SmartCast-enabled Vizio displays.
- **Protocol:** JSON-over-HTTP REST on port 7345 or 9000.
- **Features:** Emulates native remote key codesets.
