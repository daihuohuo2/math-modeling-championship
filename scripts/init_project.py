"""Initialize a competition project skeleton.

Usage:
  python init_project.py "<PROJECT_ROOT>" --competition "<竞赛>" --year "<届次>"

创建 state/decision_log.json 与标准目录合同；已存在 decision_log.json 时只报告
恢复入口，绝不覆盖用户文件。PROJECT_ROOT 不得位于 SKILL_ROOT 内。

Exit codes: 0 = created or resumed, 1 = invalid location.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIRS = [
    "input",
    "analysis",
    "src",
    "results",
    "figures",
    "paper",
    "support_materials",
    "submission",
    "review",
    "state",
]


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root")
    parser.add_argument("--competition", default=None)
    parser.add_argument("--year", default=None)
    parser.add_argument("--problem", default=None)
    parser.add_argument("--deadline", default=None)
    parser.add_argument("--language", default=None)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    skill_root = Path(__file__).resolve().parent.parent
    if root == skill_root or skill_root in root.parents:
        emit({"ok": False, "error": "PROJECT_ROOT must not be inside SKILL_ROOT"})
        return 1

    decision_log = root / "state" / "decision_log.json"
    if decision_log.is_file():
        emit({
            "ok": True,
            "resumed": True,
            "decision_log": str(decision_log),
            "message": "已有项目状态，读取 decision_log.json 恢复进度，未做任何覆盖",
        })
        return 0

    for name in DIRS:
        (root / name).mkdir(parents=True, exist_ok=True)

    log: dict = {}
    template = skill_root / "assets" / "decision_log.template.json"
    if template.is_file():
        try:
            log = json.loads(template.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            log = {}
    fills = {
        "competition": args.competition,
        "year": args.year,
        "problem_id": args.problem,
        "deadline": args.deadline,
        "paper_language": args.language,
    }
    for key, value in fills.items():
        if value is not None:
            log[key] = value
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log["created_at"] = now
    log["updated_at"] = now

    decision_log.parent.mkdir(parents=True, exist_ok=True)
    decision_log.write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    emit({
        "ok": True,
        "resumed": False,
        "project_root": str(root),
        "decision_log": str(decision_log),
        "created_dirs": DIRS,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
