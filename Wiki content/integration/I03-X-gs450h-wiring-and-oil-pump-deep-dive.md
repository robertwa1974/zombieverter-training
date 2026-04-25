# I03-X — GS450h Wiring & Oil Pump Deep Dive

**Track:** Integration (Deep Dive Extension)  
**Prerequisites:** I03 — GS450h Transaxle  
**Audience:** Intermediate  
**Estimated reading time:** 20 minutes

---

## Overview

This module covers the three most critical details of a GS450h integration that are most often done wrong: the HV connection bypass, the sync serial wiring, and the oil pump controller setup.

---

## HV Connection — The Critical Bypass

The GS450h inverter has two places you can connect HV. Only one is correct.

### The OEM Terminals — DO NOT USE

Connecting HV to the OEM positive/negative terminals routes current through the boost inductor and boost IGBT. These components are rated for approximately 100A maximum. Everything works fine on the bench and at low speed. Under sustained load at highway speed, the inverter destroys itself. At least two confirmed inverter failures from this mistake are documented in the community.

### The Brass Pillars — Correct Connection

Two brass pillars are accessed by removing a small black plastic cover and two M6 bolts (10mm head). These connect HV directly to the motor drive stage, bypassing the boost converter entirely.

**How to access:**
1. Locate the black plastic cover on the inverter body
2. Gently prize off the cover — Toyota uses adhesive
3. Remove the two M6 bolts (10mm head)
4. HV+ to one pillar, HV− to the other

> **For bench testing:** A 60V 5A power supply into the brass pillars is sufficient to verify sync serial communication and low-speed rotation. You do not need full pack voltage for initial bench testing.

---

## Sync Serial Interface — 8 Wires, 4 Differential Pairs

Unlike the Leaf (CAN) and Outlander (CAN), the GS450h uses a synchronous serial bus.

### Pin Assignments (ZombieVerter VCU)

| Signal | Direction | VCU Pin (−) | VCU Pin (+) |
|---|---|---|---|
| REQ | VCU → Inverter | 16 | 17 |
| CLK | VCU → Inverter | 18 | 19 |
| MTH | Inverter → VCU | 20 | 21 |
| HTM | VCU → Inverter | 22 | 23 |

> **Always verify against the current wiki pinout.** Pin assignments may vary between board revisions and firmware versions.

### Cable Requirements

- Use shielded twisted pair for each differential pair
- Toyota's OEM harness uses shielded twisted pairs — replicate this for reliable operation
- Building from scratch is achievable but error-prone; using the OEM harness is strongly recommended

### Connectivity Check (No HV Required)

With sync serial correctly wired and 12V applied to both VCU and inverter:
- Check `temphs` in Spot Values
- A reading of approximately 25–35°C at room temperature confirms the sync serial link is working
- A reading of 0 or negative means the sync serial is not communicating

---

## 12V Power to Inverter

From the OEM harness:

| OEM wire colour | Function |
|---|---|
| Green (×2) | 12V+ supply to inverter — join both, add fuse |
| White/black (×2) | Ground — join both |

Start with a 1A fuse and work upwards if it blows (2A → 3A → 5A). The GS450h inverter draws more than the VCU at startup.

The 12V supply to the inverter is switched by the VCU via the inverter enable relay (Pin 32). The inverter should not power up until the VCU is ready.

---

## Resolver Cable Extraction

The OEM "engine wire" harness contains the sync serial cables, resolver cables, and other signals. You use approximately 12% of the total harness.

### What to Extract

| Cable | Used for |
|---|---|
| MG1 resolver cable | Motor position sensing |
| MG2 resolver cable | Motor position sensing |
| Neutral safety switch harness (9-wire gray plug) | P/R/N/D detection |
| Shift solenoid harness (SL1, SL2) | Gear shift control (if used) |

### Key Tips

- **Blade technique:** Cut electrical tape and loom lengthwise with a sharp blade. A dull blade cuts wire insulation. Replace the blade before starting.
- **MG2 plug is at the rear of the transmission, MG1 is at the front.** Label them immediately on extraction — swapped resolver plugs cause resolver errors and the system won't run correctly.
- **Temperature sensor wires must be cut.** MG1 and MG2 temperature sensor wires (gray/green on MG2, red/blue on MG1) run inside the resolver cable bundle but terminate at the "harmonica" junction block and cannot be used. Cut them as far back as possible.
- **Gen 3 vs Gen 4:** Gen 3 (2007–2011) is the primary supported conversion platform. Gen 4 (2013+) harnesses may be physically compatible but test first.

### Buying a Harness

Search eBay for "GS450h engine wire" or "GS450h transmission harness." Expect to pay $125–200. Make lowball offers — sellers often accept. Always confirm from photos that the resolver plugs at the far end are not cut — this is the most commonly damaged part of a used harness.

---

## Oil Pump System

The GS450h inverter has its own internal oil cooling circuit. An electric oil pump must run continuously while the inverter is active — there is no mechanical pump drive in an EV conversion.

### Why It Matters

If the oil pump is not running when the inverter is active, the inverter overheats. This is not a gradual problem — the pump must run from precharge, throughout run mode, and should not stop until the inverter is fully de-energised.

### Oil Pump Specifications

| Parameter | Value |
|---|---|
| Current draw | ~25A from 12V at full speed |
| Power source | Dedicated 12V — NOT from VCU output pin |
| Control method | External controller with PWM input from VCU |
| Starting point | 30% PWM duty cycle |

### Oil Pump Controller Wiring

| Wire colour | Function |
|---|---|
| Blue | 12V+ supply to controller — 30A fuse minimum |
| Brown | Ground to controller casing |
| Black | PWM signal from VCU (GS450Hpump function) |

The controller has two connectors: power (to the pump motor) and resolver (pump position feedback).

> **⚠ The ~25A draw cannot come from a VCU output pin.** These are low-current signal outputs. Wire the controller power directly from the 12V battery or auxiliary bus with its own dedicated fuse.

### VCU Configuration

In Parameters → Dout, assign the `GS450Hpump` function to the Pump PWM output pin. Start at 30% duty cycle — this is sufficient for low-load bench operation. Increase for sustained high-load or elevated ambient temperatures.

> From V2.20A, the PumpPWM output function is freely assignable — not limited to GS450h builds. This allows coolant pump PWM control on other drivetrains using the same pin assignment method.

---

## Input Shaft Lock

Without locking the input shaft, MG1 can only spin the engine input shaft — it cannot send torque to the output. The lock forces MG1 torque through the power split device to the output shaft.

Without the lock, you lose approximately half your available torque and power. MG1 and MG2 combined with a properly locked shaft give a torque multiplication through the planetary gearset of approximately 2.6–2.7:1 for MG1's contribution.

The lock is a mechanical plate or bar with a spline fitting that bolts to the bellhousing flange and engages the engine input shaft splines. For bench testing only, Damien uses a vice grip and cable tie. For a real vehicle, a purpose-made billet lock plate is required.

---

## Common Integration Issues

| Issue | Cause | Fix |
|---|---|---|
| No temphs reading (0 or negative) | Sync serial not connected or wrong pins | Re-verify pin assignments against current wiki pinout |
| Ground loop / noise interference | Laptop USB connected to logic analyser during test | Disconnect USB/logic analyser, check chassis grounds |
| System won't stay in run after restart | ISA shunt on ignition-switched power | Move shunt to permanent power supply |
| Resolver errors | Swapped MG1/MG2 resolver connectors | Swap the resolver plugs |
| Inverter destroyed under load | HV connected to OEM terminals instead of brass pillars | Replace inverter, connect to brass pillars only |

---

*Source: Damien Maguire @Evbmw · Good Enuff Garage · openinverter.org/wiki*  
*Video sources: "GS450h EV Drivetrain Deep Dive" (2020) · "GS450h and GS300h VCU Connection" (2022) · "GS450h Transmission Wire Harness" (2025)*  
*Last verified against firmware: V2.30A (August 2025)*
