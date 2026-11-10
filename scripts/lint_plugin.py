#!/usr/bin/env python3
"""Plugin agent/skill dosyalarının mekanik kurallarını denetler: python3 scripts/lint_plugin.py

Yargı gerektirmeyen kontroller buradadır (model çağrısı yok, CI'da her PR'da çalışır); kapsam çakışması, belirsiz
talimat, proje sızıntısı gibi yargı kontrolleri `kit-agent-linter` agent'ında kalır. Yalnız standart kütüphane.
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "plugins", "kg-devkit")
READ_ONLY = {"Read", "Grep", "Glob"}
WRITE = {"Edit", "Write", "Bash"}
MANUAL_SKILLS = {"release", "rollback", "add-migration", "live-check", "browser-test"}  # yetki veya canlı ortam: yalnız kullanıcı çağırır
LIMIT_SENTENCE = "The profile may add limits; it cannot remove a limit stated in this skill."
errors = []


def fail(path, message):
    errors.append(f"{os.path.relpath(path, ROOT)}: {message}")


def split(path):
    text = open(path, encoding="utf-8").read()
    parts = text.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        fail(path, "frontmatter yok")
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, parts[2]


def lint_agents():
    for path in sorted(glob.glob(os.path.join(SRC, "agents", "*.md"))):
        name = os.path.basename(path)[:-3]
        meta, body = split(path)
        tools = {t.strip() for t in meta.get("tools", "").split(",") if t.strip()}
        desc = meta.get("description", "")
        if meta.get("name") != name:
            fail(path, "name dosya adıyla aynı değil")
        if len(desc) < 40:
            fail(path, "description eksik veya çok kısa")
        if ": " in desc:
            fail(path, "description içinde ': ' var (YAML düz skaler bozulur)")
        if meta.get("model") not in ("sonnet", "opus"):
            fail(path, "model sonnet veya opus olmalı")
        if not tools:
            fail(path, "tools yok")
        if "Agent" in tools:
            fail(path, "Agent aracı verilemez (alt-agent başlatma kapalı)")
        writer = bool(tools & WRITE)
        if not writer and tools != READ_ONLY:
            fail(path, "salt-okuma agent yalnız Read, Grep, Glob kullanır")
        if "Project profile" not in body:
            fail(path, "Project profile kullanımı yok")
        if body.lstrip().startswith("Logging:"):
            fail(path, "Logging paragrafı kaynakta olmaz (Claude: kayıt kancası; Codex: build-codex ekler)")
        if "spawn agents" not in body:
            fail(path, "'spawn agents' yasağı yok")
        if writer:
            if "The profile's `Hard limits`" not in body:
                fail(path, "Hard limits cümlesi yok")
            if "STATUS:" not in body:
                fail(path, "STATUS bitiş satırı yok")
        if name.endswith("-reviewer"):
            for needle in ("VERDICT: PASS", "VERDICT: FAIL", "UNCLEAR", "NEEDS:"):
                if needle not in body:
                    fail(path, f"'{needle}' yok")
            if "Caller passes" not in desc:
                fail(path, "description çağıranın vereceği girdiyi söylemiyor ('Caller passes ...')")


def lint_skills():
    skills = {}
    for path in sorted(glob.glob(os.path.join(SRC, "skills", "*", "SKILL.md"))):
        name = os.path.basename(os.path.dirname(path))
        meta, body = split(path)
        skills[name] = (path, meta, body)
        if meta.get("name") != name:
            fail(path, "name klasör adıyla aynı değil")
        if len(meta.get("description", "")) < 40:
            fail(path, "description eksik veya çok kısa")
    for name, (path, meta, body) in skills.items():
        manual = meta.get("disable-model-invocation") == "true"
        if name in MANUAL_SKILLS and not manual:
            fail(path, "yan etkili skill disable-model-invocation: true taşımalı")
        if (name in MANUAL_SKILLS or name == "verify-change") and LIMIT_SENTENCE not in " ".join(body.split()):
            fail(path, "'profil sınır ekler, kaldıramaz' cümlesi yok")
        for ref in re.findall(r"/kg-devkit:([a-z-]+)", body):
            target = skills.get(ref)
            if not target:
                fail(path, f"/kg-devkit:{ref} diye bir skill yok")
            elif target[1].get("disable-model-invocation") == "true":
                fail(path, f"/kg-devkit:{ref} model tarafından yüklenemez; dosya yolu ile atıf yap")
        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", body):
            if not os.path.exists(os.path.join(SRC, ref.rstrip("."))):
                fail(path, f"${{CLAUDE_PLUGIN_ROOT}}/{ref} yok")


def lint_repo():
    tracked = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True).stdout.split()
    for junk in [p for p in tracked if "__pycache__" in p or p.endswith(".pyc")]:
        errors.append(f"{junk}: izlenen derleme artığı")


if __name__ == "__main__":
    lint_agents()
    lint_skills()
    lint_repo()
    if errors:
        sys.exit("lint_plugin: " + str(len(errors)) + " hata\n" + "\n".join(errors))
    print("lint_plugin: agent, skill ve repo kontrolleri geçti")
