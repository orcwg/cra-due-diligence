#!/usr/bin/env python3
"""Validate the example due diligence record, and prove the schema refuses.

A schema that accepts its own example says nothing. Each negative case below is a
record that a free-text form cannot refuse and this schema does, so the run prints
what the schema buys rather than only that it parses.

Run: python3 validate-due-diligence-record.py   (needs jsonschema)
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover - dependency reported, never guessed
    sys.stderr.write("jsonschema is not installed; install it to run this check\n")
    raise SystemExit(2)

HERE = pathlib.Path(__file__).parent
SCHEMA = json.loads((HERE / "due-diligence-record.schema.json").read_text())
EXAMPLE = json.loads((HERE / "due-diligence-record.example.json").read_text())


def _failed(d: dict) -> dict:
    return d["properties_checked"][2]


def _test(d: dict) -> dict:
    return d["properties_checked"][3]


def low_risk_without_reason(d: dict) -> None:
    d["risk"] = {"level": "low"}
    del d["properties_checked"]


def above_low_risk_without_properties(d: dict) -> None:
    del d["properties_checked"]


def purl_without_version(d: dict) -> None:
    d["component"]["purl"] = "pkg:github/example-org/libexample-parser"


def component_without_purl(d: dict) -> None:
    d["component"] = {
        "name": "libexample-parser",
        "upstream_repository": "https://github.com/example-org/libexample-parser",
    }


def product_information_in_record(d: dict) -> None:
    d["product_release"] = "acme-gateway 5.2.0"


def check_without_time(d: dict) -> None:
    del d["performed"]["at"]


def failed_property_without_evidence(d: dict) -> None:
    del _failed(d)["evidence"]


def failed_property_without_action(d: dict) -> None:
    del _failed(d)["action_taken"]


def not_applicable_without_reason(d: dict) -> None:
    p = _failed(d)
    p["outcome"] = "not_applicable"
    p.pop("action_taken")


def test_run_without_digest(d: dict) -> None:
    del _test(d)["evidence"]


def metadata_without_date(d: dict) -> None:
    del d["maintainer_metadata"][0]["read_on"]


def missing_final_result(d: dict) -> None:
    del d["final_result"]


def tool_without_version(d: dict) -> None:
    del d["performed"]["tools"][0]["version"]


NEGATIVES = [
    ("a low-risk component with no reason for the level", low_risk_without_reason),
    ("a component above low risk with no property entries", above_low_risk_without_properties),
    ("a PURL with no version", purl_without_version),
    ("a component identified by name and repository instead of a PURL", component_without_purl),
    ("product information inside the record", product_information_in_record),
    ("a check recorded with no date and time", check_without_time),
    ("a failed property with no evidence digest", failed_property_without_evidence),
    ("a failed property with no action taken", failed_property_without_action),
    ("a property judged not applicable with no reason", not_applicable_without_reason),
    ("a test the manufacturer ran with no evidence digest", test_run_without_digest),
    ("maintainer metadata read with no date", metadata_without_date),
    ("a record with no final result", missing_final_result),
    ("a tool recorded without its version", tool_without_version),
]


def main() -> int:
    Draft202012Validator.check_schema(SCHEMA)
    validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    errors = sorted(validator.iter_errors(EXAMPLE), key=lambda e: e.json_path)
    if errors:
        print("FAIL: the example does not validate")
        for e in errors:
            print(f"  {e.json_path}: {e.message}")
        return 1
    print("PASS: the example validates")

    low = copy.deepcopy(EXAMPLE)
    low["risk"] = {"level": "low", "reason": "Formats log timestamps; no untrusted input."}
    del low["properties_checked"]
    if list(validator.iter_errors(low)):
        print("FAIL: a low-risk record with a reason and no property entries was refused")
        return 1
    print("PASS: a low-risk record stops at its final result, level and reason")

    failures = 0
    for what, mutate in NEGATIVES:
        d = copy.deepcopy(EXAMPLE)
        mutate(d)
        found = sorted(validator.iter_errors(d), key=lambda e: e.json_path)
        if found:
            print(f"PASS: refused  {what}\n        -> {found[0].json_path}: {found[0].message[:90]}")
        else:
            print(f"FAIL: accepted {what}")
            failures += 1

    print(f"\n{len(NEGATIVES) - failures} of {len(NEGATIVES)} negative cases refused")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
