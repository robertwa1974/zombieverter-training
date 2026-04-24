# A04 — Gear Selectors & Shifters

**Track:** Advanced  
**Prerequisites:** C03 — Essential Parameters: First Start, W06 — 12V Auxiliary & Ignition Wiring  
**Audience:** All levels  
**Estimated reading time:** 10 minutes

---

## Overview

The VCU supports multiple methods of direction selection — from simple toggle switches to OEM electronic shifters communicating over CAN. The method is set via two parameters: `dirmode` (controls the 12V input logic) and `gearLever` (selects OEM CAN shifter protocol if used).

> **GS450h exception:** The GS450h has a physical P/R/N/D linkage connected to the transmission neutral safety switch. Note that with the exception of Park, which physically engages the parking pawl, the other positions are a simple electrical switch. The VCU reads switch state directly — it does not use the `gearLever` CAN parameter. See Module I03.

---

## dirmode — Simple Direction Control

For builds using 12V switches or buttons rather than OEM CAN shifters.

| dirmode | Wiring | Behaviour |
|---|---|---|
| `defaultFwd` | Pin 53 only | Auto-forward in run mode. Momentary 12V to Pin 53 = reverse. Release = back to forward. |
| `switch` | Pin 54 (Fwd) + Pin 53 (Rev) | 3-position. Neither active = neutral. Best for PRND selector. |
| `button` | Single momentary | Press to toggle between forward and reverse. |
| `switchReversed` | Same as switch | Motor direction inverted — use when drivetrain spins backwards. |
| `buttonReversed` | Same as button | Toggle + inverted direction. |

### 3-Position Switch (switch mode) — Recommended

```
D position → 12V to Pin 54   (din_forward = on)
N position → neither pin      (no torque output)
R position → 12V to Pin 53   (din_reverse = on)
```

> **⚠ Verify with Spot Values before road testing.** Sit with the web interface open. Move through each selector position. Confirm `din_forward` and `din_reverse` toggle correctly. A wiring error means unintended reverse at startup.

### defaultFwd — Simplest Possible Build

Only needs one wire for reverse. Auto-Drive when in run mode. Single momentary button on Pin 53 for reverse. When released, returns to Drive. No PRND lever needed — ideal for minimal builds.

---

## OEM CAN-Based Electronic Shifters

Modern vehicles use electronic shifters that send gear position over CAN. The gear shifter class (added V2.04A) reads these messages and maps them to the VCU's internal direction and Park/Neutral states.

Set the `gearLever` parameter to match your shifter:

| Shifter | Added | Notes |
|---|---|---|
| 12V inputs (default) | Always | Standard switch wiring — Pins 53/54 |
| BMW F30 CAN e-shifter | V2.04A | Sends PRND via CAN. Clean OEM look. Reverse engineering by "project Gus." |
| JLR rotary shifter | V2.05A | Jaguar/Land Rover CAN rotary. Popular for custom builds. |
| BMW E65 7-series | V2.20A | Now uses shifter class (was hardcoded before V2.20A). |

Check the openinverter wiki for the specific CAN ID required for your shifter model.

---

## Park Gear (V2.05A+)

When Park is selected via an OEM shifter or a dedicated 12V input:

- **Torque inhibited** — no motor movement regardless of throttle position
- **HV bus maintained** — contactors stay closed, DC-DC converter active
- **Charge mode enabled** — some OBCs require Park to be selected before accepting a charge command

---

## E91 Build Example

Jamie Jones (Ohm-Grown EVs) used the OEM BMW E91 automatic shifter assembly for his conversion. The shifter physically clicks into P/R/N/D positions but sends simple 12V signals — wired directly to VCU Pins 53/54. This is the simplest way to retain an OEM shifter feel without CAN complexity.

---

*Source: Damien Maguire @Evbmw · Jamie Jones / Ohm-Grown EVs · openinverter.org*  
*Gear shifter class added V2.04A · JLR added V2.05A · Park gear added V2.05A*  
*Last verified against firmware: V2.30A (August 2025)*
