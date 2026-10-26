# kg-devkit

Project-agnostic agents, skills and rules for **Claude Code** and **Codex**: developers, test developers, reviewers
(database, tenant security), an architecture advisor, a scope advisor, and release/rollback/live-check/migration skills.
Nothing project-specific is baked in: each repo describes itself in a `## Project profile` section of its `AGENTS.md`
(see the [template](docs/project-profile-template.md)), and the agents read it first. License: MIT.

Kişisel, projeden bağımsız Claude Code ve Codex agent/skill/kural koleksiyonu (plugin + marketplace). Proje bilgisi
agent'lara gömülmez; her repo `AGENTS.md` içindeki `## Project profile` bölümünü sağlar. Aşağıdaki anlatım Türkçedir.

> **Güvenlik notu:** Agent'lar çalıştıkları reponun `AGENTS.md` dosyasını okur ve oradaki talimatlara uyar. Güvenmediğin
> bir repoda kit'i kullanma; `release`, `rollback` ve `devops-operator` canlı sistemi etkileyebilir (hepsi açık onay ister).

## Kurulum

```bash
claude plugin marketplace add kadirguloglu/kg-devkit
claude plugin install kg-devkit@kg-devkit
```

Codex agent/skill'leri ve genel kurallar için repoyu klonla (isteğe bağlı):

```bash
git clone https://github.com/kadirguloglu/kg-devkit ~/kg-devkit && cd ~/kg-devkit
./scripts/install-codex.sh          # ~/.codex/agents ve ~/.agents/skills altına symlink
./scripts/install-claude-rules.sh   # ~/.claude/rules altına symlink
```

Skill'ler `/kg-devkit:<ad>`, agent'lar `kg-devkit:<ad>` olarak görünür (Codex'te skill: `$<ad>`). Aynı adlı proje
agent'ı/skill'i plugin'i ezer. Betikler yalnız sembolik bağ kurar, var olan dosyaya dokunmaz; `--uninstall` ile kaldırılır.

## İçerik (v0.4.0)

- **Agent'lar:** `frontend-developer`, `frontend-browser-tester`, `frontend-test-developer`, `backend-developer`,
  `backend-test-developer`, `database-reviewer`, `engineering-software-architect`, `devops-engineer`, `devops-operator`,
  `tenant-security-reviewer`, `scope-advisor`
- **Skill'ler** (yalnız açıkça çağrılır): `browser-test`, `verify-change`, `add-migration`, `release`, `rollback`, `live-check`
- **Kurallar** (`rules/`, ilgili dosyalara girilince yüklenir): `kg-test-discipline`, `kg-documentation-maintenance`,
  `kg-ops-safety`. Plugin kural taşımadığı için `~/.claude/rules` altına bağlanır; Codex bunları okumaz.

## Geliştirme

Tek kaynak Claude tarafıdır. `codex/` çıktısı üretilir, elle düzenlenmez:

```bash
python3 scripts/build-codex.py           # codex/ yeniden üret (--check: güncel mi)
claude plugin validate . && claude plugin validate plugins/kg-devkit
```

CI (`.github/workflows/check.yml`) Codex çıktısının güncelliğini ve manifestleri doğrular.
Tasarım kararları ve bilinen sınırlar: [docs/inventory.md](docs/inventory.md).
