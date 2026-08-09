# Contributing

Every entry here ends up controlling real hardware. A wrong pin role or a missing voltage
warning damages equipment, so the bar is higher than for most catalogues. Read this before
opening a merge request.

## Licensing of contributions

This project is licensed under the Apache License, Version 2.0. Under Section 5 of that
licence, any contribution you intentionally submit for inclusion is licensed under the
same terms, unless you clearly state otherwise at the time you submit it.

By opening a merge request you confirm that:

- you wrote the entry, or you have the right to submit it,
- you are not copying text from a datasheet or another project under an incompatible
  licence, and
- your employer, if they have rights to your work, permits the contribution.

Specifications such as an I2C address, a voltage range or a timing floor are facts and can
be stated freely. Do not paste datasheet prose. Cite the datasheet in `datasheet_url`
instead.

## What a good entry looks like

One component per merge request. Mixed merge requests will be asked to split.

**Every field is sourced.** `datasheet_url` must be set and must resolve. If you cannot
confirm a value from a primary source, leave it null and explain in `blocked_reason`. A
null is a known gap. A guess is a fault waiting to happen, and it is worse than nothing
because the next person will trust it.

**Bind to a maintained library.** Prefer an existing driver package over writing your own.
The value of an entry is knowing which library, which address, which pin, and what happens
when the component misbehaves. It is not new driver code.

**Fill in `failure_modes`, especially when everything worked first time.** This is the most
valuable field in the file and the one people skip. Write what actually bites:

- a component that fails intermittently by design and must be retried rather than alarmed
  on,
- a pin that idles at 5V and will destroy a 3.3V input,
- a driver that must be configured before first use or it overheats the motor,
- a reading that means nothing without a per unit calibration constant.

If you spent an afternoon working something out, write it down. That afternoon is the
contribution.

**Use the shared vocabulary.** Reading slugs and units come from
`vocabulary/device-classes.json`. If your component measures something not listed, propose
the addition in the same merge request and say which Home Assistant device class it maps
to, or `null` if there is no equivalent. Do not invent a slug that duplicates an existing
one under a different name.

**Never change a published `slug`.** Recorded measurements are keyed on it. Renaming one
breaks history for every existing deployment.

## Validate before you submit

```sh
pip install jsonschema
python tools/validate.py
```

It runs the JSON Schemas in `schema/` and the cross-file checks: filename against `key`,
entry against `index.json`, reading slugs and units against the vocabulary, and status
against the presence and contents of the driver block. [SPEC.md](SPEC.md) explains each
rule. A contribution that does not pass is not ready for review.

## Verification

[VERIFYING.md](VERIFYING.md) is the step by step guide, covering sensors, actuators and
boards. The rules below are the short version.

An entry is `draft` until a named person has run it against the physical component and
confirmed the readings are plausible or the commands take effect. Only then does it become
`verified`, and only a `verified` entry will be provisioned by a conforming tool.

To claim verification, fill the `verified` block with who ran it, the date, the exact board
and the operating system. "Works on a Pi" is not enough. Board revisions and OS versions
change GPIO behaviour.

**Two people sign an entry off.** `verified.by` is who ran it on hardware,
`verified.reviewed_by` is who confirmed that work, and they must be different people. A
maintainer confirms a contributor's entry before it reaches `verified`.

A maintainer who owns the hardware may self-verify with `reviewed_by` null and
`verified.evidence_url` linking the captured probe output, broker log and wiring
photograph. The evidence is public and stands in place of the reviewer.

Submitting a `draft` entry is genuinely useful on its own. Someone else with the component
can verify it later. Do not mark your own entry verified to get it merged faster.

## Vendors

If you make or supply a component, you can endorse its entry with a `vendor` block. It is
optional, it grants nothing, and it does not make the entry provisionable.

- Open a merge request against your own product's entry
- Set `organisation`, `domain`, `date`, `scope` and `evidence_url`
- `evidence_url` must be https and on your own domain. That page is what proves the
  endorsement is yours, so it cannot be claimed on your behalf
- `scope` is what you are actually confirming: `specifications`, `driver`, `harness`

Correcting a wrong specification on your own product is worth more than the stamp.

## Boards

Board entries carry a `harness` block instead of a `driver` block, and the first question
it answers is how a device program gets onto the board and how it then reaches the
platform.

Pick the `provisioning_model` that matches how the board is actually programmed, and list
every model that works in `supported_provisioning_models`. A microcontroller is a first
class target here. There is no status or flag that excludes one, and a contribution will
not be rejected for adding a board that does not run Linux.

Be exact about `transport`. A board with no Wi-Fi cannot reach an MQTT broker on its own,
and `mqtt_client: null` with a note naming the gateway or border router it needs is the
correct entry. Leaving it looking connectable is the failure people lose a weekend to.

Be honest about `local_inference`. `llm.viable: false` with a note explaining the limit is
a complete and useful answer. Do not leave the block empty because a board cannot run a
language model, and do not claim a model size you have not run.

`gpio.library` is board specific even between boards with identical pinouts. Do not copy it
from a similar board. Confirm it.

## Review

Expect questions about failure modes and about how you verified. That is the review doing
its job, not an objection to the contribution.

Entries that guess, that omit `datasheet_url`, or that claim verification without a board
and OS will be sent back.
