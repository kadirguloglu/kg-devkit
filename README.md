# kg-devkit

Project-agnostic agents, skills and rules for **Claude Code** and **Codex**: developers, test developers, reviewers
(database, tenant security), an architecture advisor, a scope advisor, and release/rollback/live-check/migration skills.
A Claude-only safety hook asks for approval before `kubectl`/`helm`/`terraform`/`docker`/cloud-CLI mutations, database migration applies, secret reads and destructive git commands (best-effort, fail-open without Python).
Nothing project-specific is baked in: each repo describes itself in a `## Project profile` section of its `AGENTS.md`
(see the [template](docs/project-profile-template.md)), and the agents read it first. License: MIT.

Kişisel, projeden bağımsız Claude Code ve Codex agent/skill/kural koleksiyonu (plugin + marketplace). Proje bilgisi
agent'lara gömülmez; her repo `AGENTS.md` içindeki `## Project profile` bölümünü sağlar. Aşağıdaki anlatım Türkçedir.

**Dokümanlar / Docs**
- [Agent gereksinimleri](docs/agent-requirements.md) – her agent'ın okuduğu profil alanları, varsayımları ve profil yokken davranışı (plugin'i incelemeden önce buraya bak / start here when evaluating the plugin).
- [Project profile şablonu](docs/project-profile-template.md) – kendi reponda doldurulacak bölüm.
- [Tasarım kararları ve sınırlar](docs/inventory.md).
- [Değişiklik günlüğü](CHANGELOG.md) – sürüm sürüm kullanıcıya dönük değişiklikler.
- [Mimari analiz raporları](docs/analysis/00-executive-summary.md) – agent/skill/hook incelemesi, bulgular ve uygulama durumu.
- [Proje hazırlık raporu prompt'u](docs/prompts/project-readiness-report.md) – bir projenin kit agent/skill'lerine ne kadar hazır olduğunu (dolu/eksik profil alanı, hangi agent çalışır/durur) raporlatmak için.
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

- **Agent'lar (15):** `frontend-developer`, `frontend-browser-tester`, `frontend-test-developer`, `backend-developer`,
  `backend-test-developer`, `database-reviewer`, `engineering-software-architect`, `devops-engineer`, `devops-operator`,
  `tenant-security-reviewer`, `scope-advisor`, `api-contract-reviewer`, `dependency-supply-chain-reviewer`,
  `performance-reviewer`, `observability-reviewer`. Riskli işler için `devops-operator`, `database-reviewer`,
  `tenant-security-reviewer`, `api-contract-reviewer` ve `dependency-supply-chain-reviewer` `opus`, diğerleri `sonnet` modelini kullanır. `tenant-security-reviewer` ve `scope-advisor`
  çok kiracılı projeler içindir (tek müşterili projede `scope-advisor` `NOT-APPLICABLE` döner). Ayrıntı: [agent gereksinimleri](docs/agent-requirements.md).
- **Skill'ler:** yalnız açıkça çağrılanlar `browser-test`, `add-migration`, `release`, `rollback`, `live-check`; `verify-change`
  yetki vermediği için model iş bitiminde kendiliğinden de çağırabilir. Reviewer tetikleme profilin `Finish gate` alanından,
  o yoksa kit'in varsayılan tablosundan (`references/finish-gate-default.md`) gelir.
- **Kurallar** (`rules/` tek kaynak): `kg-test-discipline`, `kg-documentation-maintenance`, `kg-ops-safety`. Plugin içinde
  `test-discipline`, `docs-maintenance`, `ops-safety` skill'leri olarak gelir (model ilgili dosyalarla çalışırken yükler; Codex'te
  de skill olarak kurulur). İstersen aynı kuralları `~/.claude/rules` altına da bağlayabilirsin (`install-claude-rules.sh`).
- **Güvenlik kancası** (yalnız Claude): `hooks/guard-infra.py`, canlı ortamı değiştiren `kubectl`/`oc`/`helm`/`terraform`/`tofu`
  komutlarını ve secret okumayı (küme, bulut secret servisleri, `vault`, `sops`); `docker`/`docker compose`, migration uygulama
  (`dotnet ef`, Prisma, Alembic, Django, Rails, Flyway…), dağıtım araçları (`helmfile`, `pulumi`, `argocd`, `flux`, `ansible-playbook`…),
  bulut CLI'larının (`doctl`, `gcloud`, `az`, `oci`, `aws`) oluşturma/değiştirme/silme/durdurma/dağıtım komutlarını; ayrıca
  `git push --force`, `git reset --hard`, `git clean -f` ve secret görünümlü dosyanın `git add` edilmesini kullanıcı onayına
  düşürür (bloklamaz; mesajda çalıştıran agent yazar). Fiilden önce gelen bayrakları, satır devamını ve `bash -c`/`ssh`/`sudo`
  sarmalayıcılarını çözer; tırnak içindeki metni, `--help` ve `--dry-run=client` komutlarını sormaz. Yalnız Bash komut metnine
  bakar: kabuk kısayolu/fonksiyon, değişken, betik içinde çağrılan komutlar ve MCP araçları görünmez; `python3`/`python` yoksa
  sessizce geçer. Etkileşimsiz çalışmada (`claude -p`, `dontAsk`) onay isteyen komut reddedilir. Ayarlar:
  `KG_GUARD_LOCAL_COMPOSE=allow` (uzak hedefi olmayan `docker compose` sorulmaz), `KG_GUARD_DISABLE=git,migrate,deploytools`
  (adı verilen grupları kapatır). Plugin ile birlikte gelir; Codex'te yoktur, orada yalnız agent metin kuralları geçerlidir.
- **Çalışma kaydı** (yalnız Claude): `hooks/agent_run_log.py` her agent çalıştırmasını plugin veri dizinindeki
  `agent-runs.jsonl` dosyasına yazar (yalnız olay, oturum ve agent kimliği/türü, izin modu, zaman ve `VERDICT`/`STATUS` değeri;
  prompt, komut veya rapor metni yok).
  Özet: `python3 <plugin>/hooks/agent_run_log.py --summary ~/.claude/plugins/data/<kg-devkit dizini>`; kapatmak için `KG_AGENT_LOG=off`.
- **Sonuç satırı zorlaması** (yalnız Claude): `hooks/require_outcome.py`, bir reviewer raporunu `VERDICT:` satırı olmadan veya bir
  yazar agent `STATUS:` satırı olmadan bitirirse agent'ı bir kez geri çevirip satırı ister (ikinci durmada karışmaz; satırın
  değerini denetlemez). Kapatmak için `KG_REQUIRE_OUTCOME=off`.

## Sürümleme

`main`'e her push'ta GitHub Actions (`bump-version.yml`) `plugins/kg-devkit/.claude-plugin/plugin.json` sürümünü artırır ve
`chore(release): vX.Y.Z` commit'i atar. Varsayılan **patch**; merge/commit mesajına `[minor]` veya `[major]` yazarsan o seviye artar.
Güncel sürüm için `plugin.json`'a bak; README'ye sürüm yazılmaz.

## Geliştirme

Tek kaynak Claude tarafıdır. Plugin dağıtımı `codex/`, bu reponun bakım araçları `.codex/` altında üretilir;
üretilen dosyalar elle düzenlenmez. Python 3.11+ yeterlidir; dönüşüm betikleri ek paket gerektirmez.

```bash
python3 scripts/build-codex.py            # kural skill'lerini, codex/ ve .codex/ çıktılarını güncelle
python3 scripts/build-codex.py --check    # üretilen dosyaların güncelliğini denetle
python3 scripts/test_guard_infra.py       # kanca testleri (kurallar, uçtan uca, süre sınırı, çalışma kaydı)
python3 scripts/lint_plugin.py            # agent/skill mekanik kuralları
python3 scripts/test_sync_claude_codex.py # bakım dönüşümü ve kanca testleri
claude plugin validate . && claude plugin validate plugins/kg-devkit
claude plugin eval plugins/kg-devkit --trust-plugin --allow-tools Bash --runs 1 --no-publish   # davranış testleri (ücretli, elle)
```

Bu repoyu geliştirirken dört bakım agent'ı kullanılır: `kit-doc-sync`, `kit-agent-linter`, `kit-release-notes`,
`kit-prompt-sync`. Kaynakları `.claude/agents/`, Codex karşılıkları `.codex/agents/*.toml` altındadır.
Claude'un `sonnet`/`opus` model adları Codex'e taşınmaz; Codex agent'ları oturumun modelini devralır. İlk üçü
`read-only`, yalnız iki profil prompt'unu güncelleyebilen `kit-prompt-sync` ise `workspace-write` kullanır.
Bakım araçları yalnız bu repo içindir; `install-codex.sh` bunları global olarak kurmaz ve tüketici projelerin
`Project profile` alanlarına yeni bir gereksinim eklenmez.

Yalnız `.claude` değişikliklerini aktarmak veya düzenlerken otomatik izlemek için:

```bash
python3 scripts/sync-claude-codex.py         # .claude → .codex
python3 scripts/sync-claude-codex.py --check # güncel değilse hata koduyla çıkar; dosya yazmaz
python3 scripts/sync-claude-codex.py --watch # 1 saniyede bir kontrol eder; Ctrl+C ile durur
```

Betik mevcut agent metadata'sını, `.claude/settings.json` içindeki kanca tanımlarını ve bakım kancasını çevirir.
Her Claude özelliği için genel dönüştürücü değildir: desteklenmeyen yeni dosya türü veya ayarda hata verir.
`.codex/.claude-sync.json` kaynak ve çıktı özetlerini izler; özel Codex dosyaları korunur, elle değiştirilmiş
üretilen dosyada çakışma bildirilir. Değişiklikleri kaynak `.claude` dosyasında yapıp yeniden üret.

Claude'da `.claude/settings.json`, Codex'te üretilen `.codex/hooks.json` yerel `Stop` kancasını kaydeder.
Codex kancası `.codex/hooks/kit-review-gate.py` dosyasını çalıştırır. Kit kaynakları değiştiğinde ilgili bakım
agent'larının çalıştırılmasını ister; changelog güncellenmeden kaynak değişirse `kit-release-notes` da istenir.
Bu bir hatırlatıcıdır; agent'ların çalıştığını veya `PASS` verdiğini kendi başına kanıtlamaz.
Codex'te proje ve kanca için normal güven arayüzündeki onay gerekir; dönüşüm betiği güven kaydı yazmaz.
Yerel agent keşfi veya `Stop` kancası desteği olmayan eski istemcilerde aynı çalışma davranışı garanti edilmez.

CI (`.github/workflows/check.yml`) üretilen dosyaların güncelliğini, dönüşüm/kanca testlerini, agent/skill lint'ini ve manifestleri doğrular.
Tasarım kararları ve bilinen sınırlar: [docs/inventory.md](docs/inventory.md).
