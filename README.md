# ZombieVerter VCU Training Series

A structured, multi-format training series for the [ZombieVerter](https://github.com/damienmaguire/Stm32-vcu) open-source EV conversion Vehicle Control Unit (VCU). Designed and maintained by Damien Maguire (EVBMW) and the [openinverter.org](https://openinverter.org) community.

**Firmware target:** V2.30A (August 2025)  
**Audience:** DIY EV converters — complete beginners through intermediate builders

---

## Output Files

| File | Description |
|---|---|
| `zombieverter-training-complete.html` | Complete classroom slide deck — 159 slides, self-contained single file, all diagrams embedded |
| `zombieverter-training-manual.pdf` | Printable reference manual — all 28 modules with wiring diagrams |
| `zombieverter-wiki-pages.zip` | MediaWiki `.wiki` + source `.md` files for openinverter.org wiki import |

Open `zombieverter-training-complete.html` in any modern browser — no server or internet connection required. Use `← →` arrow keys or the Prev/Next buttons to navigate. `↑ ↓` jumps between modules. `Esc` toggles the module sidebar.

---

## Curriculum

28 modules across 6 tracks:

### F — Foundation
| Module | Title |
|---|---|
| F01 | What Is a VCU and Why Do You Need One |
| F02 | ZombieVerter Ecosystem Overview |
| F03 | EV Drivetrain Fundamentals |
| F04 | High Voltage Safety |

### H — Hardware
| Module | Title |
|---|---|
| H01 | VCU Hardware Walkthrough |

### W — Wiring
| Module | Title |
|---|---|
| W01 | Wiring Philosophy & Best Practices |
| W02 | Throttle & Brake Wiring |
| W03 | Contactor & Precharge Circuit |
| W04 | HVIL — High Voltage Interlock Loop |
| W05 | Cooling System Control |
| W06 | 12V Auxiliary & Ignition Wiring |

### C — Configuration
| Module | Title |
|---|---|
| C00 | Firmware Version History |
| C01 | Flashing Firmware |
| C02 | Web Interface Walkthrough |
| C03 | Essential Parameters: First Start |
| C04 | Throttle Calibration |
| C06 | Fault Codes & Status Flags |

### I — Integration
| Module | Title |
|---|---|
| I01 | Nissan Leaf Inverter |
| I02 | Tesla Drive Units (SDU & LDU) |
| I03 | GS450h Transaxle |
| I03-X | GS450h — Wiring & Oil Pump Deep Dive |
| I04 | Mitsubishi Outlander Drive Unit |

### A — Advanced
| Module | Title |
|---|---|
| A01 | Regen Tuning |
| A02 | Charge Control & Popular Chargers |
| A03 | BMS Integration |
| A04 | Gear Selectors & Shifters |
| A05 | CAN Gateway & Multi-Node Systems |
| A06 | Firmware Customisation & Contributing |

---

## Wiring Diagrams

All diagrams are light-theme SVG/PNG, verified against the ZombieVerter V2.30A firmware and the openinverter.org community build documentation.

| Diagram | Module | Description |
|---|---|---|
| F02 | Foundation | VCU ecosystem overview — inputs, outputs, CAN devices |
| W02 | Wiring | Throttle pedal wiring — dual-channel pot |
| W03 | Wiring | Contactor & precharge circuit — NEG / PRCH / POS |
| W04 | Wiring | HVIL loop — high voltage interlock |
| W06 | Wiring | 12V auxiliary & ignition wiring |
| I01 | Integration | Nissan Leaf inverter connections |
| I03 | Integration | GS450h transaxle — sync serial, resolvers, shifter |
| A02 | Advanced | CP/PP charging pilot wiring |
| A05 | Advanced | CAN bus topology — daisy-chain, termination |

The slide deck also includes an **interactive HV junction box schematic** (Wiring track) — a 12-step animated circuit builder showing the full HV wiring sequence including contactors, precharge, IVT-S shunt, OBC charger connections, LV coil drives, 12V bus, EVSE pilot signals, and CAN bus routing.

---

## Critical Facts — Never Wrong

These facts are verified across all modules and must remain accurate:

- `udcsw` defaults to 330V — blocks all bench testing without HV
- `throtmax` defaults to 0 — most common cause of "throttle does nothing"
- `potmin` / `potmax` are set **inside** mechanical travel range (opposite to most systems)
- ISA shunt requires **permanent** 12V — never ignition-switched
- ISA U1 must connect to **inverter side** of main contactor — never battery side
- GS450h HV connects to **brass pillars only** — never the OEM terminals (destroys boost IGBT)
- V2.00A (May 2023) was a major rewrite — treat all V1 content with caution
- Regen only became reliable in V2.15A (April 2024)
- After any major firmware upgrade: reselect inverter type, save, reboot

---

## Repository Structure

```
zombieverter-training/
├── README.md
├── INDEX.md                          ← Curriculum overview
├── foundation/
│   ├── F01-what-is-a-vcu-and-why-do-you-need-one.md
│   ├── F02-zombieverter-ecosystem-overview.md
│   ├── F03-ev-drivetrain-fundamentals.md
│   └── F04-high-voltage-safety.md
├── hardware/
│   └── H01-vcu-hardware-walkthrough.md
├── wiring/
│   ├── W01-wiring-philosophy-and-best-practices.md
│   ├── W02-throttle-and-brake-wiring.md
│   ├── W03-contactor-and-precharge-circuit.md
│   ├── W04-hvil-high-voltage-interlock-loop.md
│   ├── W05-cooling-system-control.md
│   └── W06-12v-auxiliary-and-ignition-wiring.md
├── configuration/
│   ├── C00-firmware-version-history.md
│   ├── C01-flashing-firmware.md
│   ├── C02-web-interface-walkthrough.md
│   ├── C03-essential-parameters-first-start.md
│   ├── C04-throttle-calibration.md
│   └── C06-fault-codes-and-status-flags.md
├── integration/
│   ├── I01-nissan-leaf-inverter.md
│   ├── I02-tesla-ldu.md
│   ├── I03-gs450h-transaxle.md
│   ├── I03-X-gs450h-wiring-and-oil-pump-deep-dive.md
│   └── I04-mitsubishi-outlander-drive-unit.md
└── advanced/
    ├── A01-regen-tuning.md
    ├── A02-charge-control-and-chargers.md
    ├── A03-bms-integration.md
    ├── A04-gear-selectors-and-shifters.md
    ├── A05-can-gateway-and-multi-node-systems.md
    └── A06-firmware-customisation-and-contributing.md
```

---

## Content Sources

This training series was built from **219 YouTube video transcripts** covering ZombieVerter builds, EV drivetrain integration, and hands-on commissioning content. No web pages or forum posts were used as primary sources — all technical claims are grounded in video evidence from real builds.

### Video sources by channel

| Channel | Videos | Focus |
|---|---|---|
| Damien Maguire / [@Evbmw](https://www.youtube.com/@Evbmw) | ~155 | ZombieVerter firmware, GS450h, Leaf, Outlander, OBC integration, bench testing |
| Jamie Jones / [Ohm-Grown EVs](https://www.youtube.com/@OhmGrownEVs) | ~24 | Complete BMW E91 conversion build series — Episodes 1–20+ |
| Good Enuff Garage | ~16 | Beginner-focused bench-level ZombieVerter tutorials, BMW E91 build |
| Various EV builders | ~24 | Supporting EV conversion content |

### Supporting references

- [openinverter.org](https://openinverter.org) — community wiki, parameter reference, firmware changelog
- ZombieVerter firmware source and commit history — [github.com/damienmaguire/Stm32-vcu](https://github.com/damienmaguire/Stm32-vcu)
- openinverter.org community forum — for edge cases and hardware variant notes

---

## Contributing

Pull requests welcome. Check `INDEX.md` for modules marked as pending. When a new firmware release drops, update `C00` (Firmware Version History) first, then check affected modules before updating the firmware target version in this README.

**Before submitting:** verify all parameter names, pin numbers, and voltage values against the current firmware. Flag time-sensitive content with staleness markers: 🟢 Current / 🟡 Verify / 🔴 Outdated.

---

## Credits

- **Damien Maguire** — ZombieVerter design, firmware, and the vast majority of primary technical content
- **Jamie Jones / Ohm-Grown EVs** — Complete BMW E91 conversion documentation, Episodes 1–20+
- **Good Enuff Garage** — Beginner-friendly ZombieVerter bench tutorials and E91 build content
- **Mitch Elliott** — Audi e-tron OBC reverse engineering
- **Project Gus** — BMW F30 CAN e-shifter reverse engineering
- **openinverter.org community** — testing, documentation, inverter integration, forum knowledge base

---

*ZombieVerter VCU Training Series · github.com/robertwa1974/zombieverter-training · openinverter.org · V2.30A*
