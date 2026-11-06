# kg-devkit

Project-agnostic agents, skills and rules for **Claude Code** and **Codex**: developers, test developers, reviewers
(database, tenant security), an architecture advisor, a scope advisor, and release/rollback/live-check/migration skills.
A Claude-only safety hook asks for approval before `kubectl`/`helm`/`terraform` mutations and secret reads.
Nothing project-specific is baked in: each repo describes itself in a `## Project profile` section of its `AGENTS.md`
(see the [template](docs/project-profile-template.md)), and the agents read it first. License: MIT.

Kişisel, projeden bağımsız Claude Code ve Codex agent/skill/kural koleksiyonu (plugin + marketplace). Proje bilgisi
agent'lara gömülmez; her repo `AGENTS.md` içindeki `## Project profile` bölümünü sağlar. Aşağıdaki anlatım Türkçedir.

**Dokümanlar / Docs**
- [Agent gereksinimleri](docs/agent-requirements.md) – her agent'ın okuduğu profil alanları, varsayımları ve profil yokken davranışı (plugin'i incelemeden önce buraya bak / start here when evaluating the plugin).
- [Project profile şablonu](docs/project-profile-template.md) – kendi reponda doldurulacak bölüm.
- [Tasarım kararları ve sınırlar](docs/inventory.md).
- [Gereksinim dokümanını üreten prompt](docs/prompts/generate-agent-requirements.md) – agent eklenince/değişince dokümanı yeniden üretmek için.
- [Project profile üreten prompt](docs/prompts/generate-project-profile.md) – yeni projenin `## Project profile` bölümünü repodan çıkarttırmak için.

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

## İçerik

- **Agent'lar (11):** `frontend-developer`, `frontend-browser-tester`, `frontend-test-developer`, `backend-developer`,
  `backend-test-developer`, `database-reviewer`, `engineering-software-architect`, `devops-engineer`, `devops-operator`,
  `tenant-security-reviewer`, `scope-advisor`. Riskli işler için `devops-operator`, `database-reviewer` ve
  `tenant-security-reviewer` `opus`, diğerleri `sonnet` modelini kullanır. `tenant-security-reviewer` ve `scope-advisor`
  çok kiracılı projeler içindir (tek müşterili projede `scope-advisor` `NOT-APPLICABLE` döner). Ayrıntı: [agent gereksinimleri](docs/agent-requirements.md).
- **Skill'ler** (yalnız açıkça çağrılır): `browser-test`, `verify-change`, `add-migration`, `release`, `rollback`, `live-check`
- **Kurallar** (`rules/`, ilgili dosyalara girilince yüklenir): `kg-test-discipline`, `kg-documentation-maintenance`,
  `kg-ops-safety`. Plugin kural taşımadığı için `~/.claude/rules` altına bağlanır; Codex bunları okumaz.
- **Güvenlik kancası** (yalnız Claude): `hooks/guard-infra.py`, canlı ortamı değiştiren `kubectl`/`oc`/`helm`/`terraform` komutlarını
  ve secret okumayı kullanıcı onayına düşürür (bloklamaz). Plugin ile birlikte gelir; Codex'te yoktur, orada yalnız agent metin kuralları geçerlidir.

## Sürümleme

`main`'e her push'ta GitHub Actions (`bump-version.yml`) `plugins/kg-devkit/.claude-plugin/plugin.json` sürümünü artırır ve
`chore(release): vX.Y.Z` commit'i atar. Varsayılan **patch**; merge/commit mesajına `[minor]` veya `[major]` yazarsan o seviye artar.
Güncel sürüm için `plugin.json`'a bak; README'ye sürüm yazılmaz.

## Geliştirme

Tek kaynak Claude tarafıdır. `codex/` çıktısı üretilir, elle düzenlenmez:

```bash
python3 scripts/build-codex.py           # codex/ yeniden üret (--check: güncel mi)
python3 scripts/test_guard_infra.py      # güvenlik kancası kural testleri
claude plugin validate . && claude plugin validate plugins/kg-devkit
```

Bu repoyu geliştirirken `.claude/agents/` altındaki bakım agent'ları kullanılır: `kit-doc-sync`, `kit-agent-linter`, `kit-release-notes` (plugin'e dahil değildir, kullanıcılara gitmez).

CI (`.github/workflows/check.yml`) Codex çıktısının güncelliğini, kanca testlerini ve manifestleri doğrular.
Tasarım kararları ve bilinen sınırlar: [docs/inventory.md](docs/inventory.md).
