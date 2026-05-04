# A02 — Charge Control & Popular Chargers

**Track:** Advanced  
**Prerequisites:** C03 — Essential Parameters: First Start, W03 — Contactor & Precharge Circuit  
**Audience:** All levels  
**Estimated reading time:** 20 minutes

---

## Overview

The ZombieVerter supports AC onboard charging, CHAdeMO DC fast charging, and CCS via the BMW i3 LIM or Foccci open-source controller. One VCU can manage any of these, and combinations are possible (e.g. Leaf PDM for AC plus CHAdeMO for fast charging in the same vehicle).

### Supported Chargers

| Charger | AC Power | Notes |
|---|---|---|
| Nissan Leaf PDM Gen1 | 3.3 kW | Simplest setup — no CP/PP wiring to VCU |
| Nissan Leaf PDM Gen2 | 6.6 kW | Recommended first build |
| Nissan Leaf PDM Gen3 | 6.6 kW | 2018+ Leaf. Improved in V2.22A |
| Mitsubishi Outlander OBC | 3.3 kW | AC + DC-DC. Two 12V feeds required. |
| VW Golf PHEV OBC | 3.3 kW | VAG protocol. Two CAN buses. |
| Audi e-tron OBC | 7.2–11 kW | Most popular VW option. |
| MG ZS Gen1 OBC | 6.6 kW | VAG protocol. |
| MG ZS Gen2 OBC | 6.6–11 kW | 3-phase capable. |
| Tesla Gen2 charger | 10 kW | Requires open-source controller board. |
| Tesla Gen3 charger | 18.5 kW | Requires Gen3 v2 controller board. |
| Elcon | 1.5–6.6 kW | Universal J1772 charger. |
| CHAdeMO | DC 50+ kW | Native VCU support. 6 PCB jumpers required. |
| CCS (BMW i3 LIM) | DC fast | Salvaged from i3. Type 1 and 2. |
| CCS (Foccci) | DC fast | Open-source controller. V2.20A one-click setup. |

---

## Understanding CP and PP Signals

Every J1772 / Type 2 AC charging setup uses two signals from the charge port to the VCU. Understanding these is essential before wiring any charger except the Leaf PDM.

### Control Pilot (CP)

The EVSE (charge station) generates the CP signal. It tells the car how much current is available and detects when the car is ready to charge. The car signals readiness by pulling down the pilot voltage through a resistor.

| State | CP voltage | Meaning |
|---|---|---|
| A | +12V DC | No vehicle connected |
| B | +9V DC | Vehicle present, not ready |
| C | +6V PWM | Vehicle ready — charging permitted |
| D | +3V PWM | Ready + ventilation required |

The PWM duty cycle encodes available current: 10% = 6A · 25% = 15A · 50% = 30A.

**CpSpoof (V2.20A+):** The VCU can generate a fake State C signal via a PWM output pin, so chargers that need CP confirmation (Outlander OBC, Foccci, some VW OBCs) start charging without a full J1772 charge port. Assign the `CpSpoof` function to a high-side PWM output pin in the Dout section.

### Proximity Pilot (PP)

PP detects whether a cable is physically plugged in. A resistor inside the cable connector pulls down a 5V sense line. Different cable current ratings use different resistor values.

| PP resistor in cable | Cable rating |
|---|---|
| Open circuit | No cable / disconnected |
| 1.5 kΩ | 13A cable |
| 680 Ω | 20A cable |
| 220 Ω | 32A cable |

**PP wiring — voltage divider circuit:**

The PP sense line requires a two-resistor voltage divider:
- **Upper resistor (pull-up):** 330Ω from VCU 5V supply (Pin 48) to the PP sense line
- **Lower resistor (to ground):** This is the resistor built into the charge port or cable connector:
  - **Type 1 (J1772) connectors:** 2.7kΩ to ground
  - **Type 2 (IEC 62196) connectors:** 4.7kΩ to ground
  - Note: many charge ports already have this lower resistor installed — check before adding one

The VCU analogue input reads the voltage at the midpoint of this divider. Different cable PP resistors change the midpoint voltage, allowing the VCU to detect both cable presence and current rating.

**Setup:** Assign the `ProxPilot` function to an analogue input pin. Watch `PPVal` in Spot Values while plugging in a cable. Set `PPthreshold` just above the reading when the cable is fully inserted. Note that different cables (13A vs 32A) will give different `PPVal` readings — set your threshold for the lowest-rated cable you intend to use.

> **Leaf PDM exception:** The Leaf PDM detects cable insertion internally via its own CP circuit. You do not need to wire PP to the VCU for a Leaf PDM build.

---

## Charge Mode Operation

Charge mode is triggered automatically when the VCU detects cable insertion via PP/ProxPilot, or a CHAdeMO/CCS handshake begins.

### What Changes in Charge Mode

| Aspect | In charge mode |
|---|---|
| `opmode` | Shows "charge" |
| HV contactors | Closed — HV bus live for charging |
| Throttle commands | Ignored — zero torque to inverter |
| DC-DC converter | Active — charges 12V battery from HV |
| Charge current | VCU sends power/current command to OBC via CAN |

### Key Charge Parameters

| Parameter | What it does |
|---|---|
| `chargerType` | Selects your OBC (LeafPDM, Outlander, VAG, Tesla…) |
| `chargePower` | Watts requested from OBC (Leaf PDM) |
| `chargeCurrent` | Max AC current limit (A) |
| `chargeVoltage` | Target / maximum pack voltage |
| `PPthreshold` | PP ADC value that triggers charge mode |
| `chargeStart` / `chargeStop` | Scheduled charge timer (hour of day) |

### Setup Checklist

1. Set `chargerType` — save to flash
2. Wire PP if required (not Leaf PDM): 330Ω pull-up to 5V → analogue input → assign ProxPilot → calibrate PPthreshold
3. Wire CpSpoof if required: assign to PWM output. Needed for Outlander, Foccci, most VW OBCs
4. Set `chargeVoltage` and `chargeCurrent` limits
5. Test: plug in cable → watch `opmode` in Spot Values → should transition to "charge" → watch `idc` for current flow

---

## Nissan Leaf PDM

The simplest charging setup. The PDM combines the AC charger and DC-DC converter in one unit.

**Minimum requirements:** 12V power · HV bus · CAN. No CP/PP wiring to VCU. No PWMs, no HVIL, no special relay logic. Set `chargerType` = LeafPDM and the VCU handles all CAN messaging.

**Power control:**

```
chargerType = LeafPDM
chargePower = 1000   ← start at 1kW, ramp up
chargePower = 3300   ← Gen1 max
chargePower = 6600   ← Gen2/3 max
chargePower = 0      ← stop charger
```

> **DC-DC note:** The PDM's DC-DC activates in charge mode. Ensure permanent 12V on VCU — a 12V dropout reboots the VCU mid-session.

---

## Mitsubishi Outlander OBC

3.3 kW AC charger + DC-DC converter. Supported since V2.01A.

> **🔴 Two 12V power inputs — both must be fed.** The Outlander OBC has two separate 12V connectors. Both must be powered. Wiring only one: `opmode` shows "charge" but `idc` = 0 and no current flows. This is the most common Outlander charging failure.

**CP/PP wiring required.** From V2.20A, use `CpSpoof` PWM output for CP. Wire PP with 330Ω pull-up to 5V.

V2.20A also added a required CAN heartbeat message — without it the OBC stops after a timeout. Current firmware handles this automatically.

---

## VW / Audi OBC and MG ZS

All use VAG protocol — set `chargerType` = VAG.

> **🔴 Two separate CAN buses required.** VW chargers use "Hybrid CAN" and "Powertrain CAN" internally. Both must connect to different VCU CAN ports. Wire only one bus and the charger ignores you.

**Audi e-tron OBC** (7.2–11 kW): Most popular VW option. The VCU sends startup CAN commands that disable OEM requirements for charge port lock feedback and LIN features — no OEM Audi charge port needed. Community credit: Mitch Elliott's reverse engineering.

**MG ZS Gen2** (11 kW): 3-phase capable. Also VAG protocol.

All VW/MG chargers need PP wiring (330Ω pull-up) and CpSpoof or physical CP circuit.

---

## Tesla Gen2 and Gen3 Chargers

Both require dedicated open-source controller boards — available from evbmw.com or build from GitHub.

**Gen2 (10 kW, Model S pre-2017):** Requires HV first, then CAN frames, then AC mains applied at a specific moment (~frame 31,645 in the message sequence). The controller board handles this automatically. Do not attempt to drive with raw CAN.

**Gen3 (18.5 kW, Model S/X 2017+):** Three-phase AC. Requires Gen3 v2 controller board. US and EU variants have different internal junction box wiring.

Both need a standard Type 2 charge port. PP sense → VCU ProxPilot analogue input (330Ω pull-up). CP is generated by the controller board.

Tesla Gen2 DCDC converter also supported as of V2.04A.

---

## CHAdeMO DC Fast Charging

Native VCU support — no extra controller board needed, but the PCB must be configured first.

### PCB Configuration — 6 Solder Jumpers

On the PCB rear silk screen, solder:
- **SJ6, SJ7, SJ8, SJ9** — enables HS CAN3
- **2 jumpers above R31** — adds fault-tolerant termination

Without all 6, CHAdeMO handshake will not complete.

### 12V Signal Wiring

| CHAdeMO socket pin | Connect to |
|---|---|
| Pin 1 | 12V chassis GND |
| Pin 2 | Contactor coil + (both coils paralleled) |
| Pin 4 | VCU GP Out 3 (charge enable/disable) |
| Pin 10 | Contactor coil − (both coils) |
| CAN H/L | CAN3 on VCU |

CHAdeMO does not need PP — handshake is fully CAN + 12V signal based.

### CCS — BMW i3 LIM or Foccci

| Method | Notes |
|---|---|
| BMW i3 LIM | Salvaged from i3. Provides CCS Type 1 and 2. Connect via ZV Comms CAN parameters. |
| Foccci | Open-source CCS controller. V2.20A one-click setup. Default CAN Node ID = 22. Uses CpSpoof PWM from VCU. |

---

## Charger Selection Guide

| Charger | Power | Complexity | CP/PP to VCU | Best for |
|---|---|---|---|---|
| Leaf PDM Gen2 | 6.6 kW | Low | Not needed | First build, Leaf stack |
| Outlander OBC | 6.6 kW | Medium | PP + CpSpoof | Outlander builds |
| VW Golf PHEV OBC | 3.3 kW | Medium | PP + CP | European builds, cheap |
| Audi e-tron OBC | 7.2–11 kW | Medium | PP + CpSpoof | High-power AC |
| MG ZS Gen2 OBC | 11 kW | Medium | PP + CpSpoof | 3-phase 11kW |
| Tesla Gen2 | 10 kW | High — controller board | Full charge port | High AC power |
| Tesla Gen3 | 18.5 kW | High — controller board | Full charge port | Maximum AC speed |
| CHAdeMO | DC 50+ kW | High — PCB jumpers + wiring | Not needed | Public fast charging |

> **Recommended first build:** Leaf PDM Gen2. Most documented, no PP wiring to VCU, fewest gotchas.

---

*Source: Damien Maguire @Evbmw · Good Enuff Garage · openinverter.org*  
*Last verified against firmware: V2.30A (August 2025)*
