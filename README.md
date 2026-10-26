# kg-devkit

Kişisel, projeden bağımsız Claude Code agent ve skill koleksiyonu (plugin + marketplace).
Proje bilgisi agent'lara gömülmez; her repo `AGENTS.md` içindeki `## Project profile` bölümünü sağlar
([şablon](docs/project-profile-template.md)).

## Kurulum

```bash
claude plugin marketplace add ~/Documents/GitHub/kg-devkit
claude plugin install kg-devkit@kg-devkit
```

Skill'ler `/kg-devkit:<ad>`, agent'lar `kg-devkit:<ad>` olarak görünür. Aynı adlı proje agent'ı/skill'i
plugin'i ezer; projeye özel sürüm gerektiğinde yerel dosya yeterlidir.

## Kurallar (rules)

Plugin kural taşımaz; `rules/` altındaki genel kurallar kullanıcı düzeyine bağlanır ve ilgili `paths` dosyalarına
girildiğinde yüklenir (projenin kendi kurallarıyla birlikte, onların önceliği vardır):

```bash
./scripts/install-claude-rules.sh            # ~/.claude/rules altına symlink
./scripts/install-claude-rules.sh --uninstall
```

- `kg-test-discipline` (test dosyaları), `kg-documentation-maintenance` (`docs/**`, README, ADR), `kg-ops-safety` (deploy, k8s, Dockerfile, CI).
- Codex `~/.claude/rules` okumaz; Codex'te bu ilkeler agent/skill gövdelerindedir.

## Codex

Tek kaynak Claude tarafıdır. `codex/` çıktısı üretilir, elle düzenlenmez:

```bash
python3 scripts/build-codex.py           # codex/ yeniden üret (--check: güncel mi)
./scripts/install-codex.sh               # ~/.codex/agents ve ~/.agents/skills altına symlink
./scripts/install-codex.sh --uninstall
```

Codex'te skill'ler `$verify-change` biçiminde çağrılır. Agent'lar `.toml` olarak ~/.codex/agents altından yüklenir.

## İçerik (v0.4.0)

- Agent'lar: `frontend-developer`, `frontend-browser-tester`, `frontend-test-developer`, `backend-developer`,
  `backend-test-developer`, `database-reviewer`, `engineering-software-architect`, `devops-engineer`, `devops-operator`,
  `tenant-security-reviewer`, `scope-advisor`
- Skill'ler: `browser-test`, `verify-change`, `add-migration`, `release`, `rollback`, `live-check`

CI: `.github/workflows/check.yml` Codex çıktısının güncelliğini ve manifestleri doğrular.

Taşıma durumu ve açık kararlar: [docs/inventory.md](docs/inventory.md).
