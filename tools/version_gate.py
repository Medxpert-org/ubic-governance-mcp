#!/usr/bin/env python3
"""Release gate: one version in every place it is repeated, and immutable action pins.

Two classes of defect this repository has already produced:

1. Version drift. The package version lives in exactly one place
   (`ubic_governance.__version__`, pulled into `pyproject.toml` through
   `dynamic = ["version"]`). `server.json` repeats it, and the icon pointer
   repeats it a third time. If they disagree, a release advertises one version
   and ships another.

2. A workflow that cannot start. GitHub rejected this repository's first
   `version-gate.yml` with `startup_failure` because steps used floating tags
   (`actions/checkout@v4`); every existing workflow here pins a full 40-character
   commit SHA. A new workflow that uses a tag fails before a single step runs, so
   the failure looks like the gate itself is broken.

Exit 0 = consistent. Exit 1 = at least one defect, printed with the file to edit.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
problems = []


def fail(msg):
    problems.append(msg)


# ---------------------------------------------------------------- version drift
init = (ROOT / "ubic_governance" / "__init__.py").read_text(encoding="utf-8")
m = re.search(r'__version__\s*=\s*"([^"]+)"', init)
if not m:
    fail("ubic_governance/__init__.py: no __version__ literal")
    version = None
else:
    version = m.group(1)
    print(f"source version: {version}")

pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
if re.search(r'^version\s*=\s*"', pyproject, re.M):
    fail('pyproject.toml: a literal version= is present; the version is meant to be dynamic = ["version"]')

name_m = re.search(r'^name\s*=\s*"([^"]+)"', pyproject, re.M)
pkg_name = name_m.group(1) if name_m else None
if not pkg_name:
    fail("pyproject.toml: no project name")

if version:
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    if server.get("version") != version:
        fail(f"server.json: version {server.get('version')!r} != {version!r}")
    for p in server.get("packages", []):
        if p.get("identifier") != pkg_name:
            fail(f"server.json: package identifier {p.get('identifier')!r} != {pkg_name!r}")
        if p.get("version") != version:
            fail(f"server.json: package version {p.get('version')!r} != {version!r}")
    for icon in server.get("icons", []):
        src = icon.get("src", "")
        if "@main" in src or "@refs/heads" in src:
            fail(f"server.json: icon {src!r} follows a moving branch; pin it to @v{version}")
        elif f"@v{version}" not in src:
            fail(f"server.json: icon {src!r} is not pinned to @v{version}")
        if not (ROOT / "icon.svg").exists():
            fail("server.json: an icon is advertised but icon.svg is not in the repository")
    print(f"manifest checked: {pkg_name} {version}")

# ------------------------------------------------------------ immutable pins
USES = re.compile(r"\buses:\s*([^#\s]+)")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
wf_dir = ROOT / ".github" / "workflows"
if wf_dir.is_dir():
    pinned = 0
    for wf in sorted(wf_dir.glob("*.yml")):
        for line_no, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), 1):
            hit = USES.search(line)
            if not hit:
                continue
            spec = hit.group(1)
            if spec.startswith("./"):
                continue
            ref = spec.split("@", 1)[1] if "@" in spec else ""
            if not HEX40.match(ref):
                fail(f"{wf.name}:{line_no}: {spec} is not pinned to a 40-character commit SHA "
                     f"(floating tags make the workflow fail with startup_failure)")
            else:
                pinned += 1
    print(f"action pins checked: {pinned} pinned to full SHAs")

if problems:
    print("\nRELEASE GATE: FAIL")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("RELEASE GATE: PASS")
