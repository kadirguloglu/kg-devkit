#!/usr/bin/env python3
"""Stop kancası: kit kaynakları değiştiyse bakım agent'larının çalışmasını ister.

- plugins/kg-devkit/agents/** veya codex/agents/** değiştiyse -> kit-agent-linter
- agent, skill, kural, kanca, betik, workflow, doküman veya README değiştiyse -> kit-doc-sync
- plugin kaynağı, kural, betik veya workflow değiştiyse ve CHANGELOG.md son çalıştırmadan beri değişmediyse -> kit-release-notes

Her agent için ayrı bir özet tutulur (.git/kit-review-gate/state.json). Özet yalnız o agent'ın baktığı klasörlerdeki dosyaların
içeriğinden hesaplanır; dal, origin/main veya commit geçmişine bağlı değildir: commit atmak, dal ilerlemesi veya kanca betiğini
düzenlemek tetiklemez, yalnız ilgili dosyaların içeriği değişince o agent bir kez daha istenir. Özet yoksa (yeni klon) başlangıç
olarak HEAD'deki commit'li içerik kabul edilir; böylece yalnız commit'lenmemiş/izlenmeyen değişiklikler ilk durdurmayı tetikler.
Salt-okuma git komutları dışında bir şey çalıştırmaz; hata olursa sessizce izin verir.
"""
import hashlib, json, os, subprocess

LINT = ("plugins/kg-devkit/agents/", "codex/agents/")
SRC = ("plugins/", "rules/", "scripts/", ".github/workflows/")
DOCS = SRC + ("docs/", ".claude/agents/", "README.md", "CHANGELOG.md")
CHANGELOG = "CHANGELOG.md"


def git(*args, raw=False):
    out = subprocess.run(["git", *args], capture_output=True, check=True).stdout
    return out if raw else out.decode()


def digests(paths, read):
    def one(sel):
        h = hashlib.sha256()
        for f in sorted(p for p in paths if sel(p)):
            h.update(f.encode())
            try:
                h.update(read(f))
            except Exception:
                h.update(b"<yok>")
        return h.hexdigest()[:24]

    return {
        "lint": one(lambda p: p.startswith(LINT)),
        "docs": one(lambda p: p.startswith(DOCS) and p != CHANGELOG),
        "src": one(lambda p: p.startswith(SRC)),
        "changelog": one(lambda p: p == CHANGELOG),
    }


def main():
    try:
        os.chdir(git("rev-parse", "--show-toplevel").strip())
        work = set(git("ls-files").split()) | set(git("ls-files", "--others", "--exclude-standard").split())
        cur = digests(work, lambda f: open(f, "rb").read())

        state_dir = os.path.join(git("rev-parse", "--git-dir").strip(), "kit-review-gate")
        state_file = os.path.join(state_dir, "state.json")
        try:
            old = json.load(open(state_file))
        except Exception:
            head = set(git("ls-tree", "-r", "--name-only", "HEAD").split())
            old = digests(head, lambda f: git("show", "HEAD:" + f, raw=True))

        want = []
        if cur["lint"] != old["lint"]:
            want.append("`kit-agent-linter` (agent dosyaları değişti)")
        if cur["docs"] != old["docs"]:
            want.append("`kit-doc-sync` (README/doküman/prompt kaynakla uyumlu mu)")
        if cur["src"] != old["src"] and cur["changelog"] == old["changelog"]:
            want.append("`kit-release-notes` (kaynak değişti ama CHANGELOG.md güncellenmedi; sürüm notu taslağı ve [minor]/[major] önerisi için)")

        if cur != old or not os.path.exists(state_file):
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
