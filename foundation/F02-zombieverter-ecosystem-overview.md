# F02 — ZombieVerter Ecosystem Overview

**Track:** Foundation  
**Prerequisites:** F01 — What is a VCU and Why Do You Need One  
**Audience:** All levels  
**Estimated reading time:** 10 minutes

---

## What Is the ZombieVerter?

The ZombieVerter is an open-source Vehicle Control Unit (VCU) designed specifically for DIY electric vehicle conversions. It was created by Damien Maguire (EVBMW) with contributions from the broader openinverter.org community.

Its core purpose is to solve a real problem: modern EV conversion projects often reuse salvaged components — motors, inverters, chargers, battery packs — from wrecked or retired EVs. Each of these components uses different control signals and communication protocols. Building a custom controller for every possible combination would be impractical. The ZombieVerter instead provides a general-purpose VCU with a wide variety of inputs, outputs, and pre-built support for the most common donor vehicle components.

In short: **the ZombieVerter is the brain that makes mismatched salvaged EV parts work together.**

---

## The People Behind It

| Person / Group | Role |
|---|---|
| **Damien Maguire (EVBMW)** | Primary hardware designer, firmware lead, project creator |
| **Johannes Huebner (johu)** | Creator of the underlying openinverter firmware framework the VCU builds on |
| **openinverter.org community** | Ongoing firmware contributions, inverter support classes, testing, documentation |

The project is genuinely open-source. Schematics and firmware are available on GitHub. PCB design files for the current production revision (V1.a) are available through Damien's Patreon at the Design Files tier.

---

## Where the Community Lives

| Resource | URL | What's There |
|---|---|---|
| **Main wiki** | openinverter.org/wiki | Hardware docs, wiring guides, parameter references |
| **Forum** | openinverter.org/forum | Support threads, development discussion, build logs |
| **GitHub (firmware)** | github.com/damienmaguire/Stm32-vcu | Source code, firmware releases |
| **GitHub (hardware V1)** | github.com/damienmaguire/Stm32-vcu/tree/master/Hardware/Zombie | PCB files (V1 only) |
| **EVBMW Webshop** | evbmw.com | Boards for purchase |
| **Damien's YouTube** | youtube.com/@Evbmw | Build videos, firmware walkthroughs |
| **Patreon** | patreon.com/evbmw | PCB design files (V1.a), early access content |

> **Note:** The forum is the single best source for troubleshooting. Most problems have been encountered and solved by someone before. Search before posting.

---

## Hardware Features

The ZombieVerter VCU is built around an STM32F107 microcontroller (or GD32F107 on some early pandemic-era boards — see Module C01 for the distinction). An ESP8266 Wi-Fi module provides the wireless interface.

**On-board interfaces:**
- On-board Wi-Fi (ESP8266)
- 3× CAN bus interfaces
- LIN bus
- Synchronous serial interface (used for GS450h, GS300h, Prius)
- OBD-II interface
- 3× high-side PWM driver outputs
- 5× low-side outputs
- 3× ground-pull input pins

**Connector:** 56-pin Aptiv (formerly Delphi) connector. Part numbers:
- Connector (cable side): Aptiv 56-pin connector
- Header (board side): Aptiv 56-pin header
- Terminal removal tool: Aptiv/Delphi Part No. 210S048

---

## Software Features

All configuration is done through a browser-based web interface — no laptop software to install, no USB cables required for normal operation. You connect to the VCU's Wi-Fi access point and navigate to its IP address in any browser.

**What the firmware manages:**
- Contactor sequencing (negative, positive, precharge)
- Charger control and charge timers
- Motor/inverter control (torque requests via CAN or serial)
- Heater control
- Water pump and coolant fan control
- Throttle mapping and regen
- BMS limits (charge/discharge current limiting)
- ISA IVT shunt initialization and monitoring
- Data logging and live graphing

---

## Currently Supported Hardware

> *This list grows with each firmware release. Always check the wiki for the latest.*

### Motors / Drive Units
| Component | Interface |
|---|---|
| Nissan Leaf Gen1/2/3 inverter/motor | CAN (180V minimum) |
| Lexus GS450h inverter / L110 gearbox | Sync serial |
| Lexus GS300h inverter / L210 gearbox | Sync serial |
| Toyota Prius/Yaris/Auris Gen3 | Sync serial |
| Mitsubishi Outlander front/rear motors | CAN |
| OpenInverter controller board | CAN |

### Chargers / DC-DC Converters
| Component | Notes |
|---|---|
| Nissan Leaf PDM (Gen1, 2, 3) | Charger + DC-DC combined unit |
| Mitsubishi Outlander OBC | Charger + DC-DC combined unit |
| Tesla Model S DC-DC converter | |
| BMW i3 LIM module | Enables CCS DC fast charging (Type 1 & Type 2) |
| CHAdeMO DC fast charging | Via internal CAN |
| Foccci CCS controller | |
| Elcon charger | |

### Heaters
| Component | Interface |
|---|---|
| VAG/VW PTC water heater | LIN bus |
| VAG/VW cabin heater | LIN bus |
| Opel Ampera / Chevy Volt 6.5kW heater | |
| Mitsubishi Outlander water heater | |

### BMS / Battery Monitoring
| Component | Notes |
|---|---|
| ISA IVT shunt | Primary current/voltage monitoring method |
| Nissan Leaf ZE1 BMS / battery pack | |
| Renault Kangoo 36 BMS | |
| Orion BMS | |
| SimpBMS | |
| BMW S-BOX | |
| VW E-BOX | |

> **Important:** The ZombieVerter does **not** implement direct BMS cell-level communication. It uses the ISA shunt for pack-level monitoring (voltage, current, state of charge). Cell-level BMS functions (balancing, per-cell voltage/temp) are handled by a separate BMS device such as SimpBMS, which communicates with the VCU via CAN.

### Vehicle CAN Integration (Dashboard / Instrument Cluster)
| Vehicle | Notes |
|---|---|
| BMW E46 (1998–2005 3-series) | CAN + digital IO |
| BMW E39 (1996–2003 5-series) | CAN + digital IO |
| BMW E65 (2001–2008 7-series) | CAN |
| BMW E9x | CAN |
| Mid-2000s VAG vehicles | CAN |
| Subaru | CAN |

---

## How the VCU Fits Into a Conversion

A typical ZombieVerter-based conversion looks like this:

```
[Throttle Pedal] ──────────────────────────────────┐
[Brake Signal]  ──────────────────────────────────┐ │
[Forward/Reverse] ────────────────────────────────┤ │
[Ignition/Start] ─────────────────────────────────┤ │
                                                   ▼ ▼
                                          ┌─────────────────┐
[ISA Shunt] ──────────── CAN ────────────▶│                 │──── CAN ────▶ [Inverter/Motor]
[BMS (SimpBMS)] ──────── CAN ────────────▶│  ZombieVerter   │──── CAN ────▶ [Charger/OBC]
[BMW i3 LIM] ─────────── CAN ────────────▶│      VCU        │──── LIN ────▶ [Heater]
                                          │                 │──── Serial ─▶ [GS450h]
                                          └────────┬────────┘
                                                   │ Low-side outputs
                                          ┌────────┴────────────────────┐
                                    [Neg Contactor] [Pos Contactor] [Precharge]
                                    [Coolant Pump]  [Cooling Fan]   [12V Relay]
```

The VCU is the central coordinator. It reads driver inputs, monitors pack state via the shunt, sequences the contactors, and sends torque commands to the inverter — all configurable through the web interface without writing a line of code.

---

## Getting a ZombieVerter Board

There are two ways to obtain a board:

**Buy one from the EVBMW webshop:**
- Fully-built (tested, programmed, no soldering required) — recommended for most users
- Partially-built kit (some assembly required)
- Lead time: up to 4 weeks from order

**Build one yourself:**
- PCB design files for V1 are on GitHub (free)
- PCB design files for the current V1.a revision require Patreon membership
- You will need to source and solder components yourself

> **Note:** Boards from the webshop come **pre-programmed** and ready to use. You do not need to flash firmware before first use.

---

## What's Next

- **H01** — VCU Hardware Walkthrough: a physical tour of the board, connectors, and indicators
- **C01** — Flashing Firmware: only needed if you have a blank board or need to recover a bricked unit
- **C02** — The Web Interface Walkthrough: connecting to the VCU and navigating the UI

---

*Source: openinverter.org/wiki/ZombieVerter_VCU | openinverter.org community*  
*Last verified against firmware: V2.30A (August 2025)*
