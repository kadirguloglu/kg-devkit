#!/usr/bin/env python3
"""Stop kancası: kit kaynakları değiştiyse bakım agent'larının çalışmasını ister.

- plugins/kg-devkit/agents/** veya codex/agents/** değiştiyse -> kit-agent-linter
- agent, skill, kural, kanca, betik, workflow, doküman veya README değiştiyse -> kit-doc-sync
Aynı değişiklik kümesi için yalnız bir kez durdurur (özet .git/kit-review-gate/ altında tutulur), böylece döngü olmaz.
Salt-okuma git komutları dışında bir şey çalıştırmaz; hata olursa sessizce izin verir.
"""
import hashlib, json, os, subprocess, sys

LINT = ("plugins/kg-devkit/agents/", "codex/agents/")
DOCS = ("plugins/", "rules/", "scripts/", ".github/workflows/", "docs/", ".claude/agents/", "README.md", "CHANGELOG.md")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def main():
    try:
        root = git("rev-parse", "--show-toplevel").strip()
        os.chdir(root)
        base = None
        for ref in ("origin/main", "origin/master", "main", "master"):
            try:
                base = git("merge-base", "HEAD", ref).strip()
                break
            except subprocess.CalledProcessError:
                continue
        files = set(git("diff", "--name-only", base or "HEAD~1").split())
        files |= set(git("diff", "--name-only", "HEAD").split())
        files |= set(git("ls-files", "--others", "--exclude-standard").split())
        lint = sorted(f for f in files if f.startswith(LINT))
        docs = sorted(f for f in files if f.startswith(DOCS))
        if not lint and not docs:
            return
        h = hashlib.sha256()
        h.update(git("diff", base or "HEAD~1").encode())
        h.update(git("diff", "HEAD").encode())
        for f in sorted(f for f in files if os.path.isfile(f) and not git("ls-files", f).strip()):
            h.update(f.encode()); h.update(open(f, "rb").read())
        marker_dir = os.path.join(git("rev-parse", "--git-dir").strip(), "kit-review-gate")
        marker = os.path.join(marker_dir, h.hexdigest()[:24])
        if os.path.exists(marker):
            return
        os.makedirs(marker_dir, exist_ok=True)
        open(marker, "w").close()
    except Exception:
        return
    todo = []
    if lint:
        todo.append("`kit-agent-linter` (agent dosyaları değişti: " + ", ".join(lint[:6]) + (" …" if len(lint) > 6 else "") + ")")
    if docs:
        todo.append("`kit-doc-sync` (README/doküman/prompt kaynakla uyumlu mu)")
    reason = ("Kit kaynakları değişti; bitirmeden önce şu bakım agent'larını Agent aracıyla çalıştır ve bulguları raporla/düzelt: "
              + " ve ".join(todo) + ". Hedef olarak bu değişiklik kümesini ver. Zaten çalıştırdıysan sonucu özetleyip bitir.")
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    main()
