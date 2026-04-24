# A01 — Regen Tuning

**Track:** Advanced  
**Prerequisites:** C03 — Essential Parameters: First Start, C04 — Throttle Calibration  
**Audience:** Intermediate  
**Firmware minimum:** V2.15A (April 2024) — regen was not reliably functional before this release  
**Estimated reading time:** 12 minutes

---

## Important Firmware Note

> **Regen was not reliably implemented until V2.15A (April 2024).** Any content — videos, forum posts, tutorials — about ZombieVerter regen from before April 2024 refers to a non-functional or experimental implementation. Do not follow pre-V2.15A regen instructions.
>
> V2.20A (December 2024) added `revRegen` — control of regen behaviour in the reverse direction.

---

## How Regen Works on the ZombieVerter

Regen reverses the normal energy flow. Instead of the battery powering the motor, the motor acts as a generator — converting kinetic energy (vehicle momentum) back into electrical energy and pushing it into the battery.

The VCU triggers regen by sending a **negative torque command** to the inverter. From the inverter's perspective, it's the same as a forward torque command but in the opposite direction. The inverter's control loops handle the actual energy reversal.

There are two distinct regen mechanisms:

**Throttle-lift regen** — triggered by lifting the throttle. When `throtmin` is set to a negative value (e.g. -5), lifting the throttle produces a light braking effect rather than pure coast.

**Brake regen** — triggered by the brake pedal signal. Additional regen on top of (or instead of) throttle-lift regen when the brake is pressed.

---

## The Key Parameters

### throtmin — Throttle-Lift Regen

| throtmin value | Effect |
|---|---|
| 0 (default) | No regen on throttle lift — pure coast |
| -5 | Light one-pedal style regen |
| -20 | Moderate regen — noticeable engine-brake feel |
| -50 | Strong regen — aggressive deceleration on throttle lift |

Start conservative (e.g. -5) and increase gradually. Aggressive regen values feel unnatural and can be unsettling for passengers who aren't expecting strong deceleration on every throttle lift.

> Damien's personal preference for his E39 GS450h build: "I'm not a huge fan of regen myself" — but notes that many builders want it for practical range extension and one-pedal driving feel.

### brakelight output

When regen is active — either from throttle lift or brake pedal — the VCU can activate the brake lights via an assigned output pin. Assign the `BrakeLight` output function to a digital output pin in the Dout section. Without this, regen deceleration happens without brake lights — a safety concern.

### revRegen (V2.20A+)

Controls whether regen is active in reverse direction. Some builds need regen in reverse (regenerative downhill reverse), others don't. Toggle on or off.

---

## Drivetrain-Specific Regen Behaviour

Regen behaviour varies by inverter type. This is why pre-V2.15A regen was unreliable — each drivetrain handles negative torque commands differently, and the VCU firmware needed per-drivetrain tuning.

**Nissan Leaf inverter:** Regen works well in V2.15A+. The Leaf motor and inverter were designed for aggressive regen in the OEM vehicle (e-Pedal). Supports strong negative torque values.

**GS450h transaxle:** Regen via MG2 works in V2.15A+. The automatic gear shifting (added V2.15A) accounts for regen: it downshifts before regen engages at low speeds to avoid drivetrain shock. Damien notes the downshift during regen deceleration on his E39.

**Prius Gen3:** Regen supported.

**Outlander:** Regen supported from V2.15A.

---

## Tuning Process

### Step 1 — Start with throttle-lift only

Set `throtmin` = -5. Drive at moderate speed and lift the throttle gently. You should feel a light braking effect. Watch `idc` in Spot Values (via OBD or web interface) — it should go negative (current flowing back into battery) when regen is active.

If `idc` stays at zero or positive: regen is not working. Check firmware version is V2.15A+, check that `throtmin` is saved to flash, verify that `throtmax` is not zero.

### Step 2 — Increase gradually

Increase `throtmin` by -5 increments. At each step, test the feel:
- Does the deceleration feel proportional to throttle lift?
- Does it come on smoothly or with a jerk?
- Does it feel predictable to a passenger in the back seat?

Stop when it feels natural. Most builders settle between -10 and -30.

### Step 3 — Verify brake lights

Plug in a brake light tester or have someone observe while you trigger regen. Brake lights must illuminate whenever regen is actively decelerating the vehicle.

### Step 4 — Check BMS limits

The BMS charge current limit caps how much regen current can flow back into the battery. If `idc` during regen hits the BMS charge limit and flattens, the inverter is limiting regen to protect the battery — this is correct behaviour. You cannot tune past this limit without raising the BMS charge current setting.

---

## Common Regen Problems

| Symptom | Likely cause | Fix |
|---|---|---|
| No regen at all | Firmware < V2.15A | Update firmware |
| No regen at all | throtmin = 0 | Set to negative value and save to flash |
| Jerky/harsh regen onset | throtmin too negative | Reduce magnitude (closer to 0) |
| Regen cuts out unexpectedly | BMS charge limit hit | Raise BMS max charge current if battery allows |
| Brake lights not on during regen | BrakeLight output not assigned | Assign BrakeLight function to a Dout pin |
| Regen feels inconsistent | Dual-pot mismatch triggering plausibility fault | Recalibrate both throttle channels |
| GS450h drivetrain jerk on regen | Auto gear shift timing | Expected behaviour — V2.15A downshifts before regen |

---

## One-Pedal Driving

With `throtmin` set to an appropriate negative value, the vehicle can be driven almost entirely with the throttle pedal — lift for regen deceleration, press for acceleration. Friction brakes are used only for final stops.

This style of driving:
- Increases range by recovering kinetic energy
- Reduces brake wear significantly
- Requires a learning period — new drivers should be warned about the strong deceleration on throttle lift
- Is most effective on routes with repeated stop-start patterns (urban driving)

---

*Source: Damien Maguire @Evbmw — "ZombieVerter VCU Firmware 2.15" (April 2024) · "ZombieVerter VCU Software V2.04" (January 2024)*  
*Regen first working: V2.15A (April 2024) · revRegen added: V2.20A (December 2024)*  
*Last verified against firmware: V2.30A (August 2025)*
