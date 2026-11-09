# Değişiklik günlüğü

Sürümler `main`'e her push'ta otomatik artar (`bump-version.yml`): varsayılan patch, merge mesajında `[minor]`/`[major]`
ile seviye seçilir. Bu dosya kullanıcıya dönük etkiyi özetler; taslağı `kit-release-notes` agent'ı çıkarır
(bkz. [docs/inventory.md](docs/inventory.md)). Kategoriler: **Kırıcı**, **Eklenen**, **Değişen**, **Düzeltilen**, **Doküman/Altyapı**.

## Yayınlanmadı (öneri: patch)
- **Değişen:** `generate-agent-requirements.md` kaldırıldı; yerine `project-readiness-report.md`: tüketici projede çalışıp "bu proje için hangi agent/skill
  HAZIR / ÇIKARIM / DURUR / UYGULANAMAZ" raporu verir (matris prompt'a gömülü, kit iç yapısı girmez). Eski prompt agent dosyalarının repoda olduğunu
  varsaydığı için tüketici projede kit'in iç yapısını döküyordu. `kit-prompt-sync` gömülü matrisin `agent-requirements.md` ile uyumunu denetler.
- **Doküman/Altyapı:** `generate-project-profile.md` prompt'u kendi içinde eksiksiz: profil şablonu prompt'un içine gömüldü, kg-devkit reposundaki
  dosyalara ihtiyaç duymadan başka projede kopyala-yapıştır çalışır.
  `kit-prompt-sync`, gömülü şablonun `docs/project-profile-template.md` ile aynı kalmasını da denetler.
- **Doküman/Altyapı:** `docs/prompts/` altındaki iki prompt soru-cevap akışına çevrildi: önce repo/mevcut doküman taranır, cevabı bulunanlar
  sorulmaz, yalnız belirsiz/bulunamayan noktalar (en çok 4'lü gruplar) kullanıcıya sorulur. Gereksinim prompt'u artık skill'leri ve kuralları da
  kapsar; `agent-requirements.md`'ye Skill tablosu, profil şablonuna `Production` altında bulut CLI kimlik ve rollback komutu eklendi.
- **Düzeltilen:** `Stop` kancasının özeti artık `origin/main`'e göre diff'ten değil, bakılan klasörlerdeki izlenen dosyaların içeriğinden
  hesaplanır; dal veya `origin/main` ilerlemesi (ör. PR merge'ü) boşuna tetiklemez. Özet yoksa (yeni klon) başlangıç HEAD'deki
  commit'li içeriktir.
- **Doküman/Altyapı:** Yeni bakım agent'ı `kit-prompt-sync` (`.claude/agents/`, plugin'e girmez): profil gereksinimi değişince yalnız
  `docs/prompts/generate-project-profile.md` ve `docs/prompts/project-readiness-report.md` dosyalarını günceller. `Stop` kancası
  `plugins/kg-devkit/`, `rules/`, `docs/project-profile-template.md` veya `docs/agent-requirements.md` değişince onu da ister (yalnız bu repoda).
  Çakışma giderildi: `kit-doc-sync` artık `docs/prompts/*` içeriğini denetlemez (yalnız sürüm/bağlantı), içeriğin tek sahibi `kit-prompt-sync`.

## 0.8.1 – 2026-11-06 ([#13](https://github.com/kadirguloglu/kg-devkit/pull/13))
- **Değişen:** `dependency-supply-chain-reviewer` modeli `sonnet` → `opus` (diğer güvenlik reviewer'larıyla aynı katman). Agent log satırları profilin rapor dilini izler (Türkçe dışıysa aynı iki satır o dilde); altı reviewer'a ortak
  "profil farklı geçme ifadesi adlandırırsa onu da yaz" kuralı, `database-reviewer` ve `tenant-security-reviewer`'a "Do not spawn agents"
  eklendi; bu ikisindeki alan-özel ifadeler (finansal hesap, silinmiş kullanıcı kimliği, para/yükleme temizliği) profile bırakıldı;
  `dependency-supply-chain-reviewer` CI sınırı netleştirildi (pinleme/güven/secret; workflow mantığı `devops-engineer`'da).
  `build-codex.py`'den artık gereksiz `kg-devkit:` önek kuralı kaldırıldı.
- **Doküman/Altyapı:** `.claude/settings.json` `Stop` kancası (`.claude/hooks/kit-review-gate.py`): kit kaynakları değişince
  `kit-agent-linter` ve `kit-doc-sync` çalıştırılmasını ister; kaynak değişip `CHANGELOG.md` değişmediyse `kit-release-notes` da istenir; özet agent başına ve dosya içeriğine bağlıdır (kanca betiği düzenlemesi ve commit yeniden tetiklemez) (yalnız bu repoda).

## 0.8.0 – 2026-11-06 (öneri: `[minor]`)
- **Eklenen:** 4 salt-okuma reviewer agent'ı: `api-contract-reviewer` (opus; kırıcı API değişikliği ve backend/frontend sözleşme sapması),
  `dependency-supply-chain-reviewer` (bağımlılık, lockfile, lisans, CI action tedarik zinciri), `performance-reviewer` (uygulama/UI performansı;
  şema ve sorgu `database-reviewer`'da kalır) ve `observability-reviewer` (log/metrik/trace, log'a hassas veri sızması, yutulan hatalar).
  Hepsi `VERDICT: PASS/FAIL/UNCLEAR` ile biter; Codex çıktısı üretildi.
- **Değişen:** Project profile şablonuna `API contract`, `Dependencies`, `Performance`, `Observability` alanları eklendi
  (şablon, profil üreten prompt ve `agent-requirements.md` güncellendi). Agent sayısı 11 → 15.

## 0.7.0 – 2026-11-06 (öneri: `[minor]`)
- **Değişen:** Güvenlik kancası kapsamı genişledi: `docker`/`docker compose`, `dotnet ef database update|drop`, bulut CLI'ları
  (`doctl`, `gcloud`, `az`, `oci`, `aws`) ve `kubectl exec|port-forward|run|expose|config use-context` onaya düşer. Kanca testleri
  genişletildi. Sınırlar README/`inventory.md`'de belgelendi (yalnız Bash metni, fail-open).
- **Düzeltilen:** `add-migration`, `live-check` ve `rollback` skill'leri ORM ve orkestratör-nötr yazıldı (EF Core ve DigitalOcean örnekleri
  kaldırıldı/örneğe çevrildi); `live-check` kancayı atlatan `k()` kısayolunu önermiyor. Test betiği plugin dizininde `__pycache__` oluşturmuyor.

## 0.6.4 – 2026-11-06 ([#9](https://github.com/kadirguloglu/kg-devkit/pull/9), [#10](https://github.com/kadirguloglu/kg-devkit/pull/10))
- **Doküman/Altyapı:** `CODEOWNERS` ve `SECURITY.md` eklendi; `main` ruleset ile korundu. `bump-version`, ruleset'i geçmek için
  `BUMP_TOKEN` (yönetici fine-grained jetonu) ile push eder.

## 0.6.3 – 2026-11-06 ([#8](https://github.com/kadirguloglu/kg-devkit/pull/8))
- **Doküman/Altyapı:** `CHANGELOG.md` eklendi.

## 0.6.2 – 2026-11-06 ([#7](https://github.com/kadirguloglu/kg-devkit/pull/7))
- **Doküman/Altyapı:** Repo içi bakım agent'ları eklendi (`.claude/agents/`: `kit-doc-sync`, `kit-agent-linter`,
  `kit-release-notes`; plugin'e ve Codex çıktısına girmez).
- **Düzeltilen:** `docs/inventory.md` skill yetkileri ve tek müşterili proje kapsamı düzeltildi; `agent-requirements.md`
  `tenant-security-reviewer` satırı agent metniyle eşlendi; hook testleri tüm korunan fiilleri kapsıyor (45 örnek);
  `backend-test-developer` ve `devops-operator` description'larına "ne için değil" eklendi.

## 0.6.1 – 2026-11-06 ([#6](https://github.com/kadirguloglu/kg-devkit/pull/6))
- **Doküman/Altyapı:** README'den sabit sürüm kaldırıldı; kanca, model katmanları ve sürümleme anlatıldı.
- **Düzeltilen:** Yanlışlıkla izlenen `__pycache__` dosyası çıkarıldı, `.gitignore` eklendi.

## 0.6.0 – 2026-11-06 ([#5](https://github.com/kadirguloglu/kg-devkit/pull/5))
- **Doküman/Altyapı:** `docs/prompts/` altındaki iki prompt model, kanca, `Hard limits`, `Persistence` alanları ve
  iddia doğrulamasını kapsayacak şekilde güncellendi.

## 0.5.0 – 2026-11-06 ([#4](https://github.com/kadirguloglu/kg-devkit/pull/4))
- **Eklenen:** Claude'a özgü PreToolUse güvenlik kancası (`hooks/guard-infra.py`): canlı `kubectl`/`oc`/`helm`/`terraform`
  değişikliklerini ve secret okumayı kullanıcı onayına düşürür (bloklamaz). Codex'te yoktur.
- **Değişen:** `database-reviewer`, `tenant-security-reviewer`, `devops-operator` `opus` modeline geçti. Yazan agent'lar
  profildeki `Hard limits` bölümünü okur (yalnız kısıt ekler). EF Core'a özgü ifadeler `Persistence` profil girdisine
  bağlandı (ORM, migration artefaktları, filtre bypass API'leri). `engineering-software-architect` sabit başlıklarla yanıt verir.
- **Düzeltilen:** Codex çıktısında `kg-devkit:database-reviewer` öneki kaldırıldı.
- **Kullanıcının yapması gerekenler:** zorunlu bir şey yok; isteğe bağlı olarak `AGENTS.md` profilinde `Persistence` ve
  `Hard limits` alanlarını doldur. Profilde `kubectl`/`helm`/`terraform` değişikliklerini "onaysız çalışır" diye yazdıysan kaldır.

## 0.4.1 – 2026-11-06 ([#3](https://github.com/kadirguloglu/kg-devkit/pull/3))
- **Eklenen:** `main`'e her push'ta plugin sürümünü otomatik artıran iş akışı (`bump-version.yml`, `scripts/bump-version.py`).

## 0.4.0
- İlk kayıtlı sürüm: 11 agent, 6 skill, 3 kural, Claude plugin + marketplace ve Codex çıktısı.
