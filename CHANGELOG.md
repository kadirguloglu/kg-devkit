# Değişiklik günlüğü

Sürümler `main`'e her push'ta otomatik artar (`bump-version.yml`): varsayılan patch, merge mesajında `[minor]`/`[major]`
ile seviye seçilir. Bu dosya kullanıcıya dönük etkiyi özetler; taslağı `kit-release-notes` agent'ı çıkarır
(bkz. [docs/inventory.md](docs/inventory.md)). Kategoriler: **Kırıcı**, **Eklenen**, **Değişen**, **Düzeltilen**, **Doküman/Altyapı**.

## Yayınlanmadı (öneri: `[minor]`)
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
