# Changelog

All notable changes to this registry are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

`registry_version` versions the **content** and follows semantic versioning:

- **MAJOR** — an entry is removed, or a published `slug` or `key` changes
- **MINOR** — an entry is added, or an entry reaches `verified`
- **PATCH** — a correction that does not change a `key`, a reading slug or a command set

`schema_version` is a separate integer and increments only on a breaking format change.
It is listed against any release that changes it.

## [Unreleased]

## [0.2.0] — 2026-08-09

Schema version 2.

Microcontrollers are first class targets. Version 0.1.0 marked any board that could not
host a Linux provisioning agent as `unsupported` and instructed consumers to refuse it
permanently. That was wrong: it described a limit of one provisioning pipeline as a
property of the hardware, and it excluded the most widely deployed IoT parts in existence.

### Added

- 14 ESP32 board entries. Official Espressif development kits for every current SoC
  family — `esp32-devkitc-v4`, `esp32-s2-saola-1`, `esp32-s3-devkitc-1`,
  `esp32-c3-devkitm-1`, `esp32-c6-devkitc-1`, `esp8684-devkitm-1`, `esp32-h2-devkitm-1`,
  `esp32-p4-function-ev-board` — plus `esp32-cam`, `nodemcu-32s`, `lilygo-t-display-s3`,
  `seeed-xiao-esp32c3`, `seeed-xiao-esp32s3` and `m5stack-core2`
- `harness.supported_provisioning_models`, listing every pipeline a board accepts.
  `harness.provisioning_model` is now the default rather than the only option
- `harness.flash` — how an image gets onto the board: method, tool, port hint, baud rate
  and the bootloader quirks that make a board look dead
- `harness.transport` — network types, MQTT client, TLS and OTA support. A null
  `mqtt_client` states that the board needs a gateway or border router
- `harness.local_inference.llm` — whether a language model runs on the board, the largest
  parameter count that fits, model size in GB, working quantisation levels and runtimes
- `harness.local_inference.tinyml` — on-device ML frameworks, recorded separately because
  a board can be capable at quantised vision and incapable of hosting a language model
- `harness.local_inference.accelerator` and `usable_memory_gb`
- `verified.reviewed_by` and `verified.evidence_url`, supporting maintainer
  self-verification against published evidence
- Validator rules: the default provisioning model must appear in the supported list; every
  board needs a toolchain and a network transport; a `linux-agent` board needs `python3`,
  a service manager and probe commands; a non-Linux board must not declare a service
  manager; a USB or DFU flash method must name its tool; a verified entry needs either a
  reviewer or an evidence URL, and the reviewer may not be the person who ran it

### Changed

- `status` records verification progress only. The values are `unverified`, `draft` and
  `verified`
- `provisioning_model` values are now `linux-agent`, `micropython`, `arduino-sketch` and
  `vendor-firmware`, replacing `linux-agent` and `firmware`
- All four Arduino microcontroller boards move from `unsupported` to `draft` with a real
  harness. Portenta H7 and Nicla Vision default to `micropython`; Nicla Voice and Nano
  Matter default to `arduino-sketch`
- `arduino-uno-q-4gb` records the dual-processor architecture: Debian on the QRB2210,
  UNO headers wired to the STM32U585, and header access from Linux going through the
  Arduino Bridge rather than a local gpiochip. The bridge API and pin numbering remain
  unconfirmed and are marked as such
- `khadas-mind-2` specifications recorded from a physical unit: Core Ultra 7 258V
  (Lunar Lake), 32GB LPDDR5X, 1TB NVMe. Previously listed as Meteor Lake with null memory
  and storage
- `raspberry-pi-5-8gb` and `raspberry-pi-5-16gb` carry different language model ceilings,
  which is the reason they are separate entries

### Removed

- The `unsupported` status
- `harness.supported` and `harness.blocked_reason`. The top-level `blocked_reason` on
  sensors and actuators is unaffected — it records a fact that could not be sourced, which
  is a different thing

### Fixed

- `bin/build_drivers.py` crashed on components removed in an earlier release. It now skips
  a missing entry file and reports which ones it skipped

### Migration from schema version 1

- A consumer matching `status == "unsupported"` will no longer match anything. Boards that
  carried it are now `draft` and become provisionable when verified
- A consumer reading `harness.supported` must read `harness.provisioning_model` and select
  a pipeline instead. There is no longer a boolean that means "refuse this board"
- `harness.blocked_reason` is gone. Deployment constraints now live in
  `harness.transport.notes` and `harness.flash.notes`

## [0.1.0] — 2026-08-08

Schema version 1. First public release.

### Added

- 9 board entries, 16 sensor entries and 5 actuator entries
- JSON Schemas for board, sensor and actuator entries with shared definitions
- `vocabulary/device-classes.json`, adopting Home Assistant device class names and
  canonical units
- `vocabulary/lookups.json` for component types and protocols
- `tools/validate.py`, running the schemas plus the cross-file rules a schema cannot
  express
- `SPEC.md`, `CONTRIBUTING.md` and `VERIFYING.md`
- Apache 2.0 licence and NOTICE

[Unreleased]: https://github.com/IntelliConnectIoT/intelliconnect-component-registry/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/IntelliConnectIoT/intelliconnect-component-registry/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/IntelliConnectIoT/intelliconnect-component-registry/releases/tag/v0.1.0
