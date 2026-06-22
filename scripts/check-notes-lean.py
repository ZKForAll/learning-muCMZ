#!/usr/bin/env python3
"""Type-check every ```lean code block in the project notes.

Extracts the fenced ```lean blocks from the given markdown files (default
notes/*.md), concatenates them in document order under a Mathlib preamble, and
runs `lake env lean` on the result. Concatenation is intentional, so a later
block may use definitions introduced by an earlier one (literate style).

Usage:
    python3 scripts/check-notes-lean.py [file.md ...]

Exit status is non-zero if any block fails to type-check.
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Preamble prepended before the extracted blocks. Mathlib supplies ZMod, Fact,
# AddCommGroup, Module, etc.; ToMathlib.PFunctor.Free supplies VCVio's `FreeM`;
# the OracleComp modules supply `OracleComp`, `ProbComp`, `evalDist`, `probEvent`.
# Add `import MuCMZ` here once the notes reference project definitions.
PREAMBLE = (
    "import Mathlib\n"
    "import ToMathlib.PFunctor.Free\n"
    "import VCVio.OracleComp.ProbComp\n"
    "import VCVio.OracleComp.EvalDist\n"
)

FENCE = re.compile(r"^```+\s*lean\b", re.IGNORECASE)
FENCE_END = re.compile(r"^```+\s*$")


def extract_blocks(path):
    """Return a list of (start_line, code) for each ```lean block in `path`."""
    blocks = []
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    i = 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            start = i + 1
            body = []
            i += 1
            while i < len(lines) and not FENCE_END.match(lines[i]):
                body.append(lines[i])
                i += 1
            blocks.append((start, "".join(body)))
        i += 1
    return blocks


def main(argv):
    files = argv[1:] or sorted(glob.glob(os.path.join(REPO, "notes", "*.md")))
    if not files:
        print("no markdown files to check")
        return 0

    pieces = [PREAMBLE]
    total = 0
    for path in files:
        rel = os.path.relpath(path, REPO)
        for start, code in extract_blocks(path):
            total += 1
            pieces.append(f"\n-- {rel}:{start}\n{code}")
        print(f"{rel}: {len(extract_blocks(path))} lean block(s)")

    if total == 0:
        print("no ```lean blocks found")
        return 0

    with tempfile.NamedTemporaryFile(
        "w", suffix=".lean", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write("".join(pieces))
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["lake", "env", "lean", tmp_path], cwd=REPO
        )
    finally:
        os.unlink(tmp_path)

    if result.returncode == 0:
        print(f"OK: {total} lean block(s) type-check")
    else:
        print(f"FAIL: type-checking reported errors (exit {result.returncode})")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
