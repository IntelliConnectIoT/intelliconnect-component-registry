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

**Verification is not self service.** A maintainer who is not the contributor confirms the
entry before it is marked verified. This is deliberately inconvenient. It is the only thing
standing between the registry and a field that quietly damages someone's hardware.

Submitting a `draft` entry is genuinely useful on its own. Someone else with the component
can verify it later. Do not mark your own entry verified to get it merged faster.

## Boards

Board entries carry a `harness` block instead of a `driver` block, and the first question
it answers is whether the board can host a provisioning agent at all.

Be honest about `unsupported`. A microcontroller that cannot run a general purpose
operating system is not a gap in the registry to be worked around later. It is a permanent
fact, and recording it saves the next person the same investigation.

`gpio.library` is board specific even between boards with identical pinouts. Do not copy it
from a similar board. Confirm it.

## Review

Expect questions about failure modes and about how you verified. That is the review doing
its job, not an objection to the contribution.

Entries that guess, that omit `datasheet_url`, or that claim verification without a board
and OS will be sent back.
