# Prompt: projenin kg-devkit hazırlık raporu (soru-cevap)

kg-devkit agent ve skill'lerinin **bu projede** ne kadar çalışacağını raporlatır: hangi `Project profile` alanı dolu/eksik,
hangi agent tam çalışır, hangisi koddan çıkarımla çalışır, hangisi durur. Projenin kök dizininde Claude Code veya Codex'e ver
(kg-devkit reposunu açman gerekmez; agent/skill dosyaları projede olmayabilir, plugin'den gelir). Kit'in kendi
dokümanı için [agent-requirements.md](../agent-requirements.md); eksik alanları doldurmak için
[profil üreten prompt](generate-project-profile.md).

````markdown
Görev: Bu projenin kg-devkit agent/skill'leri için ne kadar hazır olduğunu raporla. Kod, AGENTS.md, CLAUDE.md ve diğer dosyalara
dokunma; yalnız oku. Dil: Türkçe. Önce ilgili soruların yanıtlarını projede ara. Ardından bulgu olup olmamasına bakmadan
ilgili her soruyu kullanıcıya en çok 4 soruluk gruplarla sor (AskUserQuestion varsa onu kullan).

Önemli: agent/skill dosyalarını bu repoda arama ve "bulunamadı" diye raporlama; kit plugin'den gelir. Bu prompt'taki matris tek
kaynaktır. Kit'in iç yapısını (commit, bakım agent'ları, Codex üretimi, kit tutarsızlıkları) rapora yazma.

## 1. Keşif (yalnız oku)
AGENTS.md (yoksa CLAUDE.md) içindeki `## Project profile` bölümünü oku; yoksa "profil yok" de ve repodan çıkar. Her bilgi için dayanak
dosyayı not et:
- Kiracı modeli: tek müşterili mi, çok müşterili/kiracılı mı (kod, belge, DB şeması)
- Canlı ortam: Kubernetes (context+namespace), compose/host, ya da yok (deploy/manifest/CI dosyaları)
- Frontend ve çalışan dev uygulaması var mı; dev URL ve test girişi belgeli mi
- Veri katmanı: ORM, migration komutu/dizini; API şeması/OpenAPI; paket yöneticileri ve lockfile
- App Store veya Google Play kapsamı varsa uygulama/mağaza bağlantıları, pazarlar ve diller, hedef kullanıcı ve marka dili,
  doğrulanmış özellikler, analitik olayları, veri dönemi ve mağaza varlıkları veya kanıt dosyaları
- Profilde hangi alanlar dolu: Layers/dirs, Commands, Dev app, Router/navigation files, Rule docs, Conventions, Scope mechanisms,
  Security review, Persistence, API contract, Dependencies, Performance, Observability, ASO (isteğe bağlı), SEO (isteğe bağlı), Finish gate, Release, Production,
  Report language, Hard limits

## 2. Matris (kit agent'ı / skill'i -> ihtiyaç)
Durum kuralı: gerekli alan dolu -> HAZIR; alan yok ama koddan çıkarabilir -> ÇIKARIM (raporda belirtir); zorunlu alan yok ve
agent çıkarım yapmaz -> DURUR; koşul yok -> UYGULANAMAZ.
ASO rolleri için `ASO` alanı isteğe bağlıdır. İlgili kapsam ve kanıt profilde veya çağrı girdisinde tamamlanıyorsa HAZIR,
kısmi kanıtla ilerlenebiliyorsa ÇIKARIM yaz. Eldeki kanıtla yapılabilecek işi ve eksik girdinin hangi kararı etkilediğini belirt.
Gerektiğinde güncel resmî Apple veya Google belge bölümünü çağrı girdisine eklenebilecek kanıt olarak belirt.
Mağaza kapsamında iş yoksa UYGULANAMAZ yaz.

| Agent / skill | Alanlar | Alan yoksa |
| --- | --- | --- |
| `backend-developer` | Layers/dirs, Commands, Rule docs, Conventions, Persistence, Hard limits | ÇIKARIM |
| `backend-test-developer` | Layers/dirs, Commands, Rule docs (testler), Hard limits; tenancy/soft delete kuralları yalnız profil bildiriyorsa | ÇIKARIM |
| `frontend-developer` | Layers/dirs, Commands, Rule docs, Hard limits | ÇIKARIM |
| `frontend-test-developer` | Commands, Rule docs (testler), Hard limits | ÇIKARIM |
| `database-reviewer` | Persistence, Conventions, Rule docs | ÇIKARIM |
| `tenant-security-reviewer` | Security review, Conventions, Persistence (filtre bypass API'leri), teknik doküman bölümleri (güvenlik, depolama, arka plan işleri) | ÇIKARIM; kiracı yoksa düz yetki/sahiplik ve girdi işleme (enjeksiyon, XSS, secret) incelemesi |
| `api-contract-reviewer` | API contract, Layers/dirs, Conventions (hata/Result) | ÇIKARIM |
| `dependency-supply-chain-reviewer` | Dependencies, Hard limits | ÇIKARIM |
| `performance-reviewer` | Performance, Layers/dirs, Commands | ÇIKARIM (bütçeyi varsayar, söyler) |
| `observability-reviewer` | Observability, Conventions (hata), Rule docs | ÇIKARIM |
| `seo-lead` | SEO (isteğe bağlı), Report language | SEO profili yoksa repo/istek kanıtıyla kapsamlar; eksikleri bildirir |
| `seo-technical-specialist` | SEO framework/site/sitemap/markets (isteğe bağlı) | İlgili kaynakları ve verilen kanıtı inceler; canlı davranış doğrulanmadıysa söyler |
| `seo-keyword-research-specialist` | SEO markets/languages/audience/pages/competitors (isteğe bağlı) | Gerçek arama verisi yoksa hacim/zorluk uydurmaz; nitel hipotezleri işaretler |
| `seo-content-strategist` | SEO audience/markets/languages/pages/constraints (isteğe bağlı) | Verilen sayfaları inceler; doğrulanmamış ürün/hukuk/tıp iddiası eklemez |
| `seo-offpage-specialist` | SEO site/market/competitors (isteğe bağlı), backlink evidence | Veri yoksa profil analizi yapmaz; ücretli/manipülatif link önermez |
| `seo-data-analyst` | SEO conversion goals, analytics/Search Console, baseline (isteğe bağlı) | Export yoksa ölçüm planı verir; Search Console clicks ≠ GA4 sessions |
| `seo-ai-search-specialist` | SEO site/markets/languages/brand facts (isteğe bağlı) | Canlı gözlem yoksa hipotez der; citation veya özel sıralama faktörü garanti etmez |
| `seo-local-international-specialist` | SEO business type, countries/languages/URLs (isteğe bağlı) | Yerel veya uluslararası hedef yoksa `NOT-APPLICABLE` döner |
| `scope-advisor` | Scope mechanisms, Report language | `Scope mechanisms` yoksa çağrılmaz; yalnız limit/varsayılan/kural/format/izin/bildirim/isteğe bağlı akış değişikliğinde çağrılır; tek müşterili projede UYGULANAMAZ (`NOT-APPLICABLE`) |
| `engineering-software-architect` | Layers/dirs, Conventions, Scope mechanisms, Rule docs, Finish gate | ÇIKARIM |
| `aso-lead` | ASO (isteğe bağlı), hedef, pazar ve platformlar, eldeki kanıt ve varsa uzman raporları | Mevcut girdiden kapsam, öncelik ve uzmanların ihtiyaçlarını çıkarır |
| `aso-search-specialist` | ASO (isteğe bağlı), hedef, mağaza bağlantıları veya görüntüleri, varsa arama ve rakip kanıtı | Mevcut kanıtla terim hipotezleri ve doğrulama ihtiyaçları çıkarır |
| `aso-copy-localization-specialist` | ASO (isteğe bağlı), hedef diller ve pazarlar, listeleme veya brief, marka dili, doğrulanmış özellikler ve varsa arama bulguları | Kanıtın desteklediği taslağı yazar ve doğrulama gerektiren noktaları belirtir |
| `aso-creative-specialist` | ASO (isteğe bağlı), dönüşüm hedefi, pazarlar, mevcut varlık veya taslaklar, doğrulanmış faydalar ve varsa performans kanıtı | Mevcut kanıtla görsel brief ve hipotezler çıkarır |
| `aso-growth-analyst` | ASO (isteğe bağlı), ölçüm dönemi, mağaza ve uygulama içi ölçümler, olay tanımları, trafik kırılımı ve varsa deney verisi | Eldeki ölçümü kullanır. Veri veya örneklem yetersizse kazanan ilan etmez. |
| `aso-release-reviewer` | ASO (isteğe bağlı), varsa profildeki reviewer geçme ifadesi, hedef platform/pazar, mağaza taslağı veya diff, değişen varlıklar ve varsa ölçüm kanıtı | Hüküm için gereken kanıt eksikse `NEEDS:` ile bildirir ve `VERDICT: UNCLEAR` döner. |
| `frontend-browser-tester`, `browser-test` | Dev app (URL + yerel test girişi), Commands (start/status), Router/navigation files, Layers/dirs, Hard limits; Claude in Chrome eklentisi | URL veya test girişi yoksa DURUR |
| `devops-engineer` | Production, Report language, Hard limits | Production yoksa yalnız statik dosyaya bakar; canlı komuttan önce hedefi sorar |
| `devops-operator` | Production (hedef, secret konumları, registry, topoloji, runbook), Hard limits | DURUR |
| `live-check` | Production (context, namespace, durum komutu, bulut CLI kimlik komutu, iş yükleri, sağlık URL'leri + beklenen kodlar, runbook) | Production veya zorunlu hedef/sağlık bilgileri yoksa DURUR |
| `rollback` | Production (hedef, rollback/deploy komutu, sağlık URL'leri + beklenen kodlar, iş yükleri, registry, kanıt yöntemlerini belirten runbook), Persistence (migrations dizini) | Production veya hedef/sağlık bilgileri yoksa DURUR; başarılı release, image → kaynak/revision ve uygulanan şema kanıtı eksikse uygulama DURUR |
| `release` | Release, Commands, Finish gate, `AGENTS.md`/`CLAUDE.md` sınırları; `deploy` ile Production (hedef, deploy/durum komutu, sağlık URL'leri + beklenen kodlar) | Release yoksa sorar; deploy için Production bilgileri eksikse DURUR; Finish gate yoksa kit'in varsayılan gate tablosu kullanılır; zorunlu review yoksa/FAIL/UNCLEAR ise commit DURUR |
| `add-migration` | Persistence, Conventions, Finish gate, Report language | Persistence yoksa ORM aracını bulur, çalıştırmadan önce onaylatır; Finish gate yoksa kit'in varsayılan gate tablosu kullanılır; gate belirsizse veya zorunlu review yoksa/FAIL/UNCLEAR ise doğrulama DURUR |
| `verify-change` | Commands, Rule docs, Finish gate, Report language | ÇIKARIM; Finish gate yoksa kit'in varsayılan gate tablosu kullanılır; zorunlu review yoksa/FAIL/UNCLEAR ise doğrulama DURUR |

Deploy/sağlık değerlerini Production'da ara; yalnız orada eksik olan değerler eski Release girdisinden alınabilir.
İki kaynaktaki değerler çelişirse ilgili işlem DURUR. Rollback için başarılı release kanıtı, image digest → kaynak
commit/revision eşlemesi ve uygulanan şemanın salt-okunur doğrulama yöntemini runbook'tan kontrol et; Git geçmişini
tek başına canlı şema kanıtı sayma. Gerekli reviewer yoksa veya sonucu FAIL/UNCLEAR ise doğrulamayı geçmiş gösterme.

Her agent ve skill ayrıca profildeki `Report language`'ı izler; `Hard limits` yalnız matriste yazan satırlarda okunur ve yalnız kısıt ekler. Commit/push yok (yalnız `release` kullanıcı
çağırınca commit+push yapar). Plugin kancası canlıyı değiştiren veya secret okuyan komutları, migration/dağıtım araçlarını ve `git push --force`/`reset --hard`/`clean -f`/secret dosyası `git add` komutlarını, ayrıca bir kit agent'ının içinden gelen `git commit`/`push`/`merge`/`rebase`/`tag`/`cherry-pick`/`revert` komutlarını onaya düşürür (ana oturumun commit'i etkilenmez; yalnız Claude'da; `KG_GUARD_DISABLE`, `KG_GUARD_LOCAL_COMPOSE` ortam değişkenleri bazı grupları gevşetir).
`test-discipline`, `docs-maintenance`, `ops-safety` kural skill'leri profil alanı gerektirmez; skill'lerdeki sınırları profil kaldıramaz, yalnız ekleyebilir.
Agent'lar profili bağlamda görüyorsa dosyayı yeniden okumaz: hem `AGENTS.md` hem `CLAUDE.md` varsa ve profil `AGENTS.md` içindeyse `CLAUDE.md`'de `@AGENTS.md` satırı olmalı, yoksa ana oturum profili görmez (bunu uyarı olarak raporla).

## 3. Eşleştirme ve soru-cevap
Keşif bulgularını matrisle eşleştir ve hazır olma durumunu etkileyen soruları belirle. Kiracı modeli, canlı ortam türü ve
hedefi, tarayıcı testi ihtiyacı, `Finish gate` ve `Hard limits` gibi ilgili başlıkları kullanıcıya sor.

- Bir cevap bulduysan değeri ve `yol:satır` dayanağını paylaş. Güncel ve doğru olduğunu doğrulat veya düzeltmesini iste.
- Kaynaklar çelişiyorsa aday değerleri dayanaklarıyla paylaş ve hangisinin geçerli olduğunu sor.
- Cevap bulamadıysan baktığın dosyaları kısaca belirt ve bilgiyi kullanıcıdan iste.

Mağaza kapsamı olan projelerde ilgili ASO girdilerini de aynı şekilde sor. Gizli değerler için yalnız dosya yolunu belirt.
Kullanıcının bu oturumda yanıtladığı soruyu tekrarlama. Bulguları yanıtlara göre güncelle ve her agent ve skill'in durumunu
matrisle belirle. Kullanıcı "geç" derse ilgili durumu "BELİRSİZ" bırak.

## 4. Çıktı (sohbette; dosya yazma)
1. **Özet tablo:** agent/skill | durum (HAZIR / ÇIKARIM / DURUR / UYGULANAMAZ / BELİRSİZ) | neden (eksik alan veya dayanak).
2. **Eksik alanlar:** alan -> hangi agent/skill'i açar/iyileştirir; etkisi büyükten küçüğe sırala.
3. **Bu projeye özgü uyarılar:** örn. çok müşterili ama `Scope mechanisms` yok, canlı ortam var ama `Production` yok.
4. **Sonraki adım:** eksik alanlar için kg-devkit "Project profile üreten prompt"unu çalıştırmayı öner (içeriğini kendin yazma).
Raporu kullanıcı isterse `docs/kg-devkit-hazirlik.md` olarak kaydet (önce sor); başka dosyaya dokunma. Commit ve push yapma.
````
