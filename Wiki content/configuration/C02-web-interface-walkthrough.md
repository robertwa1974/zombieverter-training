# C02 — The Web Interface Walkthrough

**Track:** Firmware & Configuration  
**Prerequisites:** H01 — VCU Hardware Walkthrough  
**Audience:** All levels  
**Estimated reading time:** 10 minutes

---

## Overview

All ZombieVerter configuration is done through a browser-based web interface served by the on-board ESP8266 Wi-Fi module. There is no desktop software to install, no USB cable required for normal operation, and no command line interaction needed for day-to-day use.

---

## Connecting to the Web Interface

### Minimum Requirements for First Power-Up
- A fully built ZombieVerter VCU
- Two wires connecting Pin 55 (ground) and Pin 56 (12V+) to a stable 12V supply
- A computer, tablet, or phone with Wi-Fi

### Step-by-Step

1. Apply stable 12V power to Pins 55 and 56
2. The `acty` LED on the board should begin **flashing** — this confirms the MCU is running
3. On your device, scan for Wi-Fi networks and connect to the ZombieVerter access point:
   - **SSID:** `inverter` or `zom_vcu` (varies by firmware version)
   - **Password:** `inverter123`
4. Open a browser and navigate to: **`192.168.4.1`**
5. The openinverter web interface should load

### If You Cannot Connect

**Symptom: Wi-Fi network appears but browser cannot reach 192.168.4.1**

Some recent boards use a new Wi-Fi module variant that does not automatically assign your device an IP address via DHCP. If this happens:

- Manually set your device's IP address to `192.168.4.2` (or any address in the `192.168.4.x` range other than `.4.1`)
- Set the subnet mask to `255.255.255.0`
- Set the gateway to `192.168.4.1`
- Try the browser again

**Symptom: `acty` LED is not flashing**

The MCU is not running. Check:
- 12V is present on Pin 56
- Ground is present on Pin 55
- If the board previously had a failed firmware update, it may need ST-Link recovery (see Module C01)

---

## Interface Layout

The web interface is divided into several sections. The exact layout varies slightly between firmware versions, but the core structure is consistent.

### Top Bar
Displays:
- Firmware version (if this shows `null`, the firmware is corrupted — see Module C01)
- Current VCU status / opmode
- Live spot values for key parameters (UDC, motor RPM, etc.)

### Parameters Tab
The main configuration area. Parameters are grouped into categories:

| Category | What's in it |
|---|---|
| **Motor** | Throttle limits, ramp rates, rev limiter, direction mode |
| **Charger** | Charger type, charge current limits, charge timer settings |
| **Comms** | CAN bus assignments, inverter type, shunt type, ISA mode, CANID settings |
| **Throttle** | potmin, potmax, pot2min, pot2max, potmode |
| **Din** | Configurable digital input pin assignments |
| **Dout** | Configurable digital output pin assignments |
| **Temps** | Temperature setpoints for fan, pump, heater enable |
| **Contactors** | udcmin, udclim, udcsw, shunt type |
| **BMS** | BMS current limits, cell voltage limits |

### Spot Values Tab
Live read-only values from the VCU. Essential for diagnostics and calibration. Key spot values:

| Spot Value | What it shows |
|---|---|
| `pot` | Raw ADC reading from throttle channel 1 |
| `pot2` | Raw ADC reading from throttle channel 2 |
| `potnom` | Normalised throttle position (0–100) |
| `udc` | HV bus voltage from shunt |
| `invudc` | HV voltage reported by the inverter |
| `idc` | DC current from shunt |
| `opmode` | Current VCU operating mode |
| `invstat` | Inverter status |
| `din_brake` | Brake input state (must be "off" for torque) |
| `din_forward` | Forward input state |
| `din_reverse` | Reverse input state |
| `din_start` | Start input state |
| `speed` | Motor speed (RPM) |
| `torque` | Requested torque |
| `temphs` | Heatsink temperature |
| `tempm` | Motor temperature |
| `PPVal` | Proximity pilot ADC value (if used) |

### Logging / Graphing
The interface includes a real-time graphing capability. Select which spot values to plot, set the update interval, and watch live traces. Useful for:
- Verifying throttle linearity
- Watching precharge voltage rise
- Diagnosing temperature issues
- Tuning regen behaviour

### Save / Load
Parameters can be saved to flash (persistent across power cycles) or exported/imported as JSON files. Always **save to flash** after changing parameters — changes held only in RAM are lost on power cycle.

---

## Parameter Workflow

The typical workflow for any configuration change:

1. Make the change in the Parameters tab
2. Observe the effect in Spot Values (some changes take effect immediately)
3. When satisfied, click **Save to Flash**
4. Reboot if required (some parameters only take effect after reboot)

> **Always save to flash before testing with HV.** A power interruption during testing will otherwise revert your configuration.

---

## Configuring Input/Output Pin Functions

Digital input and output pin assignments are made through the `Din` and `Dout` parameter categories. This is where you tell the VCU what function each configurable pin serves.

**Important:** The web interface does not prevent you from making invalid assignments — for example, assigning an output function to an input-only pin. The VCU will accept the assignment but the hardware will not respond. Always verify that your assignment matches the physical pin type (see Module H01 for the pin type table).

---

## Inverter Type Selection

One of the first and most important settings is the `inverter` parameter under **Comms**. This tells the VCU which motor control protocol to use:

| Value | Inverter |
|---|---|
| 0 | None — no inverter connected |
| 1 | Nissan Leaf Gen1/2/3 (CAN) |
| 2 | Lexus GS450h (sync serial) |
| 3 | UserCAN — not currently used |
| 4 | OpenInverter board (CAN) |
| 5 | Toyota Prius Gen3 (sync serial) |
| 6 | Outlander — deprecated |
| 7 | Lexus GS300h (sync serial) |
| 8 | Mitsubishi Outlander rear (CAN) |

Set this before attempting to communicate with your inverter.

---

## Vehicle Integration Type

The `vehicle` parameter selects the CAN profile for dashboard/instrument cluster integration:

| Value | Vehicle |
|---|---|
| 0 | BMW E46 |
| 1 | BMW E6x+ (E60, E90, etc.) |
| 2 | Classic — digital IO only, no vehicle CAN |
| 3 | None |
| 5 | BMW E39 |
| 6 | VAG |
| 7 | Subaru |
| 8 | BMW E31 |

If you are not integrating with an OEM instrument cluster, set this to `None` or `Classic`.

---

## ESP32 CAN Bus Web Interface (Alternative)

The VCU also supports an ESP32-based CAN bus web interface as an alternative to the built-in ESP8266. If you use this:

- The Node ID is **hard-coded to 3**
- Note that the FOCCCI (CCS charge controller) has a default Node ID of 22 — no conflict, but be aware if you are also using FOCCCI

---

## What's Next

- **C03** — Essential Parameters: First Start
- **C04** — Throttle Calibration

---

*Source: openinverter.org/wiki/ZombieVerter_VCU*  
*Last verified against firmware: V2.30A (August 2025)*
