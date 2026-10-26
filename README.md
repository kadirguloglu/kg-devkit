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

## İçerik (v0.1.0)

- agent `frontend-developer`, agent `frontend-browser-tester`, skill `browser-test`

Taşıma durumu ve açık kararlar: [docs/inventory.md](docs/inventory.md).
