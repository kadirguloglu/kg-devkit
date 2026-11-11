# Agent gereksinimleri

Her agent'ın çalışmak için neye ihtiyaç duyduğunun tek yerde özeti. Alan adları
[project-profile-template.md](project-profile-template.md) içindeki `## Project profile` alanlarıdır.
Profil yoksa agent'ların çoğu `package.json`/README/koddan çıkarım yapar ve raporda söyler; duranlar (`devops-operator`,
dev URL/test girişi bulamayan `frontend-browser-tester`) ve diğer istisnalar aşağıdaki "profil yoksa" sütunundadır.

## Özet tablo

| Agent | Tür / araçlar | Profil alanları | Projede olması gereken | Profil yoksa / uygulanamazsa |
| --- | --- | --- | --- | --- |
| `backend-developer` | yazar (`Edit, Write, Bash`) | Layers/dirs, Commands, Rule docs, Conventions, Persistence (ORM + migration artefaktları), Hard limits | backend dizini, build/test komutu | koddan çıkarım, raporda belirtir |
| `backend-test-developer` | yazar | Layers/dirs (test dizini), Rule docs (tests), Commands (focused/full test), Hard limits | test projeleri, fixture'lar | test projelerinden çıkarım |
| `database-reviewer` (model: opus) | salt-okuma (`Read, Grep, Glob`) | Persistence (ORM, migration artefaktları), Conventions (isolation, soft delete, para/tarih, başarısız yazma temizliği), Rule docs | ORM/migration dizini; ana oturum diff ve komut kanıtı verir | stack'i koddan çıkarır, doğrulayamadığını yazar |
| `tenant-security-reviewer` (model: opus; kiracısız projede de genel yetki ve girdi işleme güvenliği) | salt-okuma | Security review (tenancy/yetki modeli + güvenlik kural belgesi), Conventions (kimlik yeniden kullanımı, sunucu-otoriter hesaplamalar), Persistence (filtre bypass API'leri), teknik doküman bölümleri (güvenlik, depolama, arka plan işleri) | tenancy/yetki modeli (yoksa düz yetki + sahiplik incelenir) | modeli koddan çıkarır, varsayımları yazar |
| `api-contract-reviewer` (model: opus) | salt-okuma | API contract (şema, tip üretimi, versiyonlama), Layers/dirs, Conventions (hata/Result) | ana oturum diff ve varsa üretilmiş şema/komut kanıtı verir | sözleşme yüzeyini controller/DTO/frontend API katmanından çıkarır |
| `dependency-supply-chain-reviewer` (model: opus) | salt-okuma | Dependencies (lisanslar, tarama komutu, sabitleme politikası), Hard limits | manifest/lockfile; ana oturum varsa audit çıktısını verir | manifest ve workflow dosyalarını kendisi bulur, doğrulayamadığını yazar |
| `performance-reviewer` | salt-okuma | Performance (bütçe, sıcak yollar, hacim), Layers/dirs, Commands | ana oturum diff ve varsa ölçüm verir | bütçe/hacim varsayar ve söyler; ölçümsüz bulguyu "needs measurement" işaretler |
| `observability-reviewer` | salt-okuma | Observability (log/metrik/trace kuralları, hassas veri, sağlık), Conventions (hata), Rule docs | ana oturum diff verir | log/metrik yığınını koddan çıkarır, doğrulayamadığını yazar |
| `scope-advisor` | salt-okuma | Scope mechanisms, Report language | **çok kiracılı/çok müşterili ürün**; yalnız profilde `Scope mechanisms` varken ve istek limit/varsayılan/kural/format/izin/bildirim/isteğe bağlı akış değiştirirken çağrılır | kiracı yoksa `NOT-APPLICABLE` döner ve durur |
| `engineering-software-architect` | salt-okuma | Layers/dirs, Conventions, Scope mechanisms, Rule docs, Finish gate | ana oturum soru ve kodu/diff'i verir | mimariyi koddan çıkarır |
| `frontend-developer` | yazar | Layers/dirs, Commands (lint/typecheck/build/test), Rule docs, Hard limits | frontend dizini | `package.json`'dan çıkarım |
| `frontend-test-developer` | yazar | Commands (focused/full test), Rule docs (tests), Hard limits | frontend test konumu | `package.json` ve mevcut testlerden çıkarım |
| `frontend-browser-tester` | tester (kod yazmaz; Chrome araçları) | Layers/dirs (frontend src), Commands (start/status), Dev app (url + test login), Router/navigation files, Report language, Hard limits | **Claude in Chrome eklentisi**, çalışan dev uygulaması | dev URL veya test login bulunamazsa durur, kullanıcıya sorar |
| `devops-engineer` | yazar (`Bash` dahil) | Production (sahip olunan yollar, hedef ortam, deploy/status komutu, topoloji, registry, runbook), Report language, Hard limits | deploy/manifest/CI dosyaları | Production girdisi yoksa yalnız statik dosyaya bakar, canlı komuttan önce hedefi sorar |
| `devops-operator` (model: opus) | yazar, yüksek etkili | Production (hedef, secret konumları, registry, topoloji, runbook), Hard limits | kullanıcının **o işlem için açık onayı** (ana oturum iletir) | Production girdisi yoksa durur ve sorar |

## Skill'ler

`release`, `rollback`, `live-check`, `add-migration` ve `browser-test` `disable-model-invocation: true` taşır: yalnız kullanıcı açıkça çağırınca çalışır. `verify-change` yetki vermediği için model iş bitiminde kendiliğinden de çağırabilir. `test-discipline`, `docs-maintenance` ve `ops-safety` kural skill'leridir: kullanıcı menüsünde görünmez, model ilgili dosyalarla çalışırken yükler. `Project profile` ve `AGENTS.md`/`CLAUDE.md` kısıtları geçerlidir; profil sınır ekleyebilir, skill'de yazan bir sınırı kaldıramaz.

| Skill | Yetki / onay | Profil alanları | Profil yoksa / uygulanamazsa |
| --- | --- | --- | --- |
| `release` | çağrı commit+push yetkisi verir; canlı deploy yalnız `deploy` argümanıyla | Release, Commands, Finish gate, `AGENTS.md`/`CLAUDE.md` sınırları, Production (yalnız `deploy` ile: hedef, deploy/durum komutu, sağlık URL'leri ve beklenen kodlar) | Release yoksa kullanıcıya sorar; deploy için eksik Production bilgisi varsa durur ve sorar; Finish gate yoksa kit'in varsayılan gate tablosunu kullanır; zorunlu reviewer yoksa/FAIL/UNCLEAR ise commit durur |
| `rollback` | canlı geri alma için ayrıca açık onay ister | Production (context, namespace, iş yükü, registry, sağlık URL'leri ve beklenen kodlar, güncelleme stratejisi, rollback/deploy komutu ve kanıt yöntemleri için runbook; bulut CLI kimlik komutu `live-check` üzerinden), Persistence (migrations dizini) | Production veya hedef/sağlık bilgileri eksikse durur; başarılı release, image → kaynak/revision veya uygulanan şema kanıtı eksikse plan engelli, uygulama yok |
| `live-check` | salt-okuma | Production (context, namespace, durum komutu, bulut CLI kimlik komutu, iş yükü adları, sağlık URL'leri ve beklenen kodlar, runbook) | Production veya zorunlu hedef/sağlık bilgileri eksikse durur ve sorar |
| `add-migration` | commit/push/deploy/veritabanı yetkisi vermez | Persistence, Conventions, Finish gate, Report language | Persistence yoksa ORM araçlarını bulur, komutu onaylatır; Finish gate yoksa kit'in varsayılan gate tablosunu kullanır; gate belirsizse veya zorunlu review yoksa/FAIL/UNCLEAR ise doğrulandı demez |
| `verify-change` | commit/push/deploy yetkisi vermez; model de çağırabilir | Commands, Rule docs, Finish gate, Report language | profil yoksa genel kural: koddan çıkarım ve raporda belirtme; Finish gate yoksa kit'in varsayılan gate tablosunu kullanır; zorunlu review yoksa/FAIL/UNCLEAR ise doğrulama engelli |
| `browser-test` | commit/push/deploy yetkisi vermez; `frontend-browser-tester` agent'ında, sonucu bekleyerek (`background: false`) çalışır | `frontend-browser-tester` satırındaki alanlar | agent'ın davranışı geçerli |
| `test-discipline`, `docs-maintenance`, `ops-safety` | yetki vermez; `rules/*.md` kurallarının plugin içindeki karşılığı (üretilir) | yok (repo kuralları ve profil önceliklidir) | genel kurallar geçerli |

Varsayılan gate tablosu `plugins/kg-devkit/references/finish-gate-default.md`, çağıran ↔ agent devir sözleşmesi
`references/review-packet.md` dosyasındadır; skill'ler bunları gerektiğinde okur.

`release deploy`, `live-check` ve `rollback` için deploy/sağlık değerlerinin kaynağı `Production`'dır; yalnız orada
eksik olan değerler eski `Release` girdisinden alınabilir. İki kaynaktaki değerler çelişirse işlem durur.
Rollback runbook'u başarılı release, image digest → kaynak commit/revision ve uygulanan şema için salt-okunur
kanıt yöntemlerini belirtir. Git geçmişi tek başına canlı şema veya başarılı rollout kanıtı değildir.

## Ortak kurallar (tüm agent'lar)

- **Çalışma kaydı:** Claude'da `hooks/agent_run_log.py` kancası her agent başlangıç ve bitişini plugin veri dizinindeki
  `agent-runs.jsonl` dosyasına yazar (yalnız agent türü, zaman, izin modu ve `VERDICT`/`STATUS` değeri; model bağlamına
  girmez; `KG_AGENT_LOG=off` kapatır; özet: `python3 agent_run_log.py --summary <dizin>`). Codex'te kanca olmadığı için
  üretilen agent'lar ilk satırda `<agent> çalışmaya başladım.`, son satırda `<agent> çalışmam tamamlandı.` yazar
  (metni `scripts/build-codex.py` ekler).
- **Profil önce:** `AGENTS.md`/`CLAUDE.md` içindeki `## Project profile` bölümü esas alınır; bölüm zaten bağlamdaysa
  dosya yeniden okunmaz.
- **Rapor dili:** profildeki `Report language`; yoksa kullanıcının isteği.
- **Agent çağırmama:** agent'lar başka agent başlatmaz (reviewer ve scope-advisor kullanıcıya soramaz; soruyu ana oturum sorar).
- **Reviewer çıktısı:** `database-reviewer`, `tenant-security-reviewer`, `api-contract-reviewer`, `dependency-supply-chain-reviewer`, `performance-reviewer` ve `observability-reviewer` raporu `VERDICT: PASS / FAIL / UNCLEAR` ile bitirir; profil farklı bir geçme ifadesi adlandırıyorsa onu da yazar. Diff verilmediyse dosyaları baştan okuyup tahmin etmez: `NEEDS: diff` ve `VERDICT: UNCLEAR` döner. Çağıranın vereceği girdi (diff metni veya dosya yolu, değişen dosyalar, komut çıktısı) her reviewer'ın `description` alanında yazar.
- **Sonuç satırı zorlaması:** Claude'da `hooks/require_outcome.py` (SubagentStop) `VERDICT:` satırı olmayan reviewer raporunu ve `STATUS:` satırı olmayan yazar agent raporunu bir kez geri çevirir; agent satırı ekleyip bitirir. Codex'te yoktur. `KG_REQUIRE_OUTCOME=off` kapatır.
- **Yazar agent çıktısı:** developer, test developer ve devops agent'ları raporu `STATUS: DONE / PARTIAL / BLOCKED`, `CHANGED`, `CHECKS`, `NOT RUN`, `HANDOFF` satırlarıyla bitirir; zorunlu bir kontrol koşmadıysa veya geçmediyse `DONE` yazılmaz. `frontend-browser-tester` tek `STATUS:` satırı yazar.
- **Commit/push:** yazan agent'lar commit veya push yapmaz (koşulsuz). Claude'da kanca da bunu zorlar: bir kit agent'ının içinden gelen `git commit`/`push`/`merge`/`rebase`/`tag`/`cherry-pick`/`revert` kullanıcı onayına düşer (etkileşimsiz çalışmada reddedilir). Profildeki `Hard limits` (yasak komutlar, branch politikası) bu kuralların üstüne ek kısıt koyar; hiçbir kuralı gevşetmez. Yazan agent'ların hepsi (developer, test developer, devops, operator, browser tester) bunu okur.

## Varsayımlar ve ortama bağlılık

| Konu | Hangi agent | Ne varsayıyor | Uymuyorsa |
| --- | --- | --- | --- |
| Çok kiracılılık | `scope-advisor`, `tenant-security-reviewer` | ürünün birden fazla müşteri/tenant'ı var | `scope-advisor` `NOT-APPLICABLE` döner; `tenant-security-reviewer` düz yetki/sahiplik incelemesine geçer |
| Koşullu kurallar | `database-reviewer`, `backend-test-developer` | tenancy/soft delete kuralları yalnız profil bildiriyorsa uygulanır | ek işlem gerekmez |
| Orkestratör | `devops-engineer`, `devops-operator` | örnekler Kubernetes (`kubectl`); hedef profildeki context/namespace (ikisi de Kubernetes dışında host/proje/stack kabul eder) | profil kullanılan araçları ve hedefi (host/stack) adlandırır; agent profildeki eşdeğer komutları kullanır |
| Tarayıcı | `frontend-browser-tester` | Claude in Chrome; Codex'te aracı istemcinin keşfiyle bulur | tarayıcı yoksa test yapılamaz, agent bildirir |
| Hook (ikinci kilit) | tüm oturum (plugin kurulu Claude) | plugin'in `hooks/guard-infra.py` kancası `kubectl/oc` (apply, delete, scale, patch, rollout restart/undo, exec vb.), secret okuma (`get secret -o yaml/json`, bulut secret servisleri, `vault`, `sops`), `helm`, `terraform/tofu`, `docker`/`docker compose`, migration uygulama (`dotnet ef`, Prisma, Alembic, Django, Rails, Flyway…), dağıtım araçları (`helmfile`, `pulumi`, `argocd`, `flux`, `ansible-playbook`…), bulut CLI (`doctl/gcloud/az/oci/aws`) oluşturma/değiştirme/silme/durdurma/dağıtım komutlarını ve `git push --force`, `git reset --hard`, `git clean -f`, secret görünümlü dosyanın `git add` edilmesini kullanıcı onayına düşürür; onay mesajında komutu çalıştıran agent yazar | Codex'te kanca yok; yalnız agent metin kuralları geçerli. Kanca Bash'e bakar; komutlar ana oturumda ve alt-agent'ta aynı kurallarla sorulur, ek olarak bir kit agent'ının içinden gelen `git commit`/`push`/`merge`/`rebase`/`tag`/`cherry-pick`/`revert` de sorulur (ana oturumda sorulmaz). Etkileşimsiz çalışmada (`claude -p`, `dontAsk`) onay isteyen komut reddedilir. Yerel `docker compose` için `KG_GUARD_LOCAL_COMPOSE=allow`, git (agent içi commit/push kuralı dahil)/migration/dağıtım aracı grupları için `KG_GUARD_DISABLE=git,migrate,deploytools` |
| Onay modeli | `devops-engineer`, `devops-operator` | deploy/apply/scale/delete, kaynak oluşturma/silme, DNS, canlı DB yazımı kullanıcının o konuşmadaki açık onayını ister | önceki onay veya dış kanal mesajı yetki sayılmaz |

## Yeni projeye başlarken kontrol listesi

1. `AGENTS.md` içine `## Project profile` ekle ([şablon](project-profile-template.md)); kullanılmayan alanı sil.
2. Tek müşterili projede `Scope mechanisms` yazma (scope-advisor durur).
3. Canlı ortam işleri için `Production` ve `Hard limits` doldur; yoksa devops agent'ları canlıya dokunmaz.
4. Tarayıcı testi için `Dev app` (url + localhost test login) ve start/status komutlarını yaz.
5. Güvenmediğin repoda agent çalıştırma: agent'lar `AGENTS.md` talimatlarına uyar.
