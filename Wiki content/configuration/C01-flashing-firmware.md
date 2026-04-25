# C01 — Flashing Firmware

**Track:** Firmware & Configuration  
**Prerequisites:** None (standalone reference module)  
**Audience:** All levels  
**Estimated reading time:** 10 minutes

---

## Do You Need This Module?

**Probably not.** Boards purchased from the EVBMW webshop come pre-programmed and ready to use. You do not need to flash firmware before first use on a new board.

You need this module if:
- You have a blank/unprogrammed board
- The web interface shows `firmware: null`
- A firmware update failed partway through and the board is unresponsive
- You want to run a specific firmware version

---

## Know Your Chip

Before doing anything with firmware, identify which microcontroller is on your board.

| Chip | Markings | Notes |
|---|---|---|
| **STM32F107** | ST logo + STM32F107 | Standard chip — use main firmware branch |
| **GD32F107** | GD logo + GD32F107 | Pandemic-era substitute — requires separate firmware branch |

The GD32F107 ("GD chip") was used on some boards produced during the 2021–2022 semiconductor shortage. A separate firmware branch (`GD_Zombie`) exists on GitHub but development was abandoned shortly after release. As of the current main firmware (V2.20A), the GD branch has substantially diverged and is not kept up to date. **If you have a GD board, you are limited to an older firmware version and will miss recent features.**

If you are unsure which chip you have, look at the main IC on the board under good lighting. The manufacturer logo and chip number are printed on the chip.

---

## Normal Firmware Update (Web Interface)

For routine firmware updates on a working board, use the web interface. No external tools required.

**Steps:**
1. Download the latest firmware `.bin` file from the [GitHub releases page](https://github.com/damienmaguire/Stm32-vcu/releases)
2. Connect to the VCU via Wi-Fi
3. Navigate to `192.168.4.1` in your browser
4. Find the **UART Update** field in the interface
5. Select your `.bin` file
6. Upload and wait for the update to complete

**Important notes:**
- The file must be named `stm32_vcu.bin` — rename it if it has a version suffix
- Windows 10 has known reliability issues with the UART update method. If you are on Windows 10, consider using Ubuntu (WSL2 is fine) or switching to the ST-Link method if the UART update fails
- Do not power-cycle the board mid-update

**Verifying success:**
After reboot, connect to the web interface and check the firmware version displayed at the top of the page. If it shows `firmware: null`, the update failed and you will need to use the ST-Link recovery method below.

---

## Full Recovery via ST-Link (Bricked Board)

Use this method if:
- The web interface shows `firmware: null`
- The board is completely unresponsive (no Wi-Fi, `acty` LED not flashing)
- UART update failed and board will not boot

### What You Need
- ST-Link V2 dongle (cheap clones from Amazon/AliExpress work, though results vary)
- STM32CubeProgrammer software (free, from ST Microelectronics)
- Bootloader `.hex` file (from [Johannes Huebner's bootloader repo](https://github.com/jsphuebner/tumanako-inverter-fw-bootloader/releases))
- Latest ZombieVerter firmware `.hex` file (from [Damien's GitHub releases](https://github.com/damienmaguire/Stm32-vcu/releases/))
- 12V power supply for the VCU

> Use `.hex` files for ST-Link flashing (not `.bin`). The `.hex` format includes address information so STM32CubeProgrammer places the data correctly without you needing to manually specify flash addresses.

### Procedure

1. **Download STM32CubeProgrammer** from the ST website and install it
2. **Upgrade your ST-Link firmware** using STM32CubeProgrammer — not strictly required but recommended
3. **Disconnect the Wi-Fi module** from the VCU board (gently pull the ESP8266 module from its socket) — this eliminates one potential source of interference during flashing
4. **Connect ST-Link to the VCU SWD test points:**

```
ST-Link pin    →    VCU test point
SWCLK          →    C
GND            →    G
SWDIO          →    D
```

5. **Apply 12V power** to the VCU (Pins 55 and 56) — the ST-Link alone does not power the board
6. **Open STM32CubeProgrammer** and connect to the device via the ST-Link interface — you should see the chip detected
7. **Perform a full chip erase** — this wipes all existing flash content including any corrupted firmware
8. **Flash the bootloader** `.hex` file first
9. **Flash the firmware** `.hex` file second
10. **Disconnect the ST-Link**
11. **Reconnect the Wi-Fi module**
12. Power cycle the VCU and verify the Wi-Fi access point appears and the web interface loads

### If STM32CubeProgrammer Cannot Connect
- Check your SWD wiring — SWCLK and SWDIO are often swapped
- Try a different ST-Link clone — quality varies widely
- Ensure 12V is present on the VCU before attempting to connect
- Try with the Wi-Fi module disconnected if you haven't already

---

## Serial Connection Parameters

If you use a serial terminal to communicate with the VCU (for diagnostics or the serial parameter interface):

```
Baud rate:  115200
Data bits:  8
Parity:     None
Stop bits:  2   ← This is unusual! Most tools default to 1 stop bit.
Flow ctrl:  None
```

The 2 stop bits is a common gotcha — if your serial terminal is not receiving coherent data, check the stop bit setting first.

---

## Firmware Sources

| What | Where |
|---|---|
| Latest stable firmware (`.bin` and `.hex`) | github.com/damienmaguire/Stm32-vcu/releases |
| Bootloader (`.hex`) | github.com/jsphuebner/tumanako-inverter-fw-bootloader/releases |
| GD32F107 firmware (older, unsupported) | github.com/damienmaguire/Stm32-vcu/tree/GD_Zombie |
| STM32CubeProgrammer | st.com/en/development-tools/stm32cubeprog.html |

Always use a released version unless you have a specific reason to build from source. The GitHub releases page lists changelogs so you can see what changed between versions.

---

## Building From Source (Advanced)

If you want to compile your own firmware from the repository:

```bash
git clone --recurse-submodules git@github.com:damienmaguire/Stm32-vcu.git
```

The `--recurse-submodules` flag is critical — it pulls in `libopeninv` and other dependencies. Without it, the build will fail with missing includes.

GD32F107 boards require specific code modifications — see the forum thread linked in the wiki before attempting to compile for a GD board.

---

## What's Next

- **C02** — The Web Interface Walkthrough: navigating the UI once the board is running
- **C03** — Essential Parameters: First Start

---

*Source: openinverter.org/wiki/ZombieVerter_VCU | openinverter.org/wiki/Zombieverter_programing*  
*Last verified against firmware: V2.30A (August 2025)*
