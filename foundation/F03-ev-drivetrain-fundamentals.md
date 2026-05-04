# F03 — EV Drivetrain Fundamentals

**Track:** Foundation  
**Prerequisites:** F01 — What Is a VCU  
**Audience:** Complete beginners  
**Estimated reading time:** 12 minutes

---

## Two Voltage Domains

Every EV conversion has two completely separate electrical systems that must never be directly connected to each other:

**High Voltage (HV) domain** — the traction system. Battery pack, inverter, motor, onboard charger, DC-DC converter input. Typically 200–450V DC in ZombieVerter-based conversions. Orange cables by convention. Fatal at the current levels available.

**Low Voltage (LV) domain** — the vehicle electronics. 12V battery, VCU, lights, accessories, sensors, CAN buses, instrument cluster. Conventional automotive 12V. The VCU lives entirely in the LV domain — it controls the HV domain through contactors and CAN commands, but never carries HV itself.

The DC-DC converter bridges these domains in one direction only: it takes HV input and produces 12V output to charge the LV battery. Current never flows the other way.

---

## The Traction Chain

From driver input to wheel torque, the path is:

```
Throttle pedal → VCU (torque demand) → Inverter (AC phase switching) → Motor → Gearbox/wheels
```

**Throttle pedal** — generates a 0–5V analog signal (Hall effect or potentiometer). The VCU reads this and maps it to a 0–100% torque demand.

**VCU** — translates driver demand to a CAN torque command in the inverter's protocol. Also enforces limits from the BMS, manages regen, handles direction.

**Inverter** — takes DC from the HV battery and switches it as three-phase AC to the motor. Switches at high frequency (typically 10–15 kHz) to produce sinusoidal current. Controls motor torque precisely by controlling the phase currents.

**Motor** — converts electrical energy to mechanical torque. In hybrid-derived systems (Leaf, GS450h, Prius, Outlander) the motor is a permanent magnet AC machine — efficient, high power density, well-suited for EV use.

**Resolver or encoder** — the motor position sensor. Tells the inverter exactly where the rotor is so it can switch phases at the right time. Without resolver feedback, the inverter cannot control the motor. The resolver cables run from the motor back to the inverter — these are the fragile signal cables that must be treated carefully.

---

## Motor Types You'll Encounter

**Permanent Magnet AC (PMAC / IPMSM)** — used in Nissan Leaf (EM57, EM61), Mitsubishi Outlander, most modern EV traction motors. High efficiency, high torque density. Requires resolver feedback. The ZombieVerter supports several of these via CAN.

**Induction (AC)** — used in older Tesla Model S/X. Lower peak efficiency than PMAC but simpler magnetics. Supported via the openinverter board.

**Dual motor (Power split)** — the GS450h and Prius use two motor-generators (MG1 and MG2) with a planetary gearset between them. In EV conversion use MG2 provides primary traction, MG1 provides additional torque when the input shaft is locked. See Module I03 for detail.

---

## Contactor Logic and Precharge

The HV battery cannot be connected directly to the inverter. The inverter contains large DC bus capacitors — connecting HV to uncharged capacitors causes an instantaneous high-current surge that can weld the contactor contacts permanently closed or destroy the capacitors.

The solution is precharge: a resistor in series with the positive HV rail that limits inrush current while the capacitors charge slowly.

**The sequence:**
1. Negative contactor closes (HV− connected to inverter)
2. Precharge contactor closes (HV+ through resistor to inverter)
3. Capacitors charge slowly — bus voltage rises over ~2–5 seconds
4. When bus voltage reaches threshold (`udcsw`), main positive contactor closes
5. Precharge contactor opens (resistor bypassed)
6. System enters run mode — full HV available

The VCU manages this entire sequence. The ISA shunt or equivalent sensor provides the bus voltage reading that tells the VCU when precharge is complete.

> **Why this matters for first-time builders:** `udcsw` defaults to 330V. With no HV battery connected on the bench, the bus voltage never reaches 330V. Precharge appears to fail repeatedly. The fix is to set `udcsw` to 0 or 15V for bench testing. See Module C03.

---

## Regenerative Braking

Regen reverses the energy flow. When the driver lifts the throttle or presses the brake, the VCU sends a negative torque command to the inverter. The inverter runs the motor as a generator, converting kinetic energy back to DC electricity and pushing it back into the battery.

The amount of regen is controlled by:
- `throtmin` — negative value = throttle-lift regen (e.g. -5 = light regen when foot off throttle)
- Brake input — `din_brake` can trigger regen in addition to friction braking
- BMS current limits — the BMS caps how much current can flow back into the battery

> Regen was first reliably implemented in V2.15A (April 2024). Content about regen from before this date refers to a non-functional or experimental implementation.

---

## The ISA Shunt — Pack Monitoring

The VCU cannot directly measure HV bus voltage — it operates entirely in the 12V domain. An external sensor bridges this gap.

The ISA IVT-S shunt sits in series with the HV bus. It measures voltage, current, and calculates state of charge, then transmits these readings over CAN to the VCU. The VCU uses this data to:
- Monitor precharge progress (is the bus voltage rising?)
- Know when precharge is complete (has it reached `udcsw`?)
- Enforce discharge and charge current limits
- Report pack state to the driver

The ISA shunt must have permanent 12V power — the same always-on feed as the VCU. If powered from ignition-switched supply it loses its coulomb count state when the key is off, and the next startup may read stale or zero UDC.

---

## Isolation and Grounding

The HV system must be electrically isolated from the vehicle chassis (LV ground). This isolation is safety-critical — if HV+ or HV− contact the chassis, the chassis becomes energised at HV potential.

The ISA shunt measures the voltage difference between HV+ and HV− without either being referenced to chassis ground. The inverter is similarly isolated. The battery pack enclosure may be grounded to chassis for EMC reasons but the battery terminals must not be.

**HVIL (High Voltage Interlock Loop)** is a low-current 12V loop that passes through every HV connector in the system. If any HV connector is opened or a cable is disconnected, the loop breaks, the VCU detects it and immediately opens the contactors. See Module W04.

---

*Source: Damien Maguire @Evbmw — "Lexus GS450h EV Drivetrain Deep Dive" (June 2020)*  
*Last verified against firmware: V2.30A (August 2025)*
