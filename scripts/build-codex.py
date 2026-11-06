#!/usr/bin/env python3
"""Claude kaynaklarından (plugins/kg-devkit) Codex çıktısını üretir: codex/agents/*.toml ve codex/skills/*.

Tek kaynak Claude tarafıdır; codex/ elle düzenlenmez. Yalnız standart kütüphane (Python 3.11+).
Kullanım: python3 scripts/build-codex.py          # codex/ dizinini yeniden üretir
          python3 scripts/build-codex.py --check  # codex/ güncel değilse çıkış kodu 1
"""
import glob
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "plugins", "kg-devkit")
OUT = os.path.join(ROOT, "codex")
WRITE_TOOLS = {"Edit", "Write", "Bash", "NotebookEdit"}

# Claude'a özgü araç adları geçen paragraflar: (ajan adı, eski metin) -> Codex metni. Eski metin bulunamazsa derleme durur.
AGENT_REPLACEMENTS = {
    "frontend-browser-tester": [
        (
            "- Load the Chrome tools in one `ToolSearch` (`select:` with every tool you need), call\n"
            "  `tabs_context_mcp` first, work in a new tab you create, close it at the end.",
            "- Read the available Chrome browser skill before browser use. Discover available browser\n"
            "  tools using the client's tool discovery mechanism and follow their documentation.\n"
            "  Inspect existing tabs first, work in a new tab you create, close it at the end.\n"
            "  Do not assume Claude-specific ToolSearch or tabs_context_mcp tools are available.",
        ),
        (
            "- Check requests with `read_network_requests` (payload/status of the changed call) and\n"
            "  `read_console_messages` with a pattern for errors; report framework/console errors you trigger.",
            "- Check the changed request payload/status and console errors using available browser\n"
            "  tools when supported; report framework/console errors you trigger and observation limits.",
        ),
        ("Manual browser check in Chrome (Claude in Chrome)", "Manual browser check in Chrome (Codex in Chrome)"),
    ],
}

# Skill gövdesi Codex'te tamamen farklı olanlar (Claude `context: fork` / $ARGUMENTS kullanır).
SKILL_BODY_OVERRIDES = {
    "browser-test": """# Browser test of a change

In the running dev app, use Chrome to test only the frontend changes that were just made.
Scope, environment, data and report rules live in the `frontend-browser-tester` agent definition.
Take the commit range, file or focus note from the user's invocation as the target; do not rely on
`$ARGUMENTS` expansion or Claude fork metadata.
Call the `frontend-browser-tester` role through the available sub-agent tool, passing the target and limits in the task text.
If the sub-agent tool/role is unavailable, read the definition and do the same check in the main session, and report that limitation.

- Empty target: take the working-tree changes; if the tree is clean, use `HEAD~1..HEAD`.
- A commit range (`abc123..HEAD`, `HEAD~3..HEAD`): take the frontend diff of that range.
- A file or a free-text note: narrow the scope to it.

Do not change code or commit/push; report any defect with repro steps.
""",
}

SKILL_NAMES = "verify-change|add-migration|release|rollback|live-check|browser-test"


def split_md(path):
    parts = open(path, encoding="utf-8").read().split("---", 2)
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, parts[2].strip() + "\n"


def codexify(text):
    text = re.sub(r"`?/kg-devkit:(" + SKILL_NAMES + r")`?", r"`$\1`", text)
    text = re.sub(r"(?<![\w/])/(" + SKILL_NAMES + r")\b", r"$\1", text)
    return text


def toml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build():
    files = {}
    for md in sorted(glob.glob(os.path.join(SRC, "agents", "*.md"))):
        name = os.path.basename(md)[:-3]
        meta, body = split_md(md)
        for old, new in AGENT_REPLACEMENTS.get(name, []):
            if old not in body and old not in meta["description"]:
                sys.exit(f"{name}: değiştirilecek metin kaynakta yok:\n{old}")
            body = body.replace(old, new)
            meta["description"] = meta["description"].replace(old, new)
        tools = {t.strip() for t in meta.get("tools", "").split(",") if t.strip()}
        read_only = bool(tools) and not (tools & WRITE_TOOLS)
        if '"""' in body:
            sys.exit(f"{name}: gövde üç çift tırnak içeriyor")
        out = f"name = {toml_str(meta['name'])}\ndescription = {toml_str(meta['description'])}\n"
        if read_only:
            out += 'sandbox_mode = "read-only"\n'
        out += 'developer_instructions = """\n' + codexify(body).rstrip("\n") + '"""\n'
        files[f"agents/{name}.toml"] = out
    for sk in sorted(glob.glob(os.path.join(SRC, "skills", "*", "SKILL.md"))):
        name = sk.split(os.sep)[-2]
        meta, body = split_md(sk)
        body = SKILL_BODY_OVERRIDES.get(name, codexify(body))
        files[f"skills/{name}/SKILL.md"] = (
            f"---\nname: {meta['name']}\ndescription: {meta['description']}\n---\n\n{body.lstrip()}"
        )
        if meta.get("disable-model-invocation") == "true":
            files[f"skills/{name}/agents/openai.yaml"] = "policy:\n  allow_implicit_invocation: false\n"
    return files


def main():
    files = build()
    if "--check" in sys.argv:
        stale = []
        for rel, content in files.items():
            p = os.path.join(OUT, rel)
            if not os.path.exists(p) or open(p, encoding="utf-8").read() != content:
                stale.append(rel)
        existing = {os.path.relpath(p, OUT) for p in glob.glob(os.path.join(OUT, "**", "*"), recursive=True) if os.path.isfile(p)}
        stale += sorted(existing - set(files))
        if stale:
            print("codex/ güncel değil:", *stale, sep="\n - ")
            sys.exit(1)
        print("codex/ güncel.")
        return
    shutil.rmtree(OUT, ignore_errors=True)
    for rel, content in files.items():
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(content)
    print(f"{len(files)} dosya üretildi → codex/")


main()
