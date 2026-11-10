# 09 — Yeni bileşen önerileri ve bileşen kararları

> **Durum notu:** Bu rapor `6b14d73` (v0.8.9) commit'indeki durumu anlatır; dosya yolu ve satır numaraları o commit'e
> göredir, bağlantılar dosyaların güncel hâline gider. Bulguların uygulama durumu ve canlı deney sonuçları:
> [13-implementation-status.md](13-implementation-status.md).

İlke: yeni bileşen sayısı başarı ölçütü değildir. Aşağıda değerlendirilen adaylardan **yeni agent 0**, **yeni hook
betiği 1** (isteğe bağlı kayıt), **yeni skill 0-3** (mevcut 3 kuralın taşınması; yeni içerik değil) ve **2 ortak
referans dosyası** önerilir. Geri kalan ihtiyaçlar mevcut bileşenlerin iyileştirilmesiyle karşılanır.

## 1. Önerilen bileşenler

### N-1 — Ortak referans: varsayılan Finish gate
| Alan | Değer |
| --- | --- |
| Tür | Skill destek dosyası (`plugins/kg-devkit/references/finish-gate-default.md`) |
| Çözdüğü problem | I-01: profilde gate yoksa reviewer tetikleme tanımsız ve skill'ler arasında tutarsız |
| Neden mevcutlarla çözülemiyor | Eşleme bugün yalnız tüketici profilinde; üç skill'e ayrı ayrı yazmak S-03 tekrarını büyütür |
| Tetiklenme | `release`, `verify-change`, `add-migration` gate adımında, **yalnız** profil gate'i yoksa okunur |
| Birlikte çalıştığı | 6 reviewer, 3 skill |
| Beklenen fayda | Reviewer'lar profilsiz/eksik profilli projede de deterministik tetiklenir; "hiçbiri tetiklenmediyse çağırma" kuralı gereksiz delegasyonu keser |
| Bağlam maliyeti | 0 sürekli; okunduğunda ~450 token (tahmin, 1,8 KB) |
| Bakım maliyeti | Düşük: reviewer eklendiğinde bir satır |
| Öncelik | **P1** — [örnek](../../plugins/kg-devkit/references/finish-gate-default.md) |

### N-2 — Ortak referans: inceleme paketi ve devir sözleşmesi
| Alan | Değer |
| --- | --- |
| Tür | Skill destek dosyası (`references/review-packet.md`) + agent `description`/rapor satırları |
| Çözdüğü problem | A-01 (girdisiz reviewer çağrısı), A-03 (yazar agent'larda bitiş durumu yok) |
| Neden mevcutlarla çözülemiyor | Sözleşme iki tarafı bağlar; tek bir agent dosyasına yazmak çağıranı bilgilendirmez |
| Tetiklenme | Gate adımında skill tarafından okunur; agent tarafı `description` ve "Return" bölümünde |
| Beklenen fayda | `UNCLEAR` turlarının azalması; diff'in tek kez üretilip yol ile paylaşılması; `STATUS` ile mekanik birleştirme |
| Bağlam maliyeti | Okunduğunda ~350 token (tahmin); agent başına +2-3 satır |
| Bakım maliyeti | Düşük |
| Öncelik | **P1** — [örnek](../../plugins/kg-devkit/references/review-packet.md) |

### N-3 — Hook: agent çalıştırma kaydı
| Alan | Değer |
| --- | --- |
| Tür | Hook (`SubagentStart`, `SubagentStop`; `async`) |
| Çözdüğü problem | A-06 (`Logging` satırlarının yerine), I-03 (reviewer'ın gerçekten çalıştığına dair iz), [07](07-performance-optimization.md) metrikleri |
| Neden mevcutlarla çözülemiyor | Plugin agent'ları kendi kancasını taşıyamaz; metin tabanlı log model bağlamını kullanır ve denetlenemez |
| Tetiklenme sıklığı | Her alt-agent başlangıç ve bitişinde (görev başına birkaç kez) |
| Çalıştırma maliyeti | ~25 ms Python süreci, eşzamansız; model bağlamına 0 token |
| Olumsuz etki | Yerelde büyüyen bir JSONL dosyası (`${CLAUDE_PLUGIN_DATA}`); yalnız meta veri (agent türü, zaman, hüküm). Gizlilik: prompt/komut/rapor metni yazılmaz |
| Bakım maliyeti | Düşük (40 satır) |
| Öncelik | **P2** — [örnek](../../plugins/kg-devkit/hooks/agent_run_log.py). `SubagentStop` girdi alan adları canlıda doğrulanmalı |

### N-4 — Yol-kapsamlı disiplin skill'leri (kuralların taşınması)
| Alan | Değer |
| --- | --- |
| Tür | Skill ×3 (`test-discipline`, `docs-maintenance`, `ops-safety`), `user-invocable: false`, `paths:` |
| Çözdüğü problem | I-02: kurallar plugin ile gelmiyor |
| Neden mevcutlarla çözülemiyor | Plugin `rules/` taşıyamaz; agent gövdeleri ana oturumu kapsamaz |
| Tetiklenme | Eşleşen dosya okunduğunda/düzenlendiğinde (dokümandaki `paths` davranışı; **E-4 ile doğrulanacak**) |
| Bağlam maliyeti | Açıklamalar sürekli bağlamda: 3 × ~40-60 token (tahmin); gövde eşleşince ~250-400 token |
| Bakım maliyeti | Orta: geçiş süresince `rules/` ile çift kaynak (Codex ve mevcut symlink kullanıcıları) → tek kaynaktan üretim betiği gerekir |
| Öncelik | **P2**, E-4'e bağlı — [örnek](../../plugins/kg-devkit/skills/test-discipline/SKILL.md) |

## 2. Mevcut bileşenlerle çözülenler (yeni bileşen önerilmez)

| İhtiyaç (istenen değerlendirme alanı) | Karar | Nasıl karşılanır |
| --- | --- | --- |
| Görev karmaşıklığına göre agent seçimi / orkestratör agent | Önerme | Ana oturum zaten yönlendirici; ayrı agent bir delegasyon katmanı ekler. `description` iyileştirmesi (A-01, A-02) |
| Otomatik kod inceleme agent'ı | Önerme | Yerleşik `/code-review`; alan reviewer'ları + varsayılan gate |
| Mimari tutarlılık | Mevcut | `engineering-software-architect` |
| Test oluşturma/doğrulama | Mevcut | İki test-developer + `verify-change` |
| Güvenlik açığı tespiti | **IMPROVE** | `tenant-security-reviewer` denetim listesine girdi işleme/enjeksiyon/XSS/gömülü secret maddesi (A-07); yerleşik `/security-review` |
| Performans analizi | Mevcut | `performance-reviewer`, `database-reviewer` |
| Refactoring planlama | Mevcut | Architect (seçenekler + ADR) |
| Kök neden analizi agent'ı | Önerme | Profil-bağımlı özel akış yok; canlı ortam için `live-check` + `devops-engineer` |
| Büyük görevi parçalama | Önerme | Ana oturum + plan modu |
| Çoklu agent koordinasyonu | **IMPROVE** | Paralel başlatma kuralı ve `STATUS` sözleşmesi (N-1, N-2); koordinatör agent değil |
| Değişiklik etki analizi | Mevcut | `api-contract-reviewer` (istemci etkisi), `database-reviewer` (veri etkisi) |
| Doküman ↔ kod tutarlılığı | Mevcut | `kg-documentation-maintenance` kuralı (→ N-4); kit'in kendi reposunda `kit-doc-sync` |
| Framework standartları skill'i | Önerme | Bilinçli karar (`docs/inventory.md:78`) |
| Dependency analizi | Mevcut | `dependency-supply-chain-reviewer` |
| Context/token optimizasyonu skill'i | Önerme | Talimat değil ölçüm sorunu ([07](07-performance-optimization.md)) |
| Büyük projede kod keşfi | Önerme | Yerleşik Explore agent'ı |
| Format/lint kancası | Önerme (kit'te) | Projeye özgü; projenin kendi ayarında |
| Kritik dosya / secret commit koruması | **IMPROVE** | Mevcut kancaya kural (I-04) |
| Büyük dosya okuma engeli | Önerme | [06](06-security-reliability.md) §4 |
| Görev sonu doğrulama kancası | Ertele | Önce `verify-change` model çağrısının etkisi ölçülsün |
| Hatalı komut sınıflandırma | Önerme | Fayda kanıtı yok |
| Proje profili üretme skill'i | Değerlendir (P3) | `docs/prompts/generate-project-profile.md` manuel skill olarak paketlenebilir |

## 3. Bileşen kararları (KEEP / IMPROVE / MERGE / SPLIT / REMOVE / REPLACE)

| Bileşen | Karar | Teknik gerekçe | Olası etki |
| --- | --- | --- | --- |
| scope-advisor | IMPROVE | A-02 | Daha az delegasyon; sorunun gerçekten sorulması |
| engineering-software-architect | IMPROVE | `description`'a girdi | Küçük |
| backend-developer, frontend-developer | IMPROVE | A-03 `STATUS`; "API/sembolün varlığını doğrula" cümlesi | Yanlış "tamamlandı" riski düşer |
| backend-test-developer, frontend-test-developer | IMPROVE | A-03 | aynı |
| frontend-browser-tester | IMPROVE | A-08 (`maxTurns`), H-04 | Döngü ve takılma riski düşer |
| api-contract / database / dependency / tenant-security reviewer | IMPROVE | A-01; tenant-security için A-07 | Tek turda sonuç |
| performance-reviewer, observability-reviewer | KEEP (+`description` girdisi) | Varsayılan gate'te danışma niteliğinde | — |
| devops-engineer | IMPROVE | `description`'tan "rollback planning" → "use /rollback"; A-04 | Çift yol azalır |
| devops-operator | IMPROVE | Kural çelişkisi ([05](05-integration-analysis.md) §4) | — |
| verify-change | IMPROVE | S-02, I-01 | Model iş bitiminde doğrulamayı başlatabilir |
| release | IMPROVE | I-01, paralel reviewer, I-05 | Tutarlı gate |
| add-migration | KEEP | Gate atfı ortak referansa | — |
| rollback | IMPROVE | S-01 | Adımlar gerçekten okunur |
| live-check | KEEP | `disallowed-tools` (S-04) isteğe bağlı | — |
| browser-test | IMPROVE | S-03 tekrarı kaldır; H-04 sonucuna göre `background: false` | — |
| guard-infra.py | **REPLACE** (aynı sözleşme, yeni ayrıştırıcı) | H-01…H-07, I-04 | Daha az kaçak ve daha az gereksiz onay; daha fazla kural = daha fazla test bakımı |
| hooks.json | IMPROVE | `timeout`, `python` yedeği | — |
| rules/*.md (3) | REPLACE (E-4 olumluysa → N-4), aksi halde KEEP | I-02 | Plugin tek başına yeterli olur |
| `Logging:` paragrafları (15) | REMOVE (N-3 devreye girince) | A-06 | `kit-agent-linter` kontrol 2 ve `agent-requirements.md` güncellenmeli |
| plugin.json | IMPROVE | M-02 | — |

MERGE ve SPLIT kararı verilen bileşen yoktur (gerekçe: [02](02-agents-analysis.md) §2).

## 4. Öneri puanlaması (1-10; **tahmin**, ölçüm değil)

"Efor": 10 = çok zahmetli. Diğer sütunlarda 10 = en iyi.

| Öneri | Tür | Fayda | Uygulama kolaylığı | Token tasarrufu potansiyeli | Güvenilirlik katkısı | Bakım kolaylığı | Mimari uyum | Efor | Risk | Öncelik |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| guard v2 (H-01…H-07) | Hook | 9 | 5 | 1 | 9 | 6 | 9 | 6 | Orta (yeni yanlış pozitif/negatif) | P0 |
| `description`'da tetik + girdi (A-01, A-02) | Agent | 8 | 9 | 7 | 7 | 9 | 10 | 2 | Düşük | P1 |
| Varsayılan gate (N-1) | Skill ref. | 8 | 8 | 5 | 9 | 8 | 9 | 3 | Düşük (profil önceliği korunur) | P1 |
| İnceleme paketi + `STATUS` (N-2) | Agent/Skill | 8 | 7 | 6 | 8 | 8 | 9 | 4 | Düşük | P1 |
| `rollback` atfı (S-01) | Skill | 6 | 10 | 1 | 7 | 10 | 10 | 1 | Düşük | P1 |
| Davranış eval seti (T-01) | Test | 8 | 5 | 3 | 8 | 6 | 9 | 6 | Düşük | P1 |
| `verify-change` model çağrısı (S-02) | Skill | 6 | 9 | 2 | 6 | 9 | 9 | 1 | Düşük-Orta (istenmeyen çağrı) | P2 |
| Kayıt kancası (N-3) | Hook | 6 | 8 | 2 | 5 | 8 | 9 | 2 | Düşük | P2 |
| Kurallar → yol-kapsamlı skill (N-4) | Skill | 6 | 5 | 0 | 6 | 5 | 7 | 5 | Orta (doğrulanmamış alan; çift kaynak) | P2 |
| `hooks.json` timeout + yedek (H-05, H-06) | Hook | 5 | 10 | 0 | 6 | 10 | 10 | 1 | Düşük | P2 |
| tenant-security kapsamı (A-07) | Agent | 6 | 8 | 0 | 6 | 8 | 9 | 2 | Düşük | P2 |
| Model/`maxTurns` ayarı (A-08, A-10) | Agent | 5 | 7 | 6 | 4 | 9 | 10 | 3 | Orta (kalite düşebilir; E-5) | P2 |
| `Logging` kaldırma (A-06) | Agent | 3 | 7 | 2 | 2 | 8 | 8 | 3 | Düşük | P3 |
| Manifest alanları (M-02) | Yapılandırma | 2 | 10 | 0 | 1 | 10 | 10 | 1 | Düşük | P3 |
