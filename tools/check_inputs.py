#!/usr/bin/env python3
"""Check every <actor>/input.json against that Actor's input schema.

By default the schema is read from the Actor's current public build
(GET https://api.apify.com/v2/acts/lindenwerk~<actor>/builds/default, no token needed).
With --schemas DIR it reads DIR/<actor>.json instead (offline check).

Checks: valid JSON object, every key exists in the schema, required keys present,
basic type, enum / items.enum values and minimum / maximum bounds.
Exit code 1 if anything fails. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTORS = [
    "german-eu-tender-matcher", "france-tender-matcher", "uk-tender-matcher", "sam-gov-contract-matcher",
    "tech-stack-detector", "seo-audit-crawler", "pdf-to-markdown-rag",
]
TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}


def live_schema(actor: str) -> dict:
    url = f"https://api.apify.com/v2/acts/lindenwerk~{actor}/builds/default"
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 (fixed https URL)
        build = json.load(resp)["data"]
    schema = build["inputSchema"]
    schema = json.loads(schema) if isinstance(schema, str) else schema
    schema["_build"] = build.get("buildNumber")
    return schema


def check(actor: str, data: dict, schema: dict) -> list[str]:
    props = schema.get("properties", {})
    errors = []
    for key in schema.get("required", []) or []:
        if key not in data:
            errors.append(f"required key missing: {key}")
    for key, value in data.items():
        spec = props.get(key)
        if spec is None:
            errors.append(f"unknown key: {key}")
            continue
        want = TYPES.get(spec.get("type"))
        if want and (not isinstance(value, want) or (spec.get("type") in ("integer", "number") and isinstance(value, bool))):
            errors.append(f"{key}: expected {spec.get('type')}, got {type(value).__name__}")
            continue
        if spec.get("enum") and value not in spec["enum"]:
            errors.append(f"{key}: {value!r} not in {spec['enum']}")
        item_enum = (spec.get("items") or {}).get("enum")
        if item_enum and isinstance(value, list):
            bad = [v for v in value if v not in item_enum]
            if bad:
                errors.append(f"{key}: {bad} not in {item_enum}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if spec.get("minimum") is not None and value < spec["minimum"]:
                errors.append(f"{key}: {value} < minimum {spec['minimum']}")
            if spec.get("maximum") is not None and value > spec["maximum"]:
                errors.append(f"{key}: {value} > maximum {spec['maximum']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--schemas", type=Path, help="directory with <actor>.json input schemas (offline)")
    args = parser.parse_args()
    failed = 0
    for actor in ACTORS:
        data = json.loads((ROOT / actor / "input.json").read_text(encoding="utf-8"))
        if args.schemas:
            schema = json.loads((args.schemas / f"{actor}.json").read_text(encoding="utf-8"))
            source = f"file {args.schemas / (actor + '.json')}"
        else:
            schema = live_schema(actor)
            source = f"live build {schema.get('_build')}"
        errors = check(actor, data, schema) if isinstance(data, dict) else ["input.json is not an object"]
        status = "OK  " if not errors else "FAIL"
        print(f"{status} {actor}: {len(data)} keys checked against {source}")
        for err in errors:
            print(f"     - {err}")
        failed += bool(errors)
    print(f"\n{len(ACTORS) - failed}/{len(ACTORS)} inputs valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
