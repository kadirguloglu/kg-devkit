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

## Codex

Tek kaynak Claude tarafıdır. `codex/` çıktısı üretilir, elle düzenlenmez:

```bash
python3 scripts/build-codex.py           # codex/ yeniden üret (--check: güncel mi)
./scripts/install-codex.sh               # ~/.codex/agents ve ~/.agents/skills altına symlink
./scripts/install-codex.sh --uninstall
```

Codex'te skill'ler `$verify-change` biçiminde çağrılır. Agent'lar `.toml` olarak ~/.codex/agents altından yüklenir.

## İçerik (v0.3.0)

- Agent'lar: `frontend-developer`, `frontend-browser-tester`, `frontend-test-developer`, `backend-developer`,
  `backend-test-developer`, `database-reviewer`, `engineering-software-architect`, `devops-engineer`, `devops-operator`
- Skill'ler: `browser-test`, `verify-change`, `add-migration`, `release`, `rollback`, `live-check`

Taşıma durumu ve açık kararlar: [docs/inventory.md](docs/inventory.md).
