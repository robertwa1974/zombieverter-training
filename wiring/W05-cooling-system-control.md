# W05 — Cooling System Control

**Track:** Wiring  
**Prerequisites:** H01 — VCU Hardware Walkthrough, C02 — Web Interface Walkthrough  
**Audience:** Intermediate  
**Estimated reading time:** 10 minutes

---

## Three Pumps — Three Different Jobs

The VCU Dout section lists several pump-related output functions in the same place. Before wiring anything, understand that these control **completely different systems** with **different purposes**:

| VCU Function | What it controls | Purpose |
|---|---|---|
| `CoolantPump` | Electric water/glycol pump | **Cools the inverter** |
| `GS450Hpump` | GS450h transmission oil pump | **Enables traction** — not cooling |
| `BrakeVacPump` | Electric vacuum pump | **Brake servo assistance** |

> **⚠️ GS450h builders:** The GS450h oil pump **pressurises the transmission** to engage its internal clutch plates so the gearset can transmit torque to the wheels. It is **not a cooling pump** and has nothing to do with inverter cooling. The GS450h inverter uses a separate water/glycol coolant loop — that is what `CoolantPump` controls. Without oil pressure the transmission cannot transmit torque, regardless of inverter state. See Module I03-X for full oil pump wiring and commissioning.

These three functions are independent. A build may need all three, some, or just one.

---

## Why Cooling Matters More in a Conversion

In an OEM EV, the cooling system is engineered alongside the drivetrain with precise flow rates, thermal mass, and thermostat control tuned for that specific motor and inverter. In a conversion, you are building a cooling system from scratch around salvaged components that were designed with different assumptions.

Under-cooling in a conversion manifests as:
- Thermal derating — the inverter reduces available torque as temperature rises
- Thermal shutdown — the inverter or motor stops completely to protect itself
- Accelerated component degradation over time

Over-cooling wastes energy running pumps and fans at full speed continuously. The VCU can manage both.

---

## What the VCU Can Control

The VCU has dedicated output functions for cooling components, assignable via the Dout section of the web interface:

| Function | What it controls | How it activates |
|---|---|---|
| `CoolantPump` | Electric coolant pump relay | On during pre-charge, charge and run mode |
| `GS450Hpump` | GS450h transmission oil pump PWM | PWM speed control via PumpPWM parameter |
| `CoolingFan` | Cooling fan relay or speed controller | Activates when temp exceeds FanTemp |
| `BrakeVacPump` | Brake vacuum pump relay | Activates when brake vacuum is low |

---

## Coolant Pump

An electric coolant pump must run whenever the inverter is active — from precharge through to run mode shutdown. Assign `CoolantPump` to a low-side digital output pin.

**Circuit:** 12V+ → relay coil → relay coil− → VCU Dout pin (low-side). When the VCU activates the output, the relay closes and supplies 12V to the pump motor.

**Pump selection:** Match the pump to the inverter's cooling system requirements. Most donor inverters (Leaf, Tesla) are designed for water/glycol coolant with flow rates in the 2–8 L/min range. An automotive heater core pump (e.g. Davies Craig EWP series) is commonly used in conversions.

**GS450h oil pump:** Uses PWM speed control, not a simple relay. See Module I03-X for full oil pump controller wiring. `PumpPWM` parameter (added V2.20A) controls duty cycle. Starting point: 30%.

---

## Cooling Fan — FanTemp (V2.20A+)

`FanTemp` sets the inverter heatsink temperature (`temphs`) at which the VCU activates the cooling fan output.

```
FanTemp = 40    → fan on when heatsink reaches 40°C
```

Set this based on your cooling system design. A well-designed cooling loop should keep the inverter heatsink below 60°C under sustained load. If `temphs` regularly reaches 80°C+, the cooling system needs more capacity.

**Monitoring:** Watch `temphs` and `tempm` in Spot Values during sustained driving. These are your primary thermal health indicators.

---

## GS450h Oil Pump — Traction, Not Cooling

> **This is not a coolant pump.** It is documented here because it appears in the same Dout section of the web interface alongside cooling outputs.

The GS450h transmission uses hydraulic oil pressure to engage its internal clutch plates. Without oil pressure, the transmission cannot transmit torque — the wheels will not turn regardless of inverter state. The pump must run from precharge throughout run mode.

- Current draw: ~25A at full speed — **must** have its own dedicated 12V feed with a 30A minimum fuse
- Do not power from a VCU output pin
- Start at 30% PWM duty cycle
- From V2.20A, the `PumpPWM` output function is freely assignable (not limited to GS450h builds)

See **Module I03-X** for full GS450h oil pump wiring, specifications, and commissioning procedure.

---

## Brake Vacuum Pump

Many non-hybrid donor vehicles use engine vacuum for brake servo assistance. In an EV conversion with no engine, this vacuum disappears. An electric vacuum pump is required for brake servo operation.

The VCU can monitor a vacuum sensor and activate a vacuum pump as needed:
1. Assign `BrakeVacSensor` to an analogue input pin
2. Assign `BrakeVacPump` to a digital output pin
3. The VCU activates the pump when vacuum drops below threshold

Alternatively, use a standalone electric vacuum pump controller — these are available as off-the-shelf units that self-regulate without VCU integration.

> **Fix note — V2.05A:** Before V2.05A, the brake vacuum pump output stayed active after ignition off. This was corrected in V2.05A (March 2024). If your pump runs continuously after key-off, update firmware.

---

## Temperature Monitoring

The VCU receives temperature data from several sources:

| Spot value | Source |
|---|---|
| `temphs` | Inverter heatsink temperature (from inverter CAN) |
| `tempm` | Motor temperature (from inverter CAN, where supported) |
| `tempcool` | Coolant temperature (if thermistor connected to VCU analogue input) |

For vehicle integration, `temphs` and `tempm` can be used to drive the OEM temperature gauge (where the vehicle class supports it) — giving the driver a real indication of drivetrain thermal state.

---

## Thermal Derating

Most supported inverters implement their own thermal derating — as heatsink temperature rises above a threshold, the inverter reduces available torque. This is done inside the inverter firmware, not by the VCU. The VCU sees reduced torque output but cannot override inverter-internal derating.

Signs of thermal derating:
- Throttle at 100% but `torque` spot value below maximum
- `temphs` above 60–70°C
- Performance gradually reduces after sustained high-load driving

Solution: more cooling. Larger radiator, higher flow pump, or additional cooling surface.

---

## Common Cooling Mistakes

**Not running the pump during precharge:** The inverter capacitors charge and the inverter initialises during precharge. Thermal load begins immediately. Assign `CoolantPump` to activate from the start of precharge, not just when the run mode is reached.

**Pump on ignition-switched power:** If the cooling pump is powered from ignition-switched supply and the VCU is on permanent power, the pump stops when the key is off but the inverter may still be thermally hot. Wire the pump to the VCU-controlled relay output so the VCU can run the pump after shutdown if needed.

**No fan control in summer:** A cooling loop without fan control may be adequate in winter ambient temperatures and completely inadequate in summer. Design for worst-case ambient temperature.

---

*Source: Damien Maguire @Evbmw — V2.20A firmware walkthrough (December 2024) · openinverter.org community builds*  
*PumpPWM and FanTemp added V2.20A · Vacuum pump fix: V2.05A (March 2024)*  
*Last verified against firmware: V2.30A (August 2025)*
