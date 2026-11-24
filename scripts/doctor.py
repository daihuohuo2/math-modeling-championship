"""Environment preflight doctor for math-modeling-championship.

Usage:
  python "<SKILL_ROOT>/scripts/doctor.py" [--project <PROJECT_ROOT>] [--json]

Checks (each reports present/missing without failing the run):
  - Python version, core scientific stack (numpy/scipy/pandas/matplotlib/openpyxl)
  - LaTeX engine (xelatex), bibtex/biber, latexmk, Pandoc
  - PDF audit tools: pdftotext, pdftoppm
  - Archivers: 7z / rar
  - pypdf / PyPDF2 (used by validate_submission.py page checks)
  - Project layout: state/decision_log.json, submission dir, checkpoints dir
Exit codes: 0 always (doctor reports, does not gate). Gate failure is decided
by the role-level commands (latex_paper.py doctor, check_env.py, etc.).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

CORE_MODULES = ["numpy", "scipy", "pandas", "matplotlib", "openpyxl"]
OPTIONAL_MODULES = ["pypdf", "PyPDF2"]
BINARIES = {
    "xelatex": "LaTeX 编译（xelatex）",
    "latexmk": "LaTeX 增量构建",
    "bibtex": "LaTeX 参考文献后端",
    "biber": "LaTeX biblatex 后端",
    "pandoc": "LaTeX→Word 转换（需要 Word 时）",
    "pdftotext": "PDF 文本抽取（非图片 PDF 校验）",
    "pdftoppm": "PDF 渲染抽检",
    "7z": "压缩包处理",
    "rar": "RAR 归档",
}


def check_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="PROJECT_ROOT to inspect")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    report: dict = {
        "python": {"version": sys.version.split()[0], "ok": sys.version_info >= (3, 9)},
        "core_modules": {m: check_module(m) for m in CORE_MODULES},
        "optional_modules": {m: check_module(m) for m in OPTIONAL_MODULES},
        "binaries": {b: bool(shutil.which(b)) for b in BINARIES},
        "project": {},
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    decision_log = project / "state" / "decision_log.json"
    report["project"] = {
        "project_root": str(project),
        "state_dir": project.joinpath("state").is_dir(),
        "decision_log": decision_log.is_file(),
        "submission_dir": project.joinpath("submission").is_dir(),
        "checkpoints_dir": project.joinpath("checkpoints").is_dir(),
    }

    core_missing = [m for m, ok in report["core_modules"].items() if not ok]
    missing_bins = [b for b, ok in report["binaries"].items() if not ok]
    critical_missing = [b for b in ("xelatex", "pdftotext") if b in missing_bins]
    report["summary"] = {
        "core_missing": core_missing,
        "critical_binaries_missing": critical_missing,
        "optional_binaries_missing": [b for b in missing_bins if b not in critical_missing],
        "note": "xelatex 缺失阻断 LaTeX 主线；pdftotext 缺失时须用 pypdf/人工完成非图片 PDF 校验；"
                "bibtex/biber/pandoc 按所选链路判断；doctor 只报告不门禁。",
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Python {report['python']['version']} {'OK' if report['python']['ok'] else 'TOO OLD'}")
        for group in ("core_modules", "optional_modules", "binaries"):
            for name, ok in report[group].items():
                print(f"  {'✓' if ok else '✗'} {name}")
        for name, ok in report["project"].items():
            if name == "project_root":
                continue
            print(f"  {'✓' if ok else '—'} project.{name}")
        print("critical missing:", critical_missing or "none")
        print("optional missing:", report["summary"]["optional_binaries_missing"] or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
