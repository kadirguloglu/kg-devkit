# 07 — Performans ve token maliyeti

**Yöntem notu:** Bu analizde yalnız *statik* büyüklükler ve kanca süreleri ölçüldü. Kit gerçek bir projede
çalıştırılmadığı için görev başına token, delegasyon sayısı ve yeniden çalışma oranı **ölçülmedi**; bu rapor onlar için
yüzde veya tasarruf rakamı vermez, ölçüm yöntemini tarif eder.

## 1. Ölçülen başlangıç değerleri

| Metrik | Değer | Kaynak |
| --- | ---: | --- |
| Plugin'in her oturuma eklediği bağlam | ~1.465 token (tahmin) | `claude --plugin-dir plugins/kg-devkit plugin details kg-devkit` (CLI 2.1.322) |
| — bunun agent açıklamaları | ~1.080 token (15 agent, 50-110 arası) | aynı |
| — bunun skill açıklamaları | ~370 token (6 skill) | aynı; dokümanla çelişir, bkz. D-03 ([03](03-skills-analysis.md) §1) |
| Agent çağrı maliyeti (sistem prompt'u) | ~630 – ~1.400 token | aynı |
| Skill çağrı maliyeti | ~280 – ~1.500 token | aynı |
| Kanca bağlam maliyeti | 0 ("harness-only") | aynı |
| Agent dosyaları toplamı | 50.068 bayt | `wc -c` |
| — tekrarlanan `Logging` + `Hard limits` satırları | 6.274 bayt (%12,5) | `grep … \| wc -c` |
| Skill dosyaları toplamı | 20.711 bayt | `wc -c` |
| Kanca süreç süresi (her Bash çağrısı) | medyan 22,9 ms, p95 32,0 ms | 40 çalıştırma, Python 3.13, Linux konteyner |
| Kanca en kötü durum | 40 KB'de 2.992 ms; 100 KB'de 20.842 ms | [04](04-hooks-analysis.md) H-05 |
| Kanca testleri | 106 örnek, <1 sn | `scripts/test_guard_infra.py` |

Çıkarım: **statik yük küçüktür.** Kit'in sürekli maliyeti ~1,5k token; tek bir agent çağrısının sistem prompt'u en çok
~1,4k. Metin kısaltarak elde edilecek kazanç bununla sınırlıdır. Asıl maliyet dinamik davranıştadır (§2).

## 2. Maliyetin asıl kaynakları (nitel; ölçülmeli)

| # | Kaynak | Neden pahalı | Kanıt (statik) | Bulgu |
| --- | --- | --- | --- | --- |
| 1 | Gereksiz delegasyon | Her alt-agent yeni bağlam açar: sistem prompt'u + profil + okunan dosyalar + rapor | `scope-advisor` her özellik/düzeltmede tetiklenecek şekilde tanımlı; tek müşterili repoda `NOT-APPLICABLE` için bile başlar | A-02 |
| 2 | Yeniden çağırma turları | Reviewer girdisiz çağrılır → `UNCLEAR` → tekrar | Girdi sözleşmesi `description`'da yok; reviewer'da `Bash` yok | A-01 |
| 3 | Aynı diff'in tekrar taşınması | Diff ana oturumda bir kez, her reviewer prompt'unda bir kez daha | Skill'ler "Give the diff and command evidence" der (release:44); dosya yoluyla paylaşım tarif edilmemiş | A-01 |
| 4 | Profilin yeniden okunması | Bağlamda zaten varsa `Read` çıktısı ikinci kopya | 15/15 agent "First read …" | A-05 |
| 5 | `opus` reviewer'lar | Birim maliyet yüksek; 5 agent | Katman kararı ölçüme dayanmıyor | A-10 |
| 6 | Sıralı reviewer çalıştırma | Süre (token değil): bağımsız 2-4 inceleme art arda | Hiçbir dosyada "paralel" talimatı yok | I-01 çözümü |
| 7 | Tetiklenmemesi gereken reviewer | Gate yokken model "emin olmak için" hepsini çağırabilir **veya** hiçbirini çağırmaz | Varsayılan gate yok | I-01 |
| 8 | Tarayıcı testi | Ekran görüntüleri ve sayfa okumaları büyük; `maxTurns` yok | `frontend-browser-tester.md:5` | A-08 |
| 9 | Kanca kaynaklı kesinti | Token değil, insan süresi: gereksiz onaylar | 36 zararsız senaryonun 24'ü sorulur | H-03 |

Büyük dosyaların gereksiz okunması: agent metinleri bunu zaten sınırlar ("Read the feature's section of the technical
documents, not the entire document", `backend-developer.md:18-19`; "never read a large fixed range by default",
`frontend-developer.md:18-19`). Burada ek öneri yok; uyulup uyulmadığı transkriptten ölçülmeli.

## 3. Önerilen metrikler ve nasıl toplanacağı

| Metrik | Tanım | Kaynak | Araç |
| --- | --- | --- | --- |
| Görev başına token | Bir kullanıcı isteğinden sonuca kadar toplam giriş+çıkış | Oturum transkripti (`transcript_path`), `/cost` | Elle veya eval raporu |
| Görev başına araç çağrısı | `tool_use` sayısı | Transkript | Betik (jq) |
| Delegasyon sayısı | Görev başına `SubagentStart` | `agent-runs.jsonl` ([öneri](proposals/hooks/agent_run_log.py)) | `jq` ile gruplama |
| Agent başına süre | `SubagentStop.ts − SubagentStart.ts` (aynı `agent_id`) | aynı | aynı |
| Hüküm dağılımı | `PASS / FAIL / UNCLEAR / none` oranı | aynı (`outcome`) | aynı |
| Yeniden çalışma | Aynı oturumda aynı `agent_type`'ın ≥2 çağrısı; `UNCLEAR` sonrası tekrar | aynı | aynı |
| Skill seçim doğruluğu | Beklenen skill çağrıldı mı | `claude plugin eval` (`tool_used: Skill` grader'ı CLI yardımında geçiyor) | Eval seti |
| Agent seçim doğruluğu | Beklenen `agent_type` başladı mı | Eval + `agent-runs.jsonl` | Eval seti |
| Kanca süresi | Süreç başına ms | `test_guard_probe.py` süre satırı; CI'da eşik | Betik |
| Kanca onay oranı | `ask` / toplam Bash çağrısı; kullanıcı ret oranı | Kancaya isteğe bağlı sayaç (komut metni yazmadan) | Öneri, P3 |
| Başarısız görev oranı | `STATUS: PARTIAL/BLOCKED` + `VERDICT: FAIL` | `agent-runs.jsonl` | jq |
| Başarılı görev başına maliyet | Toplam maliyet / `DONE`+`PASS` ile biten görev | `/cost` + yukarıdaki | Elle |

`claude plugin eval` bir "no-plugin baseline arm" çalıştırıp skor farkını raporlar (CLI yardım metni). Bu, kit'in
gerçekten fark yaratıp yaratmadığını ölçmenin en ucuz yoludur; eval dosya biçimi için resmi doküman izlenmelidir
(bu analizde eval çalıştırılmadı).

## 4. Deneyler (değişiklikten önce/sonra karşılaştırma)

| ID | Soru | Yöntem | Karar kuralı |
| --- | --- | --- | --- |
| E-1 | `scope-advisor` tetik daraltması delegasyonu azaltıyor mu? | Tek müşterili örnek repoda 10 özellik/düzeltme istemi; `agent-runs.jsonl`'de `scope-advisor` sayısı, önce/sonra | Sonra = 0 bekleniyor; çok kiracılı repoda ilgili istemlerde hâlâ çağrılmalı |
| E-2 | Alt-agent profili zaten görüyor mu? | Profilli repoda bir reviewer'a "profildeki Report language değerini dosya okumadan söyle" | Söylüyorsa A-05 düzeltmesi uygulanır; söyleyemiyorsa mevcut talimat kalır |
| E-3 | Girdi sözleşmesi `UNCLEAR` turlarını azaltıyor mu? | 5 şema değişikliği; mevcut ve önerilen `description` ile reviewer çağrı sayısı | Görev başına reviewer çağrısı 1'e yaklaşmalı |
| E-4 | Yol-kapsamlı skill yükleniyor mu? | `test-discipline` örneğini `--plugin-dir` ile yükle; bir test dosyası düzenle; `/context` | Yükleniyorsa I-02 uygulanır |
| E-5 | `dependency-supply-chain-reviewer` için `sonnet` yeterli mi? | Aynı 5 diff, iki model; bulgu sayısı/isabet ve token | İsabet farkı yoksa `sonnet` |
| E-6 | Paralel reviewer süreyi düşürüyor mu? | 3 reviewer tetikleyen diff; sıralı ve tek turda | Duvar saati süresi |

## 5. Fırsatlar (öncelik sırasıyla; hiçbiri için yüzde verilmez)

1. Yanlış/gereksiz delegasyonu kes: A-02, I-01 (varsayılan gate "hiçbiri tetiklenmediyse reviewer çağırma" der).
2. Yeniden çağırma turlarını kes: A-01 (inceleme paketi, `NEEDS:` satırı).
3. Diff'i dosya yoluyla paylaş, tetiklenen reviewer'ları tek turda başlat.
4. Profil çift okumasını E-2 sonucuna göre kaldır.
5. Model katmanını E-5 ile gözden geçir; `frontend-browser-tester`'a `maxTurns` ekle.
6. Kanca yanlış pozitiflerini azalt (insan süresi): H-03.
7. `Logging` paragraflarını kancaya taşı: bayt olarak en büyük tekrar, token olarak en küçük kazanç; öncelik düşük,
   asıl gerekçe ölçüm verisi.
