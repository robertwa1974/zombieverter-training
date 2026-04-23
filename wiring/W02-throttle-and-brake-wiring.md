# W02 — Throttle & Brake Wiring

**Track:** Wiring  
**Prerequisites:** H01 — VCU Hardware Walkthrough  
**Audience:** All levels  
**Estimated reading time:** 12 minutes

---

## Overview

The throttle and brake inputs are the primary driver interface signals. Getting them right — especially the throttle calibration — is essential for safe, predictable vehicle behaviour. This module covers the wiring; calibration parameters are covered in Module C04.

---

## Throttle Pedal Wiring

### Dual vs Single Channel

The ZombieVerter supports both single and dual-channel throttle pedals. **Dual-channel is strongly recommended** for safety — if one channel fails (open circuit, short circuit, or mechanical linkage failure), the VCU can detect the discrepancy between channels and cut torque rather than applying full throttle.

Single-channel is available but provides no redundancy. If the single pot fails in the high direction, the result is unintended full throttle. Use dual-channel wherever possible.

### Pin Assignments

| VCU Pin | Function | Connect to |
|---|---|---|
| Pin 48 | Throttle 5V supply | Throttle pot(s) positive (Vcc) |
| Pin 47 | Throttle channel 1 | Channel 1 wiper |
| Pin 46 | Throttle channel 2 | Channel 2 wiper |
| Pin 45 | Throttle ground | Throttle pot(s) negative (GND) |

For a dual-channel pedal, both pots share the 5V supply (Pin 48) and ground (Pin 45), with their wipers going to Pins 47 and 46 respectively.

For a single-channel pedal, only Pins 48, 47, and 45 are used. Set `potmode` to single in the web interface.

### Wiring Diagram

**Dual-channel throttle:**
```
Pin 48 (5V) ─────┬──────────── Pot 1 Vcc
                 └──────────── Pot 2 Vcc

Pin 47 (Ch1) ─────────────── Pot 1 Wiper
Pin 46 (Ch2) ─────────────── Pot 2 Wiper

Pin 45 (GND) ─────┬──────────── Pot 1 GND
                  └──────────── Pot 2 GND
```

**Single-channel throttle:**
```
Pin 48 (5V) ──────────────── Pot Vcc
Pin 47 (Ch1) ─────────────── Pot Wiper
Pin 45 (GND) ─────────────── Pot GND
```

---

## Understanding How the ZombieVerter Reads Throttle

This is one of the most important things to understand before calibrating — **the ZombieVerter handles potmin/potmax differently from most inverters and motor controllers.**

### The Standard Approach (Most Controllers)
Most motor controllers set `potmin` and `potmax` *outside* the mechanical travel range of the pedal. For example, if the pedal physically travels from an ADC value of 400 to 2600, you might set `potmin` to 300 and `potmax` to 2700. This way, if a value outside those limits is detected (due to an open wire, short, or mechanical failure), the controller faults safely.

### The ZombieVerter Approach (Opposite!)
The ZombieVerter sets `potmin` and `potmax` *inside* the mechanical travel range:
- `potmin` should be set **just above** the value seen at the resting (off-throttle) position
- `potmax` should be set **just below** the value seen at full throttle

This means the pedal physically travels slightly beyond both limits. The VCU uses these values to calculate a normalised 0–100 `potnom` value.

> **This trips up almost everyone coming from other systems.** If you set `potmin` below your actual resting position, the VCU will interpret the pedal as always slightly depressed. If you set `potmax` above your actual WOT value, you'll never reach 100% torque.

**Calibration procedure (covered in detail in Module C04):**
1. Watch the `pot` spot value in the web interface while moving the pedal
2. Note the value at rest — set `potmin` just above this
3. Note the value at full travel — set `potmax` just below this
4. Do the same for `pot2min` / `pot2max` if using dual-channel

---

## Throttle Parameters Quick Reference

| Parameter | Description |
|---|---|
| `potmin` | ADC value just above off-throttle resting position |
| `potmax` | ADC value just below wide-open throttle |
| `pot2min` | Same as potmin but for channel 2 |
| `pot2max` | Same as potmax but for channel 2 |
| `potmode` | `single` or `dual` — must match your wiring |
| `potnom` | Resulting normalised 0–100 throttle value (spot value, read-only) |
| `throtmin` | Minimum allowed potnom — can be negative (for throttle-lift regen) |
| `throtmax` | Maximum allowed potnom in forward direction |
| `throtramp` | Rate of potnom increase (potnom change per %/10ms) — limits rate of torque rise |
| `throtramprpm` | Motor RPM above which throtramp no longer applies |
| `revlim` | Rev limiter (motor RPM) |

### Critical Gotcha: `throtmax` Defaults to Zero

`throtmax` defaults to **0** in a fresh configuration. This means the VCU will allow zero forward torque regardless of throttle position. **This is the most common reason for a "throttle does nothing" problem on first start.** Set `throtmax` to 100 (or your desired maximum) before expecting torque output.

---

## Brake Signal Wiring

### Purpose

The brake signal serves two functions in the ZombieVerter:
1. **Safety interlock** — `din_break` must read "off" before the VCU will allow torque output. If the brake is stuck "on", the VCU will not produce torque even if throttle is applied.
2. **Regen trigger** — applying the brake can trigger regenerative braking (configured separately — see Module A01).

### Wiring

The brake input is a simple digital input:

| VCU Pin | Function | Connect to |
|---|---|---|
| Pin 49 | Brake input | 12V+ when brake pedal is pressed |

When the brake pedal is pressed, Pin 49 is pulled to 12V+. When released, Pin 49 should return to 0V (or float).

**Do not leave Pin 49 floating** — a floating input can read randomly as "on" due to electrical noise, blocking torque output unpredictably. If you are not wiring a brake signal for now (bench testing), either connect Pin 49 to ground through a resistor or confirm `din_break` reads "off" in spot values before troubleshooting torque issues.

### BrakeLight Output

The VCU can drive a brake light output from a configurable low-side output pin. Assign the `BrakeLight` function in the web interface to activate this output when the brake is pressed above a configurable threshold.

---

## Forward / Reverse Wiring

| VCU Pin | Function | Connect to |
|---|---|---|
| Pin 54 | Forward | 12V+ when forward selected |
| Pin 53 | Reverse | 12V+ when reverse selected |

Both are digital inputs pulled high to 12V+ to select direction. The direction signal can come from:
- A physical gear selector lever with detents (park/reverse/neutral/drive)
- A toggle switch
- A momentary button (set `dirmode` to `button` or `buttonReversed` in the web interface)

`dirmode` parameter options:
- `switch` — pin high = direction active
- `button` — momentary press toggles direction
- `switchReversed` — inverted logic
- `buttonReversed` — inverted momentary logic

---

## Common Wiring Mistakes

| Problem | Cause |
|---|---|
| `din_break` always shows "on" | Brake pin wired to constant 12V+, or brake switch wired NC instead of NO |
| `din_break` always shows "on" | Floating pin picking up noise — add pull-down resistor |
| `potnom` never reaches 100 | `potmax` set higher than actual WOT ADC value |
| `potnom` shows value at rest | `potmin` set lower than actual resting ADC value |
| No torque output | `throtmax` set to zero (default) |
| Erratic torque | Poor ground connection between throttle pot GND and Pin 45 |
| Channel 2 fault | `potmode` set to dual but pot2min/pot2max not calibrated |

---

## What's Next

- **C04** — Throttle Calibration: step-by-step parameter tuning in the web interface
- **W03** — Contactor & Precharge Circuit
- **A01** — Regen Tuning: brake and throttle-lift regen configuration

---

*Source: openinverter.org/wiki/ZombieVerter_VCU | openinverter.org forum threads*  
*Last verified against firmware: V2.30A (August 2025)*
