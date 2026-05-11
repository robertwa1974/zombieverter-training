# W07 — CAN Bus Wiring

**Track:** Wiring  
**Prerequisites:** H01 — VCU Hardware Walkthrough, W03 — Contactor & Precharge  
**Audience:** All levels  
**Estimated reading time:** 10 minutes

---

## Overview

The ZombieVerter communicates with the inverter, shunt, BMS, charger, and other devices over CAN bus. Getting the physical wiring, termination, and bus assignment parameters right is essential — a misconfigured CAN bus is one of the most common sources of "nothing works" at first startup.

---

## The Three CAN Buses

The VCU has three CAN interfaces:

| Bus | Physical interface | Speed | Notes |
|---|---|---|---|
| CAN1 | STM32 native CAN1 | **500 kbps** — hardcoded | Primary bus. CanSDO (web interface parameter access) is hardcoded here. |
| CAN2 | STM32 native CAN2 | **500 kbps** — hardcoded | Secondary bus. Remapped pins on the VCU PCB. |
| CAN3 | MCP25625 SPI-CAN chip | Configurable via `CAN3Speed` | Used for CHAdeMO (fault-tolerant CAN). |

Both CAN1 and CAN2 are hardcoded at 500 kbps in firmware — there is no parameter to change this. All devices on CAN1 or CAN2 must run at 500 kbps.

### CAN3 Speed Options

`CAN3Speed` parameter values:

| Value | Speed | Use case |
|---|---|---|
| 0 | 33.3 kbps | CHAdeMO fault-tolerant CAN |
| 1 | 500 kbps | Standard high-speed CAN |
| 2 | 100 kbps | — |

---

## CAN1 vs CAN2 — Are They Interchangeable?

For most devices, yes. Both run at 500 kbps and carry the same callback handler. However there is one hardware asymmetry:

> **CanSDO is hardcoded to CAN1.** The SDO communication used by the openinverter protocol (CAN ID `0x601`) listens on both buses, but SDO replies are sent on CAN1 only. This only matters if you are using SDO-based tools directly — it does not affect normal VCU operation.

In practice, use whichever bus your wiring makes convenient. The conventional layout — inverter on CAN1, shunt/BMS on CAN2 — simply reduces the chance of CAN ID conflicts between devices and is a good habit, not a hardware requirement.

---

## Baud Rates by Device

All devices used with CAN1 or CAN2 must run at **500 kbps**.

| Device | Baud rate | Notes |
|---|---|---|
| Nissan Leaf inverter | 500 kbps | |
| Mitsubishi Outlander | 500 kbps | |
| ISA IVT-S shunt | **500 kbps** ¹ | |
| SimpBMS / Orion BMS | 500 kbps | |
| BMW i3 LIM | 500 kbps | |
| CHAdeMO socket | 33.3 kbps fault-tolerant | CAN3 only — 6 PCB solder jumpers required |
| OBD2 / ELM327 | 500 kbps | |

¹ **Applies to IVT-S units flashed with the ZombieVerter-specific firmware.** Stock IVT-S units from ISA default to 1 Mbps and will not communicate with the VCU without reflashing. The ZV firmware flash is available from the openinverter.org community. A correctly flashed unit can share CAN1 or CAN2 with other 500 kbps devices. See **W08** for full IVT-S reference.

---

## Bus Assignment Parameters

Each device class has a parameter to select which physical bus it is on:

| Parameter | Assigns | Default |
|---|---|---|
| `InverterCan` | Traction inverter | CAN1 |
| `VehicleCan` | Vehicle CAN (instrument cluster) | CAN2 |
| `ShuntCan` | ISA shunt / S-BOX / VAG box | CAN1 |
| `LimCan` | i3 LIM charge interface | CAN1 |
| `ChargerCan` | OBC / charger | CAN2 |
| `BMSCan` | Cell BMS | CAN2 |
| `OBD2Can` | OBD2 interface | CAN1 |
| `CanMapCan` | Custom CAN map messages | CAN1 |
| `DCDCCan` | DC-DC converter | CAN2 |
| `HeaterCan` | CAN-controlled heater | CAN2 |

All are configurable — the defaults shown are firmware defaults from `param_prj.h` and may not match your wiring. Set each parameter to match where you physically wired the device.

---

## Typical Bus Layout

A common starting configuration:

```
CAN1 @ 500 kbps:
  Traction inverter  (InverterCan = CAN1)
  Leaf PDM charger   (ChargerCan = CAN1 — same bus as Leaf inverter)
  BMW i3 LIM         (LimCan = CAN1)
  OBD2 dongle        (OBD2Can = CAN1)

CAN2 @ 500 kbps:
  ISA IVT-S shunt    (ShuntCan = CAN2) — ZV flash, 500 kbps
  SimpBMS / Orion    (BMSCan = CAN2)
  ESP32 CAN bridge   — shares bus, 500 kbps transceiver

CAN3 @ 33.3 kbps fault-tolerant:
  CHAdeMO socket     — requires 6 PCB solder jumpers
```

This is a recommendation, not a requirement. Any device can go on either CAN1 or CAN2 as long as all devices on the same bus run at 500 kbps and there are no CAN ID conflicts between them.

---

## Physical Wiring Rules

### Use Twisted Pair

All CAN runs must use twisted pair wire. CAN H and CAN L must be twisted together. Untwisted runs in electrically noisy environments (near HV cables, near inverters) cause intermittent communication failures that are very difficult to diagnose.

Use shielded twisted pair for any run longer than ~500mm or in close proximity to HV wiring.

### Bus Topology — Not Star

CAN is a **bus** topology. All devices connect to the same two wires (CAN H and CAN L) running from one end of the bus to the other. Avoid star topologies where wires branch out from a central point.

```
CORRECT — bus topology:
[VCU] ──────────────────────────────── [Inverter]
           │              │
        [Shunt]          [BMS]

WRONG — star topology:
              [VCU]
             / | \ \
            /  |  \ \
     [Inv] [Shunt] [BMS] [Charger]
```

Keep stub branches (drops from the main bus to a device) as short as possible — under 100mm ideally.

### Termination

CAN bus requires **120Ω termination at each end of the bus** — two resistors total, one at each physical endpoint. No more, no less.

Measure across CAN H and CAN L with all devices powered off. You should read **~60Ω** (two 120Ω resistors in parallel).

- Less than 60Ω: too many terminators — find and remove the extras
- More than 60Ω (or open circuit): missing a terminator, or terminator not in place

Some inverters and OBCs have built-in 120Ω termination. Check before adding external resistors.

---

## Assigning Devices to Buses — Step by Step

1. Physically wire all CAN devices — CAN H to CAN H, CAN L to CAN L, twisted pair throughout
2. Place 120Ω terminators at the two physical ends of each bus
3. In the VCU web interface, set each `*Can` parameter to match where you wired that device
4. Save to flash
5. Reboot the VCU
6. Verify communication by checking relevant spot values (`invstat`, `udc`, BMS values)

> **Known issue:** CAN1 and CAN2 are labelled in reverse in some older wiring diagrams. If a device won't communicate despite correct physical wiring, try swapping the `*Can` parameter between 0 (CAN1) and 1 (CAN2) before rewiring anything.

---

## Diagnosing CAN Communication Failures

Work through in order:

1. Is the correct bus assignment parameter set? Check `InverterCan`, `ShuntCan`, etc.
2. Is baud rate consistent? All devices on CAN1/CAN2 must be 500 kbps.
3. Is termination correct? Measure ~60Ω across H/L with power off.
4. Try swapping the `*Can` parameter between 0 (CAN1) and 1 (CAN2) — CAN1/CAN2 label swap issue.
5. Are CAN H and CAN L wires the right way around? Try swapping them.
6. Is the cable twisted pair? Long untwisted runs in noisy environments cause intermittent failures.
7. Does the device need initialisation? (ISA shunt requires `IsaInit` — see W08)

---

## Related Modules

- **W08** — ISA IVT-S Shunt: Complete Reference (CAN IDs, init procedure, spot values)
- **C02** — Web Interface Walkthrough (where to find the `*Can` parameters)
- **C03** — Essential Parameters: First Start
- **A03** — BMS Integration

---

*Source: ZombieVerter firmware `stm32_vcu.cpp`, `param_prj.h` · openinverter.org/wiki*  
*Last verified against firmware: V2.40A*
