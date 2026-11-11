# 12 — Mimari öneriler (nihai)

> **Durum notu:** Bu rapor `6b14d73` (v0.8.9) commit'indeki durumu anlatır; dosya yolu ve satır numaraları o commit'e
> göredir, bağlantılar dosyaların güncel hâline gider. Bulguların uygulama durumu ve canlı deney sonuçları:
> [13-implementation-status.md](13-implementation-status.md).

Bu dosya kararları toplar; kanıt ve ayrıntı için ID'lerle diğer raporlara gider. Hiçbir öneri uygulanmamıştır.

## 1. Mevcut mimarinin özeti

kg-devkit üç fikir üzerine kuruludur ve üçü de sağlamdır:

1. **Profil dolaylaması.** Proje bilgisi agent'lara gömülmez; her repo `## Project profile` ile kendini tanıtır.
2. **Rol başına dar agent + en az yetki.** 15 agent; reviewer ve danışmanlar yalnız `Read, Grep, Glob`; hiçbir agent
   başka agent başlatamaz; reviewer'lar `VERDICT` ile biter.
3. **Yetkili işler manuel skill, canlı ortam için deterministik fren.** 6 skill yalnız kullanıcı komutuyla; tek kanca
   riskli altyapı komutlarını onaya düşürür.

Zayıflıklar bileşenlerin kendisinde değil, **aralarındaki bağlantılarda** toplanır:

- Çağıran ile agent arasındaki sözleşme çağıranın görmediği yerde yazılı (A-01, A-02, A-03).
- "Hangi değişiklik hangi reviewer'ı ister" bilgisi kit'te yok; tümüyle tüketici profiline bırakılmış (I-01).
- Tek deterministik fren dar ve gürültülü (H-01, H-02, H-03).
- Ana oturumun disiplin kuralları plugin ile gelmiyor (I-02); modelin çağırabildiği skill yok (S-02).
- Davranış hiç ölçülmüyor (T-01).

## 2. Üç alternatif

### A — Minimal
5 agent (`implementer`, `test-writer`, `reviewer` [tek, bölümlü denetim listesi], `architect`, `ops`), 4 skill
(`verify-change`, `release`, `rollback`+`live-check`, `add-migration`), 1 kanca (v2).

| | |
| --- | --- |
| Avantaj | En küçük sürekli bağlam (tahminen 15 yerine 5 açıklama); seçim hatası olasılığı düşük; bakım yüzeyi küçük |
| Dezavantaj | Tek `reviewer` her çağrıda tüm denetim listelerini taşır veya hangi bölümün uygulanacağını kendisi seçer; paralel bağımsız inceleme ve alan başına model katmanı kaybolur; backend/frontend sahiplik ayrımı (paralel çalışmanın dayanağı) kalkar; **tüm adlar değişir** → profiller, Codex çıktısı ve dokümanlar kırılır |
| Token etkisi (beklenti) | Sürekli bağlam azalır (~1,5k'nın bir kısmı); çağrı başına sistem prompt'u **büyür** (birleşik listeler). Net etki ölçülmeden bilinemez |
| Bakım | Düşük dosya sayısı, yüksek dosya karmaşıklığı |

### B — Dengeli (önerilen)
Bugünkü 15 agent ve 6 skill **adlarıyla** korunur. Değişen: sözleşmeler `description` ve rapor satırlarına taşınır;
2 ortak referans dosyası; kanca v2; isteğe bağlı kayıt kancası; `verify-change` model-çağrılabilir; kurallar (deney
olumluysa) yol-kapsamlı skill.

| | |
| --- | --- |
| Avantaj | Kırıcı değişiklik yok; her adım bağımsız birleştirilebilir ve geri alınabilir; çalışan güçlü yanlar (en az yetki, VERDICT, profil) aynen kalır; bulguların P0-P1'lerinin tamamını kapatır |
| Dezavantaj | 15 açıklamanın sürekli maliyeti sürer (~1,1k token, ölçüm); çakışan denetim maddeleri yönlendirme cümleleriyle yönetilir, ortadan kalkmaz |
| Token etkisi (beklenti) | Statik yük ~aynı (+3 skill açıklaması, −`Logging` paragrafları); dinamik maliyette azalma beklenir (daha az gereksiz delegasyon ve yeniden çağırma) — **ölçülecek** (E-1, E-3) |
| Bakım | +2 referans dosyası, +1 küçük kanca, daha büyük kanca testi listesi |

### C — Gelişmiş
B'ye ek: koordinatör agent (görev parçalama ve agent sıralama), `SubagentStop` ile hüküm/`STATUS` zorlaması,
`Stop` kancasıyla görev sonu doğrulama kapısı, `SubagentStart` ile profil enjeksiyonu, `PostToolUse` ile komut hatası
sınıflandırma, onay oranı telemetrisi, CI'da her PR'da eval.

| | |
| --- | --- |
| Avantaj | En yüksek deterministik güvence ve gözlemlenebilirlik |
| Dezavantaj | Koordinatör bir delegasyon katmanı ekler (her görevde ek bağlam); `Stop`/`SubagentStop` bloklamaları döngü riski taşır ve kullanıcıyı kilitleyebilir; birkaç kanca alanı canlıda doğrulanmamış; tek kişilik bakım için ağır; Codex'te karşılığı yok → iki istemci arasındaki davranış farkı büyür |
| Token etkisi (beklenti) | Artar (koordinatör + bloklama sonrası ek turlar); karşılığında hata oranı düşebilir — veri yok |
| Bakım | Yüksek |

### Seçim: **B**
Gerekçe: (1) Statik ölçümler sorunun bileşen sayısı değil bağlantılar olduğunu gösteriyor: sürekli yük yalnız ~1,5k
token. (2) A'nın kazancı küçük ve ölçülmemiş, bedeli tüm adların kırılması. (3) C'nin ek güvenceleri bugün hiçbir
ölçümle gerekçelendirilemiyor; önce B'nin kayıt kancası veri üretmeli. C'den yalnız bir parça, veri gösterirse sonradan
alınabilir: `SubagentStop` hüküm zorlaması (I-03).

## 3. Hedef mimari

Diyagram: [05-integration-analysis.md](05-integration-analysis.md) §7.

```
plugins/kg-devkit/
├── .claude-plugin/plugin.json        + license, repository, keywords
├── agents/                (15)       description = ne zaman + hangi girdi; rapor = STATUS | VERDICT
├── skills/
│   ├── verify-change/                model çağırabilir
│   ├── release/ rollback/ add-migration/ live-check/ browser-test/      manuel
│   └── test-discipline/ docs-maintenance/ ops-safety/                   (E-4 olumluysa) paths + user-invocable:false
├── references/
│   ├── finish-gate-default.md        profil gate'i yoksa
│   └── review-packet.md              çağıran ↔ agent devir sözleşmesi
└── hooks/
    ├── hooks.json                    timeout; python yedeği
    ├── guard-infra.py                belirteç tabanlı (v2)
    └── agent_run_log.py              SubagentStart/Stop → ${CLAUDE_PLUGIN_DATA}/agent-runs.jsonl
```

Sorumluluk sınırları:

| Katman | Sorumluluk | Sorumlu olmadığı |
| --- | --- | --- |
| Agent | Bir rolün yöntemi ve denetim listesi; kendi çıktısının durumu | Ne zaman çağrılacağına karar vermek; başka agent başlatmak; kullanıcı onayı almak |
| Skill | Çok adımlı, yetki gerektiren iş akışı; hangi reviewer'ın gerektiğine gate ile karar | Rolün ayrıntılı denetim listesi (agent'ta kalır) |
| Referans | Birden çok skill/agent'ın paylaştığı sözleşme | Akış |
| Hook | Yargı gerektirmeyen, yanlış pozitifi ucuz, kaçırması pahalı kontroller; kayıt | Kod kalitesi, test yeterliliği, proje komutları |
| Profil | Proje gerçekleri ve **ek** sınırlar | Kit kurallarını gevşetmek (I-05) |

## 4. Kaldırılması önerilenler

| Ne | Koşul | Bulgu |
| --- | --- | --- |
| 15 agent'taki `Logging:` paragrafı | Kayıt kancası devreye girdikten sonra | A-06 |
| `browser-test` skill'indeki yinelenen hedef kuralları (satır 18-22) | Agent'taki sürüm tek kaynak | S-03 |
| Skill'lerdeki `user-invocable: true` | — | S-05 |
| `plugins/kg-devkit/analysis/` (bu raporlar) | İncelendikten sonra `docs/analysis/`'e taşınır | M-01 |

Kaldırılması önerilen agent, skill veya kanca **yoktur**.

## 5. Birleştirilmesi önerilenler

Bileşen birleştirmesi önerilmez. Birleştirilen **içeriktir**:

| İçerik | Bugün | Hedef |
| --- | --- | --- |
| Reviewer tetikleme ve bloklama kuralı | 3 skill'de ayrı paragraflar | `references/finish-gate-default.md` |
| Reviewer girdisi ve yazar çıktısı | 6+6 agent gövdesi, 3 skill | `references/review-packet.md` |
| Legacy `Release` → `Production` geri düşme paragrafı | 3 skill | Tek cümle + profil şablonuna atıf (şablon satır 38-41 zaten tanımlıyor) |

Veri gelince yeniden değerlendirilecek adaylar: iki test-developer; `performance` + `observability` (yalnız
`agent-runs.jsonl` ikisinin de nadiren çağrıldığını gösterirse).

## 6. Yeniden yazılması gerekenler

| Bileşen | Kapsam | Örnek |
| --- | --- | --- |
| `hooks/guard-infra.py` | Tamamı (aynı sözleşme) | [guard_infra_v2.py](../../plugins/kg-devkit/hooks/guard-infra.py) |
| `scope-advisor` | `description` + "What to return" | [örnek](../../plugins/kg-devkit/agents/scope-advisor.md) |
| 6 reviewer + architect | Yalnız `description` ve giriş paragrafı | [örnek](../../plugins/kg-devkit/agents/database-reviewer.md) |
| 6 yazar agent | Yalnız "Return" paragrafı | [review-packet](../../plugins/kg-devkit/references/review-packet.md) |
| `verify-change`, `release` | Gate adımı | [örnek](../../plugins/kg-devkit/skills/verify-change/SKILL.md) |
| `rollback` | Adım 1 ve 6'daki atıf | S-01 |

## 7. Yeni eklenmesi önerilenler

| Bileşen | Tür | Öncelik | Ayrıntı |
| --- | --- | --- | --- |
| `references/finish-gate-default.md` | Referans | P1 | N-1 |
| `references/review-packet.md` | Referans | P1 | N-2 |
| `hooks/agent_run_log.py` | Hook | P2 | N-3 |
| 3 yol-kapsamlı skill (kuralların taşınması) | Skill | P2, koşullu | N-4 |
| Eval seti (`evals/`) | Test | P1 | [11](11-test-strategy.md) §3 |

Yeni agent önerilmez ([09](09-recommendations.md) §2).

## 8. Token optimizasyonu

Önce ölç, sonra kes. Sıra ve yöntem: [07-performance-optimization.md](07-performance-optimization.md) §4-5. Özet:
delegasyon sayısını azalt (A-02, I-01) → yeniden çağırmayı azalt (A-01) → diff'i yolla paylaş ve reviewer'ları paralel
başlat → profil çift okumasını deneye göre kaldır → model katmanını deneye göre ayarla. Metin kısaltma en sonda gelir.

## 9. Otomasyon fırsatları

| Fırsat | Mekanizma | Durum |
| --- | --- | --- |
| İş bitiminde doğrulama | Model-çağrılabilir `verify-change` | Öner (S-02) |
| Reviewer tetikleme | Varsayılan gate tablosu | Öner (I-01) |
| Agent çalıştırma kaydı ve metrikler | `SubagentStart/Stop` kancası | Öner (N-3) |
| Mekanik agent lint'i | CI betiği | Öner (T-02) |
| Token eşiği | `claude plugin details` CI adımı | Öner (P3) |
| Profil üretme | Manuel skill olarak paketleme | Değerlendir (P3) |
| Format/lint, test gereksinimi, büyük dosya engeli, `Stop` kapısı | Kanca | **Önerilmez** ([06](06-security-reliability.md) §4) |

## 10. Güvenlik ve doğrulama iyileştirmeleri

1. Kanca kapsamı ve isabeti: H-01, H-02, H-03, H-07, I-04.
2. Kanca dayanıklılığı: H-05 (`timeout`, girdi doğrulama), H-06 (yorumlayıcı yedeği).
3. Onay mesajında agent adı: A-04.
4. "Profil gevşetemez" cümlesi tüm skill'lerde: I-05.
5. Yazar agent'larda `STATUS`: A-03; reviewer girdisi: A-01.
6. Belirsiz kalan çalışma zamanı davranışlarının canlı doğrulaması: H-04 (HT-9, HT-10).

## 11. Uygulama planı

Fazlar ve bağımlılık grafiği: [10-improvement-roadmap.md](10-improvement-roadmap.md) §2. İlk PR adayları (hepsi küçük,
kırıcı değil): aynı dosya §3.

## 12. Nihai sorulara kısa cevaplar

| Soru | Cevap |
| --- | --- |
| Nasıl daha akıllı çalışır? | Kararı verenin (ana oturum) gördüğü metne tetik ve girdi koşullarını yazarak; reviewer tetiklemeyi profile bağımlı olmaktan çıkarıp varsayılan bir tabloya bağlayarak |
| Hangi agent'lar gerçekten gerekli? | 15'i de ayrık bir role sahip. En güçlü gerekçeli olanlar: dört "geçit" reviewer'ı (database, tenant-security, api-contract, dependency), iki developer, `devops-engineer` |
| Hangileri gereksiz? | Kanıtla "gereksiz" denebilecek agent yok. En zayıf gerekçeli: tek müşterili projelerde `scope-advisor` (bugün yine de çağrılıyor → A-02) ve gate'te adı geçmeyen projelerde `performance`/`observability`. Kullanım verisi olmadan kaldırma önerilmez |
| Hangi skill'ler eksik? | Yeni yetenek değil, taşıma: disiplin kuralları plugin içinde değil (I-02). Ayrıca modelin çağırabildiği bir doğrulama skill'i (S-02) |
| Hangi hook'lar otomasyonu iyileştirir? | Mevcut kancanın yeniden yazımı ve bir kayıt kancası. Başka kanca önerilmez |
| Ne gereksiz token tüketiyor? | Statik olarak çok az şey (~1,5k sürekli). Olası dinamik kaynaklar: `scope-advisor` boş çağrıları, girdisiz reviewer turları, diff'in her prompt'ta tekrarı, profilin çift okunması, `opus` katmanı. Hiçbiri ölçülmedi |
| Koordinasyon nasıl iyileşir? | Tek inceleme paketi + paralel reviewer + `STATUS`/`VERDICT` satırları; koordinatör agent olmadan |
| Yanlış karar nasıl azalır? | Varsayılan gate, girdi sözleşmesi, `NEEDS:` satırı, eval seti ile regresyon ölçümü |
| En az eforla en yüksek fayda? | [10](10-improvement-roadmap.md) §3'teki altı küçük değişiklik + kanca v2 |
| Sıfırdan tasarlansaydı? | Aynı üç fikir korunurdu. Farklı yapılacaklar: (1) sözleşmeler baştan `description` ve rapor satırlarında; (2) varsayılan gate kit'te, profil yalnız geçersiz kılar; (3) kurallar baştan plugin içinde yol-kapsamlı skill; (4) `Logging` yerine baştan kayıt kancası; (5) kanca baştan belirteç tabanlı ve test listesi senaryo gruplarıyla; (6) ilk agent'tan itibaren eval seti; (7) agent adlarında alan-özgü "tenant" yerine genel `security-reviewer`. Agent sayısı muhtemelen 10-12 ile başlar, ihtiyaç kanıtlandıkça bölünürdü |
