"""Validate storyboard.json against schema/storyboard.schema.json. Runs before every stage."""
import json, sys
from jsonschema import Draft202012Validator
from .common import ROOT, STORYBOARD


def validate():
    schema = json.loads((ROOT / "schema" / "storyboard.schema.json").read_text())
    sb = json.loads(STORYBOARD.read_text())
    errs = sorted(Draft202012Validator(schema).iter_errors(sb), key=lambda e: list(e.path))
    if errs:
        for e in errs:
            print(f"storyboard.json: {'/'.join(map(str, e.path)) or '<root>'}: {e.message}", file=sys.stderr)
        raise SystemExit(1)
    ids = [s["id"] for s in sb["shots"]]
    if len(set(ids)) != len(ids):
        raise SystemExit("storyboard.json: duplicate shot ids")
    return sb


if __name__ == "__main__":
    validate()
    print("storyboard.json OK")
