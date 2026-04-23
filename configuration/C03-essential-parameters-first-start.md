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
- ISA shunt connected and initialised (see Module W03)

---

## Step 1: Set the Inverter Type

**Parameter:** `inverter` (under Comms)

Set this to match your actual inverter. If you set it wrong, the VCU will send CAN messages on the wrong IDs at the wrong baud rate and nothing will communicate.

| Your inverter | Set inverter to |
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

**Parameter:** `shuntType` (under Contactors or Comms — varies by firmware version)

| Your UDC source | Set shuntType to |
|---|---|
| ISA IVT shunt | ISA |
| BMW S-BOX | SBOX |
| VW/Audi system | VAG |
| Nissan Leaf inverter | LEAF |

If you are using an ISA shunt and haven't initialised it yet, do that now — see Module W03. The VCU cannot precharge without a valid UDC reading.

Save to flash.

---

## Step 3: Set the CAN Bus Assignments

**Parameters:** `inverterCan`, `shuntCan` (under Comms)

The ZombieVerter has three CAN interfaces (CAN1, CAN2, CAN3). You need to tell the VCU which physical bus each device is connected to.

> **Note:** There is a known documentation issue where CAN1 and CAN2 are labelled in reverse in some older wiring diagrams. If you find your inverter is not communicating despite correct CAN wiring, try swapping the CAN bus assignment.

Common starting configuration:
- `inverterCan` = CAN1 (or whichever bus your inverter is on)
- `shuntCan` = same bus as the shunt wiring

Save to flash.

---

## Step 4: Set Voltage Limits

**Parameters:** `udcmin`, `udclim`, `udcsw`

| Parameter | Description | Bench test value | Real vehicle value |
|---|---|---|---|
| `udcmin` | Minimum voltage — below this, VCU will not enter run | 20V | ~80% of minimum pack voltage |
| `udclim` | Maximum voltage — above this, VCU derates | High value (e.g. 500V) | Just above max charged pack voltage |
| `udcsw` | Voltage at which precharge is complete and main contactor closes | 15V (for bench with no HV) | ~95% of nominal pack voltage |

For initial LV bench testing with no HV connected, set `udcsw` to a low value (15–20V) so precharge "completes" quickly and lets you verify the sequence.

Save to flash.

---

## Step 5: Configure Throttle (Minimum Settings)

**Parameters:** `potmin`, `potmax`, `potmode`, `throtmin`, `throtmax`

First, set `potmode`:
- `single` — one throttle pot
- `dual` — two throttle pots (recommended)

Then watch the `pot` spot value while moving the throttle pedal and set:
- `potmin` = value just **above** the resting (off-throttle) ADC reading
- `potmax` = value just **below** the full-travel ADC reading

Then set:
- `throtmin` = 0 (or a small negative value if you want throttle-lift regen)
- `throtmax` = 100

> **`throtmax` defaults to 0.** This is the single most common cause of "throttle does nothing." Set it to 100 before testing.

If using dual throttle, also calibrate `pot2min` and `pot2max` the same way while watching `pot2`.

Save to flash.

---

## Step 6: Verify Brake Signal

In Spot Values, check `din_brake`.

- It should show **"off"** when the brake pedal is not pressed
- It should show **"on"** when the brake pedal is pressed

`din_brake` must be **"off"** for the VCU to allow torque output. If it is stuck "on" with no brake pressed, check:
- Brake switch wiring (is it normally open or normally closed?)
- Is the brake pin floating? Add a pull-down resistor to ground
- Is something else connected to Pin 49 at 12V?

---

## Step 7: Verify Direction Inputs

Apply 12V to Pin 54 (forward) and check `din_forward` in Spot Values — should show "on".
Apply 12V to Pin 53 (reverse) and check `din_reverse` — should show "on".

---

## Step 8: First Precharge Test (LV Only)

With everything configured and saved to flash:

1. Apply ignition ON signal to Pin 15 (pull to 12V)
2. Briefly apply START signal to Pin 52 (momentary 12V pulse)
3. Watch Spot Values:
   - `udc` should update (even if reading 0V with no HV)
   - Contactor outputs should fire (you'll hear the contactors click in sequence)
   - If `udc` rises above `udcsw`, the main contactor should close
   - `opmode` should eventually show `run`
   - `invstat` should show `on`

**If the system stays in PRECHARGE:**
- Was the START signal held long enough? It should be a short pulse, like turning a key — but it must be long enough for the VCU to register it (at least 500ms)
- Is `udc` reading a valid value? If it reads 0, the shunt is not communicating
- Is `udcsw` reachable? For LV bench testing, lower `udcsw` to 5V if needed

**If `opmode` never reaches "run":**
- Check `din_brake` is "off"
- Check `din_forward` or `din_reverse` is "on" (VCU needs a direction selected)
- Check `udc` is above `udcmin`

---

## Step 9: First Torque Test (LV Only — No Motor Movement Expected)

With `opmode` showing `run`:

1. Apply forward direction (Pin 54 to 12V)
2. Slowly apply throttle
3. Watch `potnom` — it should rise from 0 to 100 as you press the pedal
4. Watch `torque` — it should rise proportionally

Even without HV or a connected inverter, the VCU should be sending torque commands via CAN. You can verify this with a CAN analyser if available.

---

## Complete First-Start Parameter Checklist

| Parameter | Set to | Notes |
|---|---|---|
| `inverter` | Match your hardware | Comms section |
| `shuntType` | Match your hardware | ISA, SBOX, VAG, or LEAF |
| `inverterCan` | CAN bus your inverter is on | |
| `shuntCan` | CAN bus your shunt is on | |
| `udcmin` | 20V (bench) / ~80% min pack V | |
| `udclim` | 500V (bench) / above max pack V | |
| `udcsw` | 15V (bench) / ~95% nominal pack V | |
| `potmode` | single or dual | Match wiring |
| `potmin` | Just above off-throttle ADC reading | |
| `potmax` | Just below WOT ADC reading | |
| `pot2min` | Same for channel 2 (dual only) | |
| `pot2max` | Same for channel 2 (dual only) | |
| `throtmin` | 0 | |
| `throtmax` | **100** | Default is 0 — most common gotcha |
| `vehicle` | None or Classic | Unless integrating with OEM cluster |

---

## What's Next

- **C04** — Throttle Calibration: fine-tuning potmin/potmax, ramp rates, dual-pot plausibility
- **C05** — CAN Configuration: inverter CAN profiles, baud rates, message IDs
- **C06** — Fault Codes & Status Flags: reading and interpreting faults

---

*Source: openinverter.org/wiki/ZombieVerter_VCU | openinverter.org forum threads*  
*Last verified against firmware: V2.30A (August 2025)*
