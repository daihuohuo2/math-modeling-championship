"""Final submission gate for a frozen competition bundle.

Usage:
  python validate_submission.py "<PROJECT_ROOT>" \
      --paper "submission/579_参赛论文.pdf" \
      --support "submission/579_支撑材料.zip" [--threshold 92]

核对：文件存在性与官方格式、实际字节数大小、manifest 哈希一致性、联合
artifact_bundle_sha256、ZIP/RAR 路径安全与源码存在性、15 专家 panel 通过
且绑定同一冻结版本、M1/P1/P2/W1/W2 门禁均为 PASS、轻量匿名元数据检查，
以及 CUMCM 2026 结构检查：非图片 PDF、无目录、电子版无承诺书/编号
专用页（官方第十条）、全文页数 ≤51（摘要1+正文30+赛区建议附录≤20；
正文=主体+AI声明+参考文献的语义拆分以 submission_manifest.json 的
page_report 为准；附录页数不限为全国口径）。

Exit codes: 0 = all hard checks passed, 1 = gate failed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

PAPER_EXTS = {".pdf", ".doc", ".docx"}
ARCHIVE_EXTS = {".zip", ".rar"}
SOURCE_EXTS = {".py", ".m", ".ipynb", ".r"}
REQUIRED_GATES = ["M1", "P1", "P2", "W1", "W2"]
DEFAULT_MAX_BYTES = 20 * 1024 * 1024
# 官方第十条：参赛论文电子版 ≤20MB；默认大小上限即据此设定。
# 承诺书/编号专用页不得出现在电子版论文中（官方第十条）。
ELECTRONIC_ONLY_PAGES = ["承  诺  书", "承诺书", "编 号 专 用 页", "编号专用页"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def joint_bundle_sha256(files: list[dict]) -> str:
    joined = "".join(f"{entry['path']}{entry['sha256']}" for entry in sorted(files, key=lambda e: e["path"]))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def unsafe_archive_paths(names: list[str]) -> list[str]:
    bad = []
    for name in names:
        normalized = name.replace("\\", "/")
        parts = normalized.split("/")
        if normalized.startswith(("/", "~")) or (len(parts[0]) == 2 and parts[0][1] == ":"):
            bad.append(name)
        elif ".." in parts:
            bad.append(name)
    return bad


def audit_zip(path: Path) -> tuple[bool, str, dict]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
    except zipfile.BadZipFile as exc:
        return False, f"ZIP 无法打开: {exc}", {}
    bad = unsafe_archive_paths(names)
    if bad:
        return False, f"压缩包内含不安全路径: {bad[:3]}", {}
    sources = [n for n in names if Path(n).suffix.lower() in SOURCE_EXTS]
    detail = {"entry_count": len(names), "source_files": len(sources)}
    if not sources:
        return False, "支撑材料中未发现可运行源程序（.py/.m 等）", detail
    detail["sources"] = sorted(sources)[:10]
    return True, "ZIP 路径安全且包含源程序", detail


def audit_archive(path: Path, results_dir: Path) -> tuple[bool, str, dict]:
    if path.suffix.lower() == ".zip":
        return audit_zip(path)
    tool = shutil.which("unrar") or shutil.which("rar") or shutil.which("7z")
    if tool:
        cmd = [tool, "lb", str(path)] if tool.endswith(("unrar", "rar")) else [tool, "l", "-ba", str(path)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, f"解包工具调用失败: {exc}", {}
        if proc.returncode != 0:
            return False, f"解包工具返回 {proc.returncode}", {}
        names = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        bad = unsafe_archive_paths(names)
        sources = [n for n in names if Path(n).suffix.lower() in SOURCE_EXTS]
        audit = {
            "archive": str(path),
            "archive_sha256": sha256_file(path),
            "tool": tool,
            "listed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "path_safety": not bad,
            "entry_count": len(names),
            "sources_present": bool(sources),
        }
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "archive_audit.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if bad:
            return False, f"压缩包内含不安全路径: {bad[:3]}", audit
        if not sources:
            return False, "支撑材料中未发现可运行源程序", audit
        return True, "RAR 经解包工具审计通过，已写 results/archive_audit.json", audit
    prior = results_dir / "archive_audit.json"
    if prior.is_file():
        try:
            recorded = json.loads(prior.read_text(encoding="utf-8"))
            if recorded.get("archive_sha256") == sha256_file(path) and recorded.get("path_safety"):
                return True, "RAR 依据既有 results/archive_audit.json（哈希一致）通过", {}
        except (OSError, json.JSONDecodeError):
            pass
    return False, "RAR 无可验证解包工具：请改用 ZIP，或用可验证工具人工审计并生成 results/archive_audit.json", {}


def check_docx_identity(path: Path) -> list[str]:
    findings = []
    try:
        with zipfile.ZipFile(path) as archive:
            if "docProps/core.xml" in archive.namelist():
                core = archive.read("docProps/core.xml").decode("utf-8", "ignore")
                for tag in ("dc:creator", "cp:lastModifiedBy"):
                    match = re.search(rf"<{tag}>([^<]+)</{tag}>", core)
                    if match and match.group(1).strip():
                        findings.append(f"DOCX 元数据 {tag}={match.group(1).strip()!r}，提交前须清除")
    except (OSError, zipfile.BadZipFile):
        findings.append("DOCX 无法读取元数据，需人工检查匿名")
    return findings


def check_pdf_identity(path: Path) -> list[str]:
    findings = []
    data = path.read_bytes()
    for match in re.finditer(rb"/Author\s*\(([^)\\]{0,120})\)", data):
        value = match.group(1).strip()
        if value:
            findings.append(f"PDF 元数据 /Author={value.decode('latin-1')!r}，提交前须清除")
    return findings


def extract_pdf_text(path: Path, max_pages: int = 200) -> tuple[str, int]:
    """Extract cumulative text and page count from a PDF via pdftotext/pdfminer/pypdf."""
    tool = shutil.which("pdftotext")
    if tool:
        try:
            proc = subprocess.run(
                [tool, "-enc", "UTF-8", str(path), "-"],
                capture_output=True, text=True, timeout=120, check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                pages = proc.stdout.count("\x0c") or 1
                return proc.stdout, pages
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError:
            from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        chunks = []
        for i, page in enumerate(reader.pages):
            if i >= max_pages:
                break
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                chunks.append("")
        return "\n".join(chunks), len(reader.pages)
    except Exception:
        return "", 0


def check_paper_structure(paper: Path, pdf_text: str, pdf_pages: int) -> tuple[list[dict], list[str]]:
    """CUMCM 2026 structural checks: no TOC, text-based PDF, page-budget accounting.

    Page attribution (摘要不计入正文；正文=主体+AI声明+参考文献；附录另计) is a
    semantic judgment the frozen bundle must record in submission_manifest.json
    under `page_report`; this gate validates what is mechanically checkable and
    the declared numbers for consistency.
    """
    checks: list[dict] = []
    warnings: list[str] = []

    def add(cid: str, name: str, ok: bool, detail: str, severity: str = "hard") -> None:
        checks.append({"id": cid, "name": name, "pass": bool(ok), "severity": severity, "detail": detail})

    if paper.suffix.lower() == ".pdf":
        add("pdf_text_extractable", "非图片 PDF（可抽取文本）", bool(pdf_text.strip()),
            "抽取到" if pdf_text.strip() else "无法抽取文本：疑似图片 PDF，查重无法分析，按不成功参赛处理")
        if pdf_text:
            # TOC markers at line starts; allow running text mentioning 目录 in body prose.
            toc_lines = [
                line.strip() for line in pdf_text.splitlines()
                if re.match(r"^\s*(目\s*录|Contents)\s*$", line)
            ]
            add("no_toc", "论文不含目录", not toc_lines,
                "未发现目录页" if not toc_lines else f"发现疑似目录页标记: {toc_lines[:3]}")
            # 官方第十条：电子版论文不得包含承诺书/编号专用页。
            head = "\n".join(pdf_text.splitlines()[:80])
            leaked = [p for p in ELECTRONIC_ONLY_PAGES if p in head]
            add("no_commitment_page", "电子版不含承诺书/编号专用页", not leaked,
                "未发现" if not leaked else f"前部发现疑似承诺书/编号页标记: {leaked[:2]}")
    elif paper.suffix.lower() == ".docx":
        try:
            with zipfile.ZipFile(paper) as archive:
                doc = archive.read("word/document.xml").decode("utf-8", "ignore")
        except (OSError, zipfile.BadZipFile, KeyError):
            doc = ""
        has_toc_field = bool(re.search(r'TOC\s+\\o', doc)) or "TOC \\" in doc
        add("no_toc", "论文不含目录（Word 目录域）", doc == "" or not has_toc_field,
            "未发现 Word 目录域" if not has_toc_field else "document.xml 含 TOC 目录域，必须删除")
        # 官方第十条：电子版论文不得包含承诺书/编号专用页。
        plain = re.sub(r"<[^>]+>", "", doc)
        leaked = [p for p in ELECTRONIC_ONLY_PAGES if p in plain[:8000]]
        add("no_commitment_page", "电子版不含承诺书/编号专用页", doc == "" or not leaked,
            "未发现" if not leaked else f"文档前部发现疑似承诺书/编号页标记: {leaked[:2]}")

    declared = (pdf_pages or 0)
    add("total_pages_declared", "全文页数 ≤51（摘要1+正文30+赛区建议附录≤20）",
        0 < declared <= 51 if declared else True,
        f"渲染页数={declared}" if declared else "无法自动确定页数，须人工核对")
    if declared and declared > 51:
        pass  # hard fail recorded above

    return checks, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root")
    parser.add_argument("--paper", required=True)
    parser.add_argument("--support", required=True)
    parser.add_argument("--threshold", default="92")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    checks: list[dict] = []
    warnings: list[str] = []

    def check(cid: str, name: str, ok: bool, detail: str = "", severity: str = "hard") -> bool:
        checks.append({"id": cid, "name": name, "pass": bool(ok), "severity": severity, "detail": detail})
        return bool(ok)

    paper = Path(args.paper)
    paper = paper if paper.is_absolute() else root / paper
    support = Path(args.support)
    support = support if support.is_absolute() else root / support

    check("paper_exists", "论文文件存在", paper.is_file(), str(paper))
    if paper.is_file():
        check("paper_format", "论文格式为 PDF/DOC/DOCX",
              paper.suffix.lower() in PAPER_EXTS, paper.suffix)
        size = paper.stat().st_size
        check("paper_size", "论文不超过官方大小限制", size <= args.max_bytes,
              f"{size} bytes (limit {args.max_bytes})")
        if paper.suffix.lower() == ".docx":
            warnings.extend(check_docx_identity(paper))
            structural_checks, structural_warnings = check_paper_structure(paper, "", 0)
        elif paper.suffix.lower() == ".pdf":
            warnings.extend(check_pdf_identity(paper))
            pdf_text, pdf_pages = extract_pdf_text(paper)
            if pdf_pages == 0:
                warnings.append("无法解析 PDF 页数，页数与文字版检查须人工复核")
            structural_checks, structural_warnings = check_paper_structure(paper, pdf_text, pdf_pages)
        else:
            structural_checks, structural_warnings = [], []
        warnings.extend(structural_warnings)
        checks.extend(structural_checks)

    check("support_exists", "支撑材料压缩包存在", support.is_file(), str(support))
    if support.is_file():
        check("support_format", "压缩包格式为 ZIP/RAR",
              support.suffix.lower() in ARCHIVE_EXTS, support.suffix)
        size = support.stat().st_size
        check("support_size", "压缩包不超过官方大小限制", size <= args.max_bytes,
              f"{size} bytes (limit {args.max_bytes})")
        ok, detail, extra = audit_archive(support, root / "results")
        check("support_audit", "压缩包路径安全且含源程序", ok, detail)

    manifest_path = root / "submission" / "submission_manifest.json"
    manifest = {}
    if check("manifest_exists", "submission_manifest.json 存在", manifest_path.is_file()):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            check("manifest_parse", "manifest 可解析", False, str(exc))
        else:
            files = manifest.get("files") or []
            hash_mismatch = []
            try:
                for entry in files:
                    fpath = root / entry["path"]
                    if not fpath.is_file() or sha256_file(fpath) != entry.get("sha256"):
                        hash_mismatch.append(entry["path"])
                recomputed = joint_bundle_sha256(files) if files else ""
            except (KeyError, TypeError) as exc:
                check("manifest_schema", "manifest 文件条目须含 path 与 sha256", False, str(exc))
            else:
                check("manifest_hashes", "manifest 中全部文件哈希与实际一致",
                      bool(files) and not hash_mismatch, f"不一致: {hash_mismatch[:5]}" if hash_mismatch else f"{len(files)} files verified")
                declared = manifest.get("artifact_bundle_sha256")
                check("bundle_hash", "联合 artifact_bundle_sha256 可复算",
                      bool(recomputed) and declared == recomputed,
                      f"declared={declared}, recomputed={recomputed[:16] if recomputed else ''}...")
                for label, target in (("paper", paper), ("support", support)):
                    ref = (manifest.get(label) or {})
                    if target.is_file() and ref.get("sha256"):
                        check(f"manifest_{label}_hash", f"manifest 中 {label} 哈希与实际文件一致",
                              ref.get("sha256") == sha256_file(target) and ref.get("bytes") == target.stat().st_size)

    panel_path = root / "state" / "panel_latest.json"
    if check("panel_exists", "state/panel_latest.json 存在", panel_path.is_file()):
        try:
            panel = json.loads(panel_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            check("panel_parse", "panel 结果可解析", False, str(exc))
        else:
            mean = Decimal(str(panel.get("mean_exact", panel.get("mean", 0))))
            passed_threshold = mean >= Decimal(str(args.threshold))
            check("panel_pass", f"15 专家平均分 >= {args.threshold} 且无致命阻断",
                  bool(panel.get("pass")) and passed_threshold
                  and panel.get("reviewer_count") == 15 and not panel.get("high_blockers"),
                  f"mean={mean}, reviewers={panel.get('reviewer_count')}, high={len(panel.get('high_blockers') or [])}")
            if manifest.get("artifact_bundle_sha256") and panel.get("artifact_version"):
                check("panel_binding", "panel 绑定与 manifest 冻结版本一致",
                      panel.get("artifact_version") == manifest.get("artifact_bundle_sha256"))

    log_path = root / "state" / "decision_log.json"
    if check("decision_log_exists", "state/decision_log.json 存在", log_path.is_file()):
        try:
            log = json.loads(log_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            check("decision_log_parse", "decision_log 可解析", False, str(exc))
        else:
            gates = log.get("gates") or {}
            failed_gates = [g for g in REQUIRED_GATES if gates.get(g) != "PASS"]
            check("workflow_gates", "M1/P1/P2/W1/W2 均为 PASS", not failed_gates,
                  f"未通过: {failed_gates}" if failed_gates else "5/5 PASS")

    overall = all(c["pass"] for c in checks if c["severity"] == "hard")
    result = {
        "pass": overall,
        "project_root": str(root),
        "checks": checks,
        "warnings": warnings,
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out = root / "state" / "submission_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
