"""Fast pre-submission verifier for the MICAI package.

Runs the checks that should be green before sharing the paper bundle:
  1. backend unit tests,
  2. paper-number firewall,
  3. PDF page counts,
  4. anonymous ZIP identity-token scan.

This intentionally does not regenerate heavy 30-seed experiments.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import _bootstrap


ROOT = Path(_bootstrap._find_backend()).parent
BACKEND = ROOT / "backend"
MICAI = ROOT / "MICAI"
RESULTS = Path(_bootstrap.results_dir())
IDENTITY_PATTERNS = [
    r"Yazm",
    r"Javier",
    r"Ra[uú]l",
    r"UACJ",
    r"Universidad",
    r"rebull",
    r"outlook",
    r"MIAAD",
    r"/Users/",
    r"haowei",
]


def run(cmd: list[str], cwd: Path = ROOT) -> dict:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-3000:],
        "ok": proc.returncode == 0,
    }


def pdf_pages(pdf: Path) -> int | None:
    proc = subprocess.run(["pdfinfo", str(pdf)], text=True, capture_output=True)
    if proc.returncode != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def scan_zip(zip_path: Path) -> dict:
    hits: list[dict] = []
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            data = zf.read(name)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for pat in IDENTITY_PATTERNS:
                if re.search(pat, text, flags=re.IGNORECASE):
                    hits.append({"file": name, "pattern": pat})
    return {"zip": str(zip_path), "hits": hits, "ok": not hits}


def main() -> None:
    checks: dict[str, object] = {}
    py = str(BACKEND / ".venv" / "bin" / "python")
    if not Path(py).exists():
        py = sys.executable

    checks["pytest"] = run([py, "-m", "pytest", "tests"], cwd=BACKEND)
    checks["firewall"] = run([
        py, "repro/verify_paper.py",
        "--tex", str(MICAI),
        "--results", str(RESULTS),
    ], cwd=BACKEND)
    checks["pages"] = {
        "main_submission.pdf": pdf_pages(MICAI / "main_submission.pdf"),
        "main_reducida_submission.pdf": pdf_pages(MICAI / "main_reducida_submission.pdf"),
    }
    checks["anonymous_zip_scan"] = [
        scan_zip(MICAI / "VisaPredictAI_MICAI_anonymous.zip"),
        scan_zip(MICAI / "VisaPredictAI_MICAI_reducida_anonymous.zip"),
    ]

    ok = (
        checks["pytest"]["ok"]
        and checks["firewall"]["ok"]
        and all(item["ok"] for item in checks["anonymous_zip_scan"])
    )
    checks["overall_ok"] = ok
    out = RESULTS / "reproduce_fast.json"
    out.write_text(json.dumps(checks, indent=2))
    print(json.dumps({
        "overall_ok": ok,
        "pytest": checks["pytest"]["returncode"],
        "firewall": checks["firewall"]["returncode"],
        "pages": checks["pages"],
        "anonymous_zip_hits": sum(len(item["hits"]) for item in checks["anonymous_zip_scan"]),
        "output": str(out),
    }, indent=2))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
