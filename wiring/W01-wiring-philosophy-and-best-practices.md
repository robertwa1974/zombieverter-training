# W01 — Wiring Philosophy & Best Practices

**Track:** Wiring  
**Prerequisites:** H01 — VCU Hardware Walkthrough  
**Audience:** All levels  
**Estimated reading time:** 15 minutes

---

## The Philosophy

A ZombieVerter wiring harness is not a single entity — it is three logically separate fuse blocks, each with a distinct purpose, feeding different groups of components. Understanding this structure before crimping a single terminal will save hours of debugging later.

The three groups are:

1. **Permanent power** — always live, even when the vehicle is parked
2. **Ignition ON** — live when the key is in the ON position
3. **Start position** — momentary signal only, like turning a key to START

Each group has its own fuse block. Each fuse block has its own feed from the 12V battery. Mixing these groups — feeding an ignition-switched device from permanent power, or running too much current through the ignition switch — is the most common source of mysterious electrical gremlins in EV conversions.

---

## Fuse Block Strategy

### Permanent Power Block

**What belongs here:** VCU (Pin 56), ISA shunt, any device that needs to run when the vehicle is parked (charge timer management, telematics).

**Fuse sizing:** 1–3A for VCU alone. Add appropriately for other permanent loads. Each device on this block should have its own individual fuse — don't share.

**Why separate:** The VCU and ISA shunt must have always-on power. If you feed them from ignition-switched supply, the shunt loses UDC state on key-off and precharge fails on every startup. See Module C03.

**Practical tip:** Use modular automotive fuse blocks (e.g. Dorman 4-position blocks). They connect together like Lego — start with 4 positions, add another block as devices accumulate. The bus bar makes adding feeds trivial.

### Ignition ON Block

**What belongs here:** Devices that should wake up when the key is turned on but should not draw permanent power. In a ZombieVerter build this block is typically fed from the inverter enable relay (Pin 32) rather than the ignition switch directly — the VCU controls when these devices get power.

**Why use the relay:** The inverter, charger, and DC-DC converter should not power up until the VCU is ready to manage them. Feeding them from a direct ignition feed bypasses this protection.

### Start Position Block

**What belongs here:** The start signal (Pin 52) only. This is a momentary 12V pulse — 500ms minimum — that triggers the contactor sequence. Not a sustained feed.

**Key principle:** Never run high current through the ignition switch. The ignition switch should only carry enough current to activate relays and signal pins. Fuse the ignition switch output at 5A or less.

---

## Wire Gauging

Wire gauge is specified in AWG in North America, metric cross-section (mm²) in Europe. Higher AWG number = thinner wire — the opposite of the metric system.

| Application | Suggested gauge |
|---|---|
| HV main traction cables | 35–70mm² (0 AWG or larger) |
| HV charger / DC-DC | 10–16mm² (6–4 AWG) |
| 12V main battery feed | 6–10mm² (10–8 AWG) |
| 12V fuse block feeds | 4mm² (12 AWG) |
| Signal wires (VCU pins) | 0.5–1mm² (20–18 AWG) |
| CAN bus | 0.5mm² twisted pair (22 AWG) |

> **Rule:** Rule: Size the wire for the load current. Then size the fuse just below the wire's current rating. The fuse protects the wire — the wire must already be sized to handle the device.

---

## Connector Selection

**For the VCU 56-pin header:** Use the correct Aptiv (formerly Delphi) connector with the matching terminal crimps. Available as a complete kit on AliExpress. Use a proper ratcheting crimp tool — a generic crimp tool produces unreliable crimps on these terminals.

**For signal connections:** Use automotive-grade waterproof connectors (Deutsch DT or equivalent) where connections may be exposed to moisture or vibration. Avoid bare blade connectors in the engine bay.

**For CAN bus:** Twisted pair. Either purpose-made CAN cable or twisted 22 AWG signal cable. Termination at both ends with 120Ω resistors.

**Joining wires:** Solder and heat-shrink, or proper crimp splice connectors. Never twist-and-tape. Wire nuts are not suitable for automotive use.

---

## Labelling

Label every wire at both ends before installation. Once a harness is routed and cable-tied, tracing an unlabelled wire is extremely time-consuming.

A simple label convention:
```
P56-12VPERM   ← Pin 56, permanent 12V
P15-IGNON     ← Pin 15, ignition ON signal
CAN1H-INV     ← CAN1 High, to inverter
```

Use heat-shrink label sleeves or a label maker with vinyl tape. Marker pen on tape fades in heat and oil.

---

## Dupont Cables — For Bench Only

Dupont (breadboard) jumper cables are useful for initial bench testing — they let you power up the board without committing to a permanent header. However they are loose, unreliable, and not rated for automotive vibration. Remove and replace with proper crimped terminals before the vehicle goes on the road.

---

## Building the Harness — The Sequence

Good Enuff Garage's wire harness series (April–June 2024) documents the complete ZombieVerter harness build sequence. The recommended order:

1. **Permanent power fuse block** — build first, verify VCU powers up and Wi-Fi appears
2. **Ignition switch to VCU** — add ignition ON (Pin 15) and momentary start (Pin 52)
3. **Verify run mode on bench** — 12V only, no HV — before adding anything else
4. **Forward/reverse switch** — add direction control (Pins 53/54), verify din_forward/din_reverse in Spot Values
5. **Brake signal** — add brake switch (Pin 49), verify din_brake goes on/off correctly
6. **Throttle wiring** — add pot signals, calibrate
7. **Inverter relay** — add Pin 32 output relay, test switched supply
8. **Contactor wiring** — add precharge, negative, main contactor coil wiring
9. **CAN bus** — add inverter CAN, shunt CAN
10. **HV connections** — final step, after all 12V functionality is verified

Build incrementally and verify each step before adding the next. A fault in step 3 is easy to find. The same fault buried under 8 more steps takes hours.

---

## The Safety Box Harness

The BMW Safety Box (S-BOX) is often used in BMW-based conversions to provide pack monitoring and HVIL in one unit. The S-BOX harness is covered in the wire harness series (May 2024, Parts 1 and 2). Key point: the S-BOX communicates over CAN2 and provides the `udc` reading that the VCU uses for precharge. Set `shuntType` = SBOX and `shuntCan` = CAN2.

---

## Common Wiring Mistakes

| Mistake | Consequence | Prevention |
|---|---|---|
| VCU on ignition-switched power | Shunt loses UDC, precharge fails every startup | Permanent power to Pin 56 always |
| Brake switch on normally-closed terminal | `din_brake` stuck on, no torque ever | Use normally-open (NO) terminal |
| CAN H and CAN L swapped | No communication, no fault message | Use twisted pair, check colour code |
| Missing CAN termination | Intermittent communication faults under load | 120Ω at each end of each bus |
| throtmax left at 0 | Throttle does nothing | Set to 100 — see C04 |
| Contactor coil+ wired to VCU output pin | VCU output damaged — outputs are low-side only | Coil+ to 12V, coil− to VCU pin |

---

*Source: Good Enuff Garage "DIY Wire Harness" series (April–June 2024, 10 videos) · Damien Maguire @Evbmw*  
*Last verified against firmware: V2.30A (August 2025)*
