# W08 — ISA IVT-S Shunt: Complete Reference

**Track:** Wiring · **Module:** W08  
🟢 Current — verified against ZombieVerter firmware V2.40A source  
*Source files reviewed: `isa_shunt.cpp`, `isa_shunt.h`, `stm32_vcu.cpp`, `param_prj.h`, `hwinit.cpp`*

---

## Overview

The ISA IVT-S is a combined current/voltage/temperature sensor that communicates over CAN. It is the primary source of pack voltage (`udc`) and current (`idc`) for the ZombieVerter VCU. Without it — or an equivalent shunt type — the VCU cannot perform precharge sequencing, SOC calculation, or current limiting.

This module documents the shunt's CAN protocol, initialisation procedure, firmware integration, and spot value mapping, derived directly from the ZombieVerter firmware source code.

---

## CAN Bus — Critical Fact

> **The ZombieVerter-specific IVT-S flash runs at 500 kbps.**

Both CAN1 and CAN2 on the ZombieVerter are hardcoded at 500 kbps in firmware:

```cpp
Stm32Can c (CAN1, CanHardware::Baud500);
Stm32Can c2(CAN2, CanHardware::Baud500, true);
```

The IVT-S with ZV firmware can share CAN1 or CAN2 with other 500 kbps devices — inverters, BMS modules, ESP32 interfaces, etc. **No dedicated bus is required.** Use whichever bus your wiring makes convenient; set `ShuntCan` to match.

> ⚠️ **Stock (unflashed) IVT-S units default to 1 Mbps** and will not communicate with the ZombieVerter. The unit must be flashed with the ZombieVerter-specific firmware before use. This flash is available from the openinverter.org community.

---

## ShuntType Parameter

Set in the web UI under General Setup:

| `ShuntType` value | Meaning |
|---|---|
| `0` — None | No shunt. SOC calculations disabled. |
| `1` — ISA | IVT-S shunt. Standard mode. |
| `2` — SBOX | BMW S-Box pack monitor |
| `3` — VAG | VW/Audi e-Box |
| `4` — ISA_udcsw | IVT-S shunt, alternative precharge logic variant |

For the IVT-S, set `ShuntType = ISA` (value 1).

---

## CAN Message IDs

The IVT-S broadcasts 8 messages continuously once running. The VCU registers all 8 in `ISA::RegisterCanMessages()`:

| CAN ID | Measurement | Units (raw) | Spot value |
|---|---|---|---|
| `0x521` | Current (Amperes) | mA × 1 (int32) | `idc` |
| `0x522` | Voltage U1 | mV × 1 (int32) | `udc` |
| `0x523` | Voltage U2 | mV × 1 (int32) | `udc2` |
| `0x524` | Voltage U3 | mV × 1 (int32) | `udc3` |
| `0x525` | Temperature | °C × 10 (int32) | `tmpaux` |
| `0x526` | Power | W (int32) | `power` |
| `0x527` | Amp-hours | Ah (int32) | `AMPh` |
| `0x528` | Kilowatt-hours | kWh (int32) | `KWh` |

All values are big-endian int32, bytes 2–5 of the 8-byte frame (bytes 0–1 are a status/type header).

The VCU sends commands to the shunt on **`0x411`**.

---

## U1, U2, U3 Voltage Inputs

The IVT-S has three independent voltage sense inputs:

- **U1** — Primary voltage sense. This is the input the VCU uses for `udc` (pack voltage for precharge logic). **Must be connected to the inverter/load side of the main contactor.**
- **U2** — Secondary voltage sense. Optional. Can monitor battery-side voltage. Reported as `udc2`.
- **U3** — Third voltage sense. Optional. Reported as `udc3`. `deltaV` (= U1 − U2) is also computed and shown in Spot Values.

> ⚠️ **U1 placement is safety-critical.** U1 must sense voltage on the load side of the main contactor — after precharge has charged the bus capacitors. If U1 is connected to the battery side, the VCU sees full pack voltage before precharge begins and will close the main contactor immediately into uncharged capacitors.

> 💡 **`deltaV` is a useful diagnostic.** During a healthy precharge sequence, `deltaV` (U1 − U2, with U2 on battery side) starts at pack voltage and drops toward zero as the bus caps charge. A precharge that stalls partway shows as a stable non-zero `deltaV`.

---

## 12V Power Supply

The IVT-S requires a **permanent 12V supply** — the same feed as the VCU itself.

- The VCU and shunt must power up together on the same permanent 12V rail
- This is required for the initialisation sequence to complete correctly
- If the shunt powers up after the VCU, init timing issues can occur (see Troubleshooting)
- **Never connect to an ignition-switched feed** — the shunt must remain powered to maintain coulomb counting during charging when ignition may be off

---

## Initialisation — How It Works in Firmware

From `stm32_vcu.cpp` `main()`:

```cpp
if (Param::GetInt(Param::IsaInit) == 1)
    ISA::initialize(shunt_can);
```

`IsaInit` is checked **once at boot** — not polled continuously. Setting `IsaInit = 1` and saving to flash means the next power cycle will call `ISA::initialize()`.

`ISA::initialize()` performs this sequence:

1. Sends **STOP** to the shunt — halts current measurement
2. Sends 9 channel configuration messages
3. Sends **STORE** after each — writes config to shunt flash
4. Sends **START** — resumes measurement

Hardware delays (~110ms) are inserted between each step via a busy-wait loop on the STM32.

### Step-by-step procedure

1. Wire IVT-S: CAN H/L to VCU CAN1 or CAN2, permanent 12V+, GND
2. Set `ShuntType = ISA`, `ShuntCan` to match your wiring — save to flash
3. Set `IsaInit = 1` — save to flash
4. Power cycle VCU and shunt simultaneously (shared 12V feed means this happens automatically)
5. The shunt initialises — `udc` in Spot Values should now show a reading
6. **Set `IsaInit = 0` — save to flash**
7. Reboot the VCU

> ⚠️ **`IsaInit` is not automatically cleared by the firmware.** If you leave it at 1, the full init sequence — including coulomb counter reset — runs on every boot. Always set it back to 0 and save to flash after a successful init.

---

## Additional Commands

These commands are available in the firmware but not exposed as web UI parameters:

| Function | Command ID | byte[0] | Effect |
|---|---|---|---|
| STOP | `0x411` | `0x34` | Halts measurement |
| START | `0x411` | `0x34` + byte[1]=`0x01` | Resumes measurement |
| STORE | `0x411` | `0x32` | Saves config to shunt flash |
| RESTART | `0x411` | `0x3F` | **Zeros Ah and kWh counters** — does not re-init |
| deFAULT | `0x411` | `0x3D` | Returns shunt to factory defaults — **wipes ZV flash** |

> ⚠️ **Do not send `deFAULT` to a ZV-flashed shunt.** It erases the ZV firmware configuration and reverts the shunt to 1 Mbps default baud rate, requiring reflashing.

> 💡 **`RESTART` is useful for bench sessions.** It zeroes the coulomb counter (Ah, kWh) without requiring a full re-init. Use it at the start of each test session for a clean SOC baseline.

---

## Spot Values — Complete Mapping

From `param_prj.h`:

| Spot Value | Source | Description |
|---|---|---|
| `udc` | ISA `Voltage` (0x522 / U1) | Pack voltage — primary input for precharge logic |
| `udc2` | ISA `Voltage2` (0x523 / U2) | Secondary voltage sense |
| `udc3` | ISA `Voltage3` (0x524 / U3) | Tertiary voltage sense |
| `deltaV` | U1 − U2 | Voltage difference — useful precharge diagnostic |
| `idc` | ISA `Amperes` (0x521) | Pack current (positive = discharge, negative = regen/charge) |
| `power` | ISA `KW` (0x526) | Instantaneous power in kW |
| `AMPh` | ISA `Ah` (0x527) | Cumulative amp-hours since last RESTART or init |
| `KWh` | ISA `KWh` (0x528) | Cumulative kWh since last RESTART or init |
| `tmpaux` | ISA `Temperature` (0x525) | Shunt temperature |
| `SOC` | Calculated from Ah + `BattCap` | State of charge % |

`SOC` calculation runs every 100ms only when `ShuntType != 0`.

---

## Precharge Integration

The VCU's precharge state machine uses `udc` directly. Precharge exits to RUN or CHARGE mode only when:

- `udc >= udcsw` (bus voltage has reached the switchover threshold), AND
- A minimum 1-second precharge time has elapsed, AND
- No throttle pressed, no voltage faults

If `udc < udcsw` after **5 seconds** (hardcoded `PRECHARGE_TIMEOUT` in firmware — not configurable), the VCU posts `ERR_PRECHARGE` and enters `MOD_PCHFAIL`.

---

## Troubleshooting

**`udc` reads zero after init:**
- Verify `ShuntType = ISA` and `ShuntCan` is correct — save to flash and reboot
- Check CAN H/L connections and 120Ω termination at both bus ends
- Confirm the shunt has been flashed with ZV firmware — stock units at 1 Mbps will not respond
- Re-run the init procedure

**Init timing issue — shunt doesn't respond to init:**
- Separate the 12V supplies temporarily — power the shunt first, wait 2–3 seconds, then power the VCU
- Fixes a race condition seen on some units where the shunt isn't ready when the VCU fires the init sequence at boot

**`udc` reads full pack voltage during precharge — precharge completes instantly:**
- U1 is connected to the battery side instead of the load side — move U1 to the inverter/load side of the main contactor

**Ah/kWh not resetting between sessions:**
- Coulomb counters reset on power loss to the shunt — this is expected behaviour if the shunt shares the permanent 12V feed
- To manually zero them mid-session, send a RESTART command (0x3F on 0x411)

**`IsaInit` keeps re-running on every boot:**
- `IsaInit` was not set back to 0 after initialisation — set to 0, save to flash

---

## Related Modules

- **W03** — Contactor and precharge circuit (physical wiring)
- **W07** — CAN bus wiring (topology, termination, bus assignment parameters)
- **C03** — Essential parameters: first start (`udcmin`, `udclim`, `udcsw`)
- **A03** — BMS integration (shunt + cell BMS together)

---

*Source: ZombieVerter firmware — `isa_shunt.cpp` (Jack Rickard / EVtv, adapted by Damien Maguire), `stm32_vcu.cpp` (Tom de Bree, Johannes Hübner, Damien Maguire), `param_prj.h`*  
*Last verified against firmware: V2.40A*
