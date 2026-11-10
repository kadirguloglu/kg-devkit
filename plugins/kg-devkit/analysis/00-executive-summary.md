# 00 — Yönetici özeti

**Kapsam:** kg-devkit v0.8.9 (`6b14d73`), `plugins/kg-devkit/` altındaki 15 agent, 6 skill, 1 kanca (1 olay, 1 betik),
3 yapılandırma dosyası; ilişkili 3 kural, dokümanlar, derleme/test betikleri ve CI. Analiz salt-okumadır: mevcut hiçbir
dosya değiştirilmedi, yalnız `analysis/` oluşturuldu.

**Yöntem:** tüm plugin dosyaları satır satır okundu; kanca 115 ek senaryo, bozuk girdi ve süre ölçümüyle sınandı;
`claude plugin validate` ve `claude plugin details` çalıştırıldı; yedi resmi doküman sayfasıyla karşılaştırıldı.
**Yapılmayan:** agent ve skill'ler gerçek bir projede çalıştırılmadı; kanca canlı oturumda gözlemlenmedi. Bu nedenle
seçim doğruluğu, görev başına token ve yeniden çalışma oranı ölçülmedi ve bu raporlarda tasarruf yüzdesi yoktur.

## Genel kalite puanı: 71 / 100 (statik incelemeye dayalı tahmin)

| Alan | Puan | Gerekçe |
| --- | ---: | --- |
| Agent tasarımı | 77 | En az yetki, net kapsam dışı cümleleri, `VERDICT` protokolü güçlü; çağıran sözleşmesi ve yazar agent bitiş durumu zayıf |
| Skill tasarımı | 78 | Yetki sınırları ve kanıt disiplini çok iyi; bir kırık atıf, tutarsız gate davranışı, modelin çağırabildiği skill yok |
| Hook | 52 | Doğru olay ve karar biçimi, fail-open, CI testi; ancak yaygın biçimleri kaçırıyor ve zararsız komutları soruyor |
| Entegrasyon | 62 | Reviewer tetikleme varsayılanı yok; kurallar plugin ile gelmiyor |
| Test ve ölçüm | 50 | Kanca ve eşlik testleri var; davranış testi ve ölçüm yok |
| Doküman ve dağıtım | 86 | Tutarlı, dürüst sınır beyanları, otomatik sürüm, Codex eşliği CI'da |

## En kritik 10 bulgu

Tam liste (35 bulgu: 1 P0, 10 P1, 16 P2, 8 P3): [10-improvement-roadmap.md](10-improvement-roadmap.md).

| # | ID | Öncelik | Özet |
| --- | --- | --- | --- |
| 1 | H-01 | P0 (koşullu) | Kanca `helm -n prod uninstall`, `terraform -chdir=… destroy`, `docker --context prod compose up` ve çok satırlı `kubectl` komutlarını görmüyor (25 senaryodan 3'ü yakalandı) |
| 2 | H-02 | P1 | Bulut secret okuma ve `stop/deploy/sync` fiilleri kapsam dışı (27/27 kaçtı) |
| 3 | H-03 | P1 | Zararsız 36 komuttan 24'ü onaya düşüyor (`grep 'kubectl apply'`, `--help`, `gcloud run … describe`) |
| 4 | A-01 | P1 | Reviewer'ların ihtiyaç duyduğu girdi, çağıranın göremediği agent gövdesinde yazılı |
| 5 | I-01 | P1 | Reviewer tetikleme yalnız tüketici profilinde; profilde gate yoksa `release` reviewer'sız commit edebilir |
| 6 | A-02 | P1 | `scope-advisor` her özellik/düzeltmede tetiklenecek biçimde tanımlı; ana oturuma yönelik zorunluluğu ana oturum göremez |
| 7 | S-01 | P1 | `rollback`, modelin yükleyemeyeceği `live-check` skill'ine atıf yapıyor |
| 8 | A-03 | P1 | Yazar agent'larda bitiş durumu yok; başarısız iş "tamamlandı" gibi okunabilir |
| 9 | I-02 | P1 | Test/doküman/ops kuralları plugin ile gelmiyor; varsayılan kurulumda ana oturum kuralsız |
| 10 | T-01 | P1 | Davranış testi yok; skill'ler ve tarayıcı testçisi hiç uçtan uca çalıştırılmamış |

## En fazla fayda sağlayacak 10 iyileştirme

1. Kancayı belirteç tabanlı ayrıştırıcıyla yeniden yaz ([prototip](proposals/hooks/guard_infra_v2.py); resmi 106 örnek + 115 ek senaryo geçiyor).
2. Reviewer ve danışman `description`'larına "ne zaman" ve "hangi girdi" yaz.
3. Kit'e varsayılan Finish gate tablosu ekle; üç skill ona düşsün.
4. Tek inceleme paketi (diff dosya yoluyla) ve yazar agent'larda `STATUS` bloğu.
5. `scope-advisor` tetiğini `Scope mechanisms` varlığına bağla; soruyu dönen rapora koy.
6. `rollback` → `live-check` atfını dosya yoluna çevir.
7. `hooks.json`'a `timeout` ve `python` yedeği.
8. Küçük bir `claude plugin eval` seti (agent seçimi, protokol, skill akışı).
9. `verify-change`'i modelin çağırabileceği hale getir.
10. Alt-agent kayıt kancası: sıfır token, metriklerin ham verisi; ardından `Logging` paragraflarını kaldır.

## Bileşen kararları

- **Kaldır:** agent/skill/kanca yok. İçerik olarak: `Logging` paragrafları (kayıt kancasından sonra), `browser-test`'teki yinelenen hedef kuralları.
- **Birleştir:** bileşen yok. Üç skill'de tekrar eden gate ve devir kuralları iki referans dosyasında birleşir.
- **Böl:** yok.
- **Değiştir (REPLACE):** `guard-infra.py` (aynı sözleşme); kurallar → yol-kapsamlı skill (deney olumluysa).
- **Yeni:** 2 referans dosyası, 1 isteğe bağlı kayıt kancası, eval seti. **Yeni agent yok.**

Ayrıntı: [09-recommendations.md](09-recommendations.md) §3, mimari seçenekler: [12-architecture-proposals.md](12-architecture-proposals.md).

## Token ve performans

Ölçülen statik yük küçük: plugin her oturuma ~1.465 token ekliyor; kanca Bash çağrısı başına ~23 ms. Kazanç metin
kısaltmada değil, gereksiz delegasyon ve yeniden çağırma turlarında aranmalı; bunlar için ölçüm yöntemi ve altı deney
[07-performance-optimization.md](07-performance-optimization.md)'de.

## Kabul kriterleri

| Kriter | Durum | Not |
| --- | --- | --- |
| Bütün mevcut agent'lar incelendi | Tamamlandı | 15/15 tam okundu ([02](02-agents-analysis.md)) |
| Bütün skill'ler ve referansları incelendi | Tamamlandı | 6/6; referans dosyası yok ([03](03-skills-analysis.md)) |
| Bütün hook olayları ve betikleri değerlendirildi | Kısmen tamamlandı | Betik ve yapılandırma tam; canlı oturumda tetiklenme gözlemlenmedi ([04](04-hooks-analysis.md)) |
| Manifest ve yapılandırma tutarlılığı | Tamamlandı | `validate` geçti; `details` envanteri dosyalarla uyumlu ([01](01-project-inventory.md)) |
| Sorumluluk çakışmaları belirlendi | Tamamlandı | A-09, [05](05-integration-analysis.md) §4 |
| Mevcut ve önerilen mimari diyagramları | Tamamlandı | [05](05-integration-analysis.md) §2, §7; [10](10-improvement-roadmap.md) §2 |
| Bulgular dosya referanslarıyla desteklendi | Tamamlandı | Yol ve satır; kanıt türü Ö/K/D olarak işaretli |
| Güvenlik ve performans riskleri | Kısmen tamamlandı | Statik ve kanca ölçümleri var; dinamik token/performans ölçülmedi |
| Önceliklendirilmiş plan | Tamamlandı | [10](10-improvement-roadmap.md) |
| Markdown bağlantıları kontrol edildi | Tamamlandı | Betikle: göreli bağlantıların tamamı mevcut dosyaya gidiyor |

## Doğrulanamayan ve açık konular

1. `ask` kararının arka plan/fork agent'ta ve `bypassPermissions`/`dontAsk` modunda davranışı (H-04).
2. Alt-agent'ların profili zaten bağlamda görüp görmediği (A-05, deney E-2).
3. Skill frontmatter'ında `paths` ve `disallowed-tools` davranışı (I-02, S-04, deney E-4).
4. `disable-model-invocation` skill açıklamalarının sürekli bağlam maliyeti: CLI ~370 token gösteriyor, doküman sıfır diyor (D-03).
5. `SubagentStop` girdi alanlarının adları (kayıt kancası örneği için).
6. Windows, Codex ve Claude in Chrome davranışları (bu ortamda sınanamadı).
7. Resmi doküman bulgularının bir kısmı birebir metinle değil özetle doğrulandı; [08-best-practices.md](08-best-practices.md) bunları **[Ö]** ile işaretler.
8. Başka açık kaynak plugin'lerle karşılaştırma yapılmadı.

## Bu raporların konumu hakkında (M-01)

İstek gereği raporlar `plugins/kg-devkit/analysis/` altındadır. Plugin dizininin tamamı kurulumda kullanıcı
önbelleğine kopyalandığı için bu dosyalar plugin'i kuran herkese dağıtılır; ayrıca `main`'e birleştirilirse sürüm artar
ve repo bakım kancası `plugins/**` değişikliği olarak görür. İncelendikten sonra `docs/analysis/`'e taşınması önerilir.

## Rapor dizini

| Dosya | İçerik |
| --- | --- |
| [01-project-inventory.md](01-project-inventory.md) | Dosya ağacı, bileşen envanteri, çalıştırılan komutlar |
| [02-agents-analysis.md](02-agents-analysis.md) | Agent bulguları, puanlar, koordinasyon |
| [03-skills-analysis.md](03-skills-analysis.md) | Skill bulguları, puanlar, kurallar |
| [04-hooks-analysis.md](04-hooks-analysis.md) | Kanca envanteri, ölçümler, yeniden yazım karşılaştırması |
| [05-integration-analysis.md](05-integration-analysis.md) | Akışlar, çelişkiler, mevcut ve hedef diyagramlar |
| [06-security-reliability.md](06-security-reliability.md) | Tehdit modeli, senaryo riskleri, kancaya konmaması gerekenler |
| [07-performance-optimization.md](07-performance-optimization.md) | Taban değerler, metrikler, deneyler |
| [08-best-practices.md](08-best-practices.md) | Resmi dokümanla karşılaştırma, doğrulama düzeyleri |
| [09-recommendations.md](09-recommendations.md) | Yeni bileşenler, KEEP/IMPROVE kararları, puanlama |
| [10-improvement-roadmap.md](10-improvement-roadmap.md) | Bulgu tablosu (ID kaynağı), fazlar |
| [11-test-strategy.md](11-test-strategy.md) | Kanca, eval ve lint test senaryoları |
| [12-architecture-proposals.md](12-architecture-proposals.md) | A/B/C mimarileri, hedef yapı, nihai cevaplar |
| [proposals/](proposals/README.md) | Örnek kanca, agent, skill, referans ve test dosyaları (uygulanmadı) |
