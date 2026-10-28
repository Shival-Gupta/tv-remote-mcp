# Brand Pairing Recipes & Authentication

Certain smart TV operating systems require a one-time authentication or pairing handshake before accepting remote commands. This guide provides exact instructions for each brand.

---

## 1. LG WebOS Pairing

LG Smart TVs enforce cryptographic client registration on port 3000/3001.

### Step-by-Step
1. Turn on your LG TV with your physical remote.
2. In TV Remote MCP, enter your LG TV's IP address and select **LG WebOS**.
3. Tap **Connect**.
4. The relay server initiates registration. A dialog box will appear on the TV screen:
   > **"A device (TV Remote MCP) wants to connect to your TV. Do you want to allow it?"**
5. Use your physical LG Magic Remote or directional buttons to click **"Allow"** / **"Yes"**.
6. The pairing token is automatically stored in `tv-tokens/tokens.json` by the relay. Subsequent commands will execute immediately without prompting again.

### Command Line Pairing Test
You can also trigger pairing manually using Python:
```python
from pywebostv.connection import WebOSClient

client = WebOSClient("192.168.1.11")
client.connect()
store = {}
for status in client.register(store):
    if status == WebOSClient.PROMPTED:
        print("Please approve pairing on your TV screen now...")
    elif status == WebOSClient.REGISTERED:
        print("Successfully paired and registered!")
        print("Client key:", store)
```

---

## 2. Android TV & Fire TV (ADB Pairing)

Android TV and Fire TV require ADB (Android Debug Bridge) authorization.

### Step-by-Step
1. On your TV, navigate to:
   - **Android / Google TV:** Settings &rarr; System &rarr; About &rarr; Scroll down to **Android TV OS build** and tap it **7 times** until you see *"You are now a developer!"*.
   - **Fire TV:** Settings &rarr; My Fire TV &rarr; About &rarr; Click the device name **7 times**.
2. Go back one screen to **Developer Options**.
3. Toggle **USB Debugging** (and **Network Debugging**, if present) to **ON**.
4. When TV Remote MCP or `adb` connects for the first time, a dialog appears on the TV:
   > **"Allow USB debugging? The computer's RSA key fingerprint is: ..."**
5. Check the box for **"Always allow from this computer"** and select **OK**.

---

## 3. Samsung Tizen Pairing

Modern Samsung TVs (2016+) display a notification on first connection:
1. When connecting, your TV will display an overlay:
   > **"A new device 'TV-Remote-MCP' wants to connect. Allow / Deny"**
2. Select **Allow** using your physical remote control.
3. If previously denied, navigate to:
   - TV Settings &rarr; General &rarr; External Device Manager &rarr; Device Connect Manager &rarr; Device List.
   - Locate the device and set permission to **Allow**.

---

## 4. Sony Bravia (Pre-Shared Key)

For Sony Bravia TVs requiring a Pre-Shared Key (PSK):
1. On your TV: Settings &rarr; Network &rarr; Home Network Setup &rarr; IP Control.
2. Set **Authentication** to **Normal and Pre-Shared Key**.
3. Set a simple key (e.g., `0000` or `1234`).
4. If configured, you can specify this PSK in the relay configuration.

---

## 5. Roku (Zero Pairing)

Roku requires **no pairing, no token, and no TV screen prompts**.
Ensure:
- TV Settings &rarr; System &rarr; Advanced system settings &rarr; Control by mobile apps &rarr; **Network access: Default or Permissive**.
