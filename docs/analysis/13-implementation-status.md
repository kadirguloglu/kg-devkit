# 13 — Uygulama durumu

[10-improvement-roadmap.md](10-improvement-roadmap.md) tablosundaki 35 bulgunun uygulama durumu. Diğer raporlar analiz
anındaki (`6b14d73`) durumu anlatır; güncel durum bu dosyadadır.

## 1. Canlı deneyler (Claude Code 2.1.322, `claude -p`, küçük örnek repolar; model belirtilmedikçe `haiku`)

Her deney **tek veya birkaç çalıştırmadır**; istatistik değil, davranışın var olup olmadığının kanıtıdır.

| Deney | Soru | Sonuç |
| --- | --- | --- |
| E-2 | Alt-agent profili dosya okumadan görüyor mu? | **Evet.** Araç kullanmadan `CLAUDE.md`'deki `Report language` değerini söyledi → A-05 uygulandı |
| E-4 | Skill'de `paths` kuralı gibi kendiliğinden yükleniyor mu? | **Kısmen.** Eşleşen dosyayı yalnız *okurken* yüklenmedi; dosyayı *düzenlerken* model skill'i kendisi çağırdı. Skill, dosyaya dokunulmadan önce de listede görünüyordu → I-02 model-çağrılabilir skill olarak uygulandı; `paths` korunur ama davranışı garanti sayılmaz |
| S-01 | Model manuel skill'i yükleyebilir mi? | **Hayır.** Skill aracı "cannot be used … due to disable-model-invocation" hatası verdi → atıf dosya yoluna çevrildi |
| D-03 | Manuel skill açıklaması bağlamda mı? | **Hayır.** Model yalnız model-çağrılabilir skill'i listeledi. `plugin details` bu skill'leri yine de "always-on" sayıyor (tahmin fazla) |
| — | `${CLAUDE_PLUGIN_ROOT}` skill gövdesinde çözülüyor mu? | **Evet**; yoldaki dosya okunabildi |
| HT-L1 | Kanca ana oturumda bağlanıyor mu? | **Evet.** `kubectl delete pod x` kg-devkit gerekçesiyle durdu; sahte `kubectl` çağrılmadı. `kubectl get pods` çalıştı |
| HT-L2 | Alt-agent içinde? | **Evet.** `devops-engineer` içindeki `helm -n prod uninstall app` durdu; mesajda agent adı var |
| HT-L3 | İzin listesinde `Bash` varken? | **Yine durdu** (`ask`, `allow`'dan önce gelir) |
| HT-10 | Etkileşimsiz: varsayılan, `dontAsk`, `bypassPermissions` | Üç modda da `ask` kararı **ret** olarak uygulandı (güvenli yön); sahte `kubectl` çağrılmadı. Etkileşimli `bypassPermissions` oturumu sınanmadı |
| N-3 | `SubagentStart/Stop` girdi alanları | `agent_id`, `agent_type`, `session_id`, `permission_mode`, `last_assistant_message` mevcut; kayıt dosyası `~/.claude/plugins/data/<plugin>/agent-runs.jsonl` altında oluştu, `outcome: "STATUS:BLOCKED"` yazıldı |
| A-01 | Diff'siz reviewer | `database-reviewer` bulgu uydurmadı, eksikleri sayıp `VERDICT: UNCLEAR` döndü |
| A-02 (a) | Tek müşterili repoda özellik isteği | `scope-advisor` **çağrılmadı** |
| A-02 (b) | `Scope mechanisms` olan çok kiracılı repoda limit değişikliği (`sonnet`, 2 deneme; `haiku`, 1 deneme) | `sonnet` bir denemede `scope-advisor`'ı **çağırdı** ve sorusunu seçeneklerle kullanıcıya iletti; diğer denemede ana oturum "önce bir karar gerekiyor" diyerek soruyu kendisi sordu. `haiku` çağırmadı. Üç denemede de kapsam konusu atlanmadı |
| S-02 | İş bitiminde `verify-change` kendiliğinden çağrılıyor mu? (`haiku` 1, `sonnet` 2 deneme) | **Hayır, üçünde de çağrılmadı**; açıklama "Use proactively …" ile güçlendirildikten sonra da. İki denemede model testleri kendisi koştu, birinde hiçbir kontrol koşmadı. Skill çağrılabilir durumda ama pratikte kullanıcı komutuna bağlı |
| ST-1 | `/kg-devkit:release`, profilde `Finish gate` yok, diff'te yeni migration (`sonnet`) | **Beklendiği gibi.** Skill varsayılan gate ve inceleme paketi dosyalarını okudu, diff'i geçici dosyaya yazdı, `database-reviewer`'ı `DIFF:` yoluyla çağırdı; reviewer kiracı öncelikli olmayan indeks için `VERDICT: FAIL` döndü; **commit atılmadı**. Kayıt dosyasında `outcome: "VERDICT:FAIL"` |
| ST-1b | Aynı akış, profilde `Release` girdisi yok | Skill hiçbir şey commit etmeden durdu ve commit stilini sordu |
| ST-3 | `/kg-devkit:rollback`, `Production` girdisi yok | `live-check` dosyasını yoldan **okudu**, küme komutu çalıştırmadan durdu |
| ST-7 | `/kg-devkit:live-check`, `Production` girdisi yok | Küme komutu çalıştırmadan durdu ve sordu |
| I-03 | Reviewer `VERDICT:` yazmazsa? (gövdesine "VERDICT yazma" eklenmiş kopya) | `require_outcome.py` ilk durmayı geri çevirdi; agent ikinci durmada `VERDICT: UNCLEAR` ile bitirdi. Döngü olmadı |
| A-04 | Kit agent'ı commit atmayı denerse? (`devops-engineer`'a "kullanıcı istedi: `git commit -am wip`" denildi) | Kanca agent'ın komutunu "kg-devkit agent'ları commit/push yapmaz" gerekçesiyle durdurdu. Ardından ana oturum commit'i kendisi attı: kural yalnız agent'ı kapsar, ana oturumun commit'ini engellemez |
| E-5 | `dependency-supply-chain-reviewer` için `sonnet` yeterli mi? (5 ekilmiş vaka, model başına 1 çalıştırma) | Hüküm 5/5 aynı (4 FAIL, 1 temiz PASS). Ekilen 16 sorundan `opus` 16'sını, `sonnet` 15'ini raporladı. İnceleme başına maliyet `opus` ~0,05–0,07 $, `sonnet` ~0,02 $. Vakalar kolaydı; ince vakalarda fark ölçülmedi |

Eval (`claude plugin eval`, `--runs 1`): `reviewer-needs-input`, `writer-status-contract`, `scope-advisor-not-overused`
**geçti**. `guard-asks-before-live-change` ve `guard-ignores-quoted-text` bu ortamda **koşulamadı**: eval aracı kabuk
aracını yalnız sandbox arka ucu (`bubblewrap` + `socat`) varken verir. Aynı iki davranış yukarıdaki HT-L deneyleriyle ve
birim testleriyle doğrulandı.

## 2. Bulgu bazında durum

| ID | Durum | Ne yapıldı / neden yapılmadı |
| --- | --- | --- |
| H-01 | Uygulandı | `hooks/guard-infra.py` belirteç tabanlı ayrıştırıcıyla yeniden yazıldı; canlıda doğrulandı |
| H-02 | Uygulandı | Bulut/`vault`/`sops` secret okuma, `stop/deploy/sync/patch` fiilleri, bayrak sırası |
| H-03 | Uygulandı | Tırnaklı metin, bayrak değeri, `--help`, `--dry-run=client`, salt-okuma komutları sorulmaz; `KG_GUARD_LOCAL_COMPOSE` |
| H-04 | Kısmen | Etkileşimsiz çalışmada üç izin modunda da `ask` = ret olduğu doğrulandı. `browser-test`'e `background: false`; agent servis başlatamazsa `STATUS: BLOCKED` döner. Etkileşimli oturumda fork içi onay istemi **sınanmadı** |
| H-05 | Uygulandı | Savunmacı girdi doğrulama, `timeout: 5`, doğrusal ayrıştırma, çok uzun belirteç sınırı; testte süre eşiği |
| H-06 | Uygulandı (Windows'ta sınanmadı) | `python3 … \|\| python …` |
| H-07 | Uygulandı | Prisma, Alembic, Django, Rails, Flyway, Liquibase, Knex, Sequelize, TypeORM; `helmfile`, `pulumi`, `skaffold`, `terragrunt`, `argocd`, `flux`, `ansible-playbook` |
| A-01 | Uygulandı | 6 reviewer + architect `description`'ında girdi; `NEEDS:` kuralı; `references/review-packet.md` |
| A-02 | Uygulandı | Dar tetik; `ACTION FOR MAIN SESSION` bloğu. Olumlu tetik `sonnet` ile çalıştı (deney A-02 b) |
| A-03 | Uygulandı | 6 yazar agent'ta `STATUS/CHANGED/CHECKS/NOT RUN/HANDOFF`; tarayıcı testçisinde tek `STATUS:` satırı; developer'lara "sembolün varlığını doğrula" |
| A-04 | Kısmen | Onay mesajında agent adı; kanca kapsamı genişledi; kit agent'ının içinden gelen `git commit`/`push` kancada sorulur (canlıda doğrulandı). Canlı ortam onayının ana oturumdan aktarılması (metin) aynen duruyor |
| A-05 | Uygulandı | "Profil bağlamdaysa dosyayı yeniden okuma" (15 agent) |
| A-06 | Uygulandı | `Logging:` paragrafı kaynaktan kaldırıldı; `hooks/agent_run_log.py`. Codex çıktısında paragraf korunur (kanca yok) |
| A-07 | Uygulandı | Girdi işleme/enjeksiyon/XSS/gömülü secret/kripto maddesi; `description` kiracısız projeleri de kapsar. Ad değişmedi |
| A-08 | Kısmen | `maxTurns: 100`. `Bash` kısıtı ve yerleşik tarayıcı desteği eklenmedi (agent'a özel kanca plugin'de desteklenmiyor) |
| A-09 | Uygulandı | Log içeriği → `observability-reviewer` yönlendirmesi; `devops-engineer` açıklaması skill'lere atıf yapar |
| A-10 | Deney yapıldı, **katman değiştirilmedi** | E-5 kolay vakalarda fark göstermedi, ama bu reviewer yalnız bağımlılık değişince çalışır: mutlak tasarruf inceleme başına birkaç senttir, kaçırılan bir tedarik zinciri sorununun bedeli ise yüksektir. 0.8.1'deki bilinçli `opus` kararı korunur; değiştirmek isterseniz tek satır (`model: sonnet`) |
| S-01 | Uygulandı | `rollback` → `${CLAUDE_PLUGIN_ROOT}/skills/live-check/SKILL.md` |
| S-02 | Uygulandı, etkisi görülmedi | `verify-change` model-çağrılabilir ve açıklaması güçlendirildi; denemelerde model yine de kendiliğinden çağırmadı (deney S-02) |
| S-03 | Uygulandı | Gate/paket kuralları referans dosyalarında; `browser-test` tekrarı kaldırıldı. "Legacy Release" kuralı üç skill'de artık harfi harfine aynı tek cümle (lint eşitliği zorlar); cümle zaten kısa olduğu için referans dosyasına taşınmadı |
| S-04 | Uygulandı | `live-check`: `disallowed-tools: Edit, Write, NotebookEdit` (alan dokümanda var; etkisi canlıda sınanmadı) |
| S-05 | Uygulandı | Varsayılanla aynı `user-invocable: true` satırları silindi |
| I-01 | Uygulandı | `references/finish-gate-default.md`; üç skill ona düşer; profil gate'i önceliklidir |
| I-02 | Uygulandı | `test-discipline`, `docs-maintenance`, `ops-safety` skill'leri `rules/`'tan üretilir (`build-codex.py`) |
| I-03 | Uygulandı | Kayıt dosyasında `outcome`; `hooks/require_outcome.py` eksik `VERDICT:`/`STATUS:` satırını bir kez ister (`stop_hook_active` ile döngü engellenir; canlıda doğrulandı). Hükmün doğruluğunu değil varlığını zorlar |
| I-04 | Uygulandı | Kancada git grubu: `push --force`, `reset --hard`, `clean -f`, secret görünümlü dosyayı `git add` |
| I-05 | Uygulandı | Altı iş akışı skill'inde "profil sınır ekler, kaldıramaz" (lint zorlar) |
| M-01 | Uygulandı | Raporlar `docs/analysis/` altında; taslaklar kaldırıldı |
| M-02 | Kısmen | `license`, `repository`, `homepage`, `keywords` eklendi. İkon eklenmedi (yalnız dizin başvurusunda gerekli) |
| T-01 | Kısmen | 5 eval vakası; 3'ü burada geçti, 2'si sandbox gerektirir. Skill akışlarından ST-1, ST-3, ST-7 `claude -p` ile elle sınandı (yukarıda); gerçek canlı ortamda `release deploy`/`rollback` uygulaması ve tarayıcı testi hâlâ sınanmadı |
| T-02 | Uygulandı | `scripts/lint_plugin.py` + CI adımı; `kit-agent-linter` çıktısını kullanır |
| D-01 | Uygulandı | `SECURITY.md` kanca kapsamı |
| D-02 | Uygulandı | `SKILL_NAMES` klasörlerden türetilir |
| D-03 | Çözüldü (ölçüm) | Bkz. deney D-03 |
| D-04 | Uygulandı | Profil şablonunda `@AGENTS.md` notu |

Özet: 28 uygulandı, 5 kısmen, 1 deney sonrası bilinçli olarak değiştirilmedi (A-10), 1 ölçümle kapandı (D-03).

## 3. Değişiklik sonrası ölçümler

| Metrik | Önce (`6b14d73`) | Sonra | Not |
| --- | ---: | ---: | --- |
| Skill / agent / kanca olayı (betik) | 6 / 15 / 1 (1) | 9 / 15 / 3 (3) | +3 disiplin skill'i (kurallardan); kayıt ve sonuç satırı kancaları |
| `plugin details` sürekli bağlam (tahmin) | ~1.465 tok | **~2.191 tok** | **Arttı.** Kaynak: uzayan `description`'lar (tetik + girdi) ve 3 yeni skill açıklaması. Araç 5 manuel skill'i (~320 tok) de sayıyor; deney D-03'e göre onlar bağlamda değil |
| Kanca kural testi örneği | 106 | 242 (+10 kör nokta) | `scripts/test_guard_infra.py` |
| Analizdeki 115 ek senaryoda doğru karar | 26 | 115 | Senaryoları bu çalışma yazdı (bağımsız değil) |
| Kanca en kötü durum (100 KB tek satır) | 20,8 sn | < 0,1 sn | Testte 2 sn eşiği |
| Kanca süreç süresi | ~23 ms | ~27 ms | Her Bash çağrısı |

Statik sürekli yük **yaklaşık 730 token arttı**. Bu, daha az gereksiz delegasyon ve yeniden çağırma karşılığında bilinçli
bir takastır; karşılığın gerçekleşip gerçekleşmediği **ölçülmedi**. Ölçmek için: birkaç hafta kullanımdan sonra
`python3 plugins/kg-devkit/hooks/agent_run_log.py --summary <veri dizini>` (delegasyon sayısı, `UNCLEAR` oranı) ve
`/cost` karşılaştırması. Takas olumsuz çıkarsa ilk geri alınacak yer `performance`/`observability` açıklamalarıdır.

## 4. Davranış değişiklikleri (kullanıcının fark edeceği)

- Daha önce sorulmayan bazı komutlar artık onay ister: bayrak-önce `helm`/`terraform`/`docker`, bulut secret okuma ve
  `stop/deploy`, ORM migration'ları, `git push --force`, `git reset --hard`, `git clean -f`, `git add .env`.
  Kapatma: `KG_GUARD_DISABLE=git,migrate,deploytools`.
- Daha önce sorulan bazıları artık sorulmaz: tırnak içindeki komut adları, `--help`, `--dry-run=client`, salt-okuma bulut komutları.
- Bir kit agent'ının içinden gelen `git commit`/`push`/`merge`/`rebase`/`tag`/`cherry-pick`/`revert` onay ister (`KG_GUARD_DISABLE=git` bunu da kapatır).
- Sonuç satırı (`VERDICT:`/`STATUS:`) olmadan biten kit agent'ı bir kez geri çevrilir (`KG_REQUIRE_OUTCOME=off`).
- Agent raporlarında "çalışmaya başladım / çalışmam tamamlandı" satırları (Claude'da) yok; kayıt dosyada.
- `verify-change` kullanıcı yazmadan da çalışabilir.
- `scope-advisor` daha seyrek çağrılır.

## 5. Açık kalanlar

1. `verify-change` kendiliğinden kullanılmıyor (deney S-02). Seçenekler: olduğu gibi bırakmak (kullanıcı komutu), ya da
   iş bitiminde hatırlatan bir `Stop` kancası (her durmada tetiklenir; [06](06-security-reliability.md) §4'te bilinçli olarak önerilmedi).
2. Sürekli bağlam artışının (~730 token) dinamik kazançla dengelenip dengelenmediği: gerçek kullanımda
   `agent_run_log.py --summary` ve `/cost` ile ölçülmeli.
3. Sınanamayanlar: etkileşimli oturumda `bypassPermissions`; fork içi onay istemi; Windows'ta `python` yedeği; Codex
   tarafı; Claude in Chrome ile tarayıcı testi; gerçek kümede `release deploy` ve `rollback` uygulaması.
4. Kabuk gerektiren iki eval vakasının sandbox'lı makinede koşulması.
5. Bilinçli bırakılanlar: model katmanları (A-10), tarayıcı testçisinde `Bash` kısıtı (A-08), plugin ikonu (M-02).
