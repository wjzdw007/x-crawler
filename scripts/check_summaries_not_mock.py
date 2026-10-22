#!/usr/bin/env python3
"""Fail if summary files contain known mock/placeholder markers.

Used by Daily Summary CI after generation. Checks staged files by default
so historical mock files already on main do not keep the job red forever.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from summarizer import is_mock_summary


def _git_staged_summaries() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", "crawler_data/user_summaries/"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line.endswith((".md", ".json"))]


def _all_summaries() -> list[Path]:
    root = Path("crawler_data/user_summaries")
    if not root.is_dir():
        return []
    return sorted(list(root.glob("*.md")) + list(root.glob("*.json")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Reject mock/placeholder user summaries")
    parser.add_argument("--staged", action="store_true", help="Only check git-staged summary files")
    parser.add_argument("paths", nargs="*", help="Specific files to check")
    args = parser.parse_args()

    if args.paths:
        files = [Path(p) for p in args.paths]
    elif args.staged:
        files = _git_staged_summaries()
    else:
        files = _all_summaries()

    bad = []
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if is_mock_summary(text):
            bad.append(path)

    if bad:
        print("ERROR: mock/placeholder summaries detected (will not commit):")
        for path in bad:
            print(f"  - {path}")
        print("Markers: 模拟内容 / 配置LLM API密钥后")
        return 1

    print(f"OK: {len(files)} summary file(s) have no mock markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
