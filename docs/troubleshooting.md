# Troubleshooting & FAQ

Common solutions and diagnosis steps when setting up or using TV Remote MCP.

---

## 1. Remote Says "Relay Required" or "Command Failed"

### Cause
Web browsers enforce strict security rules (CORS, mixed content, private network access restrictions) that prevent client-side JavaScript on a website from arbitrarily reaching private LAN ports like `3000`, `8001`, or `5555`.

### Solution
1. Start the local relay server on your computer:
   ```bash
   python server/relay.py
   ```
2. Check that the relay is running by visiting `http://localhost:7070/api/health` in your browser. It should respond with `{"status": "ok", "version": "1.0.0"}`.
3. If using the web remote on your phone, update the Relay URL in Remote Settings to `http://<YOUR_PC_IP>:7070` instead of `localhost`.

---

## 2. "Connection Refused" or "Host Unreachable"

### Diagnosis Checklist
1. **Is the TV turned on?**
   - Most smart TVs turn off their Wi-Fi chip in deep sleep mode unless "Wake on Wi-Fi / Mobile TV On" is enabled.
2. **Did the TV's IP address change?**
   - Home Wi-Fi routers frequently reassign DHCP IP addresses. Verify your TV's current IP address in TV Settings &rarr; Network.
   - *Recommendation:* Assign a **Static IP / DHCP Reservation** to your TV in your router settings.
3. **Are you on the same Wi-Fi network?**
   - Ensure your phone/PC is on the same 2.4GHz or 5GHz SSID as your TV, and not on a Guest network.
4. **Is AP Isolation enabled?**
   - Some routers prevent wireless clients from communicating with each other. Disable "AP Isolation" or "Client Isolation" in your router admin console.

---

## 3. LG TV Keeps Disconnecting or Asking for Pairing

### Cause
LG WebOS issues a unique client key during pairing. If this key is lost or rejected, the TV requires re-pairing.

### Solution
1. Remove stale tokens by deleting `tv-tokens/tokens.json`.
2. On your LG TV, navigate to:
   - Settings &rarr; General &rarr; External Devices &rarr; Connect to Mobile Phone &rarr; Turn ON **"Mobile TV On"** and **"Turn on via Wi-Fi"**.
3. Trigger pairing again in the web remote.

---

## 4. Turning the TV ON (Wake-on-LAN)

When a smart TV is powered off, its operating system is not actively running its HTTP or WebSocket servers. To turn it on remotely:
1. Make sure **"Quick Start+"** or **"Turn on via Wi-Fi / Mobile"** is enabled in your TV's power settings.
2. TV Remote MCP's relay includes built-in **Wake-on-LAN (WOL)** magic packet broadcasting when you tap **Power On**.
3. If WOL does not wake your TV, ensure your TV is connected via Ethernet cable or supports Wi-Fi WoWLAN.

---

## 5. Android TV / Fire TV ADB Issues

If ADB commands fail:
```bash
# Verify ADB is installed and can reach your TV
adb connect 192.168.1.XX:5555
adb devices
```
If the status shows `unauthorized`:
- Look at your TV screen and accept the ADB debugging prompt.
If the status shows `offline`:
- Disconnect and reconnect: `adb disconnect 192.168.1.XX:5555 && adb connect 192.168.1.XX:5555`.
