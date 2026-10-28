# Smart TV Brand Protocols Reference

Comprehensive reference of supported smart TV brands, network protocols, default ports, authentication mechanisms, and quirks.

---

## Brand Protocol Matrix

| Brand Identifier | Platform | Default Port(s) | Protocol | Auth Type | Native Control Library |
|---|---|---|---|---|---|
| `lg` | LG WebOS (3.0+) | `3001` (SSL) / `3000` (Plain) | WebSocket (`wss://` / `ws://`) | Pairing Key (`client_key`) | `pywebostv` |
| `samsung` | Tizen OS (2016+) | `8002` (SSL) / `8001` (Plain) | WebSocket + HTTP REST | Token / Pairing Dialog | `requests` / `websocket` |
| `roku` | Roku OS | `8060` | HTTP External Control Protocol (ECP) | None (Open REST) | Standard HTTP (`POST /keypress/`) |
| `android` | Android TV / Google TV | `5555` | ADB (Android Debug Bridge) | RSA Key Confirmation | `adb CLI` |
| `fire_tv` | Fire OS | `5555` | ADB | RSA Key Confirmation | `adb CLI` |
| `sony` | Sony Bravia (Android/Linux) | `80` | IRCC-over-HTTP (SOAP REST) | Pre-Shared Key (PSK) or PIN | Standard HTTP (`POST /sony/IRCC`) |
| `vizio` | SmartCast OS | `7345` / `9000` | HTTPS REST | Auth Token (PIN pairing) | Standard HTTPS (`PUT /key_command/`) |
| `philips` | JointSPACE OS | `1925` / `1926` | HTTP / HTTPS REST | Digest Auth / PIN | Standard HTTP |
| `panasonic` | Viera OS | `55000` | HTTP SOAP | None / PIN | Standard HTTP |
| `tcl` | Android TV / Roku OS | `5555` or `8060` | ADB or Roku ECP | OS Dependent | Standard HTTP / `adb` |

---

## Detailed Brand Specifications

### 1. LG WebOS (`lg`)
- **Transport**: WebSocket connection to `wss://<ip>:3001` (fallback to `ws://<ip>:3000` on WebOS <4.0).
- **Authentication**: On first connection, TV displays a pairing prompt asking "Allow connection?". User clicks "Yes" with LG Magic Remote. The TV assigns a `client_key` string, saved in `tv-tokens/tokens.json`.
- **Power On**: LG TVs completely close network listening sockets when powered off (Standby mode). To turn on, send a **Wake-on-LAN (WoL)** magic packet burst containing the TV's MAC address to port 9 on `255.255.255.255` and the TV's IP.
- **Power Off**: Supported via WebSocket `ssap://system/turnOff`.
- **Latency**: TV takes 5 to 15 seconds to connect to Wi-Fi after waking up via WoL.
- **SSL Fallback**: WebOS 4.0+ enforces TLS 1.2+ certificates. Always try port 3001 first with SSL bypass.

### 2. Samsung Tizen (`samsung`)
- **Transport**: WebSocket connection to `wss://<ip>:8002/api/v2/channels/samsung.remote.control?name=<base64_name>&token=<token>`.
- **Authentication**: TV displays an onscreen authorization popup. Once accepted, Samsung returns a token string.
- **Power Off**: Send key `KEY_POWER`.
- **Power On**: Wake-on-LAN (WoL) to TV MAC address.

### 3. Roku TV (`roku`)
- **Transport**: Zero-authentication HTTP REST on port `8060`.
- **Protocol**: HTTP External Control Protocol (ECP).
- **Commands**:
  - Keypress: `POST http://<ip>:8060/keypress/<KEY>` (e.g., `Home`, `Rev`, `Fwd`, `Play`, `Select`, `Left`, `Right`, `Down`, `Up`, `Back`, `VolumeUp`, `VolumeDown`, `VolumeMute`, `PowerOff`, `PowerOn`).
  - Launch App: `POST http://<ip>:8060/launch/<app_id>`.
  - Query Apps: `GET http://<ip>:8060/query/apps`.
  - Device Info: `GET http://<ip>:8060/query/device-info`.

### 4. Android TV / Fire TV (`android`, `fire_tv`)
- **Transport**: Port `5555` via Android Debug Bridge (`adb`).
- **Setup**: Developer Options -> USB Debugging / Network Debugging enabled on TV.
- **Commands**:
  - Connect: `adb connect <ip>:5555`
  - Keys: `adb -s <ip>:5555 shell input keyevent <key_code>`
    - `26`: Power Toggle
    - `24`: Volume Up
    - `25`: Volume Down
    - `164`: Mute
    - `19` / `20` / `21` / `22`: Up / Down / Left / Right
    - `23` / `66`: Select / Enter
    - `3`: Home
    - `4`: Back
    - `126` / `127` / `86`: Play / Pause / Stop
  - Launch App: `adb -s <ip>:5555 shell monkey -p <package_name> -c android.intent.category.LAUNCHER 1`

### 5. Sony Bravia (`sony`)
- **Transport**: HTTP POST SOAP on port `80` to `http://<ip>/sony/IRCC`.
- **Header**: `X-Auth-PSK: <pre_shared_key>` (configured in TV Settings -> Network -> Home Network Setup -> IP Control -> Pre-Shared Key).
- **Body**: XML envelope containing IRCC code (e.g., `AAAAAQAAAAEAAAAVAw==` for PowerOff).

---

## Wake-on-LAN (WoL) Implementation Rules

1. **Magic Packet Format**: 6 bytes of `0xFF` followed by 16 repetitions of the target 6-byte MAC address (total 102 bytes).
2. **Multi-Target Broadcast**:
   - Send to global broadcast `255.255.255.255:9`
   - Send to subnet broadcast (e.g. `192.168.1.255:9`)
   - Send to unicast IP (`<ip>:9`)
3. **Burst Sequence**: Transmit 5 consecutive packets with 20–25ms intervals to penetrate TV Wi-Fi power-save sleep intervals.
4. **MAC Storage**: Always cache MAC address in `tv-tokens/tokens.json` upon successful discovery or pairing so WoL succeeds even when ARP cache entries expire while TV is asleep.
