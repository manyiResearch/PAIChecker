#!/usr/bin/env python3
"""Validate PAIChecker input and append aligned classification output."""

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = (
    "instance_id",
    "issue_number",
    "problem_statement",
    "hints_text",
    "is_issue_mentioned",
    "pr_description",
    "pr_comments",
    "commit_message",
    "review_comments",
    "is_pr_mentioned",
    "patch",
    "test_patch",
    "files",
)
VALID_LABELS = {"SC", "FP", "DP", "IS", "UL", "Others", "No Misalignment"}


def _jsonl_objects(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Line {line_number} of {path} must be a JSON object")
        records.append(value)
    return records


def _read(args: argparse.Namespace) -> int:
    records = _jsonl_objects(args.input)
    if args.index < 0 or args.index >= len(records):
        raise ValueError(f"Index {args.index} out of range for {args.input}")
    record = records[args.index]
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    if not isinstance(record["instance_id"], str) or not record["instance_id"].strip():
        raise ValueError("instance_id must be a non-empty string")
    print(json.dumps(record, ensure_ascii=False))
    return 0


def _contains(args: argparse.Namespace) -> int:
    if not args.output.exists():
        return 1
    return 0 if any(record.get("instance_id") == args.instance_id for record in _jsonl_objects(args.output)) else 1


def _validated_classifications(path: Path) -> list[dict[str, str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid classifications JSON in {path}: {exc}") from exc
    if not isinstance(value, list) or not value:
        raise ValueError("classifications must be a non-empty JSON array")

    classifications = []
    seen = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {"label", "reason"}:
            raise ValueError("each classification must contain exactly label and reason")
        label, reason = item["label"], item["reason"]
        if label not in VALID_LABELS or not isinstance(reason, str) or not reason.strip():
            raise ValueError("each classification needs a valid label and non-empty reason")
        if label in seen:
            raise ValueError(f"duplicate classification label: {label}")
        seen.add(label)
        classifications.append({"label": label, "reason": reason.strip()})

    if "No Misalignment" in seen and len(seen) != 1:
        raise ValueError("No Misalignment cannot be combined with another label")
    return classifications


def _final_output(classifications: list[dict[str, str]]) -> str:
    return "\n".join(
        f"<classification>\n<label>{item['label']}</label>\n<reason>{item['reason']}</reason>\n</classification>"
        for item in classifications
    )


def _append(args: argparse.Namespace) -> int:
    if args.output.exists() and any(
        record.get("instance_id") == args.instance_id for record in _jsonl_objects(args.output)
    ):
        print(f"Skipped {args.instance_id}: already present in {args.output}")
        return 0
    classifications = _validated_classifications(args.classifications)
    record = {
        "instance_id": args.instance_id,
        "status": "Submitted",
        "final_output": _final_output(classifications),
        "classifications": classifications,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Appended {args.instance_id} to {args.output}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    read = subparsers.add_parser("read")
    read.add_argument("--input", type=Path, required=True)
    read.add_argument("--index", type=int, default=0)
    read.set_defaults(handler=_read)

    contains = subparsers.add_parser("contains")
    contains.add_argument("--output", type=Path, required=True)
    contains.add_argument("--instance-id", required=True)
    contains.set_defaults(handler=_contains)

    append = subparsers.add_parser("append")
    append.add_argument("--output", type=Path, required=True)
    append.add_argument("--instance-id", required=True)
    append.add_argument("--classifications", type=Path, required=True)
    append.set_defaults(handler=_append)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
