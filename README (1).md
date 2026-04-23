# ZombieVerter VCU Training Series

A structured, community-built training series for the [ZombieVerter](https://evbmw.com) open-source EV conversion Vehicle Control Unit (VCU). Designed and maintained by Damien Maguire ([@Evbmw](https://www.youtube.com/@Evbmw)) and the [openinverter.org](https://openinverter.org) community.

> **Firmware target:** V2.30A (August 2025)  
> **Status:** Active development — 16 modules complete, ~14 planned

---

## What This Is

A multi-format training resource for DIY EV converters — from complete newcomers to intermediate builders. Each topic is covered as a **markdown module** (the source of truth), a **slide deck**, and eventually a searchable static site and printable PDF.

This is not official Damien Maguire / EVBMW documentation. It is a community learning resource built on top of the openinverter.org wiki, forum, and video content.

---

## Repository Structure

```
zombieverter-training/
├── README.md
├── INDEX.md                          ← Full curriculum, all 30 planned modules
├── foundation/
│   └── F02-zombieverter-ecosystem-overview.md
├── hardware/
│   └── H01-vcu-hardware-walkthrough.md
├── wiring/
│   ├── W02-throttle-and-brake-wiring.md
│   ├── W03-contactor-and-precharge-circuit.md
│   └── W06-12v-auxiliary-and-ignition-wiring.md
├── configuration/
│   ├── C00-firmware-version-history.md
│   ├── C01-flashing-firmware.md
│   ├── C02-web-interface-walkthrough.md
│   ├── C03-essential-parameters-first-start.md
│   ├── C04-throttle-calibration.md
│   └── C06-fault-codes-and-status-flags.md
├── integration/
│   └── I03-gs450h-transaxle.md
└── slides/
    ├── zombieverter-training-complete.html   ← Combined 89-slide classroom deck
    ├── zombieverter-classroom-F02.html
    ├── zombieverter-classroom-H01.html
    └── ... (one per completed module)
```

---

## Curriculum Overview

Modules are grouped into six tracks. See [INDEX.md](INDEX.md) for the full list.

| Track | Prefix | Scope | Completed |
|---|---|---|---|
| Foundation | F | What ZV is, EV fundamentals, HV safety | F02 |
| Hardware | H | Board walkthrough, I/O, CAN bus, peripherals | H01 |
| Wiring | W | Throttle, contactor, 12V, CAN | W02, W03, W06 |
| Configuration | C | Firmware, web UI, parameters, calibration, faults | C00–C04, C06 |
| Integration | I | Inverter-specific (Leaf, GS450h, Prius, Outlander, Tesla LDU) | I03, I03-X |
| Advanced | A | Regen, BMS, charging, gear selectors, custom firmware | A02, A03, A04 |

### Where to Start

- **Complete novice** → F01 → F02 → H01 → C01 → C02 → C03
- **Experienced EV converter, new to ZombieVerter** → F02 → H01 → C02 → C03
- **Have a board, need to get it running** → C01 (blank board) → C02 → C03
- **Specific wiring question** → Jump directly to the relevant W-series module

---

## Critical Facts (Never Get These Wrong)

These are the most common sources of builder confusion. They appear in the modules but are worth knowing up front:

- **`udcsw` defaults to 330V** — blocks all bench testing until set to a reachable voltage
- **`throtmax` defaults to 0** — the single most common cause of "throttle does nothing"
- **`potmin`/`potmax` are set *inside* mechanical travel range** — opposite to most other systems
- **ISA shunt requires permanent 12V** — never ignition-switched, or it loses calibration
- **ISA U1 terminal → inverter side of main contactor** — never battery side
- **GS450h HV connects to brass pillars only** — the OEM terminals will destroy the boost IGBT
- **V2.00A (May 2023) was a major rewrite** — treat all V1 forum content with caution
- **Regen only became reliable in V2.15A (April 2024)**
- **After any major firmware upgrade:** reselect inverter type, save, reboot

---

## Firmware Version

All content is verified against **V2.30A (August 2025)**. When a new release drops:

1. Check `C00-firmware-version-history.md` first
2. Update affected modules
3. Update the firmware target in this README and in INDEX.md

Firmware source: [github.com/damienmaguire/Stm32-vcu/releases](https://github.com/damienmaguire/Stm32-vcu/releases)

---

## Staleness Flags

Time-sensitive content in the modules is tagged:

- 🟢 **Current** — verified against V2.30A
- 🟡 **Verify** — believed correct but not recently re-tested
- 🔴 **Outdated** — known to have changed; needs update

---

## Contributing

This repo is currently in **controlled expert review** (Phase 1) before public release. If you've been invited to review:

- Open an issue for factual errors, outdated content, or missing topics
- PRs welcome for typo fixes and minor corrections
- For substantive content additions, open an issue first to discuss

For technical questions about the ZombieVerter itself, the best resource is the [openinverter.org forum](https://openinverter.org/forum).

### Writing New Modules

If you want to contribute a new module:

1. Check INDEX.md for the module code and scope
2. Follow the format of an existing module (C03 or W02 are good examples)
3. Use backtick style for all parameter names: `` `udcsw` ``, `` `throtmax` ``
4. Pin numbers with prefix: Pin 15, Pin 52
5. Include a staleness flag on time-sensitive content
6. End with a "What's Next" section and a source citation

---

## Credits

- **Damien Maguire / EVBMW** — ZombieVerter designer and primary technical authority
- **Johannes Huebner (johu)** — Creator of the openinverter firmware framework
- **Good Enuff Garage** — Bench-level beginner tutorial series
- **Jamie Jones / Ohm-Grown EVs** — Complete E91 build series (Episodes 1–20+)
- **openinverter.org community** — Ongoing firmware contributions, inverter support, testing

---

## License

Content in this repository is released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — the same license used by openinverter.org wiki content. Attribution: ZombieVerter VCU Training Series contributors.

Firmware and hardware designs remain under their respective licenses at the upstream repositories.
