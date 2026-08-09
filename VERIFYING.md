# Verifying an entry

Every entry in this registry starts at `draft`. A `draft` entry carries real specifications
and a real driver block, but nobody has yet run it against the physical component. A
conforming tool refuses to provision it.

Verification is someone taking the component out of a drawer, wiring it exactly as the
entry describes, running it, and recording what happened. It is the single most useful
contribution you can make here, and it does not require you to write any registry code.

You do not need permission to start. Pick a component you own and work through this guide.

## ⚠️ Warning and disclaimer

> **Verification means powering real hardware. You do so at your own risk.**
>
> - Work on the bench, at low voltage, with a dummy load where one will do
> - Actuators move the moment power is applied — keep hands and anything fragile clear
> - The datasheet is the authority, not the entry
>
> Entries are contributed by volunteers and **can contain mistakes**, including wrong pins
> and wrong voltages. That is the whole reason verification exists.
>
> **Disclaimer of warranty and liability.** This registry and this guide are provided **as
> is and as available, without warranty or condition of any kind**, express or implied,
> including any warranty of merchantability, fitness for a particular purpose or
> non-infringement, as set out in the Apache License 2.0.
>
> **To the maximum extent permitted by law, CogniTech Systems, the IntelliConnect project,
> its maintainers and its contributors accept no liability whatsoever** for any loss,
> damage, injury or cost arising out of or in connection with the use of this registry,
> including damage to equipment or property, personal injury, business interruption, or
> loss of data or profits, whether arising in contract, tort, negligence or otherwise, and
> whether or not advised of the possibility of such damage.
>
> You alone are responsible for verifying that any wiring, voltage or command is correct
> and safe for your hardware, for your own safety, and for compliance with the electrical
> and product regulations that apply where you are. If you are not competent to carry out
> the work safely, do not carry it out.

## What you need

- The physical component, and the board you intend to verify it on
- The entry file for it, in `sensors/`, `actuators/` or `boards/`
- The datasheet linked from the entry's `datasheet_url`
- For actuators, a bench setup where an unexpected movement or output is harmless

## Step 1. Record the exact board and OS

"Works on a Pi" is not a verification. Board revisions and OS releases change GPIO
behaviour, and an entry verified on one and claimed for all of them is worse than an
unverified entry.

How the board identifies itself is not universal. Device tree boards such as the Raspberry
Pi and Jetson expose `/proc/device-tree/model`; x86 boards expose DMI instead and have no
device tree at all. Each board entry declares which file applies to it in
`harness.probe.model_file`, so check the entry for your board rather than assuming.

This covers both:

```sh
if [ -r /proc/device-tree/model ]; then
    tr -d '\0' < /proc/device-tree/model; echo
elif [ -r /sys/class/dmi/id/product_name ]; then
    cat /sys/class/dmi/id/sys_vendor 2>/dev/null
    cat /sys/class/dmi/id/product_name
else
    echo unknown
fi

[ -r /etc/os-release ] && . /etc/os-release && echo "${PRETTY_NAME:-unknown}"
uname -m
```

Keep this output. It goes into the entry verbatim.

This step assumes a `linux-agent` board. Microcontrollers are verified too, just
differently: there is no shell to collect output from, so flash the board with the
`provisioning_model` the entry declares and record what the toolchain reports instead.

- `micropython` — flash the MicroPython build, connect over the REPL and keep the output
  of the commands in `harness.probe`. `os.uname()` and `gc.mem_free()` are the equivalent
  of `/etc/os-release` and free memory
- `arduino-sketch` — record the `arduino-cli board list` output and the FQBN that compiled
  and uploaded successfully
- `vendor-firmware` — record the SDK and the version that produced a working image

Then confirm the board actually reached the broker. For a microcontroller that is the real
test, and it is the step most likely to fail.

## Step 2. Read the entry before you wire anything

Open the entry and read `driver.failure_modes` first. It exists to save you the
investigation, and several entries record faults that damage hardware:

- `hc-sr04` returns a 5V echo pulse that destroys a 3.3V GPIO input without a divider
- `sg90` stalls at its end stops and browns out a Pi sharing the 5V rail
- `dht22` fails continuously if `use_pulseio` is left on

Then read `driver.connection` for the pin roles, supply voltage and any pull-up or level
shift. Wire it exactly as written. If the datasheet and the entry disagree, stop and open
an issue rather than guessing which is right.

Check `driver.targets` as well. Every sensor and actuator driver here currently declares
`raspberrypi` and nothing else, so a Raspberry Pi is the only board these entries claim to
work on today. Verifying one on a Jetson or another board is welcome and valuable, but it
means adding that target and confirming the runtime and pin scheme there, not simply
recording that it worked.

## Step 3. Install what the entry declares

Take the package lists from `driver.runtime`. Do not substitute a library you prefer.

```sh
sudo apt install -y <apt_packages>
pip install <pip_packages>
```

For `dht22` that is:

```sh
sudo apt install -y swig liblgpio-dev python3-libgpiod
pip install adafruit-circuitpython-dht lgpio gpiod
```

If a package no longer installs, that is a finding worth reporting on its own.

## Sensors

Instantiate exactly as `driver.runtime.init` specifies, substituting your own pin or
address for the `{placeholder}` values.

```python
import adafruit_dht, board
sensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)
```

Then poll it, no faster than `driver.constraints.min_read_interval_seconds`, for long
enough to see how it behaves rather than whether it responds once. Ten minutes is a
reasonable minimum.

Confirm all of the following:

- Every reading declared in `platform.readings` is actually produced
- Values sit inside `range_min` and `range_max`, and are plausible for the room you are in
- `unit_symbol` and `decimal_places` match what the sensor really resolves
- Each entry in `failure_modes` either occurs and is handled, or is demonstrably wrong
- Sustained failure across many consecutive cycles does **not** happen

A sensor that reads 22.5°C once is not verified. A sensor that reads plausibly for ten
minutes, survives the intermittent failures its entry predicts, and recovers from them, is.

## Actuators

Actuators move things and switch loads. Verify them on a bench where nothing is attached
that can hurt anyone or damage itself.

Instantiate from `driver.runtime.init`, then work through **every** command in
`platform.states`. The command set in the registry is the exact set the platform will ever
issue, including on behalf of an AI agent, so an unverified command is a command nobody has
ever proven safe.

For `sg90` that is `SET_ANGLE`, `CENTER` and the remaining declared states. For each one:

- Send the declared `payload` shape exactly as written
- Confirm the physical result matches the `label` and `description`
- For commands with a `parameter`, test `range_min`, `range_max` and one value in between
- Confirm a value outside the declared range is rejected rather than attempted
- Watch for the failure modes, particularly current draw and end-stop stalling

Record any command that is declared but does not work. That is a defect in the entry and
finding it is the point of the exercise.

## Boards

Board entries carry a `harness` block instead of a `driver` block. Verifying one means
confirming the board can be provisioned as described.

Run every command in that entry's own `harness.probe.commands` and confirm each returns
what the entry implies. **The list differs per board and you should not carry one board's
commands to another.** A Raspberry Pi entry lists `i2cdetect`, `gpiodetect` and `gpioinfo`;
an x86 mini PC entry lists `lspci` and DMI reads instead, because it has no GPIO header to
detect.

Then confirm:

- `harness.runtime` is accurate — OS family, Python 3 availability, package manager, service manager
- `harness.component_attachment` matches reality. `gpio-header` means pin-wired components are possible; `usb-serial` means they are not, and a sensor entry that needs pins cannot be verified on that board
- `harness.gpio.library` genuinely works on this board. It is board specific even between boards with identical pinouts, so do not accept it because a similar board uses it. It is not always `libgpiod` — the Jetson entry declares `Jetson.GPIO`
- `harness.gpio.pin_scheme` matches the numbering that library actually expects, `bcm` and `board` being different schemes
- Where `harness.gpio` is null and the board has a header, that is an unfilled gap rather than a statement that there is no GPIO. Filling it is a useful contribution
- The files named in `harness.probe` exist at those paths on this board
- `harness.local_inference` is honest about what the board can do. If it claims a model
  size, run a model that size before signing it off
- `harness.transport.mqtt_client` is either a client you got connected to a broker on this
  board, or null with a note naming the gateway it needs
- `harness.provisioning_model` is the path you actually used, and every entry in
  `supported_provisioning_models` is one you know works

Verify the board on the pipeline it declares. A microcontroller that flashes, connects and
publishes is verified, exactly like a Linux board that installs the agent and publishes.
Nothing here is signed off as unsupportable.

## Step 4. Fill in the verified block

Sensors and actuators use `driver.verified`:

```json
"verified": {
    "by": "Your Name",
    "date": "2026-08-08",
    "board": "Raspberry Pi 5 Model B Rev 1.0",
    "os": "Debian GNU/Linux 12 (bookworm)"
}
```

Boards use `harness.verified`, which has no `board` field because the entry is the board:

```json
"verified": {
    "by": "Your Name",
    "date": "2026-08-08",
    "os": "Debian GNU/Linux 12 (bookworm)"
}
```

Use the exact strings from Step 1. Then change the entry's top-level `status` from `draft`
to `verified`, and increment `revision`.

If you corrected any field while testing, that correction is part of the same change. An
entry verified against wiring you had to fix is verified against the fixed wiring.

## Step 5. Submit it

Open a pull request containing the entry file and nothing else. In the description, say:

- Which component, board and OS
- How long you ran it and what you observed
- Any field you corrected, and what the real value was
- Any declared failure mode that did not occur, or any new one you hit

Raw logs are welcome. A ten minute capture of readings is more convincing than a summary.

## Who signs an entry off

Two fields, and they must name different people:

- `verified.by` — who ran the component on real hardware
- `verified.reviewed_by` — who confirmed that work

A contributor's entry is confirmed by a maintainer before it reaches `verified`. Do not
mark your own newly authored entry verified to get it merged faster.

Verifying somebody else's `draft` entry is a genuinely valuable contribution, and it is
the fastest way to move an entry to `verified`.

### Maintainer self-verification

A maintainer who owns the hardware may verify their own entry with `reviewed_by` left
null, provided `verified.evidence_url` links the captured evidence:

- The probe output for the board, or the REPL and toolchain output for a microcontroller
- A broker log showing readings arriving, with timestamps
- A photograph of the wiring as tested

The evidence is public and stands in place of the second person. `tools/validate.py`
rejects a `verified` entry that has neither a reviewer nor an evidence URL.

## If the entry is wrong

Say so. An entry that does not survive contact with the real component is exactly what this
process is designed to catch, and reporting it is not a failed contribution.

- Wrong pin, voltage or pull-up: correct it in the same pull request and explain
- Library no longer installs or has moved: correct `runtime` and explain
- Command declared but not accepted by the hardware: correct `states` and explain
- Cannot confirm a value from the datasheet or the bench: set it to `null` rather than
  leaving a plausible-looking guess, and say why

Absent facts stay null. An honest gap is worth more than a confident invention, and the
null tells the next person exactly where to look.
