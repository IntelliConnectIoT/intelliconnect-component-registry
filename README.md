# IntelliConnect Component Registry

![IntelliConnect Component Registry](assets/img/banner.svg)

![Registry version](https://img.shields.io/badge/registry-0.2.0-4D8AFF) ![Schema version](https://img.shields.io/badge/schema-v2-4D8AFF) ![Boards](https://img.shields.io/badge/boards-23-4D8AFF) ![Sensors](https://img.shields.io/badge/sensors-16-4D8AFF) ![Actuators](https://img.shields.io/badge/actuators-5-4D8AFF) ![Verified](https://img.shields.io/badge/verified-0-lightgrey) ![Licence](https://img.shields.io/badge/licence-Apache--2.0-4D8AFF)

An open registry of IoT boards, sensors and actuators for developers and agents.

## What it is for

The registry enables developers and agents to quickly understand an IoT board, sensor, or actuator
without hunting through datasheets and forum threads. One file tells you how it wires up, which
library drives it, what it reads or what commands it takes, and how it fails in the field.

IntelliConnect is powered by it. Every component the platform offers comes from here, and device
templates are built from these schemas, so anything you attach is uniform: the same reading called
the same thing in the same units, MQTT topics generated from the declared slugs, dashboards and
thresholds from the declared ranges, and an actuator that accepts only its declared commands.

Board or sensor not supported yet? Contribute it. Once your entry is verified it is added to the
platform and available to everyone.

## What each file holds

- Wiring: pin roles, supply voltage, pull-ups, level shifting
- Driver: pip and apt packages, init class and arguments, polling limits
- Readings: slug, device class, unit, range, decimal places, warn and critical thresholds
- Commands: the exact set an actuator accepts, with valid argument ranges
- Failure modes: how the part misbehaves in the field
- Verification: who ran it, on what board and OS

Boards carry a harness block instead of a driver: provisioning model, GPIO library, pin
scheme, probe commands.

## How it helps

- **No driver code.** DHT22 needs `adafruit-circuitpython-dht`, `use_pulseio` off on a
  Pi, and 2 seconds between reads. It is all in the file.
- **Dashboards work on first boot.** Readings arrive with unit, range and thresholds
  declared, and every project measuring temperature calls it `temperature` in °C.
- **Control is bounded.** A servo takes `SET_ANGLE` 0–180 and nothing else. Commands come
  from the registry, so nothing outside the set can be issued.
- **Know before you buy.** An ESP32-H2 has no Wi-Fi and cannot reach a broker without a
  border router. A mini PC has no GPIO header. An ESP32-CAM has no USB socket and needs
  GPIO0 grounded to flash. An HC-SR04 echo pin destroys a 3.3V input without a divider.
- **Know what will run on it.** Every board declares how large a language model it can
  host, on what accelerator, with which runtimes — and says plainly when the answer is
  none.

## How to use it

1. Find the component in `sensors/`, `actuators/` or `boards/` — filename is the
   lowercased model number, so `DHT22` is `dht22.json`. `index.json` lists everything.
2. Check `status`. Only `verified` is safe to provision; tools must refuse the rest.
3. Read `driver.connection` for wiring and `driver.runtime` for packages and the init call.
4. Read `failure_modes` before wiring anything.

Verifying a component on real hardware is the most useful thing you can contribute.
[VERIFYING.md](VERIFYING.md) covers it. [CONTRIBUTING.md](CONTRIBUTING.md) covers adding
a component.

## Contents

| | Count | Verified |
| --- | --- | --- |
| Boards | 23 | 0 |
| Sensors | 16 | 0 |
| Actuators | 5 | 0 |

Nothing is verified yet. Every entry carries real specifications, and 42 of the 44 carry a
full driver or harness block, but none have been signed off against physical hardware by a
named person. Until an entry reaches `verified` a conforming tool will refuse to
provision it. Signing entries off is the most useful thing you can contribute, and
[VERIFYING.md](VERIFYING.md) walks through exactly how, for sensors, actuators and boards.
You do not need to write any registry code to help, only own the component.

## Hard rules

1. **No component is ever provisioned without a `verified` driver block.** A tool
   consuming this registry must fail and report when an entry is missing, `unverified` or
   `draft`. It must not guess, must not substitute a similar component, and must not
   generate a driver of its own.

2. **Driver definitions are human-authored and human-reviewed.** Nothing here may be
   written by a model and merged without a person who has run it on the real hardware.
   Drivers run with direct hardware access; a wrong pin assignment damages equipment.

3. **`slug` is immutable once published.** Recorded measurements are keyed on it. The
   `suggested_slug` field in the vocabulary is advisory and must never be applied without
   migrating existing data.

4. **Absent facts stay null.** A missing datasheet value, an unknown range, an untested
   pull-up resistance. All of them null. Never a plausible-looking default.

## Layout

```
index.json                      summary of every entry
schema/*.json                   JSON Schema for each entry kind
vocabulary/device-classes.json  canonical reading slugs, units and device classes
vocabulary/lookups.json         component type and protocol definitions
boards/<key>.json
sensors/<key>.json
actuators/<key>.json
```

[SPEC.md](SPEC.md) defines the entry format and what a consuming tool must do. Validate a
contribution with `python tools/validate.py` before opening a pull request.
[CHANGELOG.md](CHANGELOG.md) records every release and how to migrate between schema
versions.

`<key>` is the lowercased, hyphenated model number: `DHT22` becomes `dht22`,
`HC-SR04` becomes `hc-sr04`. Where a variant materially changes what the board
can do, it gets its own entry. `raspberry-pi-5-8gb` and `raspberry-pi-5-16gb` are
separate, because available memory decides whether local inference is possible.

## Status lifecycle

| Status | Meaning | Consumer behaviour |
| --- | --- | --- |
| `unverified` | Catalogue metadata only, no driver or harness block | Refuse |
| `draft` | Block authored but not yet run on real hardware | Refuse |
| `verified` | Block authored and confirmed against the physical hardware | Provision |

An entry only reaches `verified` when a named person has run it against the real hardware
and confirmed the readings are plausible. Status records verification progress only.

`source` records where an entry came from: `platform-seed` for components imported from
the original IntelliConnect catalogue, `authored` for entries written from datasheets.
Authored entries carry more nulls, and every null is a field that still needs filling.

## Sensor entry

```json
{
    "key": "dht22",
    "kind": "sensor",
    "revision": 1,
    "status": "verified",
    "source": "platform-seed",
    "platform": {
        "name": "DHT22 Temperature & Humidity Sensor",
        "description": "...",
        "sensor_type": "environmental",
        "protocol": "1wire",
        "manufacturer": "Aosong",
        "model_number": "DHT22",
        "datasheet_url": "...",
        "read_interval_seconds": 30,
        "readings": [
            {
                "slug": "temperature",
                "device_class": "temperature",
                "label": "Temperature",
                "unit": "degrees celsius",
                "unit_symbol": "°C",
                "data_type": "float",
                "range_min": -40,
                "range_max": 80,
                "decimal_places": 1,
                "threshold_warn_low": 10,
                "threshold_warn_high": 30,
                "threshold_crit_low": 0,
                "threshold_crit_high": 40
            }
        ]
    },
    "model": {
        "aliases": ["dht22", "am2302"]
    },
    "driver": { }
}
```

`device_class` and its canonical unit come from `vocabulary/device-classes.json`, looked
up by `slug`. The vocabulary follows the Home Assistant device class names, so anything
built on this registry lines up with the wider ecosystem rather than inventing its own
terms. `aliases` are what a person might actually call the thing out loud.

## Actuator entry

The same shape, with `states` in place of `readings`. Each state is one command the
component accepts.

Commands that take an argument must declare a `parameter` block. A command with
`"parameter": null` accepts no argument, and a consumer must reject any request that
supplies one.

```json
{
    "command": "SET_ANGLE",
    "label": "Set Angle",
    "description": "Rotate to an absolute angle",
    "payload": "SET_ANGLE",
    "sort_order": 1,
    "parameter": {
        "name": "angle",
        "data_type": "integer",
        "unit_symbol": "°",
        "range_min": 0,
        "range_max": 180,
        "required": true
    }
}
```

This is what makes automated control safe to build on. The complete set of valid commands
and their argument ranges is derived from the registry, so anything outside the declared
set cannot be produced or executed, including by a language model driving the device.

## Driver block

`null` on any entry that has not been verified.

```json
"driver": {
    "targets": ["raspberrypi"],
    "interface": "gpio-single-wire",
    "connection": {
        "pins": [
            {
                "role": "data",
                "required": true,
                "notes": "Any free GPIO."
            }
        ],
        "supply_voltage": "3.3V or 5V",
        "pullup_ohms": 10000
    },
    "runtime": {
        "python_module": "drivers.dht22",
        "pip_packages": ["adafruit-circuitpython-dht"],
        "apt_packages": ["libgpiod-dev"],
        "init": {
            "class": "adafruit_dht.DHT22",
            "args": {
                "pin": "board.D{data_pin}",
                "use_pulseio": false
            }
        }
    },
    "constraints": {
        "min_read_interval_seconds": 2,
        "read_timeout_seconds": 5,
        "warmup_seconds": null
    },
    "failure_modes": ["..."],
    "verified": {
        "by": "...",
        "date": "YYYY-MM-DD",
        "board": "...",
        "os": "..."
    }
}
```

Entries bind to existing driver libraries rather than reimplementing them. The value here
is not the code. It is knowing which library, which address, which pin, and what happens
when it misbehaves.

`failure_modes` is prose, and it is the most valuable field in the file. It is what stops
the next person rediscovering that a DHT22 fails intermittently by design, that an
HC-SR04 echo pin will destroy a 3.3V input without a divider, or that a servo commanded
to its full nominal range stalls at the end stops and browns out the board. Write what
actually bites people.

## Board entry

Boards carry a `harness` block in place of a `driver` block. It answers one question
before any other: how is a device program got onto this board, and how does it then reach
the platform?

```json
"harness": {
    "provisioning_model": "micropython",
    "supported_provisioning_models": ["micropython", "arduino-sketch", "vendor-firmware"],
    "component_attachment": "gpio-header",
    "flash": {
        "method": "usb-native",
        "tool": "esptool.py",
        "port_hint": "/dev/ttyACM0",
        "baud": 921600,
        "notes": "..."
    },
    "transport": {
        "network": ["wifi", "bluetooth"],
        "mqtt_client": "umqtt.simple",
        "tls": true,
        "ota": true,
        "notes": "..."
    },
    "runtime": { },
    "gpio": { },
    "probe": { },
    "local_inference": { },
    "toolchains": ["MicroPython", "ESP-IDF", "Arduino IDE", "PlatformIO"],
    "verified": { }
}
```

`provisioning_model` is the default path. `supported_provisioning_models` lists every path
that works and always includes the default.

- **`linux-agent`** — general purpose OS. The agent installs onto it, probes the hardware,
  generates the device program and runs it as a service.
- **`micropython`** — MicroPython flashed once, device program pushed as source over USB
  or OTA, `umqtt.simple` to the broker. Changing the program does not mean reflashing.
- **`arduino-sketch`** — compiled with `arduino-cli` or PlatformIO, uploaded over USB,
  `PubSubClient` or the ESP-IDF MQTT client to the broker.
- **`vendor-firmware`** — the manufacturer's SDK: ESP-IDF, Silicon Labs Gecko SDK, the
  Syntiant NDP120 toolchain.

`component_attachment` has two values, independent of the above:

- **`gpio-header`**: components are wired to pins, so a driver's `connection.pins`
  applies.
- **`usb-serial`**: the board has no GPIO header. Components attach over USB, serial or
  network, or through an expansion dock. `connection.pins` does not apply, and a driver
  requiring a pin assignment cannot be used on that board at all.

A mini PC is `linux-agent` and `usb-serial`: an agent installs and runs normally, but the
entire pin-based half of this registry is inapplicable to it. That is a real constraint,
not a gap to be worked around.

`gpio.library` is board-specific even between boards that look interchangeable. A 40-pin
header does not imply a shared driver stack. A Raspberry Pi 5 and a Jetson with identical
pinouts need different libraries.

`transport` is the field people wish they had read first. A board with no Wi-Fi cannot
reach an MQTT broker, however capable it is otherwise, and no amount of configuration
changes that. An ESP32-H2 and an Arduino Nano Matter both need a Thread or Zigbee border
router to exist before they are any use at all.

## What will actually run on it

`local_inference` answers the question every buyer has and no product page answers
honestly: can this board run a model, and how big?

```json
"local_inference": {
    "viable": true,
    "accelerator": "cuda",
    "usable_memory_gb": 8,
    "llm": {
        "viable": true,
        "max_params_b": 8,
        "max_model_size_gb": 6,
        "quantisation": ["q4_k_m", "awq", "int4"],
        "runtimes": ["llama.cpp", "ollama", "TensorRT-LLM", "vLLM"],
        "notes": "..."
    },
    "tinyml": {
        "viable": true,
        "frameworks": ["TensorRT", "ONNX Runtime"],
        "notes": "..."
    },
    "notes": "..."
}
```

`llm` and `tinyml` are separate because the answers diverge sharply. An ESP32-S3 runs a
quantised image classifier perfectly well and will never run a language model. A Jetson
does both. A Nicla Voice runs a wake-word model on a dedicated neural processor at
microamp power, which nothing else here can do, and has no language model story at all.

Where a language model does not fit, the entry says so in plain terms rather than leaving
the field null, because "no" is a useful answer and a null is not.

## Contributing

- One component per merge request.
- Every field must be sourced from the datasheet, and `datasheet_url` must be set.
- A driver or harness block requires the `verified` sub-block naming who ran it, on what
  board, and on what OS. Without that it stays `draft` and consumers will refuse it.
- Prefer binding to a maintained driver library over writing a new one.
- Fill in `failure_modes` even when everything worked first time. Especially then.
- If you cannot confirm something from a primary source, leave it null and say why in
  `blocked_reason`. An honest gap is worth more than a confident guess.

## Attribution

The `device_class` names and canonical units in `vocabulary/device-classes.json` are
adopted from [Home Assistant](https://www.home-assistant.io/integrations/sensor/#device-class),
© Home Assistant contributors, Apache License 2.0. Using their vocabulary rather than
inventing one keeps data produced against this registry interoperable with the wider
ecosystem.

Component specifications are taken from manufacturer datasheets, cited per entry in
`datasheet_url`. Driver entries bind to third-party libraries rather than reproducing
them; each library remains under its own licence.

## ⚠️ Warning and disclaimer

> **Wiring and powering hardware from this registry is done at your own risk.**
>
> Entries are contributed by volunteers and **can contain mistakes**, including wrong pins
> and wrong voltages. The datasheet is the authority, not the entry. Work on the bench, at
> low voltage, with a dummy load where one will do.
>
> **Disclaimer of warranty and liability.** This registry is provided **as is and as
> available, without warranty or condition of any kind**, express or implied, including any
> warranty of merchantability, fitness for a particular purpose or non-infringement, as set
> out in the Apache License 2.0.
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
