# W03 — Contactor & Precharge Circuit

**Track:** Wiring  
**Prerequisites:** H01 — VCU Hardware Walkthrough, F03 — EV Drivetrain Fundamentals  
**Audience:** All levels  
**Estimated reading time:** 18 minutes

---

## Why This Module Matters

Contactor and precharge wiring is the most safety-critical part of a ZombieVerter installation. Getting it wrong can result in:
- Violent inrush current that welds contactors closed permanently
- Failure to enter run mode (the most common first-start problem)
- Unexpected HV live conditions on the vehicle chassis

Read this module completely before wiring. Do not skip the UDC section.

---

## What the Contactor System Does

The ZombieVerter manages three contactors in a standard EV conversion:

| Contactor | Purpose |
|---|---|
| **Negative** | Connects the battery negative to the HV system ground |
| **Precharge** | Connects HV positive through a resistor, to slowly charge inverter capacitors |
| **Positive (Main)** | Connects battery positive directly to the HV bus once precharge is complete |

The sequencing logic is:

```
START signal received
        │
        ▼
Negative contactor CLOSES      ◄─── always first, immediate on MOD_PRECHARGE entry
        │
        ▼
Inverter 12V enable fires      ◄─── inv_out SET (Pin 32 relay), inverter begins booting
        │
   [250ms stagger]
        │
        ▼
Precharge contactor CLOSES     ◄─── current limited by precharge resistor
        │                           HV bus begins rising
        ▼
1 second minimum precharge time enforced regardless of UDC
        │
        ▼
UDC ≥ udcsw AND UDC < udclim AND throttle released?
        │
       YES ──── [250ms stagger] ──── Main (positive) contactor CLOSES
        │
        ▼
VCU enters RUN mode  ──── opmode = "run"
        │
       NO ──── wait (up to 5 seconds total from start)
                    │
              PRECHARGE FAULT ──── prec_out cleared, ERR_PRECHARGE posted
```

> **Important:** The precharge contactor does **not** open when the main contactor closes. It remains energised throughout the entire drive session and is only de-energised when the VCU returns to `MOD_OFF`. This is the actual firmware behaviour — the precharge resistor runs in parallel with the main contactor during normal driving. See [Precharge Contactor Behaviour](#precharge-contactor-behaviour) below.

---

## UDC — The Most Important Concept in This Module

**UDC is the VCU's measurement of HV bus voltage.** It is the single most critical input to the contactor sequencing logic.

Without a valid UDC reading, the ZombieVerter **will fail precharge and never enter run mode.** This is the most common cause of first-start failures.

The VCU can receive UDC from several sources, selected via the `shuntType` parameter:

| shuntType value | Source |
|---|---|
| `ISA` | ISA IVT current/voltage shunt (most common) |
| `SBOX` | BMW S-BOX battery management unit |
| `VAG` | Volkswagen/Audi battery system |
| `LEAF` | Nissan Leaf inverter (reports pack voltage via CAN) |

**You must configure `shuntType` to match your actual hardware.** If it is set to a source that is not present or not communicating, UDC will read zero and precharge will fail immediately.

### ISA Shunt — Permanent Power Requirement

If you are using an ISA IVT shunt (the most common choice), it must have **permanent 12V power** — the same always-on supply as the VCU itself. The ISA shunt continuously monitors and reports UDC.

If the shunt is powered from an ignition-switched supply, it will lose its UDC reading when the key is off. When you next turn the key and start precharge, the VCU may see a stale or zero UDC value and behave unpredictably.

> **Rule:** ISA shunt power = always on. Same feed as the VCU.

---

## Contactor Wiring

### Electrical Concept: Low-Side Switching

All contactor outputs on the ZombieVerter are **low-side switches**. This means:
- The VCU output pin connects to the **ground leg** of the contactor coil
- When the VCU activates the output, it pulls that pin to ground, completing the circuit
- The **positive leg** of every contactor coil must be connected to 12V+

**Never connect 12V+ to the VCU contactor output pins.** These are ground-side switching outputs only.

### Pin Assignments

| VCU Pin | Function | Connects to |
|---|---|---|
| Pin 31 | Negative contactor | Ground leg of negative contactor coil |
| Pin 33 | Positive (main) contactor | Ground leg of positive contactor coil |
| Pin 34 | Precharge contactor | Ground leg of precharge contactor coil |

### Wiring Diagram (Conceptual)

```
12V+ ──────────────────┬──────────────────┬──────────────────┐
                       │                  │                  │
                    [Neg Coil+]        [Pre Coil+]       [Main Coil+]
                    [Neg Coil−]        [Pre Coil−]       [Main Coil−]
                       │                  │                  │
                    Pin 31             Pin 34             Pin 33
                    (VCU)              (VCU)              (VCU)
                       │                  │                  │
12V GND ───────────────┴──────────────────┴──────────────────┘
```

### Contactor Polarity

Some contactors are polarity-sensitive — their coil has a defined positive and negative terminal. If wired backwards, they will not close (or may close but with reduced hold force and reduced life). Check your specific contactor datasheet.

---

## Precharge Resistor

The precharge resistor limits current flow during the precharge phase, protecting both the contactor and the inverter capacitors from inrush damage.

**Sizing guidelines:**
- Typical values: 40Ω–100Ω at 50W–100W rating
- Higher resistance = slower precharge (more protection, but must complete within 5 seconds)
- Lower resistance = faster precharge (less protection, may stress contactors)
- 100Ω / 100W is a common and safe starting point for most conversions up to ~400V

**Placement:** The precharge resistor connects in series with the precharge contactor, between the positive battery terminal and the positive HV bus (inverter side).

```
Battery +  ──── [Main Contactor] ──────────────────────── HV Bus +
                                                              │
                 [Precharge Contactor] ── [Resistor] ─────────┘
```

---

## Precharge Contactor Behaviour

> 🟡 **This differs from standard EV practice — read carefully.**

In most EV systems the precharge contactor opens as soon as the main contactor closes, removing the resistor from the circuit. **The ZombieVerter firmware does not do this.**

Looking at the state machine in `stm32_vcu.cpp`: `prec_out` is set during `MOD_PRECHARGE` and is never cleared on transition to `MOD_RUN` or during normal driving. The only places `prec_out` is explicitly cleared are:

- `MOD_OFF` — after the shutdown `rlyDly` countdown completes
- `MOD_PCHFAIL` — on a precharge timeout fault

This means **the precharge contactor remains closed in parallel with the main contactor for the entire drive session.** The precharge resistor is in the circuit throughout normal operation. At typical drive currents flowing through the main contactor, the resistor carries negligible current (the main contactor provides the low-impedance path), so this has no practical effect on performance.

The implication for hardware selection: your precharge contactor and resistor must be rated for sustained energisation, not just the brief precharge interval. Most standard precharge contactors are already rated for continuous coil energisation, but verify your specific part.

---

## UDC Measurement Point — ISA Shunt

The ISA shunt must be positioned to measure the voltage at the correct point. The shunt's U1 terminal reads voltage relative to HV ground.

**During precharge, U1 should be connected to the HV bus on the inverter side of the main contactor.** As the precharge resistor charges the inverter capacitors, U1 rises toward pack voltage. When it crosses `udcsw`, the VCU closes the main contactor.

A common mistake is connecting U1 to the battery side of the main contactor. In this position, U1 reads full pack voltage immediately (before precharge even starts), and the VCU will try to close the main contactor without actually precharging the inverter capacitors — potentially welding the main contactor on first use.

> **Check:** During initial power-up with no HV connected, U1 should read 0V. Apply HV with only precharge closed — U1 should rise slowly from 0V toward pack voltage. Only then will the VCU close the main contactor.

---

## Startup Timing Detail

The firmware enforces deliberate stagger delays between each contactor event. Understanding these helps diagnose first-start timing issues.

**Full contactor sequence with timing:**

```
MOD_PRECHARGE entry:
  t=0ms      NEG contactor closes (immediate)
  t=0ms      inv_out SET — inverter 12V enable fires (immediate)
  t=250ms    PREC contactor closes (after 25-tick rlyDly)
  t=250ms–1250ms  HV bus rising, 1-second minimum precharge enforced
  t=≥1250ms  UDC check passes

MOD_RUN entry:
  t+0ms      rlyDly=25 begins
  t+250ms    MAIN contactor closes (after 25-tick rlyDly)
  t+250ms    Drive enabled

MOD_OFF (shutdown):
  t=0ms      rlyDly=250 begins (2.5-second grace period)
  t=2500ms   All contactors open simultaneously
```

The **250ms gap between NEG and PREC** is intentional — it prevents multiple contactors pulling current simultaneously and gives the inverter time to begin its own boot sequence before HV arrives on the bus.

The **2.5-second shutdown delay** (10× longer than the startup stagger) gives the inverter time to ramp torque down to zero and safely discharge gate drivers before contactors open.

---

## Inverter 12V Enable — Timing and Exceptions

The VCU fires `inv_out` (Pin 32 relay) at the very start of `MOD_PRECHARGE`, **before** the precharge contactor closes. This is deliberate: the inverter needs time to boot its own firmware and establish CAN communication before the VCU expects to talk to it. The 250ms stagger before `prec_out` provides that window.

**Exception — OpenInverter-based inverters:** When the selected inverter type is set to OpenInverter (`Inverter = OI`), `inv_out` is **not** fired during precharge. OpenInverter manages its own startup independently. If you are using an OI-based inverter and the enable relay is not firing, this is expected behaviour, not a fault.

---

## Key Parameters

These parameters control contactor and precharge behaviour:

| Parameter | Description | Typical Value |
|---|---|---|
| `udcmin` | Minimum pack voltage — below this, VCU will not enter run mode | Set to ~80% of your minimum expected pack voltage (e.g. 20V for bench testing) |
| `udclim` | Maximum pack voltage — above this, VCU derates | Set just above your fully charged pack voltage |
| `udcsw` | Voltage threshold that triggers main contactor close | Set to ~95% of your nominal pack voltage |
| `shuntType` | Source of UDC measurement | Match to your hardware: ISA, SBOX, VAG, or LEAF |

### Common First-Start Mistakes

| Symptom | Likely Cause |
|---|---|
| UDC reads 0, precharge never completes | `shuntType` wrong, shunt not powered, shunt not initialised, shunt CAN bus not connected |
| UDC reads full pack voltage immediately, main contactor fires instantly | ISA U1 connected to battery side instead of inverter side |
| Precharge times out (stays in PRECHARGE state) | `udcsw` set too high, precharge resistor too large, shunt not reporting correctly |
| VCU never attempts precharge | `udcmin` set too high (pack voltage is below the minimum threshold) |
| Precharge completes but VCU won't enter run mode | `din_break` is showing "on" — brake signal is active or stuck, blocking run mode |
| Inverter enable relay not firing, OI inverter | Expected — `inv_out` is intentionally suppressed for OpenInverter type |
| Fault code appears briefly then clears on entering run mode | Normal — `ErrorMessage::UnpostAll()` is called every 10ms cycle while in `MOD_RUN` |

---

## ISA Shunt Initialisation

A new ISA shunt must be initialised before it will communicate on CAN. This is a one-time procedure:

1. Wire the ISA shunt to permanent 12V and the correct CAN bus
2. In the web interface under **Comms**, set `shuntCan` to the CAN bus the shunt is connected to
3. Save parameters to flash
4. Under **Comms**, set `ISAMode` to **Init**
5. Save parameters to flash
6. Power cycle the VCU and shunt simultaneously (they should be on the same 12V feed)
7. The shunt initialises
8. Set `ISAMode` back to **Normal**
9. Save parameters to flash
10. Reboot the VCU

**If initialisation fails:**
Separate the shunt and VCU power supplies. Power on the shunt first, wait 2–3 seconds, then power on the VCU. This delay allows the shunt to fully boot before the VCU attempts to communicate with it. This has resolved initialisation failures for a number of users.

---

## Contactor Firing During Precharge — Inverter Enable Relay

One subtle but important wiring detail: the inverter (and charger, DCDC) should not receive its 12V "ignition/enable" signal until the VCU is ready to energise it. Premature inverter power-up can cause:
- CAN bus conflicts before the VCU has configured the inverter
- Inverter self-initialisation that conflicts with VCU sequencing

The ZombieVerter controls an external relay (via Pin 32, low-side switching) to provide a switched 12V "ignition" signal to these devices. This relay fires at the start of `MOD_PRECHARGE`, giving the inverter a 250ms head-start before the precharge contactor closes and HV arrives on the bus.

**Relay wiring:**
```
12V+ ──── [Relay coil +]
          [Relay coil −] ──── Pin 32 (VCU) ──── GND
          [Relay switch NO] ──── 12V+
          [Relay switch COM] ──── Inverter/charger enable/ignition pin
```

Check that this relay is firing during precharge by watching the inverter's power indicator or CAN traffic when you apply the Start signal.

---

## Troubleshooting Checklist

Before assuming a hardware fault, verify all of the following:

- [ ] `shuntType` matches actual hardware
- [ ] ISA shunt has permanent 12V power (not ignition-switched)
- [ ] ISA shunt has been initialised (ISAMode Init → Normal cycle)
- [ ] ISA shunt CAN bus matches `shuntCan` parameter setting
- [ ] CAN bus has correct termination (120Ω at each end of the bus)
- [ ] ISA shunt U1 is connected to inverter side of main contactor (not battery side)
- [ ] All contactor coil positive leads are connected to 12V+
- [ ] All contactor coil negative leads are connected to the correct VCU pins (31, 33, 34)
- [ ] `udcmin` is set to a sane value (try 20V for bench testing)
- [ ] `udcsw` is set below actual pack voltage
- [ ] `din_break` reads "off" in spot values (brake signal not stuck on)
- [ ] Inverter enable relay is firing during precharge (Pin 32) — except OpenInverter type

---

## What's Next

- **W04** — HVIL: High Voltage Interlock Loop
- **W07** — CAN Bus Wiring: termination and topology
- **C03** — Essential Parameters: First Start

---

*Source: openinverter.org/wiki/ZombieVerter_VCU | openinverter.org forum threads | stm32_vcu.cpp V2.40A-RW*  
*Last verified against firmware: V2.30A (August 2025)*
