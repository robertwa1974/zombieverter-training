# A03 — BMS Integration

**Track:** Advanced  
**Prerequisites:** W03 — Contactor & Precharge Circuit, C03 — Essential Parameters: First Start  
**Audience:** All levels  
**Estimated reading time:** 12 minutes

---

## Overview

The ZombieVerter does **not** implement cell-level BMS functions. It reads pack-level data from a separate BMS via CAN and enforces current limits from that BMS. This is an intentional division of labour:

- **ISA shunt** — pack-level monitoring (voltage, current, SoC). Feeds precharge logic and contactor control.
- **Cell BMS (SimpBMS, Orion, etc.)** — cell-level monitoring, balancing, per-cell protection. Sends charge/discharge limits to VCU over CAN.
- **VCU** — enforces BMS limits, manages contactors, controls inverter and charger.

---

## ISA IVT Shunt

The ISA IVT-S shunt is the recommended pack-level monitor for all ZombieVerter builds. It provides continuous measurement of voltage, current, power, and state of charge over CAN.

### What It Measures

| Measurement | Spot value |
|---|---|
| Pack voltage (U1) | `udc` |
| DC current | `idc` |
| State of charge | `SOC` |
| Instantaneous power | `power` |
| Amp-hours (coulomb count) | `AMPh` |
| Kilowatt-hours | `KWh` |

For the complete CAN message ID list, spot value mapping, and init procedure, see **W08 — ISA IVT-S Shunt: Complete Reference**.

### Permanent 12V — The Critical Rule

> **🔴 The ISA shunt must have always-on 12V — the same permanent feed as the VCU itself.**

If powered from an ignition-switched supply, the shunt loses its SoC state and UDC reading when the key is off. On the next startup, UDC reads zero → precharge fails every time.

**Rule:** ISA shunt power = always on. Same feed as VCU. Never ignition-switched.

### U1 Placement — Inverter Side of Main Contactor

The ISA shunt's U1 voltage sense wire must connect to the HV bus on the **inverter side** of the main contactor — not the battery side.

During precharge, U1 rises from 0V toward pack voltage as the inverter capacitors charge through the precharge resistor. When U1 crosses `udcsw`, the VCU closes the main contactor.

If U1 is connected to the battery side, it reads full pack voltage immediately, and the VCU tries to close the main contactor before the capacitors are charged — potentially welding the contacts on first use.

### CAN Bus

The ZombieVerter-specific IVT-S flash runs at **500 kbps** — the same as CAN1 and CAN2 on the VCU. The shunt can share either bus with other 500 kbps devices. Set `ShuntCan` to match your wiring.

> ⚠️ Stock IVT-S units default to 1 Mbps. Reflashing with the ZV-specific firmware is required before use. See W08.

### Initialisation (One-Time)

```
ShuntType = ISA
ShuntCan  = CAN1 or CAN2 (match your wiring)

→ Set IsaInit = 1 → save to flash → power cycle VCU and shunt simultaneously
→ Verify udc shows a reading in Spot Values
→ Set IsaInit = 0 → save to flash → reboot VCU
```

> ⚠️ `IsaInit` is not cleared automatically. Leaving it at 1 re-runs the full init — and resets the coulomb counter — on every boot.

If initialisation fails, power the shunt 2–3 seconds before the VCU. This allows the shunt to fully boot before the VCU attempts the init sequence.

### BMW S-BOX Alternative

Set `ShuntType = SBOX`. The BMW Safety Box provides pack voltage monitoring and HVIL (High Voltage Interlock Loop) in one unit. Popular in BMW-based builds.

---

## Cell-Level BMS Options

| BMS | Notes |
|---|---|
| **SimpBMS** | Most popular. Open-source. Designed for EV conversions. Connects to Leaf cell modules via UART (120-pin Leaf BMS connector), sends charge/discharge limits to VCU over CAN. |
| **Orion BMS** | Commercial, professional-grade. Plug-and-play CAN integration with VCU. High cost but very reliable. |
| **Nissan Leaf ZE1 BMS** | Salvaged from 62kWh Leaf. Native Leaf cell integration. Supported in V2.30A. |
| **Renault Kangoo BMS** | 36-module BMS. Added V2.20A. |
| **BMW S-BOX** | Combined pack monitor + HVIL. Set `ShuntType = SBOX`. |
| **VW E-BOX** | Volkswagen equivalent to S-BOX. Set `ShuntType = VAG`. |

---

## How BMS Limits Work

The BMS sends maximum charge and discharge current limits to the VCU via CAN. The VCU derates inverter torque commands and charge current to stay within those limits.

```
BMS sends via CAN → VCU enforces:
  Max discharge current → caps motor torque demand
  Max charge current    → caps regen / charge current
  BMS fault / over-volt → VCU opens contactors
```

### BMS Parameters

| Parameter | What it does |
|---|---|
| `BMSCan` | CAN bus the BMS is connected to |
| `BMS_Mode` | BMS protocol (SimpBMS, Orion, ZE1, etc.) |
| `maxDischargeCurrent` | VCU hard limit (A) — overrides BMS if lower |
| `maxChargeCurrent` | VCU hard limit for regen and charging |

> **⚠ Set `BMSCan` correctly.** If the BMS shares a bus with the inverter, check for CAN ID conflicts between devices. The ISA shunt and cell BMS can be on the same bus — both run at 500 kbps with the ZV IVT-S flash — or on separate buses if preferred.

---

## ISA vs Cell BMS — Both Needed

The ISA shunt and a cell BMS are complementary, not interchangeable:

- The **ISA shunt** provides UDC for precharge logic and idc for power monitoring. Without it (or `ShuntType = SBOX/VAG`), precharge sequencing cannot work.
- The **cell BMS** provides per-cell voltage monitoring, temperature, balancing, and current limits. Without it, you have no protection against individual cell over-voltage or thermal runaway.

From V2.20A, it is possible to run with `ShuntType = None` and use BMS data from the inverter and BMS directly for pack-level monitoring — demonstrated in Damien's Mitsubishi L200 truck build using a Leaf ZE1 battery pack with integrated BMS.

---

*Source: openinverter.org/wiki · Damien Maguire @Evbmw · ZombieVerter firmware source*  
*Last verified against firmware: V2.40A*
