# Değişiklik günlüğü

Sürümler `main`'e her push'ta otomatik artar (`bump-version.yml`): varsayılan patch, merge mesajında `[minor]`/`[major]`
ile seviye seçilir. Bu dosya kullanıcıya dönük etkiyi özetler; taslağı `kit-release-notes` agent'ı çıkarır
(bkz. [docs/inventory.md](docs/inventory.md)). Kategoriler: **Kırıcı**, **Eklenen**, **Değişen**, **Düzeltilen**, **Doküman/Altyapı**.

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
