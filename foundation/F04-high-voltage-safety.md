# F04 — High Voltage Safety

**Track:** Foundation  
**Prerequisites:** F03 — EV Drivetrain Fundamentals  
**Audience:** All levels — read before working on any HV system  
**Estimated reading time:** 10 minutes

---

> **This module is not optional.** High voltage EV systems can kill instantly, silently, and without warning. Read this before touching any orange cable, any contactor, or any HV terminal.

---

## The Risk

A typical EV conversion pack runs at 200–450V DC. At these voltages, as little as 100mA of current through the body is sufficient to cause fatal ventricular fibrillation. The current available from a traction pack is measured in hundreds of amps — far beyond what causes death.

The danger is compounded because:
- **DC does not let go.** AC at 50/60 Hz causes muscle contractions that may allow you to pull away. DC causes sustained muscle contraction — if you grip a live conductor your hand locks closed.
- **The capacitors retain charge.** After contactors open, the inverter bus capacitors remain charged at near-pack voltage for minutes. The pack is isolated but the inverter is still dangerous.
- **Contactors can fail closed.** A welded contactor leaves the HV system live even when the VCU believes it is off.

---

## The Two-Person Rule

**Never work on a live HV system alone.**

If something goes wrong — a shock, a fall, a fault — you need someone present who can kill the power and call for help. This is not a guideline. It is the single most important safety practice in this entire module.

---

## Personal Protective Equipment

**Minimum for any HV work:**

- **Insulated gloves rated for the voltage** — Class 0 (1000V rated) or higher. Not rubber washing-up gloves, not latex medical gloves. Proper electrical insulating gloves from a safety supplier. Inspect before every use — a pinhole is invisible and fatal.
- **Safety glasses** — arc flash and battery acid protection.
- **No jewellery** — rings, watches, and chains are conductors. Remove them entirely before working near any electrical system, HV or LV.

**Additional for battery work:**
- Face shield
- Non-conductive tools
- Insulated floor mat

---

## The Discharge Procedure

Before working on any HV component — inverter, charger, battery, contactor box — verify the system is de-energised:

1. **Key off, key removed from vehicle**
2. **Disconnect the 12V auxiliary battery** — this removes power from the VCU and prevents contactor actuation
3. **Open the HV service disconnect** — every EV pack should have a manual service disconnect (MSD) that physically breaks the HV circuit. Pull it, pocket it.
4. **Wait minimum 5 minutes** — allows inverter capacitors to discharge through bleed resistors. Some inverters take longer. Check your inverter specification.
5. **Verify with a multimeter** — set to DC voltage, highest range. Measure across HV+ and HV− at the inverter DC bus terminals. Should read near zero. If it reads anything above 50V, wait longer and measure again.
6. **Only then touch any HV component**

> **Never trust the contactors alone.** Contactors can fail closed (welded). The 12V interlock can fail. The VCU can malfunction. The only safe assumption is that the HV system is live until you have personally measured otherwise with a calibrated meter.

---

## Fusing Philosophy

Every HV conductor must be protected by a fuse rated for the maximum fault current. For a ZombieVerter-based build:

**Pack-level fusing:** One main fuse as close to the battery positive terminal as possible. This protects the entire HV circuit. Typical rating: 200–400A depending on pack and inverter capability. Use a fuse rated for the DC voltage of your pack — standard AC fuses are not suitable.

**Branch fusing:** Each major HV branch (inverter, charger, DC-DC) should have its own fuse. This allows a fault in one branch to be isolated without killing the entire system.

**Fuse ratings:** The fuse rating protects the wiring, not the load. Size fuses to the cable rating, not to the maximum current of the device. An undersized cable is a fire hazard even if the fuse doesn't blow.

**Service disconnect (MSD):** A manually operated HV disconnect that physically breaks the HV circuit. Required for safe servicing. Should be accessible without tools, in a known location, and clearly labelled. Some builders use the BMW safety box or similar contactor box as the MSD — this is acceptable only if the manual override is clearly accessible.

---

## HV Isolation vs HVIL — Two Different Concepts

This section introduces two distinct safety concepts that are frequently confused. They are not the same thing.

### HV Isolation

**What it is:** A fundamental design property of the entire HV system.

The HV bus (battery positive and negative) must be **electrically floating** — isolated from the vehicle chassis (LV ground). Neither HV+ nor HV− should have a low-resistance path to chassis.

**Why it matters:** If HV+ or HV− contacts the chassis, the chassis becomes energised at HV potential. Anyone touching the vehicle while also contacting ground completes a circuit through their body.

**How it's maintained:**
- Battery terminals are never directly connected to chassis
- Inverter and charger HV ports are internally isolated by design
- The ISA shunt measures HV differentially — neither terminal is referenced to chassis ground

**What breaks it:** A chafed HV cable touching a body panel, a failed component creating an HV-to-chassis path, or incorrect wiring (e.g. connecting HV− to chassis as a "ground" — never correct).

**This is a design property, not a circuit you wire.**

### HVIL — High Voltage Interlock Loop

**What it is:** A low-current 12V detection circuit that monitors connector integrity.

A simple series loop of 12V passes through every HV connector, service disconnect, and access panel in the system. When all connectors are fully mated, the loop is complete. When any connector is pulled, the loop opens and the VCU immediately opens the HV contactors.

**What it does:** Detects physical connector disconnection and triggers a contactor open. It does **not** detect isolation faults (HV contacting chassis).

**This is an active 12V circuit you physically wire.** See Module W04.

### Summary

| | HV Isolation | HVIL |
|---|---|---|
| What it is | A system design property | A 12V detection circuit |
| What it detects | Ground faults — HV touching chassis | Connector disconnection |
| How it works | Floating HV bus design | Series 12V loop through all HV connectors |
| What happens on failure | HV chassis energisation — silent danger | VCU opens contactors immediately |
| Do you wire it? | No — it's a design requirement | Yes — see Module W04 |

> **Neither HVIL nor HV Isolation replaces the discharge procedure.** Contactors can weld closed. HVIL circuits can fail. Isolation can be compromised. The only safe assumption before touching any HV component is that the system is live until you have personally measured otherwise.

The BMW Safety Box (S-BOX) integrates HVIL with pack-level CAN monitoring in one unit. See Module W04 for HVIL wiring.

---

## Cable Colour Conventions

| Colour | Meaning |
|---|---|
| Orange | HV cables — always treat as potentially live |
| Red | 12V positive |
| Black | 12V negative / chassis ground |
| Blue | Neutral (some charger AC wiring) |
| Brown | Line (some charger AC wiring) |

> When working on an unfamiliar vehicle, treat all orange cables as live regardless of the system state you believe it to be in.

---

## Bench Testing Safety

Most first-start testing is done on 12V only — no HV battery connected. This is intentionally the safest way to verify wiring and parameters before introducing HV risk.

When you do connect HV for the first time:
- Use a current-limited bench supply set to a low voltage (60V, 2A) before using full pack voltage
- Start with a bench precharge verification — watch `udc` rise in Spot Values before attempting run mode
- Have the 12V auxiliary battery disconnect within reach before and during the first HV test
- Verify contactor sequencing on 12V before connecting any HV cables

---

## If Someone Is Shocked

1. **Do not touch them** — if they are still in contact with a live conductor, you will be shocked too
2. **Kill the power** — pull the service disconnect, disconnect the 12V battery, use a non-conductive object to break the contact if you cannot reach the disconnect
3. **Call emergency services immediately** — even if the person appears conscious and uninjured, cardiac arrest can occur up to 24 hours after an electrical injury
4. **CPR if necessary** — electrical shock can cause cardiac arrest without obvious external injury

---

*Sources: openinverter.org community practice · BMW Safety Box series — Good Enuff Garage (April–May 2024) · general electrical safety standards*  
*Last verified: August 2025*
