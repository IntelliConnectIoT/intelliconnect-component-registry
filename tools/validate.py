import json
import os
import sys
import glob
import re

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    print("FATAL: pip install jsonschema")
    sys.exit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KINDS = {"boards": "board", "sensors": "sensor", "actuators": "actuator"}

errors = []
warnings = []


def fail(where, message):
    errors.append("%s: %s" % (where, message))


def warn(where, message):
    warnings.append("%s: %s" % (where, message))


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def build_registry():
    resources = {}
    for name in ("common", "board", "sensor", "actuator"):
        path = os.path.join(ROOT, "schema", name + ".json")
        resources[name + ".json"] = Resource.from_contents(load(path))
    return Registry().with_resources(resources.items())


def validate_schemas(registry):
    validators = {}
    for kind in ("board", "sensor", "actuator"):
        schema = load(os.path.join(ROOT, "schema", kind + ".json"))
        validators[kind] = Draft202012Validator(schema, registry=registry)

    for directory, kind in KINDS.items():
        for path in sorted(glob.glob(os.path.join(ROOT, directory, "*.json"))):
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            document = load(path)
            for error in sorted(validators[kind].iter_errors(document), key=str):
                location = "/".join(str(p) for p in error.absolute_path) or "(root)"
                fail(rel, "%s -> %s" % (location, error.message))


def validate_keys():
    for directory in KINDS:
        for path in sorted(glob.glob(os.path.join(ROOT, directory, "*.json"))):
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            document = load(path)
            expected = os.path.basename(path)[:-5]
            if document.get("key") != expected:
                fail(rel, "key '%s' does not match filename" % document.get("key"))


def validate_index():
    index = load(os.path.join(ROOT, "index.json"))

    if "schema_version" not in index:
        fail("index.json", "no schema_version")
    if "registry_version" not in index:
        fail("index.json", "no registry_version")

    for directory in KINDS:
        listed = {entry["key"] for entry in index.get(directory, [])}
        present = {
            os.path.basename(p)[:-5]
            for p in glob.glob(os.path.join(ROOT, directory, "*.json"))
        }
        for key in sorted(listed - present):
            fail("index.json", "%s lists '%s' but the file is missing" % (directory, key))
        for key in sorted(present - listed):
            fail("index.json", "%s/%s.json is not listed" % (directory, key))

        by_key = {}
        for path in glob.glob(os.path.join(ROOT, directory, "*.json")):
            document = load(path)
            by_key[document["key"]] = document
        for entry in index.get(directory, []):
            document = by_key.get(entry["key"])
            if document and entry.get("status") != document.get("status"):
                fail("index.json", "%s status '%s' but entry says '%s'" % (
                    entry["key"], entry.get("status"), document.get("status")))


def validate_vocabulary():
    classes = load(os.path.join(ROOT, "vocabulary", "device-classes.json"))["classes"]
    lookups = load(os.path.join(ROOT, "vocabulary", "lookups.json"))

    sensor_types = {i["slug"] for i in lookups.get("sensor_types", [])}
    actuator_types = {i["slug"] for i in lookups.get("actuator_types", [])}
    protocols = {i["slug"] for i in lookups.get("sensor_protocols", [])}

    for path in sorted(glob.glob(os.path.join(ROOT, "sensors", "*.json"))):
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        platform = load(path)["platform"]

        if platform["sensor_type"] not in sensor_types:
            fail(rel, "sensor_type '%s' is not in lookups" % platform["sensor_type"])
        if platform["protocol"] not in protocols:
            fail(rel, "protocol '%s' is not in lookups" % platform["protocol"])

        seen = set()
        for reading in platform["readings"]:
            slug = reading["slug"]
            if slug in seen:
                fail(rel, "duplicate reading slug '%s'" % slug)
            seen.add(slug)

            if slug not in classes:
                fail(rel, "reading slug '%s' is not in the vocabulary" % slug)
                continue

            canonical = classes[slug]
            for field in ("device_class", "unit_symbol", "data_type"):
                want = canonical.get(field)
                got = reading.get(field)
                if want is not None and got is not None and want != got:
                    fail(rel, "%s %s is '%s' but the vocabulary says '%s'" % (
                        slug, field, got, want))

            low, high = reading.get("range_min"), reading.get("range_max")
            if low is not None and high is not None and low >= high:
                fail(rel, "%s range_min %s is not below range_max %s" % (slug, low, high))

    for path in sorted(glob.glob(os.path.join(ROOT, "actuators", "*.json"))):
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        platform = load(path)["platform"]

        if platform["actuator_type"] not in actuator_types:
            fail(rel, "actuator_type '%s' is not in lookups" % platform["actuator_type"])

        seen = set()
        for state in platform["states"]:
            command = state["command"]
            if command in seen:
                fail(rel, "duplicate command '%s'" % command)
            seen.add(command)

            parameter = state.get("parameter")
            if not parameter:
                continue
            low, high = parameter.get("range_min"), parameter.get("range_max")
            if low is not None and high is not None and low >= high:
                fail(rel, "%s range_min %s is not below range_max %s" % (command, low, high))
            if parameter.get("data_type") in ("integer", "float") and low is None:
                warn(rel, "%s takes a numeric argument with no range" % command)


def validate_status():
    for directory, kind in KINDS.items():
        for path in sorted(glob.glob(os.path.join(ROOT, directory, "*.json"))):
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            document = load(path)
            status = document["status"]
            block = document.get("harness") if kind == "board" else document.get("driver")

            if status == "unverified" and block:
                fail(rel, "status is unverified but a block is present")
            if status in ("draft", "verified") and not block:
                fail(rel, "status is %s but there is no block" % status)

            if not block:
                continue

            verified = block.get("verified") or {}
            named = verified.get("by")

            if status == "verified" and not named:
                fail(rel, "status is verified but verified.by is empty")
            if status == "verified" and not verified.get("date"):
                fail(rel, "status is verified but verified.date is empty")
            if status == "verified" and not verified.get("os"):
                fail(rel, "status is verified but verified.os is empty")
            if status != "verified" and named:
                fail(rel, "verified.by is set but status is '%s'" % status)

            reviewer = verified.get("reviewed_by")
            evidence = verified.get("evidence_url")

            if status == "verified" and reviewer and named and reviewer == named:
                fail(rel, "verified.reviewed_by is the same person as verified.by")
            if status == "verified" and not reviewer and not evidence:
                fail(rel, "verified with no reviewer needs verified.evidence_url")
            if status != "verified" and reviewer:
                fail(rel, "verified.reviewed_by is set but status is '%s'" % status)

            if kind != "board":
                continue

            primary = block.get("provisioning_model")
            offered = block.get("supported_provisioning_models") or []

            if primary not in offered:
                fail(rel, "provisioning_model '%s' is not in supported_provisioning_models" % primary)
            if not block.get("toolchains"):
                fail(rel, "no toolchains listed")

            runtime = block.get("runtime") or {}
            if primary == "linux-agent" and not runtime.get("python3"):
                fail(rel, "linux-agent board does not declare python3")
            if primary == "linux-agent" and not runtime.get("service_manager"):
                fail(rel, "linux-agent board does not declare a service_manager")
            if primary != "linux-agent" and runtime.get("service_manager"):
                fail(rel, "%s board declares a service_manager" % primary)

            if primary == "linux-agent" and not (block.get("probe") or {}).get("commands"):
                fail(rel, "linux-agent board has no probe commands")

            transport = block.get("transport") or {}
            if not transport.get("network"):
                fail(rel, "no network transport declared")
            if not transport.get("mqtt_client"):
                warn(rel, "no mqtt_client declared, so the platform has no way to talk to it")

            flash = block.get("flash") or {}
            if flash.get("method") in ("usb-serial", "usb-native", "dfu") and not flash.get("tool"):
                fail(rel, "flash method '%s' with no tool" % flash.get("method"))


def validate_badges():
    path = os.path.join(ROOT, "README.md")
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as handle:
        readme = handle.read()

    index = load(os.path.join(ROOT, "index.json"))

    verified = 0
    for directory in KINDS:
        for entry in index.get(directory, []):
            if entry.get("status") == "verified":
                verified += 1

    expected = {
        "registry": str(index.get("registry_version")),
        "schema": "v%s" % index.get("schema_version"),
        "boards": str(len(index.get("boards", []))),
        "sensors": str(len(index.get("sensors", []))),
        "actuators": str(len(index.get("actuators", []))),
        "verified": str(verified),
    }

    for label, want in expected.items():
        found = re.search(r"img\.shields\.io/badge/%s-([^-]+)-" % re.escape(label), readme)
        if not found:
            warn("README.md", "no %s badge" % label)
            continue
        if found.group(1) != want:
            fail("README.md", "%s badge says '%s' but it is '%s'" % (label, found.group(1), want))


def main():
    registry = build_registry()
    validate_schemas(registry)
    validate_keys()
    validate_index()
    validate_vocabulary()
    validate_status()
    validate_badges()

    total = sum(len(glob.glob(os.path.join(ROOT, d, "*.json"))) for d in KINDS)
    print("checked %d entries" % total)

    for message in warnings:
        print("  warn  %s" % message)
    for message in errors:
        print("  FAIL  %s" % message)

    if errors:
        print("\n%d error(s)" % len(errors))
        sys.exit(1)

    print("\nok%s" % (", %d warning(s)" % len(warnings) if warnings else ""))


main()
