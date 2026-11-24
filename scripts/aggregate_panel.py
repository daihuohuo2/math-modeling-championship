"""Validate and aggregate one 15-expert review round.

Usage:
  python aggregate_panel.py --input review/panel_round_1.json \
      --output state/panel_latest.json --threshold 92

通过条件：恰好 15 个唯一合法评分（E01–E15）、顶层与每位专家独立性确认均为
true、每人至少一条可定位证据、无 high 阻断项、未舍入算术平均值 >= 阈值。
平均分展示保留两位小数，但比较一律使用未舍入 Decimal 值。

Exit codes: 0 = panel passed, 1 = panel failed or input invalid.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

EXPECTED_IDS = [f"E{i:02d}" for i in range(1, 16)]
VALID_SEVERITIES = {"high", "medium", "low"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> int:
    print(json.dumps({"pass": False, "error": message}, ensure_ascii=False))
    return 1


def reviewer_error(rev: dict, index: int) -> str | None:
    where = f"reviewers[{index}]"
    if not isinstance(rev, dict):
        return f"{where} must be an object"
    rid = rev.get("id")
    if rid not in EXPECTED_IDS:
        return f"{where}.id must be one of E01..E15, got {rid!r}"
    if not isinstance(rev.get("role"), str) or not rev.get("role").strip():
        return f"{where}.role must be a non-empty string"
    if rev.get("independent_confirmed") is not True:
        return f"{where}.independent_confirmed must be true after actual review"
    score = rev.get("score")
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        return f"{where}.score must be a number, got {score!r}"
    if not Decimal(0) <= Decimal(str(score)) <= Decimal(100):
        return f"{where}.score must be within [0, 100], got {score!r}"
    evidence = rev.get("evidence")
    if not isinstance(evidence, list) or not any(
        isinstance(e, str) and e.strip() for e in evidence
    ):
        return f"{where}.evidence needs at least one locatable item"
    for key in ("findings", "required_actions"):
        if not isinstance(rev.get(key), list):
            return f"{where}.{key} must be a list"
    blockers = rev.get("blockers")
    if not isinstance(blockers, list):
        return f"{where}.blockers must be a list"
    for b in blockers:
        if not isinstance(b, dict) or b.get("severity") not in VALID_SEVERITIES:
            return f"{where}.blockers severity must be high|medium|low"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--threshold", type=str, default="92")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.is_file():
        return fail(f"input file not found: {in_path}")
    try:
        payload = json.loads(in_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read input JSON: {exc}")
    if not isinstance(payload, dict):
        return fail("input JSON must be an object")

    if payload.get("independence_attestation") is not True:
        return fail("top-level independence_attestation must be true after actual review")

    artifact_version = payload.get("artifact_version")
    if not isinstance(artifact_version, str) or not SHA256_RE.match(artifact_version):
        return fail("artifact_version must be the frozen bundle SHA-256 (64 hex chars)")

    reviewers = payload.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) != 15:
        return fail("reviewers must contain exactly 15 entries")

    ids = [r.get("id") for r in reviewers if isinstance(r, dict)]
    if len(set(ids)) != 15:
        return fail("reviewer ids must be 15 unique values")
    if sorted(ids) != EXPECTED_IDS:
        return fail(f"reviewer ids must be exactly E01..E15, got {sorted(ids)}")

    for i, rev in enumerate(reviewers):
        error = reviewer_error(rev, i)
        if error:
            return fail(error)

    threshold = Decimal(args.threshold)
    mean = sum((Decimal(str(r["score"])) for r in reviewers), Decimal(0)) / Decimal(15)
    mean_display = mean.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    high_blockers = [
        {"id": r["id"], "description": b.get("description", "")}
        for r in reviewers
        for b in r.get("blockers", [])
        if isinstance(b, dict) and b.get("severity") == "high"
    ]
    medium_count = sum(
        1
        for r in reviewers
        for b in r.get("blockers", [])
        if isinstance(b, dict) and b.get("severity") == "medium"
    )

    ordered = sorted(reviewers, key=lambda item: Decimal(str(item["score"])))
    result = {
        "pass": bool(mean >= threshold and not high_blockers),
        "round": payload.get("round"),
        "artifact_version": artifact_version,
        "threshold": str(threshold),
        "reviewer_count": 15,
        "mean_exact": str(mean),
        "mean_display": float(mean_display),
        "high_blockers": high_blockers,
        "medium_blocker_count": medium_count,
        "weakest_reviewers": [
            {"id": item["id"], "role": item.get("role"), "score": item["score"]}
            for item in ordered[:3]
        ],
        "calibration_notes": payload.get("notes"),
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
