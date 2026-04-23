# C06 — Fault Codes & Status Flags

**Track:** Firmware & Configuration  
**Prerequisites:** C02 — Web Interface Walkthrough, C03 — Essential Parameters: First Start  
**Audience:** All levels  
**Video source:** "ZombieVerter VCU Won't RUN" (May 2024, Good Enuff Garage)  
**Estimated reading time:** 12 minutes

---

## Overview

When the ZombieVerter doesn't behave as expected, the web interface gives you two key feedback mechanisms:
- **`opmode`** — the current operating state of the VCU
- **`status` / `lastError`** — what the VCU last tried to do and why it stopped

Understanding these is the difference between spending five minutes diagnosing a problem and spending five hours replacing things that weren't broken.

---

## Operating Modes (`opmode`)

`opmode` is visible in Spot Values and shows the current state of the VCU state machine.

| opmode value | Meaning |
|---|---|
| `off` | VCU is powered but ignition is not on, or system is in standby |
| `precharge` | Start signal received — negative and precharge contactors closed, waiting for UDC to rise |
| `pch` / `PCH` | Same as precharge (abbreviated display) |
| `run` | Precharge complete, main contactor closed, system ready for torque commands |
| `charge` | System is in charge mode (HV contactors closed for charging) |

**Normal startup sequence:**
```
off → precharge → run
```

If the system goes `off → precharge → off` or `off → precharge → pch fail`, something prevented precharge from completing.

---

## The `lastError` and `status` Fields

These two spot values tell you what the VCU was trying to do and why it stopped. They are often more useful than `opmode` alone.

> **Note on naming:** The field called `lastError` is not always actually an error — it often records the last significant status change. Think of it as "last known status" rather than "last fault." Similarly, `status` reports the current blocking condition.

### Common `status` Messages

| status message | Meaning | Common cause |
|---|---|---|
| `UDC below udcsw` | Pack voltage hasn't reached the precharge completion threshold | `udcsw` set too high, shunt not communicating, wrong `shuntType` |
| `Throttle 1 2` | Throttle channel fault | `pot2min`/`pot2max` not calibrated, potmode mismatch, wiring issue |
| `din_break on` | Brake signal is active | Brake wired normally-closed instead of normally-open, floating input |

---

## The Most Common Failure: `udcsw`

This is the single most frequently missed parameter for first-time users.

**What it does:** `udcsw` is the voltage threshold that tells the VCU "precharge is complete — close the main contactor and enter run mode." It defaults to **330V**.

**The problem:** On a workbench with no HV battery connected, the VCU will never see 330V. Precharge will start, time out, and fail — every time.

**The fix:** Set `udcsw` appropriately for your situation:

| Situation | Set `udcsw` to |
|---|---|
| Bench testing, no HV connected | 0–5V (just to prove the sequencing works) |
| Bench testing with low-voltage HV source | Just below your source voltage |
| Real vehicle, known pack voltage | ~95% of nominal pack voltage |

> **Why does it default to 330V?** Setting it too low is dangerous — the main contactor could close before the inverter capacitors are adequately charged, potentially damaging or destroying the inverter. The 330V default is conservative and safe for common Nissan Leaf/Prius systems. It is intentionally set to require you to make a conscious decision about your pack voltage.

**Procedure to diagnose and fix:**

1. Go to Spot Values, enable Auto Refresh
2. Turn ignition ON → press START
3. Watch `opmode` — does it go to `precharge`? Good. Does it then fail?
4. Check `status` — if it says `UDC below udcsw`, this is your issue
5. Go to Parameters → Contactor Control → `udcsw`
6. Set to 0 for bench testing (no HV) or appropriate value for your pack
7. Save Parameters to Flash
8. Try again

---

## Precharge Failure Diagnosis Tree

```
System won't reach RUN mode
            │
            ▼
Does opmode reach "precharge"?
     │              │
    NO             YES
     │              │
     ▼              ▼
Check:        Does it then fail?
- Ignition         │
  signal on   ─── YES
  Pin 15           │
- Start signal     ▼
  on Pin 52   Check status field:
                   │
          ┌────────┼────────┐
          │        │        │
    "UDC below  "din_break  Other
    udcsw"      on"
          │        │        │
          ▼        ▼        ▼
    Check       Brake    Check shunt,
    udcsw       signal   CAN wiring,
    setting     wiring   udcmin
```

---

## Throttle Status Errors

After precharge succeeds and `opmode` reaches `run`, the next common status message involves the throttle:

### `Throttle 1 2` (or similar)

This means the VCU has a problem with one or both throttle channels. Common causes:

1. **`potmode` set to `dual` but only one channel wired** — Channel 2 reads a fixed value that disagrees with channel 1's movement
2. **`pot2min`/`pot2max` not calibrated** — Channel 2 plausibility check fails immediately
3. **Wiring fault** — One channel is open or shorted

**Diagnosis:**
1. Go to Spot Values
2. Watch `pot` and `pot2` while moving the pedal
3. Both should change. If one stays fixed, that channel has a wiring problem.
4. If both change but the system still faults, check that `pot2min`/`pot2max` are calibrated (not at defaults)

---

## `din_break` — The Brake Signal Interlock

`din_break` is a critical safety interlock. **The VCU will not produce torque while `din_break` shows "on"**, regardless of throttle position or operating mode.

This causes significant confusion because the system appears to be in run mode, the throttle appears to work (potnom changes), but the motor does nothing.

**Check in Spot Values:**
- `din_break` = **off** → normal, torque is allowed
- `din_break` = **on** → brake is active, torque is blocked

### Causes of `din_break` being stuck "on"

| Cause | Fix |
|---|---|
| Brake wired to constant 12V | Check brake switch wiring — should be normally open |
| Brake switch wired normally-closed (NC) | Use the normally-open (NO) terminal |
| Pin 49 floating with electrical noise | Add 10kΩ pull-down resistor from Pin 49 to ground |
| Brake pedal held down during testing | Release the brake |

---

## Parameter Abbreviations Reference

The ZombieVerter interface uses abbreviated parameter names that can be confusing. Common ones:

| Abbreviation | Full meaning |
|---|---|
| `udc` | Battery/pack voltage (U = voltage in German/Latin, DC = direct current) |
| `udcsw` | UDC switch — voltage at which precharge is considered complete |
| `udcmin` | UDC minimum — below this voltage, VCU will not enter run mode |
| `udclim` | UDC limit — maximum pack voltage before derating |
| `invudc` | Inverter-reported DC bus voltage |
| `opmode` | Operating mode |
| `invstat` | Inverter status |
| `pot` | Throttle channel 1 raw ADC value (pot = potentiometer, legacy name) |
| `pot2` | Throttle channel 2 raw ADC value |
| `potnom` | Normalised throttle demand (0–100) |
| `din_break` | Digital input — brake signal |
| `din_forward` | Digital input — forward direction signal |
| `din_reverse` | Digital input — reverse direction signal |
| `din_start` | Digital input — start signal |
| `temphs` | Temperature — heat sink (inside inverter) |
| `tempm` | Temperature — motor |
| `idc` | DC current from shunt |
| `pch` | Precharge (abbreviated in status messages) |

---

## Reading the Interface Efficiently

### Use Ctrl+F
The web interface is a single long page. Use browser find (Ctrl+F) to locate specific parameters or spot values quickly. Search for `udcsw` to jump directly to that parameter.

### Use Auto Refresh Strategically
Auto Refresh updates all spot values continuously. For diagnosis, turn it on and watch specific values while performing actions (turning ignition on, pressing start, moving throttle). For calibration, it's easier to turn it off and use the manual Refresh button so values don't jump while you're trying to read them.

### Use the Visible Filter
Check the Visible box for only the spot values you're currently watching, hide the rest. This dramatically reduces clutter, especially useful when diagnosing precharge issues (watch just `opmode`, `status`, `udc`) or throttle issues (watch just `pot`, `pot2`, `potnom`, `din_break`).

---

## What's Next

- **C07** — Data Logging & Live Telemetry
- **W03** — Contactor & Precharge Circuit (for deeper precharge theory)

---

*Source: "ZombieVerter VCU Won't RUN" — Good Enuff Garage (May 2024) | openinverter.org/wiki/ZombieVerter_VCU*  
*Last verified against firmware: V2.30A (August 2025)*
