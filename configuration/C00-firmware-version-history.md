# C00 — Firmware Version History & Changelog

**Track:** Firmware & Configuration  
**Prerequisites:** None — read this before any other C-track module  
**Audience:** All levels  
**Purpose:** Version reference and staleness guide for the entire training series  
**Last updated against:** V2.30A (August 2025 — latest as of this writing)

---

## Why This Module Exists

The ZombieVerter firmware has evolved significantly since first release. YouTube videos, forum posts, and even parts of this training series may reference older behaviour, renamed parameters, or features that didn't yet exist at the time of recording. This module is the **ground truth reference** for what changed when.

**How to use it:**
- Before following instructions from any video or forum post, check the video date against this changelog
- If a parameter name doesn't match what you see in your firmware, look here for renames
- If a feature described in a module isn't visible in your web interface, check the version it was introduced

---

## Firmware Version Summary Table

| Version | Release date | Era | Key theme |
|---|---|---|---|
| 1.00.A | Jun 2022 | V1 | First official release |
| 1.06A | Nov 2022 | V1 | Throttle mode bug fix, throtdead introduced |
| 1.07A | Nov 2022 | V1 | Leaf inverter bug fix |
| 1.10A | Nov 2022 | V1 | CAN3, Leaf CAN improvements |
| 1.11A | Feb 2023 | V1 | DC current limit fix |
| **2.00A** | **May 2023** | **V2 — major** | **IO matrix, virtual functions, module decoupling** |
| 2.01A | Sep 2023 | V2 | Outlander charger, VW EBox shunt, BMS module |
| 2.04A | Jan 2024 | V2 | IOMatrix analog inputs, gear shifter class, Tesla DCDC, OBD2 |
| 2.05A | Mar 2024 | V2 | Throttle UDC limit fix, LIN heater, Park gear, 250ms contactor delay |
| 2.15A | Apr 2024 | V2 | Regen, Outlander rear inverter, GS450h auto shifting, brake light regen |
| 2.17A | May 2024 | V2 | Outlander rear motor bug fix |
| 2.20A | Dec 2024 | V2 | Foccci integration, PWM functions, E90 CAN, revRegen, Kangoo BMS |
| 2.22A | Mar 2025 | V2 | IS300h fix, LIN fix, Leaf Gen3 PDM improvement |
| **2.30A** | **Aug 2025** | **V2 — current** | **Throttle smoothing, derate simplification, Leaf charging fix** |

---

## The V1 → V2 Boundary (May 2023) — The Most Important Break

**V2.00A was a major architectural rewrite.** If you see content from before mid-2023, treat it with caution. Key changes:

- **IO Matrix introduced** — configurable input/output pin assignments via web interface. Before V2, many pins had fixed functions. The `Din`/`Dout` parameter sections in the web UI are a V2 feature.
- **Module decoupling** — Leaf stack components (inverter, PDM, charger) can now be used independently. Before V2, Leaf stack required all components together.
- **Charge interface decoupling** — Any OBC can now work with any charge interface (LIM, CHAdeMO). Previously coupled.
- **Subaru vehicle module added**
- **IMPORTANT:** Upgrading from V1.xx to V2.xx requires a power cycle after update (different RTC settings)

---

## Detailed Release Notes

### 2.30A — August 2025 (Current)
**🟢 Current — this training series targets this version**

- Leaf reverse torque limiter removed
- Leaf charging fix for low current PP detection
- Throttle smoothing — `potnom` float fix
- Derate logic simplified — ramps removed
- Throttle smoothing — throttle ramping after derating added
- Tested in 3 vehicles before release: BMW E39 (GS450h/Tesla PCS/CHAdeMO), BMW E46 (Leaf Gen1/Outlander charger/i3 LIM CCS/Ampera heater), BMW E31 (Tesla LDU/Tesla Gen2 charger/Tesla DCDC/VW coolant heater/CHAdeMO)

**⚠️ Upgrade note:** No specific upgrade warnings for this release.

---

### 2.22A — March 2025
- Lexus IS300h inverter fix
- LIN bus fix for VW coolant heater
- Nissan Leaf Gen3 PDM operation improvement

**⚠️ Upgrade note:** When upgrading from earlier versions, you **must reselect your inverter type and save params** — inverter sequence numbering was updated. If running a Toyota inverter, **reboot the VCU after upgrade** or the inverter will not initialise.

---

### 2.20A — December 2024
New parameters introduced (relevant to training modules):

| New parameter | Function | Module |
|---|---|---|
| `revRegen` | Toggle regen on/off in reverse | A01 |
| `PumpPWM` | Output pin function now selectable (was GS450h only) | H01, H05 |
| `FanTemp` | Inverter or charger temp threshold for cooling fan | W05 |
| `TachoPPR` | Pulses per revolution for tachometer output | H05 |
| `TorqueDerate` | Spot value — set any time potnom derates | C06 |

Other notable changes:
- Foccci one-click setup and ZombieVerter integration
- CpSpoof PWM output for CP signal spoofing
- GS450h oil pump PWM now a selectable output function (PumpPWM)
- Outlander charge CP spoofing no longer hard-coded
- E65 shifting now uses shifter class (no longer hard-coded)
- BMW E90 lock state over CAN, warning lights, vehicle speed
- Classic Vehicle option added — has tacho output, uses 12V inputs
- Speedo output option on GS450h oil pump pin
- Voltage and current limiting now actually tapering (was broken before)
- Kangoo BMS integration added
- Heater fix — checks for HeatReq assignment
- Outlander heater + heartbeat message
- GS450h/IS300h: option for blending MG1/MG2 until 50% potnom

**⚠️ Upgrade note:** Must reselect inverter type and save params. Must reboot after upgrade. Toyota inverter users must reboot or inverter won't initialise.

---

### 2.17A — May 2024
- Fix Outlander rear motor bug (minor point release)

---

### 2.15A — April 2024
**Regen introduced for the first time as a working feature.**

Key additions:
- **Regenerative braking** — working implementation
- Outlander rear inverter support added
- Prius Gen3 temperature reading fix (was causing uneven throttle)
- Brake light output option triggered by regen
- **GS450h auto shifting** introduced
- JLR gear shifter support added
- No Vehicle CAN option added
- BMW CAN sleep and wake
- Throttle ramping fixed

**🟡 VERIFY for regen content:** Any video or forum content about regen from before April 2024 refers to a non-working or experimental implementation. Regen only became reliable in V2.15A.

---

### 2.05A — March 2024
- Throttle UDC limit bug fixed (was broken)
- Brake vacuum pump control fix (now turns off when ignition off)
- 250ms delay between HV contactor activations (needed for parallel packs)
- LIN-controlled VW heater added — **hardware note: R50 must be changed to 1kΩ and C45 to 1nF on boards ordered before 14/03/24**
- Park gear added to gear selection
- GS300h battery discharge limit fixed

**⚠️ Upgrade note:** Toyota drivetrain users must reset VCU after firmware load.

---

### 2.04A — January 2024
Major feature additions:
- IO Matrix extended to analog inputs — brake vacuum pump control via vacuum sensor, charge port PP detection
- Gear shifter class added — supports 12V inputs and BMW F30 CAN-based shifter
- Tesla Gen2 DCDC converter class added
- OBD2 class for Torque Pro via CAN/ELM327
- BMW E31 vehicle class added
- OpenInverter CAN class updated

---

### 2.01A — September 2023
- Mitsubishi Outlander PHEV charger/DCDC support added
- VW PHEV EBox shunt option added
- BMS module merged (bench tested only at release)
- Heater bug fix

**⚠️ Upgrade note:** If upgrading from V1.xx, power cycle after update.

---

### 2.00A — May 2023 — MAJOR VERSION
See "V1 → V2 Boundary" section above for full impact.

---

### 1.06A — November 2022 — Important V1 note
**Throttle potmin/potmax behaviour clarified in release notes:**

> "Please check your potmin, pot2min, potmax, pot2max values: They are the ABSOLUTE minimum and maximum. Please set them in a way that the potval can never reach them."

This confirms the inside-the-range calibration method has been present since at least V1.06A.

New in V1.06A:
- `throtdead` parameter introduced (throttle deadzone)
- Dual-channel throttle limp mode: if channels deviate >10%, throttle limited to 50% and THROTTLE12DIFF error stored
- Regen disabled entirely (re-enabled properly in V2.15A)

---

## Content Staleness Reference

Use this table when consuming training content from external sources (YouTube, forum posts):

| Content date | Firmware era | Trust level | Notes |
|---|---|---|---|
| Before Jun 2022 | Pre-release | 🔴 **Outdated** | Pre-release firmware, significant changes since |
| Jun 2022 – Apr 2023 | V1.00–V1.11 | 🔴 **Outdated** | V1 era — IO Matrix, regen, many features missing |
| May 2023 – Dec 2023 | V2.00–V2.01 | 🟡 **Verify** | V2 architecture but many features not yet present |
| Jan 2024 – Mar 2024 | V2.04–V2.05 | 🟡 **Verify** | Most wiring/config content valid, regen not working |
| Apr 2024 – Nov 2024 | V2.15–V2.17 | 🟢 **Mostly current** | Regen works, most features present, minor gaps |
| Dec 2024 onwards | V2.20+ | 🟢 **Current** | Full feature set, matches this training series |

---

## Parameter Renames / Removals Between Versions

| Parameter | Status | Notes |
|---|---|---|
| `ISAMode` | 🟢 Stable | Present since V1, still current |
| `udcsw` | 🟢 Stable | Present since V1, still current |
| `throtdead` | 🟢 Stable | Introduced V1.06A |
| `revRegen` | 🟢 Added V2.20A | Not present in older firmware |
| `PumpPWM` | 🟢 Added V2.20A | Was GS450h-only before this |
| `FanTemp` | 🟢 Added V2.20A | |
| `regenRamp` | 🟡 Check | Listed as "new but not used yet" in V1.06A release notes — verify current status |
| `HVRequest` | 🔴 Non-functioning | Listed in IO wiki as "NOT FUNCTIONING" — do not rely on |
| Outlander (inverter=6) | 🔴 Deprecated | Replaced by RearOutlander (inverter=8) |

---

## The "Inverter Sequence Numbering" Warning

**This affects anyone upgrading from V2.05A or earlier to V2.15A or later, and from any version to V2.22A.**

The numeric values of the `inverter` parameter enum changed between versions. If you upgraded without reselecting your inverter type, the VCU may be trying to control the wrong inverter protocol.

**After any major firmware upgrade, always:**
1. Go to Parameters → Comms
2. Reselect your inverter type from the dropdown
3. Save to flash
4. Reboot the VCU

---

## Staying Current

- **GitHub releases:** github.com/damienmaguire/Stm32-vcu/releases — always check here before updating
- **Forum thread:** openinverter.org/forum — development thread has release announcements
- **Damien's YouTube:** New firmware releases are typically accompanied by a walkthrough video

---

*Source: github.com/damienmaguire/Stm32-vcu/releases — full release history*  
*This module should be updated with each new firmware release.*  
*Current latest firmware: V2.30A (August 2025)*
