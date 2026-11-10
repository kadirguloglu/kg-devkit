# 02 — Agent analizi

Kapsam: `plugins/kg-devkit/agents/` altındaki 15 dosyanın tamamı. Bulgu ID'leri
[10-improvement-roadmap.md](10-improvement-roadmap.md) tablosundaki satırlarla aynıdır. Çalışma zamanı davranışına dair
ifadeler resmi dokümana dayanır ([08-best-practices.md](08-best-practices.md)); agent'lar bu analizde gerçek bir tüketici
projede **çalıştırılmadı**, bu nedenle seçim doğruluğu ve çıktı kalitesi ölçülmedi.

## 1. Sistem düzeyinde bulgular

### A-01 (P1) — Girdi sözleşmesi çağıranın göremediği yerde
Altı reviewer'ın tamamı gövdede "The main session supplies the diff, changed files and … evidence" der
(örn. [database-reviewer.md:10-11](../agents/database-reviewer.md), [api-contract-reviewer.md:10-12](../agents/api-contract-reviewer.md)).
Ana oturum agent'ın gövdesini görmez; delegasyon kararını ve prompt'u yalnız `description` alanına bakarak verir.
Hiçbir reviewer `description`'ı gereken girdiyi söylemez (satır 3). Reviewer'larda `Bash` olmadığı için diff'i kendileri
de üretemez. Sonuç: ana oturum "değişikliğimi incele" diye çağırırsa reviewer ya tüm dosyaları okuyup neyin değiştiğini
tahmin eder ya da `UNCLEAR` döner ve ikinci bir tur gerekir.
**Çözüm:** girdiyi `description`'a taşı ve tek bir "inceleme paketi" tanımla
([örnek agent](proposals/agents/database-reviewer.proposed.md), [paket](proposals/references/review-packet.md)).

### A-02 (P1) — `scope-advisor` aşırı tetikleniyor ve zorunluluğu yanlış yerde
- `description` "Before planning ANY new feature, improvement or fix request in a multi-tenant product" der
  ([scope-advisor.md:3](../agents/scope-advisor.md)). Ana oturum her özellik/düzeltme isteğinde bir alt-agent başlatmaya
  yönlendirilir. Tek müşterili projede agent başlar, profili okur ve `NOT-APPLICABLE` döner (satır 13-15): boşa giden bir
  delegasyon. Oysa `Scope mechanisms` girdisinin varlığını ana oturum kendi bağlamındaki profilden görebilir.
- "The main session MUST put your question to the user using … AskUserQuestion" (satır 44-46) agent'ın kendi sistem
  prompt'undadır; ana oturum bunu okuyamaz. Kural yalnız agent raporunda tekrar edilirse etkili olur.
**Çözüm:** [örnek](proposals/agents/scope-advisor.proposed.md) — tetik koşulu `description`'da, eylem talimatı dönen raporda.

### A-03 (P1) — Yazar agent'larda bitiş durumu ve başarı ölçütü yok
Reviewer'lar `VERDICT:` satırıyla biter; 6 yazar agent serbest metin döner ("Return changed paths, … actual checks",
[backend-developer.md:26-29](../agents/backend-developer.md)). Build başarısız olduysa veya test koşmadıysa bunu ayırt
edecek sabit bir alan yoktur; ana oturum raporu "tamamlandı" olarak okuyabilir. Ayrıca developer agent'lar test dosyasına
dokunamaz (satır 16-17) ama "Tests: only the changed behavior …" koşmaları istenir (satır 27-28): yeni davranışın testi
henüz yazılmamışsa "testler geçti" ifadesi yalnız eski testleri kapsar.
**Çözüm:** `STATUS: DONE | PARTIAL | BLOCKED` + `CHECKS` / `NOT RUN` satırları ([paket](proposals/references/review-packet.md)).

### A-04 (P2) — Onay "kulaktan dolma", ayrıcalık ayrımı yalnız metinde
`devops-operator` "only when the main session passes the user's explicit approval" der
([devops-operator.md:13-15](../agents/devops-operator.md)). Alt-agent bu onayın gerçekten verildiğini doğrulayamaz;
prompt'ta yazan bir cümledir. `devops-engineer` ile araç listesi birebir aynıdır (ikisi de satır 5), yani ayrım model
katmanı ve talimat metninden ibarettir. Gerçek kullanıcı onayını üreten tek mekanizma `PreToolUse` kancasıdır; onun
kapsamı ise dardır ([H-01, H-02](04-hooks-analysis.md)). Kanca girdisinde `agent_type` bulunduğu için (resmi doküman)
onay mesajına hangi agent'ın çalıştırdığı eklenebilir; prototipte yapıldı.

### A-05 (P2) — Profil muhtemelen iki kez okunuyor (ölçülmeli)
15 agent'ın hepsi "First read the `Project profile` section of the repo's `AGENTS.md` (or `CLAUDE.md`)" ile başlar
(satır 10 civarı). Resmi dokümana göre özel alt-agent'lar `CLAUDE.md` hiyerarşisini zaten yükler ve `AGENTS.md`
v2.1.277'den beri `CLAUDE.md` yokken doğal olarak okunur. Bu doğruysa her çağrıda profil dosyası bir kez sistem
bağlamında, bir kez de `Read` çıktısı olarak yer alır. Bu çıkarım dokümanın özet kısmına dayanır; **canlıda ölçülmedi**
(yöntem: [07](07-performance-optimization.md) §4, deney E-2).
**Çözüm:** "bağlamında görüyorsan yeniden okuma" koşulu (örnek agent'ta var).

### A-06 (P2) — `Logging:` paragrafı düşük değerli tekrar
Her agent'ın 8. satırı aynı paragraftır; yazar agent'larda son satırdaki `Hard limits` cümlesiyle birlikte toplam
6.274 bayt (agent metninin %12,5'i; ölçüm: `grep -E '^(Logging:|The profile.s `Hard limits`)' | wc -c`). "İlk çıktı
satırı" yalnız transkriptte görünür; ana oturuma dönen tek şey son mesajdır. Aynı bilgi `SubagentStart/Stop` kancasıyla
model bağlamına hiç girmeden kaydedilebilir ([örnek](proposals/hooks/agent_run_log.py)). Çağrı başına kazanç küçüktür
(~80-130 token tahmini); asıl fayda [07](07-performance-optimization.md)'deki metriklerin ham verisidir.

### A-07 (P2) — Genel uygulama güvenliği sahipsiz, ad yanıltıcı
`tenant-security-reviewer` yetki, CSRF/CORS, SSRF ve yükleme yollarını kapsar
([tenant-security-reviewer.md:19-31](../agents/tenant-security-reviewer.md)) fakat enjeksiyon (SQL/komut/şablon), XSS,
koda gömülü secret ve kriptografi kullanımı hiçbir reviewer'ın listesinde yoktur. Ad "tenant" içerdiği için kiracısız
projelerde ana oturumun bu agent'ı güvenlik incelemesi için seçme olasılığı düşer.
**Çözüm:** yeni agent değil; denetim listesine bir madde ve `description`'a "any authentication/authorization or
input-handling change, with or without tenants" ifadesi. Ad korunur (profil gate'lerinde geçiyor).

### A-08 (P2) — `frontend-browser-tester`
- `Bash` sınırsızdır ([satır 5](../agents/frontend-browser-tester.md)); "never edit code" yalnız metindir.
- `maxTurns` yok; "tool fails 2–3 times → stop" (satır 51-52) tek döngü freni ve modele bırakılmış.
- Yalnız Claude in Chrome araçlarını sayar; uzantı bağlı değilse agent çalışır ama test yapamaz.
- `browser-test` skill'i `context: fork` ile çalıştırır; servisleri başlatma adımı (satır 35) tipik olarak
  `docker compose up` olur ve kanca onaya düşürür ([H-04](04-hooks-analysis.md)).

### A-09 (P2) — Çakışan denetim maddeleri
| Konu | Agent A | Agent B | Durum |
| --- | --- | --- | --- |
| Log/hatalarda hassas veri | tenant-security:26 "sensitive data in DTOs/logs/errors" | observability:21-22 | yönlendirme cümlesi yok → çift bulgu |
| Sayfalama / sınırsız liste | database-reviewer:29-30 "unpaged lists" | performance-reviewer:20-21 "missing pagination at the API layer" | katman ayrımı var ama sınır bulanık |
| Rollback planı / olay teşhisi | devops-engineer `description`:3 | `rollback` ve `live-check` skill'leri | aynı iş iki yoldan başlar ([05](05-integration-analysis.md) §9) |
| CI dosyaları | dependency-reviewer:30 (pinleme/güven) | devops-engineer:15 (sahiplik) | açıkça ayrılmış ✔ |

### A-10 (P2) — Model katmanı ölçüme dayanmıyor
5 agent `opus`. `dependency-supply-chain-reviewer` 0.8.1'de "diğer güvenlik reviewer'larıyla aynı katman" gerekçesiyle
`opus` yapıldı (CHANGELOG), fakat agent çevrimdışıdır ve paket itibarını doğrulayamaz
([satır 23-24](../agents/dependency-supply-chain-reviewer.md)); işi çoğunlukla manifest/lockfile karşılaştırmasıdır.
`effort` ve `maxTurns` alanları hiçbir agent'ta kullanılmıyor. Katman değişikliği **öneri değil, deney konusudur**
([11-test-strategy.md](11-test-strategy.md) §4).

## 2. Agent bazlı değerlendirme

Puanlar bu analizdeki statik incelemeye dayalı **tahmindir** (ölçüm değil). Ölçütler: sorumluluk netliği (25),
seçilebilirlik/`description` (20), en az yetki (15), doğrulama ve bitiş sözleşmesi (20), verimlilik (10), hata davranışı (10).

| Agent | Puan | Güçlü yan | Temel sorunlar | Karar |
| --- | ---: | --- | --- | --- |
| scope-advisor | 66 | Hüküm kümesi net; `NOT-APPLICABLE` çıkışı var | A-02 (aşırı tetik, görünmez MUST) | IMPROVE |
| engineering-software-architect | 78 | Sabit başlıklı çıktı, "Not verified" bölümü | A-01 (soru+kod girdisi `description`'da yok); ADR konumu profilde tanımlı değil | IMPROVE (küçük) |
| backend-developer | 73 | Sahiplik sınırı ve "do not flag documented exceptions" | A-03; "Substantial" eşiği tanımsız | IMPROVE |
| backend-test-developer | 76 | "never skip or weaken assertions", kapsam listesi | A-03; `description` "after a building change" belirsiz | IMPROVE |
| frontend-developer | 74 | "Report missing API behavior instead of inventing" | A-03 | IMPROVE |
| frontend-test-developer | 76 | Ortam hatası / uygulama hatası ayrımı | A-03; backend eşiyle ~%70 ortak metin | IMPROVE |
| frontend-browser-tester | 70 | PASS/FAIL/COULD NOT RUN; `[UI-TEST]` veri kuralı | A-08, H-04 | IMPROVE |
| api-contract-reviewer | 82 | "concrete client call that breaks" kanıt şartı | A-01 | IMPROVE (yalnız `description`) |
| database-reviewer | 84 | "needs measurement" kuralı; kapsam/kapsam dışı raporu | A-01 | IMPROVE (yalnız `description`) |
| dependency-supply-chain-reviewer | 77 | "never assert reputation from memory" | A-01, A-10 | IMPROVE |
| tenant-security-reviewer | 77 | İstek izleme yöntemi (claims → sorgu → yanıt) | A-01, A-07, A-09 | IMPROVE |
| performance-reviewer | 80 | Ölçümsüz bulguyu işaretler | A-01; varsayılan gate'te danışma niteliğinde olmalı | KEEP + `description` |
| observability-reviewer | 80 | "undiagnosable failure" somutluk şartı | A-01, A-09 | KEEP + `description` |
| devops-engineer | 75 | Onaysız/onaylı işlem listesi açık | A-04; `description` skill'lerle çakışıyor | IMPROVE |
| devops-operator | 74 | Adım adım, "stop on any surprise" | A-04; `rules/kg-ops-safety.md:15` ile secret okuma çelişkisi | IMPROVE |

**MERGE/SPLIT/REMOVE adayı yok.** Değerlendirilen ve reddedilen seçenekler:
- *backend/frontend-test-developer birleştirme:* metin benzerliği yüksek, ancak adlar tüketici profillerinde ve Codex
  çıktısında geçiyor; kazanç bir `description` (~50-70 token). Kullanım verisi olmadan kırıcı değişikliğe değmez.
- *performance + observability birleştirme:* denetim listeleri ayrık; birleşik agent daha uzun ve daha az odaklı olur.
- *devops-engineer + operator birleştirme:* model katmanı ayrımı (sonnet/opus) ve "her adımda onay" disiplini kaybolur.

## 3. Koordinasyon

| Soru | Mevcut durum | Değerlendirme |
| --- | --- | --- |
| Paralel çalışabilecekler | 6 reviewer (salt-okuma, birbirinden bağımsız); backend ve frontend developer (ayrık dizin sahipliği) | Hiçbir dosyada "paralel başlat" talimatı yok; skill'ler reviewer'ları tek tek anar → öneri: [finish-gate-default](proposals/references/finish-gate-default.md) kural 1 |
| Sıralı bağımlılık | developer → test-developer → reviewer → (ana oturum) commit | Sıra yalnız `description` ifadelerinden ("after a building change") çıkarılıyor; yazılı akış yok |
| Aynı dosyaya eşzamanlı yazım | Dizin sahipliği (backend/frontend/test/deploy) çakışmayı metinle önler | Ortak dosyalar (üretilen API tipleri, changelog, doküman) sahipsiz: iki developer aynı anda dokunabilir → paralel çalıştırmada bunlar ana oturuma bırakılmalı |
| Çıktı birleştirme | Ana oturum serbest metin raporları okur | A-03 çözümüyle `STATUS`/`VERDICT` satırları birleştirmeyi mekanikleştirir |
| Sonsuz delegasyon | `tools` listelerinde `Agent` yok; "Do not spawn agents" | Yapısal olarak kapalı ✔ (dokümana göre alt-agent'lar aksi halde 3 katmana kadar başlatabilir) |
| Ana oturumun çözebileceği iş | developer `description`'ları "not routine edits" der | Doğru yönde; eşik ölçülebilir değil ("Substantial") → öneri: "birden çok katman/dosya ve bağımsız doğrulama gerektiren" |

## 4. Kalite kontrol özeti

| Ölçüt | Reviewer'lar | Yazar agent'lar | Danışmanlar |
| --- | --- | --- | --- |
| Kendi işini doğrulama | Komut çalıştıramaz; kanıtı çağırandan ister | build/lint/odaklı test | — |
| Hata durumunda davranış | `UNCLEAR` + eksik olan | "report broken tests", serbest metin | "label anything unverified" |
| Test sorumluluğu | "missing tests" raporlar | developer koşar, test-developer yazar | — |
| Başarı ölçütü | `VERDICT:` ✔ | **yok** (A-03) | sabit başlıklar (architect) |
| Yanlış "tamamlandı" riski | Düşük (hüküm zorunlu) | **Orta** | Düşük |
