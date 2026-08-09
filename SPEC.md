# Registry specification

Schema version 1.

This defines what a valid entry is, and what a tool consuming this registry must do.
`schema/*.json` is the machine-readable part. This document covers the rules a schema
cannot express.

## Layout

```
index.json                      summary of every entry, with schema_version
schema/common.json              shared definitions
schema/board.json               board entry
schema/sensor.json              sensor entry
schema/actuator.json            actuator entry
vocabulary/device-classes.json  canonical reading slugs, units and device classes
vocabulary/lookups.json         component type and protocol definitions
boards/<key>.json
sensors/<key>.json
actuators/<key>.json
```

`<key>` is the lowercased, hyphenated model number, matching `^[a-z0-9]+(-[a-z0-9]+)*$`.
The filename and the `key` field must be identical.

## Status

Every entry carries exactly one status.

| Status | Meaning | Consumer must |
| --- | --- | --- |
| `unverified` | Catalogue metadata only, no driver or harness block | Refuse |
| `draft` | Block authored, not run on real hardware | Refuse |
| `verified` | Block confirmed against the physical hardware by a named person | Provision |
| `unsupported` | Board structurally cannot host a provisioning agent | Refuse, permanently |

Rules a schema cannot enforce, checked by `tools/validate.py`:

- `unverified` must have no driver or harness block
- `draft` and `verified` must have one
- `verified` requires `verified.by`, `verified.date` and `verified.os` to be set
- Any status other than `verified` must leave `verified.by` empty
- `unsupported` applies to boards only, requires `harness.supported: false` and a
  `blocked_reason`
- The status in `index.json` must match the status in the entry file

**Verification is not self service.** A maintainer who is not the contributor confirms an
entry before it is marked `verified`. See [VERIFYING.md](VERIFYING.md).

## Absent facts stay null

A field whose value is unknown is `null`, never a plausible default, never an empty string
standing in for a number. A `null` is a documented gap and tells the next contributor
exactly where to look. A guess is indistinguishable from a fact.

Required fields must be present as keys even when their value is `null`.

## `slug` is immutable

Recorded measurements are keyed on the reading `slug`. Once an entry is published its
slugs never change. The `suggested_slug` field in the vocabulary is advisory and must not
be applied to a published entry without migrating existing data.

Renaming a component's `key` is the same thing: it is a new entry, not an edit.

## Readings resolve against the vocabulary

Every reading `slug` must exist in `vocabulary/device-classes.json`. Where the vocabulary
declares a `device_class`, `unit_symbol` or `data_type`, the reading must match it. This
is what makes two projects measuring temperature comparable.

The vocabulary follows Home Assistant device class names so data produced against this
registry lines up with the wider ecosystem.

Reading slugs must be unique within an entry, and `range_min` must be below `range_max`.

## Commands are a closed set

`platform.states` is the complete set of commands an actuator accepts. A consumer must
reject anything outside it, including a request originating from a language model.

- `command` matches `^[A-Z0-9]+(_[A-Z0-9]+)*$` and is unique within the entry
- A command taking an argument declares a `parameter` block
- `"parameter": null` means the command takes no argument, and a consumer must reject a
  request that supplies one
- A numeric parameter should declare `range_min` and `range_max`; the validator warns when
  it does not
- An `enum` parameter must declare `values`

## Drivers are human authored

No driver or harness block may be written by a model and merged without a person who has
run it on the real hardware. Drivers execute with direct hardware access, and a wrong pin
assignment damages equipment.

`failure_modes` is prose and is the most valuable field in the file. It records how the
part misbehaves in the field, so the next person does not rediscover it.

## Versioning

Three independent numbers.

| Field | Format | Increments when |
| --- | --- | --- |
| `schema_version` | Integer | The entry format breaks: a field removed, a field made required, or the meaning of a field changed. Adding an optional field is not breaking |
| `registry_version` | Semver `MAJOR.MINOR.PATCH` | Content is released |
| `revision` | Integer, per entry | That entry's content changes |

`registry_version` follows semantic versioning against the **content**, not the code:

- **MAJOR** — an entry is removed, or a published `slug` or `key` changes. Both break a
  consumer that already resolved them
- **MINOR** — an entry is added, or an entry reaches `verified`
- **PATCH** — a correction to an existing entry that does not change its `key`, its
  reading slugs or its command set

`schema_version` is deliberately not semver. It has no minor or patch component because
only a breaking format change matters to a consumer; anything else is additive and safe to
ignore.

The README badges report `registry_version`, `schema_version`, the entry count and the
verified count. `tools/validate.py` fails if any of them drift from `index.json`.

## Validation

```sh
pip install jsonschema
python tools/validate.py
```

Exit code 0 means every entry conforms. The validator runs the JSON Schemas and then the
cross-file checks above: filename against `key`, entry against `index.json`, slugs and
types against the vocabulary, and status against the presence and contents of the block.

A contribution that does not pass is not ready for review.
