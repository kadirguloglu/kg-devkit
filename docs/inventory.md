# Tasarım notları

kg-devkit, bir .NET + React çok kiracılı projede kullanılan agent, skill ve kuralların projeden bağımsız hale getirilmiş
halidir. Projeye özgü bilgi (komutlar, yollar, cluster adları, kural belgeleri) dosyalara gömülmez; her repo bunu kendi
`AGENTS.md` dosyasındaki `## Project profile` bölümünde verir ([şablon](project-profile-template.md)).

## Ne nerede

| Tür | Kaynak | Claude | Codex |
| --- | --- | --- | --- |
| Agent (15) | `plugins/kg-devkit/agents/*.md` | plugin, `kg-devkit:<ad>` | `codex/agents/*.toml` → `~/.codex/agents` |
| Skill (6) | `plugins/kg-devkit/skills/*/SKILL.md` | plugin, `/kg-devkit:<ad>` | `codex/skills/*` → `~/.agents/skills`, `$<ad>` |
| Kural (3) | `rules/*.md` | `~/.claude/rules` (symlink, plugin kural taşımaz) | okunmaz; ilkeler agent/skill gövdelerinde |
| Repo bakım agent'ı (4) | `.claude/agents/*.md` | yalnız bu repoda | `.codex/agents/*.toml`, yalnız bu repoda |
| Repo bakım kancası | `.claude/settings.json`, `.claude/hooks/kit-review-gate.py` | yerel `Stop` kancası | `.codex/hooks.json`, `.codex/hooks/kit-review-gate.py` |

`codex/` plugin dağıtımıdır; `.codex/` bu reponun yerel bakım araçlarıdır. `scripts/build-codex.py` plugin
çıktısını üretir ve `scripts/sync-claude-codex.py` ile bakım çıktısını günceller. `--check` iki çıktıyı da
dosya yazmadan doğrular. `install-codex.sh` yalnız `codex/` altındaki dağıtımı kurar; bakım agent'larını global
olarak kurmaz. Tüketici projelerin `Project profile` sözleşmesi değişmez.

## Tasarım kararları

- **Profil okuma:** Agent ve skill'ler önce `Project profile` bölümünü okur; yoksa `package.json`/README'den çıkarım yapar
  ve raporda söyler. Rapor dili profilden gelir (varsayılan: kullanıcının isteği).
- **Reviewer çıktısı:** tüm reviewer agent'ları (`database-reviewer`, `tenant-security-reviewer`, `api-contract-reviewer`, `dependency-supply-chain-reviewer`, `performance-reviewer`, `observability-reviewer`) raporu `VERDICT: PASS / FAIL / UNCLEAR` ile bitirir;
  profil farklı bir geçti ifadesi isterse onu da yazar.
- **Salt-okuma sınırı:** Reviewer, danışman ve scope agent'ları yalnız `Read, Grep, Glob` kullanır (Codex'te `sandbox_mode = "read-only"`).
- **Yan etkili skill'ler:** `release`, `rollback`, `live-check`, `add-migration`, `verify-change`, `browser-test`
  `disable-model-invocation: true` ile yalnız açıkça çağrılır. `release` çağrıldığında commit+push yetkisi verir
  (`deploy` argümanıyla ayrıca canlı deploy); `rollback` canlı geri alma için ayrıca açık onay ister; `live-check`
  salt-okumadır; `add-migration`, `verify-change` ve `browser-test` commit/push/deploy/veritabanı yetkisi vermez.
- **Skill doğrulama sınırları:** `release` son index'i denetler; dry-run stage edilmiş secret dosyalarını doğrulamaz.
  `rollback`, başarılı release ve image digest → commit/revision eşlemesini, gerçek şema uyumluluğunu ve onaylanan
  hedefle çalışan image eşleşmesini doğrular; eksik kanıtla uygulamaz. `live-check` süre sınırlı komutlar ve restart
  karşılaştırması kullanır. Deploy/sağlık değerleri `Production`'dan, migration dizini `Persistence`'dan okunur;
  eski `Release` deploy/sağlık değerleri yalnız Production'da eksikse kullanılır, çelişkide işlem durur.
- **Kapsam:** `scope-advisor` tek müşterili projede `NOT-APPLICABLE` döner ve durur; `tenant-security-reviewer` kiracı yoksa
  durmaz, düz yetki/sahiplik incelemesine geçer.
- **Otomatik sürüm:** `main`'e her push'ta `.github/workflows/bump-version.yml`, `scripts/bump-version.py` ile
  `plugins/kg-devkit/.claude-plugin/plugin.json` sürümünü artırıp `chore(release): vX.Y.Z` commit'i atar. Varsayılan
  patch; birleştirme/commit mesajında `[minor]` veya `[major]` varsa o seviye. Botun kendi commit'i yeni artış tetiklemez.
  `main`'de PR zorunlu bir ruleset olduğu için push `GITHUB_TOKEN` ile değil, repo secret'ı `BUMP_TOKEN` (yönetici hesabının
  fine-grained jetonu, yalnız bu repo, Contents: Read and write) ile yapılır; ruleset bypass listesinde **Repository admin** olmalıdır.
  Jeton süresi dolarsa `bump-version` "BUMP_TOKEN secret'ı yok/geçersiz" diye başarısız olur ve yenilenmelidir.
  Döngüyü `chore(release):` mesaj denetimi keser.
- **Altyapı kancası:** `plugins/kg-devkit/hooks/` altındaki PreToolUse kancası (`guard-infra.py`) canlı ortamı değiştiren
  veya secret okuyan `kubectl/oc/helm/terraform/tofu`, `docker`/`docker compose`, `dotnet ef database update|drop` ve bulut CLI
  (`doctl/gcloud/az/oci/aws`) komutlarını onaya düşürür (bloklamaz, `ask`). Claude'a özgüdür; Codex'te yoktur. Sınırlar: yalnız Bash
  komut metnine bakar (kabuk kısayolu/fonksiyon, betik içi komut ve MCP araçları görünmez); `python3` yoksa sessizce geçer (fail-open).
  Kural testleri: `python3 scripts/test_guard_infra.py` (CI'da çalışır).
- **Modeller:** `devops-operator`, `database-reviewer`, `tenant-security-reviewer`, `api-contract-reviewer` ve `dependency-supply-chain-reviewer` `model: opus`, diğerleri `sonnet`.
- **Kit bakım agent'ları:** kaynak `.claude/agents/`, üretilen Codex karşılığı `.codex/agents/` altındadır
  (yalnız bu repoda çalışırken; plugin'e ve `codex/` dağıtımına girmez):
  `kit-doc-sync` (README/doküman kaynakla uyumlu mu; prompt içeriğine bakmaz), `kit-agent-linter` (agent dosyaları: sızıntı, yetki, eşlik, bakım agent'larında tam okuma paragrafı, mekanik
  kontroller; CI betiği yerine agent yapar) ve `kit-release-notes` (sürüm notu ve `[minor]`/`[major]` önerisi; çıktısı `CHANGELOG.md` girdisi olarak kullanılır). Bu üçü salt-okuma
  çalışır, düzeltmeyi ana oturum yapar. `kit-prompt-sync` agent/skill/kanca/kural değişiminde profil gereksinimi değiştiyse prompt içeriğinin tek sahibidir ve yalnız
  `docs/prompts/generate-project-profile.md` ve `docs/prompts/project-readiness-report.md` dosyalarını günceller (`Edit` aracı vardır, başka dosyaya dokunmaz; `Stop` kancası `plugins/kg-devkit/` altındaki herhangi bir dosya, kural, profil şablonu veya `agent-requirements.md` değişince ister).
  Codex'te ilk üç agent `sandbox_mode = "read-only"`, `kit-prompt-sync` `workspace-write` kullanır; iki dosyalık
  yazma sınırı agent talimatında korunur. Claude `tools` listesi Codex araç erişiminin birebir karşılığı değildir.
  Claude kaynaklarındaki `sonnet`/`opus` model adları korunur; Codex karşılıkları model belirtmez, oturum modelini devralır.
- **Bakım dönüşümü:** `python3 scripts/sync-claude-codex.py` `.claude` kaynaklarını `.codex` karşılıklarına çevirir;
  `--check` fark varsa başarısız olur, `--watch` bir saniyede bir kontrol eder ve Ctrl+C ile durur.
  `.codex/.claude-sync.json` kaynak/çıktı özetleriyle yönetilen dosyaları izler. Özel Codex dosyaları korunur;
  üretilen dosya elle değiştirilmişse üzerine yazmak yerine çakışma bildirir. Desteklenmeyen yeni Claude dosya
  türü veya ayarı sessizce atlanmaz; hata verilir. Bu, bütün Claude özellikleri için genel bir dönüştürücü değildir.
  `scripts/test_sync_claude_codex.py` dönüşüm ve kanca davranışını sınar; CI'da çalışır.
- **Otomatik tetik:** `.claude/settings.json` `Stop` kancası `.claude/hooks/kit-review-gate.py` çalıştırır: agent dosyaları değiştiyse
  `kit-agent-linter`, agent/skill/kural/kanca/betik/workflow/doküman değiştiyse `kit-doc-sync` çalıştırılması istenir. Profil gereksinimi kaynakları (plugin, kural, şablon, `agent-requirements.md`) değiştiyse `kit-prompt-sync` da istenir. Her agent için ayrı, yalnız
  baktığı dosyaların içeriğinden hesaplanan özet tutulur (`.git/kit-review-gate/state.json`): commit atmak veya kanca betiğini düzenlemek
  tetiklemez, ilgili dosyalar değişince o agent bir kez istenir. Kaynak (plugin/kural/betik/workflow) değişip `CHANGELOG.md` son çalıştırmadan
  beri değişmediyse `kit-release-notes` da istenir (özet yoksa, ör. yeni klonda, başlangıç HEAD'deki commit'li içeriktir; dal ve `origin/main` ilerlemesi tetiklemez). Yalnız bu repoda geçerlidir.
  Codex karşılığı `.codex/hooks.json` içindeki yerel `Stop` kaydıyla `.codex/hooks/kit-review-gate.py` çalıştırır.
  Codex durumu `.git/codex-kit-review-gate/state.json` altında, Claude durumundan ayrı tutulur. Bu kancalar
  inceleme hatırlatıcısıdır; reviewer'ın çalıştığını veya `PASS` verdiğini doğrulamaz.
  Codex'in normal güven arayüzünde proje/kanca güveni etkin olmalıdır; senkronlama betiği güven kaydı yazmaz
  ve onay mekanizmasını atlamaz.
- **Stack paketleri yok:** .NET/React'e özgü kural paketleri bilerek eklenmedi; aynı stack'te ikinci proje gelince çıkarılır.

## Bilinen sınırlar

- Codex tarafı Claude kadar sınanmadı: agent'ların yüklenmesi ve `$verify-change` doğrulandı, diğer skill'ler denenmedi.
- `frontend-browser-tester` gerçek Chrome oturumunda denenmedi.
- `release`, `rollback`, `live-check`, `add-migration` canlı bir ortamda uçtan uca çalıştırılmadı; yalnız talimat düzeyinde gözden geçirildi.
- Yerel `.codex/agents/` keşfi ve `Stop` kancası desteği istemciye bağlıdır. Eski veya bu özellikleri
  sunmayan istemcilerde üretilen dosyalar aynı çalışma davranışını garanti etmez; hook güveni ayrıca gereklidir.
