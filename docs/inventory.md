# Tasarım notları

kg-devkit, bir .NET + React çok kiracılı projede kullanılan agent, skill ve kuralların projeden bağımsız hale getirilmiş
halidir. Projeye özgü bilgi (komutlar, yollar, cluster adları, kural belgeleri) dosyalara gömülmez; her repo bunu kendi
`AGENTS.md` dosyasındaki `## Project profile` bölümünde verir ([şablon](project-profile-template.md)).

## Ne nerede

| Tür | Kaynak | Claude | Codex |
| --- | --- | --- | --- |
| Agent (11) | `plugins/kg-devkit/agents/*.md` | plugin, `kg-devkit:<ad>` | `codex/agents/*.toml` → `~/.codex/agents` |
| Skill (6) | `plugins/kg-devkit/skills/*/SKILL.md` | plugin, `/kg-devkit:<ad>` | `codex/skills/*` → `~/.agents/skills`, `$<ad>` |
| Kural (3) | `rules/*.md` | `~/.claude/rules` (symlink, plugin kural taşımaz) | okunmaz; ilkeler agent/skill gövdelerinde |

`codex/` çıktısı `scripts/build-codex.py` ile Claude kaynağından üretilir (CI `--check` ile güncelliği doğrular).

## Tasarım kararları

- **Profil okuma:** Agent ve skill'ler önce `Project profile` bölümünü okur; yoksa `package.json`/README'den çıkarım yapar
  ve raporda söyler. Rapor dili profilden gelir (varsayılan: kullanıcının isteği).
- **Reviewer çıktısı:** `database-reviewer` ve `tenant-security-reviewer` raporu `VERDICT: PASS / FAIL / UNCLEAR` ile bitirir;
  profil farklı bir geçti ifadesi isterse onu da yazar.
- **Salt-okuma sınırı:** Reviewer, danışman ve scope agent'ları yalnız `Read, Grep, Glob` kullanır (Codex'te `sandbox_mode = "read-only"`).
- **Yan etkili skill'ler:** `release`, `rollback`, `live-check`, `add-migration`, `verify-change`, `browser-test`
  `disable-model-invocation: true` ile yalnız açıkça çağrılır; commit, deploy ve veritabanı yetkisi vermezler.
- **Kapsam:** Çok kiracılı projelere özgü `tenant-security-reviewer` ve `scope-advisor` tek müşterili projede işe yaramaz;
  profilde ilgili alan yoksa durup bildirirler.
- **Stack paketleri yok:** .NET/React'e özgü kural paketleri bilerek eklenmedi; aynı stack'te ikinci proje gelince çıkarılır.

## Bilinen sınırlar

- Codex tarafı Claude kadar sınanmadı: agent'ların yüklenmesi ve `$verify-change` doğrulandı, diğer skill'ler denenmedi.
- `frontend-browser-tester` gerçek Chrome oturumunda denenmedi.
- `release`, `rollback`, `live-check`, `add-migration` canlı bir ortamda uçtan uca çalıştırılmadı; yalnız talimat düzeyinde gözden geçirildi.
