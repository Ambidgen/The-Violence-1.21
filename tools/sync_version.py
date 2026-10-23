#!/usr/bin/env python3
"""Synchronize generated Godot metadata from scripts/version.gd.

The GDScript constant is the canonical version. This small standard-library
script intentionally updates only the two metadata files that Godot cannot
populate from a script constant.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "scripts/version.gd").read_text()
match = re.search(r'^const\s+VALUE\s*:=\s*"([^"]+)"', source, re.MULTILINE)
if not match:
    raise SystemExit("scripts/version.gd has no const VALUE")
version = match.group(1)
windows = version + ".0"
changes = {
    "project.godot": [(r'config/version="[^"]+"', f'config/version="{version}"')],
    "export_presets.cfg": [
        (r'application/file_version="[^"]+"', f'application/file_version="{windows}"'),
        (r'application/product_version="[^"]+"', f'application/product_version="{windows}"'),
    ],
}
for name, replacements in changes.items():
    path = ROOT / name
    text = path.read_text()
    for pattern, replacement in replacements:
        text, count = re.subn(pattern, replacement, text)
        if count != 1:
            raise SystemExit(f"expected one {pattern} in {name}, found {count}")
    path.write_text(text)
    print(f"{name}: {version} (Windows {windows})")
