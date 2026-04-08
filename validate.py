#!/usr/bin/env python3
"""Validate an MLCommons system_desc_id.json file against its JSON Schema spec."""

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    print("Error: jsonschema is required. Install it with: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

DEFAULT_SCHEMA = Path(__file__).parent / "system_desc_id_schema.json"


def load_json(path: Path, label: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {label} file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: {label} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)


def format_path(error: jsonschema.ValidationError) -> str:
    if error.absolute_path:
        return " -> ".join(str(p) for p in error.absolute_path)
    return "(root)"


def main():
    parser = argparse.ArgumentParser(
        description="Validate a system_desc_id.json file against the MLCommons spec."
    )
    parser.add_argument("data", metavar="data.json", help="Path to the JSON file to validate")
    parser.add_argument(
        "--schema",
        metavar="schema.json",
        default=DEFAULT_SCHEMA,
        help=f"Path to the JSON Schema (default: {DEFAULT_SCHEMA})",
    )
    args = parser.parse_args()

    data = load_json(Path(args.data), "Data")
    schema = load_json(Path(args.schema), "Schema")

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))

    if not errors:
        print(f"✓ {args.data} is valid.")
        sys.exit(0)

    print(f"✗ {args.data} has {len(errors)} error(s):\n")
    for i, err in enumerate(errors, 1):
        path = format_path(err)
        print(f"  [{i}] {path}")
        print(f"      {err.message}\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
