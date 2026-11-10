# 01 — Proje envanteri

> **Durum notu:** Bu rapor `6b14d73` (v0.8.9) commit'indeki durumu anlatır; dosya yolu ve satır numaraları o commit'e
> göredir, bağlantılar dosyaların güncel hâline gider. Bulguların uygulama durumu ve canlı deney sonuçları:
> [13-implementation-status.md](13-implementation-status.md).

İncelenen commit: `6b14d73` (`chore(release): v0.8.9`), dal `claude/tender-ride-sdje5l`. Tüm plugin dosyaları
(22 dosya, 74.357 bayt) ve aşağıda listelenen ilişkili dosyalar satır satır okundu.

## 1. Gerçek dosya ağacı

```
kg-devkit/
├── .claude-plugin/marketplace.json          marketplace tanımı (1 plugin, source ./plugins/kg-devkit)
├── plugins/kg-devkit/
│   ├── .claude-plugin/plugin.json           name, version 0.8.9, description, author
│   ├── agents/            15 × .md          (50.068 bayt)
│   ├── skills/            6 × SKILL.md      (20.711 bayt; referans/yardımcı dosya YOK)
│   └── hooks/
│       ├── hooks.json                       PreToolUse / matcher "Bash"
│       └── guard-infra.py                   55 satır, yalnız stdlib
├── rules/                 3 × .md           plugin DIŞINDA; ~/.claude/rules'a symlink ile kurulur
├── codex/                 üretilen çıktı    (15 agent .toml, 6 skill + openai.yaml)
├── .claude/               repo bakım araçları (4 kit-* agent, Stop kancası) — plugin'e girmez
├── .codex/                .claude'un üretilen karşılığı
├── scripts/               build-codex.py, sync-claude-codex.py, bump-version.py, 2 kurulum betiği, 2 test
├── docs/                  agent-requirements, inventory, project-profile-template, prompts/ (2)
└── .github/               check.yml, bump-version.yml, CODEOWNERS
```

**Bulunmayanlar (varsayılmadı, doğrulandı):** `plugins/kg-devkit/commands/` yok; plugin içinde `settings.json`,
`.mcp.json`, `bin/`, `monitors/`, `evals/` yok; repo kökünde `CLAUDE.md` ve `AGENTS.md` yok (kit kendi
`Project profile`'ını taşımıyor; bakım bilgisi `.claude/agents/kit-*.md` ve README içinde).

## 2. Sayılar

| Tür | Adet | Not |
| --- | --- | --- |
| Agent (plugin) | 15 | 5 `opus`, 10 `sonnet`; 8 salt-okuma, 6 yazar, 1 tarayıcı testçisi |
| Skill (plugin) | 6 | hepsi `disable-model-invocation: true` |
| Hook olayı / betik | 1 / 1 | `PreToolUse(Bash)` → `guard-infra.py` |
| Command | 0 | (resmi dokümana göre komutlar skill'lerle birleşti; eksiklik değil) |
| Yapılandırma | 3 | `plugin.json`, `hooks.json`, `marketplace.json` |
| Kural (plugin dışı) | 3 | `kg-test-discipline`, `kg-documentation-maintenance`, `kg-ops-safety` |
| Bakım agent'ı / kancası (plugin dışı) | 4 / 1 | yalnız bu repoda |

## 3. Agent envanteri

Boyut ve token sütunları ölçümdür: bayt `wc -c`, token `claude --plugin-dir plugins/kg-devkit plugin details kg-devkit`
(Claude Code 2.1.322) çıktısındaki *tahmini* değerlerdir.

| Agent | Model | Araçlar | Bayt | Sürekli tok. | Çağrı tok. | Okuduğu profil alanları | Atıf yaptığı agent |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| [scope-advisor](../../plugins/kg-devkit/agents/scope-advisor.md) | sonnet | Read, Grep, Glob | 4.085 | ~100 | ~1,2k | Scope mechanisms | — |
| [engineering-software-architect](../../plugins/kg-devkit/agents/engineering-software-architect.md) | sonnet | Read, Grep, Glob | 2.288 | ~70 | ~650 | Layers, Conventions, Finish gate | — |
| [backend-developer](../../plugins/kg-devkit/agents/backend-developer.md) | sonnet | Read, Edit, Write, Bash, Grep, Glob | 2.654 | ~50 | ~780 | Layers, Commands, Conventions, Persistence, Hard limits | — |
| [backend-test-developer](../../plugins/kg-devkit/agents/backend-test-developer.md) | sonnet | aynı (yazar) | 2.286 | ~70 | ~640 | test dizini, Commands, Hard limits | — |
| [frontend-developer](../../plugins/kg-devkit/agents/frontend-developer.md) | sonnet | aynı (yazar) | 2.389 | ~50 | ~700 | Layers, Commands, Rule docs, Hard limits | — |
| [frontend-test-developer](../../plugins/kg-devkit/agents/frontend-test-developer.md) | sonnet | aynı (yazar) | 2.180 | ~50 | ~630 | Commands, Rule docs, Hard limits | — |
| [frontend-browser-tester](../../plugins/kg-devkit/agents/frontend-browser-tester.md) | sonnet | Read, Grep, Glob, Bash, ToolSearch + 16 `mcp__claude-in-chrome__*` | 5.141 | ~70 | ~1,4k | Dev app, Router, Commands, Hard limits | — |
| [api-contract-reviewer](../../plugins/kg-devkit/agents/api-contract-reviewer.md) | opus | Read, Grep, Glob | 3.432 | ~90 | ~1k | API contract, Layers, Conventions | tenant-security, database |
| [database-reviewer](../../plugins/kg-devkit/agents/database-reviewer.md) | opus | Read, Grep, Glob | 3.676 | ~50 | ~1,1k | Persistence, Conventions | (güvenlik reviewer'ı, adsız) |
| [dependency-supply-chain-reviewer](../../plugins/kg-devkit/agents/dependency-supply-chain-reviewer.md) | opus | Read, Grep, Glob | 3.575 | ~80 | ~1,1k | Dependencies, Hard limits | devops-engineer, tenant-security |
| [tenant-security-reviewer](../../plugins/kg-devkit/agents/tenant-security-reviewer.md) | opus | Read, Grep, Glob | 3.457 | ~60 | ~1,1k | Security review, Persistence | database |
| [performance-reviewer](../../plugins/kg-devkit/agents/performance-reviewer.md) | sonnet | Read, Grep, Glob | 3.355 | ~80 | ~980 | Performance, Commands | database |
| [observability-reviewer](../../plugins/kg-devkit/agents/observability-reviewer.md) | sonnet | Read, Grep, Glob | 3.373 | ~90 | ~990 | Observability, Conventions | tenant-security, devops-engineer |
| [devops-engineer](../../plugins/kg-devkit/agents/devops-engineer.md) | sonnet | Read, Edit, Write, Bash, Grep, Glob | 3.687 | ~60 | ~1,1k | Production, Hard limits | — |
| [devops-operator](../../plugins/kg-devkit/agents/devops-operator.md) | opus | aynı (yazar) | 4.490 | ~110 | ~1,3k | Production, Hard limits | devops-engineer |

Ortak yapı (15/15): satır 8 `Logging:` paragrafı; "önce `Project profile` oku"; rapor dili; "Do not spawn agents".
Yazar 6 agent + tarayıcı testçisi: son satırda `Hard limits` cümlesi. 6 reviewer: `VERDICT: PASS/FAIL/UNCLEAR`.
Hiçbir agent'ın `tools` listesinde `Agent` yok → alt-agent başlatma yapısal olarak da kapalı.

## 4. Skill envanteri

| Skill | Frontmatter | Bayt | Çağrı tok. | Verdiği yetki | Atıf |
| --- | --- | ---: | ---: | --- | --- |
| [verify-change](../../plugins/kg-devkit/skills/verify-change/SKILL.md) | manuel | 2.823 | ~840 | yok | profilin Finish gate'i |
| [add-migration](../../plugins/kg-devkit/skills/add-migration/SKILL.md) | manuel, `argument-hint` | 3.458 | ~1k | yok (DB'ye uygulamaz) | Finish gate |
| [release](../../plugins/kg-devkit/skills/release/SKILL.md) | manuel, `[deploy]` | 4.602 | ~1,4k | commit + push; `deploy` ile canlı | Finish gate |
| [rollback](../../plugins/kg-devkit/skills/rollback/SKILL.md) | manuel, `[image-tag]` | 4.925 | ~1,5k | plan; uygulama ayrı onayla | `/kg-devkit:live-check` |
| [live-check](../../plugins/kg-devkit/skills/live-check/SKILL.md) | manuel | 3.717 | ~1,1k | salt-okuma | `devops-engineer` |
| [browser-test](../../plugins/kg-devkit/skills/browser-test/SKILL.md) | manuel, `context: fork`, `agent: frontend-browser-tester` | 1.186 | ~280 | yok | agent'a devreder |

## 5. Hook ve yapılandırma envanteri

| Dosya | İçerik | Kullanan |
| --- | --- | --- |
| [hooks/hooks.json](../../plugins/kg-devkit/hooks/hooks.json) | 1 `PreToolUse`, matcher `Bash`, `type: command`, timeout alanı yok | Claude Code (ana oturum + alt-agent'lar) |
| [hooks/guard-infra.py](../../plugins/kg-devkit/hooks/guard-infra.py) | 8 regex kuralı → `permissionDecision: "ask"` | hooks.json; `scripts/test_guard_infra.py` (106 örnek, CI) |
| [.claude-plugin/plugin.json](../../plugins/kg-devkit/.claude-plugin/plugin.json) | 4 alan; `license`/`repository`/`keywords` yok | Claude Code, `scripts/bump-version.py` |
| [marketplace.json](../../.claude-plugin/marketplace.json) | 1 plugin girdisi | `claude plugin marketplace add` |

## 6. Plugin dışı ama davranışı belirleyen dosyalar

| Dosya | İlişki |
| --- | --- |
| `rules/*.md` (3) | Ana oturumun test/doküman/ops disiplinini taşır; yalnız `install-claude-rules.sh` çalıştırılırsa yüklenir ([I-02](10-improvement-roadmap.md)) |
| `docs/project-profile-template.md` | 18 alanlı `Project profile` sözleşmesi; agent ve skill'lerin tek proje bilgisi kaynağı |
| `docs/agent-requirements.md` | Agent → profil alanı matrisi (dokümantasyon; kaynak değil) |
| `scripts/build-codex.py` | Agent/skill'leri Codex biçimine çevirir; `model` ve `tools` taşınmaz, hook Codex'te yoktur |
| `.claude/hooks/kit-review-gate.py` | Bu repoda `Stop` kancası; `plugins/` altındaki her değişikliği kaynak sayar ([M-01](10-improvement-roadmap.md)) |
| `.github/workflows/check.yml` | Codex eşliği, kanca testleri, `claude plugin validate` (CLI 2.1.304'e sabit) |

## 7. Doğrulama komutları (bu analizde çalıştırılanlar)

| Komut | Sonuç |
| --- | --- |
| `python3 scripts/test_guard_infra.py` | `guard-infra: 106 örnek geçti` |
| `python3 scripts/build-codex.py --check` | `codex/ güncel.` |
| `python3 scripts/test_sync_claude_codex.py` | `Ran 20 tests … OK` |
| `claude plugin validate .` / `… plugins/kg-devkit` | `Validation passed` (tek uyarı: ikon yok) |
| `claude --plugin-dir plugins/kg-devkit plugin details kg-devkit` | 6 skill, 15 agent, 1 hook; sürekli ~1.465 token |
| `python3 …/test_guard_probe.py (karşılaştırma betiği; senaryoları `scripts/test_guard_infra.py`'ye taşındı)` | mevcut kanca 115 ek senaryonun 26'sında beklenen kararı verdi |
