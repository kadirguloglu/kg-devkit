# Prompt: projenin kg-devkit hazırlık raporu (soru-cevap)

kg-devkit agent ve skill'lerinin **bu projede** ne kadar çalışacağını raporlatır: hangi `Project profile` alanı dolu/eksik,
hangi agent tam çalışır, hangisi koddan çıkarımla çalışır, hangisi durur. Projenin kök dizininde Claude Code veya Codex'e ver
(kg-devkit reposunu açman gerekmez; agent/skill dosyaları projede olmayabilir, plugin'den gelir). Kit'in kendi
dokümanı için [agent-requirements.md](../agent-requirements.md); eksik alanları doldurmak için
[profil üreten prompt](generate-project-profile.md).

````markdown
Görev: Bu projenin kg-devkit agent/skill'leri için ne kadar hazır olduğunu raporla. Kod, AGENTS.md, CLAUDE.md ve diğer dosyalara
dokunma; yalnız oku. Dil: Türkçe. SORU-CEVAP yürüt: repodan cevaplanabilen hiçbir şeyi sorma; yalnız çözülemeyen
noktaları en çok 4 soruluk gruplarla (AskUserQuestion varsa onunla) sor.

Önemli: agent/skill dosyalarını bu repoda arama ve "bulunamadı" diye raporlama; kit plugin'den gelir. Bu prompt'taki matris tek
kaynaktır. Kit'in iç yapısını (commit, bakım agent'ları, Codex üretimi, kit tutarsızlıkları) rapora yazma.

## 1. Keşif (yalnız oku)
AGENTS.md (yoksa CLAUDE.md) içindeki `## Project profile` bölümünü oku; yoksa "profil yok" de ve repodan çıkar. Her bilgi için dayanak
dosyayı not et:
- Kiracı modeli: tek müşterili mi, çok müşterili/kiracılı mı (kod, belge, DB şeması)
- Canlı ortam: Kubernetes (context+namespace), compose/host, ya da yok (deploy/manifest/CI dosyaları)
- Frontend ve çalışan dev uygulaması var mı; dev URL ve test girişi belgeli mi
- Veri katmanı: ORM, migration komutu/dizini; API şeması/OpenAPI; paket yöneticileri ve lockfile
- Profilde hangi alanlar dolu: Layers/dirs, Commands, Dev app, Router/navigation files, Rule docs, Conventions, Scope mechanisms,
  Security review, Persistence, API contract, Dependencies, Performance, Observability, Finish gate, Release, Production,
  Report language, Hard limits

## 2. Matris (kit agent'ı / skill'i -> ihtiyaç)
Durum kuralı: gerekli alan dolu -> HAZIR; alan yok ama koddan çıkarabilir -> ÇIKARIM (raporda belirtir); zorunlu alan yok ve
agent çıkarım yapmaz -> DURUR; koşul yok -> UYGULANAMAZ.

| Agent / skill | Alanlar | Alan yoksa |
| --- | --- | --- |
| `backend-developer` | Layers/dirs, Commands, Rule docs, Conventions, Persistence, Hard limits | ÇIKARIM |
| `backend-test-developer` | Layers/dirs, Commands, Rule docs (testler), Hard limits; tenancy/soft delete kuralları yalnız profil bildiriyorsa | ÇIKARIM |
| `frontend-developer` | Layers/dirs, Commands, Rule docs, Hard limits | ÇIKARIM |
| `frontend-test-developer` | Commands, Rule docs (testler), Hard limits | ÇIKARIM |
| `database-reviewer` | Persistence, Conventions, Rule docs | ÇIKARIM |
| `tenant-security-reviewer` | Security review, Conventions, Persistence (filtre bypass API'leri), teknik doküman bölümleri (güvenlik, depolama, arka plan işleri) | ÇIKARIM; kiracı yoksa düz yetki/sahiplik incelemesi |
| `api-contract-reviewer` | API contract, Layers/dirs, Conventions (hata/Result) | ÇIKARIM |
| `dependency-supply-chain-reviewer` | Dependencies, Hard limits | ÇIKARIM |
| `performance-reviewer` | Performance, Layers/dirs, Commands | ÇIKARIM (bütçeyi varsayar, söyler) |
| `observability-reviewer` | Observability, Conventions (hata) | ÇIKARIM |
| `scope-advisor` | Scope mechanisms, Report language | tek müşterili projede UYGULANAMAZ (`NOT-APPLICABLE`) |
| `engineering-software-architect` | Layers/dirs, Conventions, Scope mechanisms, Rule docs, Finish gate | ÇIKARIM |
| `frontend-browser-tester`, `browser-test` | Dev app (URL + yerel test girişi), Commands (start/status), Router/navigation files, Layers/dirs, Hard limits; Claude in Chrome eklentisi | URL veya test girişi yoksa DURUR |
| `devops-engineer` | Production, Report language, Hard limits | Production yoksa yalnız statik dosyaya bakar; canlı komuttan önce hedefi sorar |
| `devops-operator` | Production (hedef, secret konumları, registry, topoloji, runbook), Hard limits | DURUR |
| `live-check` | Production (context, namespace, durum komutu, bulut CLI kimlik komutu, iş yükleri, sağlık URL'leri + beklenen kodlar, runbook) | DURUR |
| `rollback` | Production (hedef, rollback/deploy komutu, sağlık URL'leri, iş yükleri, registry, runbook), Persistence (migrations dizini) | DURUR |
| `release` | Release, Commands, Finish gate, Hard limits; `deploy` ile Production | Release yoksa kullanıcıya sorar |
| `add-migration` | Persistence, Conventions, Finish gate, Report language | ORM aracını repoda bulur, çalıştırmadan önce onaylatır |
| `verify-change` | Commands, Rule docs, Finish gate, Report language | ÇIKARIM |

Her agent ve skill ayrıca profildeki `Report language`'ı izler; `Hard limits` yalnız matriste yazan satırlarda okunur ve yalnız kısıt ekler. Commit/push yok (yalnız `release` kullanıcı
çağırınca commit+push yapar). Plugin kancası canlıyı değiştiren komutları onaya düşürür (yalnız Claude'da).

## 3. Eşleştirme ve soru-cevap
Keşif bulgularını matrisle eşleştirip her agent/skill için durumu belirle. Şunlar kaynaktan çözülemezse sor (çözülürse sorma):
kiracı modeli, canlı ortam türü/hedefi, tarayıcı testi istenip istenmediği, `Finish gate`/`Hard limits` belgede yoksa gerçekten
yok mu. Çıkarım yapabildiğin şeyi sorma; "geç" denirse durumu "BELİRSİZ" bırak.

## 4. Çıktı (sohbette; dosya yazma)
1. **Özet tablo:** agent/skill | durum (HAZIR / ÇIKARIM / DURUR / UYGULANAMAZ / BELİRSİZ) | neden (eksik alan veya dayanak).
2. **Eksik alanlar:** alan -> hangi agent/skill'i açar/iyileştirir; etkisi büyükten küçüğe sırala.
3. **Bu projeye özgü uyarılar:** örn. çok müşterili ama `Scope mechanisms` yok, canlı ortam var ama `Production` yok.
4. **Sonraki adım:** eksik alanlar için kg-devkit "Project profile üreten prompt"unu çalıştırmayı öner (içeriğini kendin yazma).
Raporu kullanıcı isterse `docs/kg-devkit-hazirlik.md` olarak kaydet (önce sor); başka dosyaya dokunma. Commit ve push yapma.
````
