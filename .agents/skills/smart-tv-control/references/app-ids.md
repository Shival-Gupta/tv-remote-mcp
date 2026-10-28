# Smart TV App Identifiers Reference

Lookup table of application package names, app IDs, and input identifiers across smart TV platforms.

---

## 1. Popular Streaming Apps

| Application | LG WebOS ID | Roku App ID | Android TV / Fire TV Package | Apple TV URL Scheme |
|---|---|---|---|---|
| **YouTube** | `youtube.leanback.v4` | `837` | `com.google.android.youtube.tv` | `youtube://` |
| **Netflix** | `netflix` | `12` | `com.netflix.ninja` | `nflx://` |
| **Amazon Prime Video** | `amazon` | `13` | `com.amazon.amazonvideo.livingroom` | `aiv://` |
| **Disney+** | `com.disney.disneyplus-prod` | `291097` | `com.disney.disneyplus` | `disneyplus://` |
| **Spotify** | `spotify-beehive` | `22271` | `com.spotify.tv.android` | `spotify://` |
| **Apple TV+** | `com.apple.appletv` | `551012` | `com.apple.atve.androidtv.appletv` | `appletv://` |
| **Hulu** | `hulu` | `2285` | `com.hulu.livingroomplus` | `hulu://` |
| **HBO Max / Max** | `com.wbd.stream` | `61322` | `com.wbd.stream` | `max://` |
| **Twitch** | `com.twitch.tv.android` | `10202` | `tv.twitch.android.app` | `twitch://` |
| **Plex** | `cdp-30` | `13535` | `com.plexapp.android` | `plex://` |
| **Web Browser** | `com.webos.app.browser` | *(N/A)* | `org.chromium.chrome` | *(N/A)* |

---

## 2. Input Source Identifiers

### LG WebOS Inputs
Use `set_input` with one of the following input strings:
- `HDMI_1` / `com.webos.app.hdmi1`
- `HDMI_2` / `com.webos.app.hdmi2`
- `HDMI_3` / `com.webos.app.hdmi3`
- `HDMI_4` / `com.webos.app.hdmi4`
- `com.webos.app.livetv` (Live TV Antenna/Cable)
- `com.webos.app.externalinput.av1` (Composite AV)

### Roku TV Inputs
Use `launch_app` or keypress with Roku input IDs:
- `tvinput.hdmi1`
- `tvinput.hdmi2`
- `tvinput.hdmi3`
- `tvinput.hdmi4`
- `tvinput.dtv` (Tuner TV)
- `tvinput.cvbs` (AV Input)

### Android TV / Sony Bravia Inputs
Send intent via ADB:
- `adb shell am start -a android.intent.action.VIEW -d "content://android.media.tv/passthrough/com.sony.dtv.tvinput.hdmi%2F.HdmiInputService%2FHW1"` (Sony HDMI 1)
- Generic: Send `TV_INPUT` key (`keycode 178`) or D-pad navigate input menu.
