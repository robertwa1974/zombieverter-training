# C03 — Essential Parameters: First Start

**Track:** Firmware & Configuration  
**Prerequisites:** C02 — Web Interface Walkthrough, W02, W03  
**Audience:** All levels  
**Estimated reading time:** 15 minutes

---

## Overview

This module walks you through the minimum parameter set required to bring a ZombieVerter system to life for the first time. Follow these steps in order. Do not skip ahead to HV testing until the LV checks are complete.

---

## Before You Start: LV Bench Test

You should be able to complete the entire first-start sequence with **12V only** — no HV battery connected. This lets you verify wiring, parameters, and sequencing logic before introducing any HV risk.

Required for LV bench test:
- ZombieVerter VCU with 12V power
- Wi-Fi connected device with web interface open
- Throttle pedal (or a potentiometer simulating one)
- Brake signal (a simple switch to 12V)
- Forward/Reverse signal (switches to 12V)
- Ignition ON and START signals (switches to 12V)
- Contactor coils connected (they will click — no HV needed to verify sequencing)
- ISA shunt connected and initialised (see Module W08)

---

## Step 1: Set the Inverter Type

**Parameter:** `Inverter` (under General Setup)

Set this to match your actual inverter. If you set it wrong, the VCU will send CAN messages on the wrong IDs at the wrong baud rate and nothing will communicate.

| Your inverter | Set `Inverter` to |
|---|---|
| Nissan Leaf (any gen) | 1 |
| Lexus GS450h | 2 |
| Toyota Prius Gen3 | 5 |
| Mitsubishi Outlander (rear) | 8 |
| OpenInverter board | 4 |
| Nothing yet | 0 |

Save to flash.

---

## Step 2: Set the Shunt Type

**Parameter:** `ShuntType` (under General Setup)

| Your UDC source | Set `ShuntType` to |
|---|---|
| ISA IVT-S shunt | ISA |
| BMW S-BOX | SBOX |
| VW/Audi system | VAG |
| Nissan Leaf inverter | LEAF |
| None | None |

Save to flash.

### ISA Shunt Initialisation Procedure

If you are using an ISA shunt it must be initialised before it will report UDC. The VCU cannot precharge without a valid UDC reading.

> **The ISA shunt and VCU must share the same permanent 12V feed** — this is required for the init sequence to work and for accurate readings during charging when ignition is off.

1. Wire the ISA shunt to permanent 12V+ and the CAN bus
2. Set `ShuntType = ISA` and `ShuntCan` to the correct CAN bus — save to flash
3. Set `IsaInit = 1` — save to flash
4. Power cycle the VCU and shunt **at the same time** (shared 12V feed means this is automatic)
5. The shunt will initialise — `udc` in Spot Values should now show a reading
6. **Set `IsaInit = 0` — save to flash**
7. Reboot the VCU

> ⚠️ **`IsaInit` is not cleared automatically by the firmware.** If left at 1, the full init sequence (including coulomb counter reset) runs on every boot. Always set it back to 0 after a successful init.

> **If the shunt doesn't initialise:** Separate the shunt and VCU power supplies temporarily, power the shunt first, then power the VCU 2–3 seconds later. This fixes a timing issue seen with some units.

For the complete IVT-S reference including CAN IDs, spot value mapping, and troubleshooting, see **W08**.

---

## Step 3: Set the CAN Bus Assignments

**Parameters:** `InverterCan`, `ShuntCan` (under General Setup)

The ZombieVerter has three CAN interfaces. You need to tell the VCU which physical bus each device is connected to.

> **Note:** There is a known documentation issue where CAN1 and CAN2 are labelled in reverse in some older wiring diagrams. If your inverter is not communicating despite correct CAN wiring, try swapping the bus assignment parameter value before rewiring.

Common starting configuration:
- `InverterCan` = CAN1 (or whichever bus your inverter is on)
- `ShuntCan` = match your shunt wiring (CAN1 or CAN2)

Save to flash.

---

## Step 4: Set Voltage Limits

**Parameters:** `udcmin`, `udclim`, `udcsw`

| Parameter | Description | Firmware default | What to set |
|---|---|---|---|
| `udcmin` | Below this, VCU will not enter run mode | **450V** | ~80% of minimum pack voltage |
| `udclim` | Above this, VCU derates | **520V** | Just above fully charged pack voltage |
| `udcsw` | Precharge complete — main contactor closes | **330V** | ~95% of nominal pack voltage |

> ⚠️ **`udcmin` defaults to 450V and `udclim` to 520V.** Both must be lowered for any build using a sub-400V pack or the VCU will never enter run mode.

For initial LV bench testing with no HV connected, set `udcsw` to a low value (15–20V) so precharge "completes" quickly and lets you verify the contactor sequencing.

> **Precharge timeout is 5 seconds** — hardcoded in firmware. If `udc` has not reached `udcsw` within 5 seconds, the VCU posts `ERR_PRECHARGE` and enters `MOD_PCHFAIL`. Ensure your precharge resistor is sized to charge the bus capacitors within this window.

Save to flash.

---

## Step 5: Configure Throttle (Minimum Settings)

**Parameters:** `potmin`, `potmax`, `potmode`, `throtmin`, `throtmax`

First, set `potmode`:
- `SingleChannel` — one throttle pot
- `DualChannel` — two throttle pots (recommended for safety)

Then watch the `pot` spot value while moving the throttle pedal and set:
- `potmin` = value just **above** the resting (off-throttle) ADC reading
- `potmax` = value just **below** the full-travel ADC reading

> ⚠️ **ZombieVerter `potmin`/`potmax` are set inside the mechanical travel range** — opposite to most systems. This is intentional: if the sensor fails or the connector pulls out, the VCU sees a value outside the calibrated range and cuts throttle safely.

Then set:
- `throtmin` = 0 (or a small negative value for throttle-lift regen)
- `throtmax` = 100

> ⚠️ **`throtmax` defaults to 100.** If your throttle does nothing, check this parameter first — it is the most common first-start gotcha.

If using dual throttle, also calibrate `pot2min` and `pot2max` the same way while watching `pot2`.

Save to flash.

---

## Step 6: Verify Brake Signal

In Spot Values, check `din_brake`.

- It should show **"off"** when the brake pedal is not pressed
- It should show **"on"** when the brake pedal is pressed

> `din_brake` must be **"off"** for the VCU to allow torque output. If it is stuck "on" with no brake pressed, check the brake switch wiring (normally open vs normally closed), check for a floating pin, or add a pull-down resistor to ground.

---

## Step 7: Verify Direction Inputs

Apply 12V to Pin 54 (forward) and check `din_forward` in Spot Values — should show "on".  
Apply 12V to Pin 53 (reverse) and check `din_reverse` — should show "on".

---

## Step 8: First Precharge Test (LV Only)

With everything configured and saved to flash:

1. Apply ignition ON signal to Pin 15
2. Briefly apply START signal to Pin 52 (momentary 12V pulse)
3. Watch Spot Values:
   - Contactor outputs should fire in sequence (you'll hear them click)
   - `udc` should update
   - If `udc` rises above `udcsw`, the main contactor closes
   - `opmode` should reach `run`

**If the system stays in PRECHARGE:**
- Is `udc` reading a valid value? If zero, the shunt is not communicating — check W08
- Is `udcsw` reachable? For LV bench testing with no HV, lower `udcsw` to 5V
- Remember: precharge has a 5-second timeout — if `udc` doesn't reach `udcsw` in time, the VCU faults to `MOD_PCHFAIL`

**If `opmode` never reaches "run":**
- Check `din_brake` is "off"
- Check `din_forward` or `din_reverse` is "on" — VCU requires a direction selected
- Check `udc` is above `udcmin`

---

## Step 9: First Torque Test (LV Only)

With `opmode` showing `run`:

1. Apply forward direction (Pin 54 to 12V)
2. Slowly apply throttle
3. Watch `potnom` — should rise from 0 to 100 as you press the pedal
4. Watch `torque` — should rise proportionally

Without HV or a connected inverter, the VCU sends torque commands via CAN. Verify with a CAN analyser if available.

---

## Complete First-Start Parameter Checklist

| Parameter | Firmware default | What to set | Notes |
|---|---|---|---|
| `Inverter` | 0 | Match your hardware | General Setup |
| `ShuntType` | 0 — None | Match your hardware | ISA, SBOX, VAG, or LEAF |
| `InverterCan` | CAN1 | Match your wiring | |
| `ShuntCan` | CAN1 | Match your wiring | |
| `udcmin` | **450V** | ~80% of min pack voltage | ⚠️ Must lower for all sub-400V builds |
| `udclim` | **520V** | Just above fully charged pack voltage | |
| `udcsw` | **330V** | ~95% of nominal pack voltage | Set 15–20V for LV bench test |
| `potmode` | SingleChannel | Match wiring | |
| `potmin` | 0 | Just above off-throttle ADC reading | Inside mechanical travel |
| `potmax` | 4095 | Just below WOT ADC reading | Inside mechanical travel |
| `pot2min` | 4095 | Same for channel 2 (dual only) | |
| `pot2max` | 4095 | Same for channel 2 (dual only) | |
| `throtmin` | -100 | 0 (or small negative for lift regen) | |
| `throtmax` | **100** | 100 | Default is correct — verify if throttle unresponsive |
| `throtmaxRev` | 30 | Raise if more reverse torque needed | Firmware defaults to 30% in reverse |
| `revlim` | 6000 rpm | Set appropriate for your motor | |
| `IsaInit` | 0 | Toggle 1→0 to init ISA shunt | See W08 — must reset to 0 after init |
| `Vehicle` | 0 (BMW E46) | None or Classic | Unless integrating with OEM cluster |

---

## What's Next

- **C04** — Throttle Calibration: fine-tuning potmin/potmax, ramp rates, dual-pot plausibility
- **C05** — CAN Configuration: inverter CAN profiles, baud rates, message IDs
- **C06** — Fault Codes & Status Flags: reading and interpreting faults
- **W08** — ISA IVT-S Shunt: Complete Reference

---

*Source: openinverter.org/wiki · ZombieVerter firmware `param_prj.h`, `stm32_vcu.cpp`*  
*Last verified against firmware: V2.40A*
