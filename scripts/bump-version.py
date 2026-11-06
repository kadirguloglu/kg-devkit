#!/usr/bin/env python3
"""plugins/kg-devkit/.claude-plugin/plugin.json içindeki sürümü artırır (semver).

Kullanım: python3 scripts/bump-version.py [patch|minor|major]   # varsayılan: patch
          python3 scripts/bump-version.py --from-message "<commit mesajı>"
            mesajda [major] -> major, [minor] -> minor, aksi halde patch
Yeni sürümü stdout'a yazar. Yalnız standart kütüphane.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "kg-devkit", ".claude-plugin", "plugin.json")


def level_from_message(msg: str) -> str:
    low = msg.lower()
    if "[major]" in low:
        return "major"
    if "[minor]" in low:
        return "minor"
    return "patch"


def bump(version: str, level: str) -> str:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        sys.exit(f"Geçersiz sürüm: {version!r} (X.Y.Z bekleniyor)")
    major, minor, patch = map(int, m.groups())
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main(argv):
    if len(argv) == 3 and argv[1] == "--from-message":
        level = level_from_message(argv[2])
    elif len(argv) <= 2 and (argv[1:] or ["patch"])[0] in ("patch", "minor", "major"):
        level = (argv[1:] or ["patch"])[0]
    else:
        sys.exit(__doc__)
    with open(PLUGIN, encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = bump(data["version"], level)
    with open(PLUGIN, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(data["version"])


if __name__ == "__main__":
    main(sys.argv)
