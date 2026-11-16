#!/usr/bin/env python3
"""Version gate: one version, in the places that can disagree.

The package version lives in exactly one place (`ubic_governance.__version__`,
pulled into `pyproject.toml` through `dynamic = ["version"]`). Everything else
that repeats it — `server.json` and its package pointer, the icon CDN pin — must
agree with that single source, or CI fails here instead of surfacing as a
half-advertised release later.

Exit 0 = consistent. Exit 1 = at least one disagreement, printed with the file
that needs editing.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
problems = []


def fail(msg):
    problems.append(msg)


# 1. the single source of truth
init = (ROOT / "ubic_governance" / "__init__.py").read_text(encoding="utf-8")
m = re.search(r'__version__\s*=\s*"([^"]+)"', init)
if not m:
    fail("ubic_governance/__init__.py: no __version__ literal")
    version = None
else:
    version = m.group(1)
    print(f"source version: {version}")

# 2. pyproject must derive its version from that source, not carry a second literal
pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
if re.search(r'^version\s*=\s*"', pyproject, re.M):
    fail('pyproject.toml: a literal version= is present; the version is meant to be dynamic = ["version"]')

name_m = re.search(r'^name\s*=\s*"([^"]+)"', pyproject, re.M)
pkg_name = name_m.group(1) if name_m else None
if not pkg_name:
    fail("pyproject.toml: no project name")

# 3. server.json and its package pointer
if version:
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    if server.get("version") != version:
        fail(f"server.json: version {server.get('version')!r} != {version!r}")
    for p in server.get("packages", []):
        if p.get("identifier") != pkg_name:
            fail(f"server.json: package identifier {p.get('identifier')!r} != {pkg_name!r}")
        if p.get("version") != version:
            fail(f"server.json: package version {p.get('version')!r} != {version!r}")
    # 4. the icon must point at the release tag, never at a moving branch
    for icon in server.get("icons", []):
        src = icon.get("src", "")
        if "@main" in src or "@refs/heads" in src:
            fail(f"server.json: icon {src!r} follows a moving branch; pin it to @v{version}")
        elif f"@v{version}" not in src:
            fail(f"server.json: icon {src!r} is not pinned to @v{version}")
        if not (ROOT / "icon.svg").exists():
            fail("server.json: an icon is advertised but icon.svg is not in the repository")
    print(f"manifest checked: {pkg_name} {version}")

if problems:
    print("\nVERSION GATE: FAIL")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("VERSION GATE: PASS")
