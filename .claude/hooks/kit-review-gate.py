#!/usr/bin/env python3
"""Stop kancası: kit kaynakları değiştiyse bakım agent'larının çalışmasını ister.

- plugins/kg-devkit/agents/** veya codex/agents/** değiştiyse -> kit-agent-linter
- agent, skill, kural, kanca, betik, workflow, doküman veya README değiştiyse -> kit-doc-sync
- plugin kaynağı, kural, betik veya workflow değiştiyse ve CHANGELOG.md son çalıştırmadan beri değişmediyse -> kit-release-notes

Her agent için ayrı bir özet tutulur (.git/kit-review-gate/state.json). Özet yalnız o agent'ın baktığı dosyaların içeriğinden
hesaplanır: commit atmak veya kanca betiğini düzenlemek hiçbir şeyi yeniden tetiklemez, yalnız ilgili dosyaların içeriği değişince
o agent bir kez daha istenir. Salt-okuma git komutları dışında bir şey çalıştırmaz; hata olursa sessizce izin verir.
"""
import hashlib, json, os, subprocess

LINT = ("plugins/kg-devkit/agents/", "codex/agents/")
SRC = ("plugins/", "rules/", "scripts/", ".github/workflows/")
DOCS = SRC + ("docs/", ".claude/agents/", "README.md", "CHANGELOG.md")
CHANGELOG = "CHANGELOG.md"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def digest(paths):
    h = hashlib.sha256()
    for f in sorted(paths):
        h.update(f.encode())
        try:
            h.update(open(f, "rb").read())
        except OSError:
            h.update(b"<silindi>")
    return h.hexdigest()[:24]


def main():
    try:
        os.chdir(git("rev-parse", "--show-toplevel").strip())
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
        lint = [f for f in files if f.startswith(LINT)]
        docs = [f for f in files if f.startswith(DOCS) and f != CHANGELOG]
        src = [f for f in files if f.startswith(SRC)]
        changelog = digest([CHANGELOG]) if os.path.exists(CHANGELOG) else ""
        cur = {"lint": digest(lint), "docs": digest(docs), "src": digest(src), "changelog": changelog}

        state_dir = os.path.join(git("rev-parse", "--git-dir").strip(), "kit-review-gate")
        state_file = os.path.join(state_dir, "state.json")
        try:
            old = json.load(open(state_file))
        except Exception:
            old = {}

        want = []
        if lint and cur["lint"] != old.get("lint"):
            want.append("`kit-agent-linter` (agent dosyaları değişti: " + ", ".join(sorted(lint)[:6]) + (" …" if len(lint) > 6 else "") + ")")
        if docs and cur["docs"] != old.get("docs"):
            want.append("`kit-doc-sync` (README/doküman/prompt kaynakla uyumlu mu)")
        if src and cur["src"] != old.get("src"):
            # CHANGELOG ilk çalıştırmada dal farkına, sonraki çalıştırmalarda son özete göre güncel sayılır
            touched = (CHANGELOG in files) if "changelog" not in old else (cur["changelog"] != old["changelog"])
            if not touched:
                want.append("`kit-release-notes` (kaynak değişti ama CHANGELOG.md güncellenmedi; sürüm notu taslağı ve [minor]/[major] önerisi için)")

        if cur != old:
            os.makedirs(state_dir, exist_ok=True)
            json.dump(cur, open(state_file, "w"))
        if not want:
            return
    except Exception:
        return
    reason = ("Kit kaynakları değişti; bitirmeden önce şu bakım agent'larını Agent aracıyla çalıştır ve bulguları raporla/düzelt: "
              + " ve ".join(want) + ". Hedef olarak bu değişiklik kümesini ver. Zaten çalıştırdıysan sonucu özetleyip bitir.")
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    main()
