# ZombieVerter VCU Training Series — Module Index

**Version:** 0.1 (initial draft from wiki source)  
**Status:** Foundation modules complete — video transcript content pending  
**Last updated:** 2025

---

## How to Use This Series

Modules are organized into tracks. Each track can be entered at different points depending on your experience level:

- **Complete novice** → Start at F01, work sequentially
- **Experienced EV converter, new to ZombieVerter** → Start at F02, then jump to H01 and C02
- **Have a board, need to get it running** → C01 (if blank board), then C02 → C03
- **Specific wiring question** → Jump directly to the relevant W-series module

Modules list their prerequisites at the top. Cross-references between modules are marked in "What's Next" sections.

---

## Track F — Foundation

| Module | Title | Status | Key Topics |
|---|---|---|---|
| F01 | What Is a VCU and Why Do You Need One | ⬜ Pending | VCU role in EV conversion, what it replaces |
| **F02** | **ZombieVerter Ecosystem Overview** | ✅ **Draft complete** | Features, supported hardware, community resources |
| F03 | EV Drivetrain Fundamentals | ⬜ Pending | HV/LV systems, contactor logic, motor types |
| F04 | Safety First — Working with High Voltage | ⬜ Pending | PPE, isolation testing, fusing philosophy |

---

## Track H — Hardware

| Module | Title | Status | Key Topics |
|---|---|---|---|
| **H01** | **VCU Hardware Walkthrough** | ✅ **Draft complete** | Board layout, connector, LEDs, SWD test points, full pin table |
| H02 | Inputs & Outputs Deep Dive | ⬜ Pending | Electrical characteristics, voltage limits, current ratings |
| H03 | CAN Bus on the VCU | ⬜ Pending | CAN1/2/3, termination, baud rates, traffic types |
| H04 | Power Supply & Grounding | ⬜ Pending | 12V requirements, grounding strategy, ground loops |
| H05 | Supported Peripherals | ⬜ Pending | Throttle pots, BMS integration, pumps, fans, DC-DC |

---

## Track W — Wiring

| Module | Title | Status | Key Topics |
|---|---|---|---|
| W01 | Wiring Philosophy & Best Practices | ⬜ Pending | Wire gauging, connectors, labeling, shielding |
| **W02** | **Throttle & Brake Wiring** | ✅ **Draft complete** | Dual/single pot, pin assignments, potmin/potmax gotcha |
| **W03** | **Contactor & Precharge Circuit** | ✅ **Draft complete** | Low-side switching, UDC, ISA shunt placement, sequencing |
| W04 | HVIL — High Voltage Interlock Loop | ⬜ Pending | What HVIL is, how to wire a loop, VCU integration |
| W05 | Cooling System Control | ⬜ Pending | Pump/fan relay wiring, thermistor inputs, PWM fan |
| W06 | 12V Auxiliary & Ignition Wiring | ⬜ Pending | Wake-on-ignition, switched power, DC-DC integration |
| W07 | CAN Bus Wiring | ⬜ Pending | Twisted pair, termination, topology, isolating noisy nodes |

---

## Track C — Firmware & Configuration

| Module | Title | Status | Key Topics |
|---|---|---|---|
| **C01** | **Flashing Firmware** | ✅ **Draft complete** | STM32 vs GD32, web UI update, ST-Link recovery, serial params |
| **C02** | **Web Interface Walkthrough** | ✅ **Draft complete** | Wi-Fi connection, interface layout, spot values, save to flash |
| **C03** | **Essential Parameters: First Start** | ✅ **Draft complete** | Full first-start checklist, LV bench test procedure |
| C04 | Throttle Calibration | ⬜ Pending | pot calibration, dual-pot plausibility, ramp rates |
| C05 | CAN Configuration | ⬜ Pending | Inverter profiles, baud rate, enabling/disabling messages |
| C06 | Fault Codes & Status Flags | ⬜ Pending | Reading fault bits, common faults and causes |
| C07 | Data Logging & Live Telemetry | ⬜ Pending | Serial stream, CAN logging, graphing parameters |

---

## Track I — Inverter Integration

| Module | Title | Status | Key Topics |
|---|---|---|---|
| I00 | Generic Inverter Integration — Principles | ⬜ Pending | CAN torque request model, enable/run sequence |
| I01 | Nissan Leaf Inverter (EM57/EM61) | ⬜ Pending | CAN IDs, resolver, cooling, Gen1/2/3 differences |
| I02 | Tesla Large Drive Unit (LDU) | ⬜ Pending | CAN handshake, HVIL, resolver, cooling pump |
| I03 | Toyota Lexus GS450h Transaxle | ⬜ Pending | Sync serial interface, dual-motor architecture, trans control |
| I04 | Mitsubishi Outlander PHEV Drive Unit | ⬜ Pending | CAN interface, torque limits, cooling |
| I05 | Bringing Up a New/Unsupported Inverter | ⬜ Pending | CAN sniffing methodology, reverse engineering |

---

## Track A — Advanced

| Module | Title | Status | Key Topics |
|---|---|---|---|
| A01 | Regen Tuning | ⬜ Pending | Brake regen, throttle-lift regen, blending, feel tuning |
| A02 | BMS Integration | ⬜ Pending | CAN BMS handshake, charge enable/disable logic |
| A03 | Charge Control | ⬜ Pending | J1772 pilot, EVSE handshake, OBC CAN control |
| A04 | Building Custom Firmware | ⬜ Pending | Dev environment, compiling, contributing back |
| A05 | CAN Gateway & Multi-Node Systems | ⬜ Pending | CAN bridging, instrument cluster integration |

---

## Source Material Status

| Source | Status | Notes |
|---|---|---|
| openinverter.org/wiki/ZombieVerter_VCU | ✅ Full content captured | Via MediaWiki API — complete wikitext |
| openinverter.org/wiki/ZombieVerter_IO | ✅ Partial (search snippets) | robots.txt blocks direct fetch |
| openinverter.org/wiki/Zombieverter_Parameters_and_Spot_Values | ✅ Partial (search snippets) | robots.txt blocks direct fetch |
| openinverter.org/wiki/Zombieverter_programing | ✅ Partial (search snippets) | robots.txt blocks direct fetch |
| openinverter.org forum threads | ✅ Partial (search snippets) | Key gotchas captured |
| Damien Maguire YouTube channel | ⬜ Pending | yt-dlp transcript extraction needed |
| GitHub source code / param_prj.h | ⬜ Pending | Parameter definitions |

---

## Known Content Gaps (Require SME Input or Video Transcripts)

The following topics have **no good written source** and will require either video transcript extraction or direct knowledge from a subject matter expert:

- GS450h sync serial protocol specifics
- Mitsubishi Outlander CAN protocol details
- Tesla LDU CAN handshake sequence
- CHAdeMO wiring and protocol
- BMW i3 LIM integration procedure
- Real-world regen tuning values and feel
- ISA shunt CAN message IDs and timing
- Typical precharge resistor sizing for common pack voltages

---

*This is a living document. Modules will be updated as video transcripts and additional wiki content are incorporated.*
