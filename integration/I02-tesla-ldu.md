# I02 — Tesla Drive Units (SDU & LDU)

**Track:** Integration  
**Prerequisites:** C03 — Essential Parameters: First Start, W03 — Contactor & Precharge  
**Audience:** Intermediate  
**Estimated reading time:** 15 minutes

---

## Overview

Tesla drive units are increasingly popular in EV conversions — powerful, well-engineered, and becoming more available as early Model S vehicles reach end-of-life. The ZombieVerter controls Tesla drive units via an openinverter replacement logic board that installs in the inverter in place of the OEM Tesla logic board.

> **Critical distinction:** The openinverter board replaces the LOGIC board inside the inverter — not the entire inverter. The power electronics, motor, and housing remain OEM. Only the small control board that sits inside the inverter housing is replaced.

---

## Small Drive Unit (SDU) vs Large Drive Unit (LDU)

| | SDU | LDU |
|---|---|---|
| Model | Model S rear (pre-2016), Model 3 rear | Model S/X rear (2013+) |
| Peak power | ~220kW | ~375kW |
| Weight | ~100kg | ~145kg |
| Layout | Compact — suits smaller builds | Larger — needs more space |
| Availability | Good | Good and increasing |
| OI board version | V2.1 | V2.1 |

Both use the same openinverter board and the same ZombieVerter integration approach.

---

## The OpenInverter Board

The openinverter replacement board is available from evbmw.com or can be built from the GitHub files. It provides:
- CAN interface to the VCU
- Motor position encoding
- Gate drive signals to the IGBT modules in the power stage
- Replacement of all OEM Tesla logic functionality needed for EV conversion use

**Set `inverter` = OIBoard (4) in VCU parameters.**

---

## Pre-Installation Checks — Do These Before Soldering Anything

Damien's 2023 video documents a systematic 8-step process. Inverter failures in Tesla conversions almost always result from skipping these steps. Follow them in order.

### Step 1 — DC Bus Diode Test

With the inverter completely unpowered and disconnected, set multimeter to diode test mode. Connect positive probe to HV+ terminal, negative probe to HV− terminal. You should see: voltage rising from near zero as the capacitors charge, then climbing to open circuit. This confirms no dead short on the DC bus.

Reverse the probes (negative to HV+, positive to HV−). You should see approximately 0.6V — the forward voltage of the body diodes. This is correct.

> If you see a direct short (0V) in either direction: the inverter has failed IGBT modules. Do not proceed.

### Step 2 — Phase Diode Tests

With multimeter negative on HV− bus, positive probe on each of the three motor phase terminals (U, V, W) in turn. Each should show increasing voltage then open circuit (capacitors charging). This confirms the upper IGBT body diodes are intact.

Reverse: negative probe on HV+, positive on each phase. Should see ~0.6V on each. This confirms the lower IGBT body diodes are intact.

Any phase showing a direct short = failed IGBT on that phase. Do not proceed.

### Step 3 — 12V Logic Board Test (OEM board still installed)

Apply 12V power to the logic board connector only — do not connect HV. The board should draw approximately 200–300mA and show some activity (LEDs, CAN frames on a bus monitor). If the board draws no current or draws excessive current, investigate before proceeding.

### Step 4 — Solder the OpenInverter Board

Remove the OEM logic board. Solder the openinverter board connectors carefully — cold joints on the gate driver connections cause intermittent or failed gate switching. Inspect under magnification before proceeding.

### Step 5 — 12V Test With OI Board

Apply 12V to the logic board connector with the OI board installed. The board should power up, CAN should be active, no excessive current draw.

### Step 6 — Install Board Into Inverter

Reinstall the cover. The board is now installed but HV has not been applied yet.

### Step 7 — 12V Test With OI Board Installed in Inverter

Apply 12V again — verify normal operation with the board in its installed position.

### Step 8 — Encoder Test Before Any HV

With the VCU connected, CAN active, and 12V applied: rotate the motor shaft slowly by hand. Watch encoder or resolver readings in the VCU Spot Values. The values should change smoothly as the shaft rotates. If they don't — investigate the encoder wiring before applying HV.

> **Only after completing all 8 steps should you apply HV to the drive unit.**

---

## Why These Steps Matter

Damien's 2023 video was specifically created in response to a pattern of inverter failures in the community. The failures were caused by:

1. **Applying HV before the DC bus was verified** — a pre-existing fault that would have been caught by the diode test
2. **Applying HV before the encoder was verified** — the inverter attempts motor commutation immediately on HV application; if encoder data is wrong it commands incorrect phase currents and destroys the power stage

The OI board itself is not expensive. The IGBT modules in the inverter power stage are expensive and difficult to source. The 8-step process is 30 minutes of work that prevents a catastrophic and expensive failure.

---

## HVIL on Tesla Drive Units

Tesla drive units have an HVIL connector that must be looped for the inverter to operate. The HVIL connector carries a low-current loop through the HV connector housing — if the HV cover is removed, the loop breaks.

In a conversion, the HVIL connector must either be looped (a simple wire jumper connecting both pins) or integrated into the vehicle's HVIL circuit. Leaving it unconnected will prevent the inverter from entering run mode.

---

## Cooling Requirements

Tesla drive units are liquid cooled. In the OEM vehicle, they use Tesla's proprietary coolant loop with a pump, radiator, and chiller. In a conversion, you need an aftermarket electric coolant pump, a radiator or heat exchanger, and thermostat control.

The VCU can control a coolant pump via the `CoolantPump` output function and a fan via `CoolingFan` with the `FanTemp` threshold parameter (added V2.20A).

Minimum coolant flow should be maintained whenever the inverter is active. Unlike the GS450h which uses oil, the Tesla drive unit uses water/glycol coolant.

---

## VCU Parameters

```
inverter    = 4          (OpenInverter board)
inverterCan = CAN1
```

---

## Community Resources

The Volvo V50 Tesla Model 3 drive unit project (2025) is the most recent documented Tesla LDU conversion with ZombieVerter. Three build videos are available on Damien's channel documenting the integration process with current firmware.

---

*Source: Damien Maguire @Evbmw — "Using Tesla Drive Units with OpenInverter Board" (July 2023) · "Volvo V50 Tesla Model 3 Drive Unit" series (2025)*  
*Last verified against firmware: V2.30A (August 2025)*
