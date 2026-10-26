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

## İçerik (v0.2.0)

- Agent'lar: `frontend-developer`, `frontend-browser-tester`, `frontend-test-developer`, `backend-developer`,
  `backend-test-developer`, `database-reviewer`, `engineering-software-architect`, `devops-engineer`, `devops-operator`
- Skill'ler: `browser-test`, `verify-change`, `add-migration`, `release`, `rollback`, `live-check`

Taşıma durumu ve açık kararlar: [docs/inventory.md](docs/inventory.md).
