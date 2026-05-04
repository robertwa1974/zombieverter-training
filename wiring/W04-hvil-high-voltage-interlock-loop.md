# W04 — HVIL — High Voltage Interlock Loop

**Track:** Wiring  
**Prerequisites:** F04 — High Voltage Safety, W03 — Contactor & Precharge Circuit  
**Audience:** Intermediate  
**Estimated reading time:** 10 minutes

---

## What Is HVIL?

The High Voltage Interlock Loop (HVIL) is a low-current 12V detection circuit that passes through every HV connector, service disconnect, and access panel in the system. If any connector is unplugged, any panel is removed, or any HV cable is broken, the loop opens — and the VCU immediately opens the HV contactors.

HVIL transforms accidental HV contact from a likely fatal event into a contactor-open event. Instead of unplugging an HV cable while the system is live, you unplug the HVIL pin first (or simultaneously), the VCU sees the broken loop, and the HV bus drops before you can touch a live terminal.

---

## How It Works

The HVIL circuit is a simple series loop:

```
VCU HVIL out → Connector 1 loop → Connector 2 loop → Battery disconnect → VCU HVIL in
```

Each HV connector in the system has two small signal pins (the HVIL pins) that are internally shorted together within the connector. When all connectors are fully mated, the loop is complete and current flows. When any connector is pulled, the loop opens, current stops, and the VCU opens the contactors.

The VCU monitors the loop return signal. A break in the loop triggers an immediate contactor open regardless of opmode.

---

## The BMW Safety Box (S-BOX)

A commonly used solution in ZombieVerter BMW builds is the BMW Safety Box. The S-BOX is an OEM battery isolation module from early E-series BMW/Mini hybrid vehicles that combines:

- Negative and positive contactors with precharge
- HVIL monitoring
- Pack voltage monitoring (CAN)
- Manual service disconnect

For BMW-based conversions it provides all of these functions in a single tested unit. Set `shuntType` = SBOX in VCU parameters.

The S-BOX communicates over CAN2 by default. Set `shuntCan` = CAN2. The S-BOX provides `udc` to the VCU — this is what drives precharge completion detection.

---

## Wiring HVIL From Scratch

For builds not using the S-BOX, HVIL can be implemented with:

**HV connectors with HVIL pins:** Use HV connectors that have dedicated interlock pins (e.g. Delphi/Aptiv HV connectors used on Leaf, many OEM components). These have two small signal pins alongside the power pins. Wire all HVIL pins in series.

**Manual service disconnect:** A physical plug or lever that disconnects both the HV circuit AND the HVIL loop when pulled. The HVIL break triggers a contactor open, then the HV disconnect is physical.

**VCU integration:** The HVIL signal connects to a VCU digital input pin. Assign the `HVIL` function to this pin in the Din section. Configure as active-low (pin pulled to ground through the loop, open = fault) or active-high depending on your implementation.

---

## S-BOX Integration

### VCU Wiring

| S-BOX terminal | Connect to |
|---|---|
| 12V+ | Permanent 12V (same feed as VCU) |
| GND | Chassis ground |
| CAN H | VCU CAN2H |
| CAN L | VCU CAN2L |
| Contactor coil− (neg) | VCU Pin 31 |
| Contactor coil− (pos) | VCU Pin 33 |
| Precharge coil− | VCU Pin 34 |
| HV+ | Battery positive (via fuse) |
| HV− | Battery negative |

### VCU Parameters

```
shuntType = SBOX
shuntCan  = CAN2
```

The VCU will send CAN commands to the S-BOX to open and close its internal contactors as part of the normal precharge sequence.

### Connectivity Check

With S-BOX powered and CAN connected:
- Check `udc` in Spot Values — should show a non-zero value if the S-BOX is communicating and the HV battery is connected
- Check `status` — should not show a CAN communication error

---

## HVIL on OEM Drive Unit Connectors

Many OEM inverters and drive units have built-in HVIL connectors:

**Nissan Leaf:** The large HV connector on the Leaf PDM/inverter has an integral interlock. In OEM use this connects to the vehicle HVIL loop. In a conversion it should be either looped (jumped) or integrated into your HVIL circuit.

**Tesla drive units:** Have an HVIL connector that must be looped or connected to the vehicle HVIL circuit. An unlooped HVIL connector prevents the inverter from entering run mode.

**GS450h:** The HV connectors at the brass pillar connection points do not have integral HVIL pins — the interlock is handled at the battery/contactor box level.

---

## Without HVIL

Builds without HVIL are possible — many simple conversions omit it. Without HVIL:

- Disconnecting any HV connector while the system is live is potentially fatal
- The VCU has no automatic protection against accidental HV exposure during service
- You rely entirely on the manual service disconnect and your own procedural discipline

If omitting HVIL, the discharge procedure (Module F04) must be followed rigorously every single time before touching any HV component. There are no shortcuts.

---

*Source: Good Enuff Garage BMW Safety Box series (April–May 2024) · openinverter.org/wiki*  
*Last verified against firmware: V2.30A (August 2025)*
