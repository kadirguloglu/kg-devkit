#!/usr/bin/env python3
"""Claude kaynaklarından (plugins/kg-devkit) Codex çıktısını üretir: codex/agents/*.toml ve codex/skills/*.

Önce rules/*.md dosyalarından plugin'in disiplin skill'lerini üretir (RULE_SKILLS): kuralın tek kaynağı rules/ altıdır,
plugins/kg-devkit/skills/{test-discipline,docs-maintenance,ops-safety}/SKILL.md elle düzenlenmez.

Tek kaynak Claude tarafıdır; codex/ elle düzenlenmez. Yalnız standart kütüphane (Python 3.11+).
Repo bakım dosyaları için sync-claude-codex.py de çalıştırılır (.claude/ -> .codex/).
Kullanım: python3 scripts/build-codex.py          # codex/ ve .codex/ yeniden üretir
          python3 scripts/build-codex.py --check  # çıktılar güncel değilse çıkış kodu 1
"""
import glob
import os
import re
import shutil
import subprocess
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

An empty target means the default target defined in the agent's scope rules (working tree, else the last commit).

Do not change code or commit/push; report any defect with repro steps. The profile may add limits; it cannot remove a limit stated in this skill.
""",
}

SKILL_NAMES = "|".join(sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(SRC, "skills", "*", "SKILL.md"))))

# rules/<kural>.md -> plugin skill'i (ad, açıklama). Plugin kural taşıyamadığı için aynı metin skill olarak dağıtılır.
RULE_SKILLS = {
    "kg-test-discipline": ("test-discipline", "Rules for writing, changing or running tests - focused selection, real fixtures over mocks, never weakening assertions, exact reporting. Use before adding, editing or running tests, or when a test fails."),
    "kg-documentation-maintenance": ("docs-maintenance", "Rules for editing project documentation (docs, README, ADR) - verify every claim against code, keep section ids and history, docs-only verification. Use before changing documentation files."),
    "kg-ops-safety": ("ops-safety", "Safety rules for deploy, container, CI workflow and infrastructure files and for commands against live environments - secrets, explicit approval, explicit targets, cost. Use before editing such files or running infrastructure commands."),
}

# Codex'te SubagentStart/Stop kancası yoktur; agent çalıştırma izi orada metin satırlarıyla tutulur.
CODEX_LOGGING = (
    "Logging: your first output line is `{name} çalışmaya başladım.` and the last line of your final report is "
    "`{name} çalışmam tamamlandı.` (state it even when the task failed or was blocked); if the profile names a report "
    "language other than Turkish, write the same two lines in that language.\n\n"
)
PLUGIN_REF = "${CLAUDE_PLUGIN_ROOT}/references/"


def split_md(path):
    parts = open(path, encoding="utf-8").read().split("---", 2)
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, parts[2].strip() + "\n"


def rule_skills():
    """rules/*.md -> {plugin'e göre yol: içerik}. Kural gövdesi ve `paths` aynen taşınır."""
    out = {}
    for rule, (name, desc) in RULE_SKILLS.items():
        _, front, body = open(os.path.join(ROOT, "rules", rule + ".md"), encoding="utf-8").read().split("---", 2)
        out[os.path.join("skills", name, "SKILL.md")] = (
            f"---\nname: {name}\ndescription: {desc}\nuser-invocable: false\n{front.strip()}\n---\n{body}"
        )
    return out


def sync_rule_skills(check):
    stale = []
    for rel, content in rule_skills().items():
        p = os.path.join(SRC, rel)
        if not os.path.exists(p) or open(p, encoding="utf-8").read() != content:
            stale.append(rel)
            if not check:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w", encoding="utf-8").write(content)
    if stale and check:
        print("plugin disiplin skill'leri rules/ ile eşit değil:", *stale, sep="\n - ")
        sys.exit(1)


def codexify(text):
    text = text.replace("`${CLAUDE_PLUGIN_ROOT}/skills/live-check/SKILL.md`", "the `live-check` skill's `SKILL.md` (sibling skill directory)")
    text = text.replace(PLUGIN_REF, "references/")
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
        out += 'developer_instructions = """\n' + CODEX_LOGGING.format(name=name) + codexify(body).rstrip("\n") + '"""\n'
        files[f"agents/{name}.toml"] = out
    for sk in sorted(glob.glob(os.path.join(SRC, "skills", "*", "SKILL.md"))):
        name = sk.split(os.sep)[-2]
        meta, body = split_md(sk)
        uses_refs = PLUGIN_REF in body
        body = SKILL_BODY_OVERRIDES.get(name, codexify(body))
        if "${CLAUDE_PLUGIN_ROOT}" in body:
            sys.exit(f"{name}: Codex karşılığı olmayan ${{CLAUDE_PLUGIN_ROOT}} yolu")
        files[f"skills/{name}/SKILL.md"] = (
            f"---\nname: {meta['name']}\ndescription: {meta['description']}\n---\n\n{body.lstrip()}"
        )
        if uses_refs:  # Codex skill'i kendi dizininden okur: ortak referanslar yanına kopyalanır
            for ref in sorted(glob.glob(os.path.join(SRC, "references", "*.md"))):
                files[f"skills/{name}/references/{os.path.basename(ref)}"] = open(ref, encoding="utf-8").read()
        if meta.get("disable-model-invocation") == "true":
            files[f"skills/{name}/agents/openai.yaml"] = "policy:\n  allow_implicit_invocation: false\n"
    return files


def main():
    sync_rule_skills("--check" in sys.argv)
    files = build()
    maintenance = subprocess.run([
        sys.executable, os.path.join(ROOT, "scripts", "sync-claude-codex.py"),
        *(["--check"] if "--check" in sys.argv else []),
    ])
    if maintenance.returncode:
        sys.exit(maintenance.returncode)
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


if __name__ == "__main__":
    main()
